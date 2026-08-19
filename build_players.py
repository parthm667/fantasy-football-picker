#!/usr/bin/env python3
"""Merge agent-researched 2026 fantasy data into a single players.json database."""
import json, re, unicodedata

D = "data"

def load(f):
    with open(f"{D}/{f}") as fh:
        return json.load(fh)

rb, wr, qbte, adp_list, kdst = load("rb.json"), load("wr.json"), load("qbte.json"), load("adp.json"), load("kdst.json")
byes = kdst["byes"]

SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}
ALIASES = {
    "kenny gainwell": "kenneth gainwell",
    "hollywood brown": "marquise brown",
    "eddy pineiro": "eddy pineiro",
    "mike washington": "mike washington",
    "gabe davis": "gabriel davis",
    "cam ward": "cameron ward",
}

def norm(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = s.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9 ]", "", s)
    toks = [t for t in s.split() if t not in SUFFIXES]
    s = " ".join(toks)
    return ALIASES.get(s, s)

players = {}   # key: (norm, pos)
conflicts, created = [], []

def add(rec, pos):
    key = (norm(rec["name"]), pos)
    if key in players:
        conflicts.append(("dup", rec["name"], pos))
        return
    players[key] = {
        "name": rec["name"], "pos": pos, "team": rec.get("team", ""),
        "bye": rec.get("bye", 0) or 0, "proj": float(rec.get("proj", 0) or 0),
        "rec": float(rec.get("rec", 0) or 0),
        "adp": float(rec["adp"]) if rec.get("adp") not in (None, "") else 999.0,
        "ecr": rec.get("ecr"), "est": False,
    }

for r in rb: add(r, "RB")
for r in wr: add(r, "WR")
for r in qbte["qb"]: add(r, "QB")
for r in qbte["te"]: add(r, "TE")
for r in kdst["k"]: add(r, "K")
for r in kdst["dst"]: add(r, "DST")

# --- Merge in overall ADP list (authoritative ordering) ---
matched = 0
for a in adp_list:
    key = (norm(a["name"]), a["pos"])
    if key in players:
        p = players[key]
        p["adp"] = float(a["adp"])            # overall list wins
        if p["team"] != a["team"]:
            conflicts.append(("team", a["name"], p["team"], a["team"]))
        matched += 1
    else:
        created.append(a["name"])
        players[key] = {
            "name": a["name"], "pos": a["pos"], "team": a["team"],
            "bye": 0, "proj": 0.0, "rec": 0.0, "adp": float(a["adp"]),
            "ecr": None, "est": True,
        }

# --- Fill byes from schedule map (authoritative) ---
for p in players.values():
    if p["team"] in byes:
        p["bye"] = byes[p["team"]]

# --- Estimate proj for created players via same-position ADP->proj interpolation ---
def interp_proj(pos, adp):
    pts = sorted([(q["adp"], q["proj"]) for q in players.values()
                  if q["pos"] == pos and not q["est"] and q["proj"] > 0 and q["adp"] < 400],
                 key=lambda t: t[0])
    if not pts:
        return 80.0
    if adp <= pts[0][0]:
        return pts[0][1]
    for (a1, p1), (a2, p2) in zip(pts, pts[1:]):
        if a1 <= adp <= a2:
            f = 0 if a2 == a1 else (adp - a1) / (a2 - a1)
            return p1 + f * (p2 - p1)
    # extrapolate: decay past the last known point
    last_a, last_p = pts[-1]
    return max(20.0, last_p * (0.985 ** (adp - last_a)))

for p in players.values():
    if p["est"]:
        p["proj"] = round(interp_proj(p["pos"], p["adp"]), 1)

# --- Late/undrafted ADP: give 999s a sane depth ordering (250+) ---
undrafted = sorted([p for p in players.values() if p["adp"] >= 400],
                   key=lambda p: -p["proj"])
for i, p in enumerate(undrafted):
    p["adp"] = 250.0 + i * 2.0

# --- Calibrate TE curve (source projections run hot beyond TE3 vs historical PPR finishes) ---
TE_HIST = [(1,265),(2,245),(3,225),(4,200),(6,178),(8,164),(10,152),(12,143),(15,130),(20,115),(25,103),(30,93),(35,85)]
def te_hist(rank):
    if rank <= TE_HIST[0][0]: return TE_HIST[0][1]
    for (r1,v1),(r2,v2) in zip(TE_HIST, TE_HIST[1:]):
        if r1 <= rank <= r2:
            return v1 + (v2-v1)*(rank-r1)/(r2-r1)
    return TE_HIST[-1][1]
