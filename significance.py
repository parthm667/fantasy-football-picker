#!/usr/bin/env python3
"""
Significance tests for two proposed model features:
  H1 (durability): games missed in year N predicts games missed in year N+1
  H2 (handcuff):   RB backup production rises with starter games missed
Only features that pass (p < 0.05, meaningful effect) get implemented.
"""
import json, math, re, unicodedata
from collections import defaultdict

SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}
def norm(n):
    s = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return " ".join(t for t in s.split() if t not in SUFFIXES)

G = json.load(open("data2/games.json"))
HC = json.load(open("data2/handcuffs.json"))

def missed(g): return max(0, 17 - min(17, g))

def pearson(x, y):
    n = len(x)
    mx, my = sum(x)/n, sum(y)/n
    sxy = sum((a-mx)*(b-my) for a, b in zip(x, y))
    sxx = sum((a-mx)**2 for a in x); syy = sum((b-my)**2 for b in y)
    if sxx == 0 or syy == 0: return 0, 1
    r = sxy / math.sqrt(sxx*syy)
    t = r * math.sqrt((n-2) / max(1e-9, 1-r*r))
    # two-sided p from t (normal approx fine at n>60)
    p = 2 * (1 - phi(abs(t)))
    return r, p

def phi(z):  # standard normal CDF
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))

def ols(x, y):
    n = len(x); mx, my = sum(x)/n, sum(y)/n
    sxx = sum((a-mx)**2 for a in x)
    b = sum((a-mx)*(c-my) for a, c in zip(x, y)) / sxx
    a0 = my - b*mx
    resid = [c - (a0 + b*a) for a, c in zip(x, y)]
    s2 = sum(r*r for r in resid) / (n - 2)
    se_b = math.sqrt(s2 / sxx)
    t = b / se_b
    p = 2 * (1 - phi(abs(t)))
    return a0, b, se_b, t, p

# =============== H1: durability persistence ===============
print("=" * 62)
print("H1: does missing games persist year-over-year? (pooled 23->24, 24->25)")
def year_map(arr): return {(norm(n), p): missed(g) for n, p, g in arr}
pairs = []
for (a, b) in [("y2023", "y2024"), ("y2024", "y2025")]:
    ya, yb = year_map(G[a]), year_map(G[b])
    for k, mA in ya.items():
        if k in yb:
            pairs.append((k[1], mA, yb[k]))
print(f"n = {len(pairs)} player-season pairs")
x = [p[1] for p in pairs]; y = [p[2] for p in pairs]
r, pv = pearson(x, y)
a0, slope, se, t, pslope = ols(x, y)
print(f"Pearson r = {r:.3f}  (p = {pv:.4f})")
print(f"OLS: missed_next = {a0:.2f} + {slope:.3f} * missed_prev   (SE {se:.3f}, t {t:.2f}, p {pslope:.4f})")

# two-proportion: prior missed>=4 vs <=1 -> P(missed>=4 next year)
hi = [p for p in pairs if p[1] >= 4]; lo = [p for p in pairs if p[1] <= 1]
p_hi = sum(1 for p in hi if p[2] >= 4) / len(hi)
p_lo = sum(1 for p in lo if p[2] >= 4) / len(lo)
pp = (sum(1 for p in hi if p[2] >= 4) + sum(1 for p in lo if p[2] >= 4)) / (len(hi) + len(lo))
z = (p_hi - p_lo) / math.sqrt(pp * (1 - pp) * (1/len(hi) + 1/len(lo)))
pz = 2 * (1 - phi(abs(z)))
print(f"P(miss>=4 next | missed>=4 prior) = {p_hi:.3f} (n={len(hi)})")
print(f"P(miss>=4 next | missed<=1 prior) = {p_lo:.3f} (n={len(lo)})")
print(f"relative risk = {p_hi/p_lo:.2f}, z = {z:.2f}, p = {pz:.4f}")
per_pos = defaultdict(list)
for pos, mA, mB in pairs: per_pos[pos].append((mA, mB))
for pos, lst in sorted(per_pos.items()):
    rr, pp2 = pearson([a for a, _ in lst], [b for _, b in lst])
    print(f"   {pos}: n={len(lst)}, r={rr:.3f} (p={pp2:.3f})")
