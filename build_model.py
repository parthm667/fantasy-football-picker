#!/usr/bin/env python3
"""
Backtest 2025: how predictive were preseason projections vs the market (ADP),
and what did the season-outcome distribution around expectations look like?
Outputs model_params.json consumed by the draft engine.
"""
import json, re, unicodedata, math
from collections import defaultdict

SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}
ALIASES = {
    "kenny gainwell": "kenneth gainwell",
    "hollywood brown": "marquise brown",
    "chigoziem okonkwo": "chig okonkwo",
    "cameron ward": "cam ward",
    "gabe davis": "gabriel davis",
}
def norm(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", "", s)
    toks = [t for t in s.split() if t not in SUFFIXES]
    return ALIASES.get(" ".join(toks), " ".join(toks))

bt = json.load(open("data2/backtest.json"))
POS = ["QB", "RB", "WR", "TE"]

actual = {}
posmin = defaultdict(lambda: 1e9)
for a in bt["actual2025"]:
    actual[(norm(a["name"]), a["pos"])] = a["pts"]
    posmin[a["pos"]] = min(posmin[a["pos"]], a["pts"])

def get_actual(key, pos):
    # censored: drafted but not in top-N actuals => scored below the list floor
    return actual.get(key, 0.7 * posmin[pos])

# preseason positional ranks from ADP
adp_rank, adp_overall = {}, {}
cnt = defaultdict(int)
for a in bt["adp2025"]:
    key = (norm(a["name"]), a["pos"])
    cnt[a["pos"]] += 1
    adp_rank[key] = cnt[a["pos"]]
    adp_overall[key] = a["adp"]

proj = {(norm(p["name"]), p["pos"]): p["proj"] for p in bt["proj2025"]}
proj_rank = {}
by_pos_proj = defaultdict(list)
for (k, pos), v in proj.items():
    by_pos_proj[pos].append(((k, pos), v))
for pos, lst in by_pos_proj.items():
    lst.sort(key=lambda t: -t[1])
    for i, (key, _) in enumerate(lst):
        proj_rank[key] = i + 1

def spearman(pairs):
    # pairs: list of (a, b) -> spearman rho
    n = len(pairs)
    if n < 5: return None
    def ranks(vals):
        order = sorted(range(n), key=lambda i: vals[i])
        r = [0] * n
        for rank, i in enumerate(order): r[i] = rank + 1
        return r
    ra = ranks([p[0] for p in pairs]); rb = ranks([p[1] for p in pairs])
    d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1 - 6 * d2 / (n * (n * n - 1))

# ---------- OLS quadratic in log(rank) ----------
def fit_quad(xs, ys):
    n = len(xs)
    Sx = sum(xs); Sx2 = sum(x*x for x in xs); Sx3 = sum(x**3 for x in xs); Sx4 = sum(x**4 for x in xs)
    Sy = sum(ys); Sxy = sum(x*y for x,y in zip(xs,ys)); Sx2y = sum(x*x*y for x,y in zip(xs,ys))
    # solve [[n,Sx,Sx2],[Sx,Sx2,Sx3],[Sx2,Sx3,Sx4]] [a,b,c] = [Sy,Sxy,Sx2y]
    A = [[n,Sx,Sx2,Sy],[Sx,Sx2,Sx3,Sxy],[Sx2,Sx3,Sx4,Sx2y]]
    for i in range(3):
        p = A[i][i]
        for j in range(i+1,3):
            f = A[j][i]/p
            for k in range(i,4): A[j][k] -= f*A[i][k]
    c = A[2][3]/A[2][2]
    b = (A[1][3]-A[1][2]*c)/A[1][1]
    a = (A[0][3]-A[0][1]*b-A[0][2]*c)/A[0][0]
    return a,b,c
def quad(coef, x): return coef[0]+coef[1]*x+coef[2]*x*x

params = {}
print(f"{'pos':<4}{'n':>4} {'rho(ADP)':>9} {'rho(proj)':>10} {'bestW(proj)':>12} {'pBust':>7} {'sigma':>7}")
overall_pairs_adp, overall_pairs_proj, overall_triples = [], [], []

for pos in POS:
    keys = [k for k in adp_rank if k[1] == pos]
    rows = []
    for k in keys:
        act = get_actual(k, pos)
        rows.append((k, adp_rank[k], act))
    # Spearman: ADP rank vs actual (negate rank so higher=better)
    pr_adp = [(-r, a) for (_, r, a) in rows]
    rho_adp = spearman(pr_adp)
    both = [(k, r, a) for (k, r, a) in rows if k in proj_rank]
    pr_proj = [(-proj_rank[k], a) for (k, r, a) in both]
    rho_proj = spearman(pr_proj)
    overall_pairs_adp += pr_adp; overall_pairs_proj += pr_proj
    overall_triples += [(proj_rank[k], r, a) for (k, r, a) in both]

    # blend search on the joined subset
    bestW, bestRho = 0.5, -2
    for wi in range(0, 11):
        w = wi / 10
        pairs = [(-(w * proj_rank[k] + (1 - w) * r), a) for (k, r, a) in both]
        rho = spearman(pairs)
        if rho is not None and rho > bestRho: bestRho, bestW = rho, w

    # outcome distribution: iteratively-trimmed quadratic fit of actual vs log(rank)
    xs = [math.log(r) for (_, r, a) in rows]; ys = [a for (_, r, a) in rows]
    coef = fit_quad(xs, ys)
    for _ in range(2):
        keep = [(x, y) for x, y in zip(xs, ys) if y > 0.45 * max(20, quad(coef, x))]
        if len(keep) < 8: break
        coef = fit_quad([k[0] for k in keep], [k[1] for k in keep])
    resid = [(x, y / max(25, quad(coef, x))) for x, y in zip(xs, ys)]
    busts = [r for r in resid if r[1] < 0.5]
    pBust = len(busts) / len(resid)
    core = [math.log(min(2.6, r[1])) for r in resid if r[1] >= 0.5]
    mu = sum(core) / len(core)
    sigma = math.sqrt(sum((c - mu) ** 2 for c in core) / max(1, len(core) - 1))
    # bust-rate rank slope: early (top-18) vs late
    early = [r for r in resid if r[0] <= math.log(18)]
    late = [r for r in resid if r[0] > math.log(18)]
    pB_e = sum(1 for r in early if r[1] < 0.5) / max(1, len(early))
    pB_l = sum(1 for r in late if r[1] < 0.5) / max(1, len(late))
    params[pos] = {
        "pBust": round(pBust, 3), "pBustEarly": round(pB_e, 3), "pBustLate": round(pB_l, 3),
        "sigmaCore": round(sigma, 3),
        "rhoAdp": round(rho_adp, 3), "rhoProj": round(rho_proj, 3) if rho_proj else None,
        "bestW": bestW, "n": len(rows),
    }
    print(f"{pos:<4}{len(rows):>4} {rho_adp:>9.3f} {(rho_proj or 0):>10.3f} {bestW:>12.1f} {pBust:>7.2f} {sigma:>7.3f}")

# overall blend
bestW, bestRho = 0.5, -2
for wi in range(0, 21):
    w = wi / 20
    pairs = [(-(w * pr + (1 - w) * ar), a) for (pr, ar, a) in overall_triples]
    rho = spearman(pairs)
    if rho > bestRho: bestRho, bestW = rho, w
rho_adp_all = spearman(overall_pairs_adp); rho_proj_all = spearman(overall_pairs_proj)
print(f"\nOVERALL rho(ADP)={rho_adp_all:.3f} rho(proj)={rho_proj_all:.3f}  best blend w(proj)={bestW:.2f} rho={bestRho:.3f}")
params["_global"] = {"bestW": bestW, "rhoAdp": round(rho_adp_all,3), "rhoProj": round(rho_proj_all,3), "rhoBlend": round(bestRho,3)}
params["K"] = {"pBust": 0.05, "pBustEarly": 0.05, "pBustLate": 0.05, "sigmaCore": 0.12}
params["DST"] = {"pBust": 0.08, "pBustEarly": 0.08, "pBustLate": 0.08, "sigmaCore": 0.18}
json.dump(params, open("model_params.json", "w"), indent=1)
print("\nwrote model_params.json")