tes = sorted([p for p in players.values() if p["pos"]=="TE"], key=lambda p:-p["proj"])
for i,p in enumerate(tes):
    r = i+1
    w = 0.8 if r <= 3 else 0.4
    p["proj"] = round(w*p["proj"] + (1-w)*te_hist(r), 1)

# --- Correction from Aug-2026 news verification: Tank Dell returned to practice,
#     analysts project ~WR50 range (600-800 yds), not an out-for-season 25 pts ---
for p in players.values():
    if norm(p["name"]) == "tank dell":
        p["proj"], p["rec"] = 125.0, 45.0

# --- Merge full expert consensus ranks (CBS Aug-2026 top 200, cross-verified) ---
ecr_list = json.load(open(f"{D}2/ecr.json".replace("data2", "data2")))
ALIASES.update({"chigoziem okonkwo": "chig okonkwo"})
ecr_matched, ecr_missed = 0, []
for p in players.values(): p["ecr"] = None
for e in ecr_list:
    key = (norm(e["name"]), e["pos"])
    if key in players:
        players[key]["ecr"] = e["ecr"]; ecr_matched += 1
    else:
        ecr_missed.append(e["name"])

# --- Merge half-PPR / standard ADP; estimate for unmatched via per-pos median shift ---
fmts = json.load(open("data2/adp_formats.json"))
for fkey, jkey in [("half", "adpHalf"), ("std", "adpStd")]:
    fm = {}
    for a in fmts[fkey]:
        fm[(norm(a["name"]), a["pos"])] = a["adp"]
    shifts = {}
    for pos in ["QB", "RB", "WR", "TE", "K", "DST"]:
        ds = [fm[k] - players[k]["adp"] for k in fm
              if k in players and k[1] == pos and 60 <= players[k]["adp"] <= 200]
        ds.sort()
        shifts[pos] = ds[len(ds)//2] if ds else 0.0
    matched = 0
    for k, p in players.items():
        if k in fm:
            p[jkey] = fm[k]; matched += 1
        elif p["adp"] >= 240:
            p[jkey] = p["adp"]
        else:
            p[jkey] = round(max(1.0, p["adp"] + shifts[p["pos"]]), 1)
    print(f"{jkey}: matched {matched}, shifts {shifts}")

# --- Estimate receptions for ADP-created players (needed for format conversion) ---
import statistics
ratio = {}
for pos in ["RB", "WR", "TE"]:
    rs = [q["rec"] / q["proj"] for q in players.values()
          if q["pos"] == pos and not q["est"] and q["proj"] > 60 and q["rec"] > 0]
    ratio[pos] = statistics.median(rs) if rs else 0
for p in players.values():
    if p["est"] and p["pos"] in ratio and not p["rec"]:
        p["rec"] = round(p["proj"] * ratio[p["pos"]], 1)

print("ECR matched:", ecr_matched, "| unmatched ECR names:", ecr_missed if ecr_missed else "none")

# --- Kalshi layer: team win-total environment + fantasy-leader probabilities ---
kl = json.load(open("data2/kalshi.json"))
wtmap = kl["winTotals"]
for p in players.values():
    t = wtmap.get(p["team"])
    if t:
        p["wtLine"] = t["line"]
        p["wt"] = round(t["line"] + (t["overProb"] - 0.5) * 2, 2)   # effective expected wins
    else:
        p["wtLine"], p["wt"] = None, 8.5
kl_matched, kl_missed = 0, []
for p in players.values(): p["klProb"] = None
for pos, lst in kl["leaders"].items():
    ssum = sum(x["prob"] for x in lst) or 1.0
    for x in lst:
        key = (norm(x["name"]), pos)
        if key in players:
            players[key]["klProb"] = round(x["prob"] / ssum, 4)     # renormalized (thin books)
            kl_matched += 1
        else:
            kl_missed.append(x["name"] + "/" + pos)
print("Kalshi leaders matched:", kl_matched, "| unmatched:", kl_missed if kl_missed else "none")

# --- Durability (H1 passed significance: RR 1.71, z=3.02, p=0.0025 pooled 2023-25) ---
# Bust-prob multiplier from recent games missed; fitted group rates shrunk 50%:
# <=1 missed -> x0.898, >=4 missed -> x1.183, linear between; no NFL history -> 1.0
gm = json.load(open("data2/games.json"))
g24 = {(norm(n), pos): g for n, pos, g in gm["y2024"]}
g25 = {(norm(n), pos): g for n, pos, g in gm["y2025"]}
n_hi = n_lo = n_none = 0
for p in players.values():
    k = (norm(p["name"]), p["pos"])
    m25 = 17 - min(17, g25[k]) if k in g25 else None
    m24 = 17 - min(17, g24[k]) if k in g24 else None
    if m25 is None and m24 is None:
        p["dur"], p["durM"] = 1.0, None
        n_none += 1
    else:
        rm = 0.65 * m25 + 0.35 * m24 if (m25 is not None and m24 is not None) else (m25 if m25 is not None else m24)
        if rm <= 1: d = 0.898
        elif rm >= 4: d = 1.183
        else: d = 0.898 + (1.183 - 0.898) * (rm - 1) / 3.0
        p["dur"], p["durM"] = round(d, 3), round(rm, 1)
        if d >= 1.15: n_hi += 1
        if d <= 0.91: n_lo += 1
print(f"durability: {n_hi} elevated-risk, {n_lo} durable, {n_none} no-history (rookies/new)")

# --- Draft-day refresh (Aug 16): verified news corrections + current 8-team half-PPR ADP ---
news = json.load(open("data2/news_aug16.json"))
for p in players.values(): p["news"] = None
for c in news["corrections"]:
    k = (norm(c["name"]), c["pos"])
    if k in players:
        p = players[k]
        m = c.get("projMult", 1.0)
        p["proj"] = round(p["proj"] * m, 1)
        p["rec"] = round(p["rec"] * m, 1)
        p["news"] = (c["issue"].split(";")[0])[:64]
    else:
        print("news unmatched:", c["name"], c["pos"])
print("news corrections applied:", sum(1 for p in players.values() if p["news"]))

a8 = json.load(open("data2/adp8h.json"))
a8m = {(norm(x["name"]), x["pos"]): x["adp"] for x in a8["adp"]}
hit = 0
for k, p in players.items():
    if k in a8m:
        p["adpHalf"] = float(a8m[k]); hit += 1
    elif p["adpHalf"] < 240:
        p["adpHalf"] = round(p["adpHalf"] * 0.8, 1)   # rescale leftover values to 8-team pick units
print(f"8-team half-PPR ADP: {hit} matched verbatim, remainder rescaled x0.8")

# --- Position rank, tiers, weekly sd, ids ---
GAMES = 17.0
for pos in ["QB", "RB", "WR", "TE", "K", "DST"]:
    group = sorted([p for p in players.values() if p["pos"] == pos], key=lambda p: -p["proj"])
    tier, prev = 1, None
    # tier gap threshold per position (season pts)
    thr = {"QB": 16, "RB": 14, "WR": 14, "TE": 15, "K": 6, "DST": 6}[pos]
    ntier = 1
    for i, p in enumerate(group):
        p["posRank"] = i + 1
        if prev is not None and (prev - p["proj"]) >= thr and ntier < 9:
            tier += 1; ntier += 1
        p["tier"] = tier
        prev = p["proj"]

for p in players.values():
    ppg = p["proj"] / GAMES
    if p["pos"] == "K":      sd = 4.0
    elif p["pos"] == "DST":  sd = 5.5
    else:                    sd = min(11.0, max(3.0, 1.8 + 0.42 * ppg))
    p["sd"] = round(sd, 2)
    p["ppg"] = round(ppg, 2)
    p["id"] = re.sub(r"[^a-z0-9]+", "-", norm(p["name"]) + "-" + p["pos"].lower()).strip("-")

out = sorted(players.values(), key=lambda p: p["adp"])
with open("players.json", "w") as fh:
    json.dump(out, fh, indent=None, separators=(",", ":"))

# --- Report ---
from collections import Counter
cnt = Counter(p["pos"] for p in out)
print("TOTAL:", len(out), dict(cnt))
print("ADP-list matched:", matched, "| created from ADP list (proj estimated):", len(created))
for c in created: print("   est:", c)
print("conflicts:", conflicts if conflicts else "none")
ids = Counter(p["id"] for p in out)
dups = [k for k, v in ids.items() if v > 1]
print("dup ids:", dups if dups else "none")
missing_bye = [p["name"] for p in out if not p["bye"]]
print("missing bye:", missing_bye if missing_bye else "none")
print("\nTop 12 overall by ADP:")
for p in out[:12]:
    print(f'  {p["adp"]:>6} {p["pos"]:<3} {p["name"]:<24} proj={p["proj"]:>6} tier={p["tier"]}')
print("\nTier breaks (RB):", [(p["posRank"], p["name"], p["tier"]) for p in sorted(out, key=lambda x: x["adp"]) if p["pos"]=="RB"][:14])