H1_PASS = pslope < 0.05 and slope > 0
print("H1 VERDICT:", "SIGNIFICANT — implement" if H1_PASS else "NOT significant — do not implement")

# =============== H2: handcuff effect ===============
print("=" * 62)
print("H2: does backup RB production rise with starter games missed? (n=%d pairs)" % len(HC))
# control for backup quality via log(ADP); response = backup points
X1 = [missed(h["starter"]["g"]) for h in HC]
X2 = [math.log(min(300, h["backup"]["adp"])) for h in HC]
Y  = [h["backup"]["pts"] for h in HC]
# two-var OLS via residualization (Frisch–Waugh)
_, b2, _, _, _ = ols(X2, Y)
a2 = sum(Y)/len(Y) - b2*sum(X2)/len(X2)
Yr = [y_ - (a2 + b2*x2) for y_, x2 in zip(Y, X2)]
_, b21, _, _, _ = ols(X2, X1)
a21 = sum(X1)/len(X1) - b21*sum(X2)/len(X2)
X1r = [x1 - (a21 + b21*x2) for x1, x2 in zip(X1, X2)]
a0h, bh, seh, th, ph = ols(X1r, Yr)
print(f"backupPts ~ starterMissed (controlling log backup ADP):")
print(f"  slope = {bh:.2f} pts per starter game missed  (SE {seh:.2f}, t {th:.2f}, p {ph:.4f})")
# simple group comparison
big = [h["backup"]["pts"] for h in HC if missed(h["starter"]["g"]) >= 5]
small = [h["backup"]["pts"] for h in HC if missed(h["starter"]["g"]) <= 1]
def welch(a, b):
    ma, mb = sum(a)/len(a), sum(b)/len(b)
    va = sum((x-ma)**2 for x in a)/(len(a)-1); vb = sum((x-mb)**2 for x in b)/(len(b)-1)
    t = (ma - mb) / math.sqrt(va/len(a) + vb/len(b))
    return ma, mb, t, 2*(1-phi(abs(t)))
ma, mb, tw, pw = welch(big, small)
print(f"  mean backup pts: starter missed>=5 -> {ma:.0f} (n={len(big)}) vs starter missed<=1 -> {mb:.0f} (n={len(small)}); Welch t={tw:.2f}, p={pw:.4f}")
H2_PASS = ph < 0.05 and bh > 0
print("H2 VERDICT:", "SIGNIFICANT — implement" if H2_PASS else "NOT significant — do not implement")

# =============== fitted implementation params (shrunk 50%, capped) ===============
out = {"H1": {"pass": H1_PASS}, "H2": {"pass": H2_PASS}}
if H1_PASS:
    rr = p_hi / p_lo
    base = pp  # pooled rate
    # durability multiplier on bust prob: interp from missed games, shrunk 50% toward 1
    mult_hi = 1 + 0.5 * (p_hi/base - 1)
    mult_lo = 1 + 0.5 * (p_lo/base - 1)
    out["H1"].update({"r": round(r, 3), "slope": round(slope, 3), "p": round(pslope, 5),
                      "multLo": round(max(0.80, mult_lo), 3), "multHi": round(min(1.40, mult_hi), 3),
                      "loThresh": 1, "hiThresh": 4})
if H2_PASS:
    mean_backup = sum(Y)/len(Y)
    # bust season for a starter ~ E[missed | bust] ≈ 9.5 games -> backup gain
    gain = bh * 9.5 / mean_backup          # fractional boost
    out["H2"].update({"slope": round(bh, 2), "p": round(ph, 5),
                      "boost": round(min(0.60, 0.5 * gain), 3)})   # shrunk 50%, capped
json.dump(out, open("sig_params.json", "w"), indent=1)
print("\nwrote sig_params.json:", json.dumps(out))
