#!/usr/bin/env python3
"""
Build lookahead-safe engine inputs for backtest years.
Inputs per year N use ONLY: preseason-N ADP, preseason-N projections,
games played in N-2/N-1 (durability), and (2025 secondary only) Aug-2025 Kalshi quotes.
Actuals are written to a SEPARATE file that the engine never sees.
"""
import json, re, sys, unicodedata

SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}
ALIASES = {
    "robbie chosen": "robby anderson", "nyheim millerhines": "nyheim hines",
    "nyheim miller hines": "nyheim hines", "hollywood brown": "marquise brown",
    "kenny gainwell": "kenneth gainwell", "chigoziem okonkwo": "chig okonkwo",
    "cameron ward": "cam ward", "gabe davis": "gabriel davis",
    "will fuller v": "will fuller", "dj chark": "d j chark",
}
def norm(n):
    s = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", "", s)
    s = " ".join(t for t in s.split() if t not in SUFFIXES)
    return ALIASES.get(s, s)

TE_HIST = [(1,265),(2,245),(3,225),(4,200),(6,178),(8,164),(10,152),(12,143),(15,130),(20,115),(25,103),(30,93),(35,85)]
def te_hist(rank):
    if rank <= 1: return 265
    for (r1,v1),(r2,v2) in zip(TE_HIST, TE_HIST[1:]):
        if r1 <= rank <= r2: return v1 + (v2-v1)*(rank-r1)/(r2-r1)
    return 85

def dur_mult(m_prev2, m_prev1):
    """fitted: <=1 missed -> 0.898, >=4 -> 1.183 (recency-weighted missed games)"""
    if m_prev1 is None and m_prev2 is None: return 1.0, None
    if m_prev1 is not None and m_prev2 is not None: rm = 0.65*m_prev1 + 0.35*m_prev2
    else: rm = m_prev1 if m_prev1 is not None else m_prev2
    if rm <= 1: d = 0.898
    elif rm >= 4: d = 1.183
    else: d = 0.898 + (1.183-0.898)*(rm-1)/3.0
    return round(d, 3), round(rm, 1)

def build(year, adp, proj, games_prev2, len_prev2, games_prev1, len_prev1,
          te_cal=True, kalshi=None, out_suffix=""):
    players = {}
    for a in adp:
        k = (norm(a["name"]), a["pos"])
        players[k] = {"name": a["name"], "pos": a["pos"], "team": a.get("team", "UNK"),
                      "adp": float(a["adp"]), "proj": None}
    for p in proj:
        k = (norm(p["name"]), p["pos"])
        if k in players: players[k]["proj"] = float(p["proj"])
        else: players[k] = {"name": p["name"], "pos": p["pos"], "team": "UNK",
                            "adp": None, "proj": float(p["proj"])}
    # TE calibration (same engine pipeline transform)
    if te_cal:
        tes = sorted([p for p in players.values() if p["pos"] == "TE" and p["proj"]],
                     key=lambda p: -p["proj"])
        for i, p in enumerate(tes):
            w = 0.8 if i < 3 else 0.4
            p["proj"] = round(w*p["proj"] + (1-w)*te_hist(i+1), 1)
    # fill missing proj by ADP interpolation within position
    for pos in ["QB", "RB", "WR", "TE"]:
        pts = sorted([(p["adp"], p["proj"]) for p in players.values()
                      if p["pos"] == pos and p["proj"] and p["adp"]], key=lambda t: t[0])
        for p in players.values():
            if p["pos"] != pos or p["proj"] is not None: continue
            if p["adp"] is None: continue
            a = p["adp"]
            if not pts: p["proj"] = 80; continue
            if a <= pts[0][0]: p["proj"] = pts[0][1]; continue
            done = False
            for (a1, v1), (a2, v2) in zip(pts, pts[1:]):
                if a1 <= a <= a2:
                    p["proj"] = v1 + (v2-v1)*(a-a1)/(a2-a1); done = True; break
            if not done: p["proj"] = max(20, pts[-1][1] * 0.985 ** (a - pts[-1][0]))
    # deep pool: proj-only players get late synthetic ADP
    extras = sorted([p for p in players.values() if p["adp"] is None], key=lambda p: -(p["proj"] or 0))
    for i, p in enumerate(extras): p["adp"] = 250.0 + 2*i
    # durability from prior two seasons
    g2 = {(norm(n), pos): g for n, pos, g in games_prev2}
    g1 = {(norm(n), pos): g for n, pos, g in games_prev1}
    for k, p in players.items():
        m2 = (len_prev2 - min(len_prev2, g2[k])) if k in g2 else None
        m1 = (len_prev1 - min(len_prev1, g1[k])) if k in g1 else None
        p["dur"], p["durM"] = dur_mult(m2, m1)
    # kalshi (2025 secondary only)
    for p in players.values():
        p["wt"], p["wtLine"], p["klProb"], p["ecr"] = None, None, None, None
    if kalshi:
        wt = kalshi.get("winTotals", {})
        tm_fix = {"JAC": "JAX", "LA": "LAR"}
        wtn = {tm_fix.get(t, t): v for t, v in wt.items()}
        for p in players.values():
            t = tm_fix.get(p["team"], p["team"])
            if t in wtn and wtn[t].get("line") is not None:
                op = wtn[t].get("overProb")
                p["wtLine"] = wtn[t]["line"]
                p["wt"] = round(wtn[t]["line"] + ((op - 0.5) * 2 if op is not None else 0), 2)
        for pos, lst in kalshi.get("leaders", {}).items():
            for x in lst:
                k = (norm(x["name"]), pos)
                if k in players: players[k]["klProb"] = x["prob"]
    out = []
    for p in sorted(players.values(), key=lambda p: p["adp"]):
        if not p["proj"]: continue
        out.append({"name": p["name"], "pos": p["pos"], "team": p["team"], "bye": 4 + (hash(p["team"]) % 10),
                    "proj": round(p["proj"], 1), "rec": 0, "adp": p["adp"], "adpHalf": p["adp"], "adpStd": p["adp"],
                    "ecr": None, "est": False, "wt": p["wt"], "wtLine": p["wtLine"], "klProb": p["klProb"],
                    "dur": p["dur"], "durM": p["durM"],
                    "id": re.sub(r"[^a-z0-9]+", "-", norm(p["name"]) + "-" + p["pos"].lower()).strip("-")})
    fn = f"bt_players_{year}{out_suffix}.json"
    json.dump(out, open(fn, "w"))
    print(f"{fn}: {len(out)} players, dur-flagged {sum(1 for p in out if p['dur']>=1.15)}, kalshi-wt {sum(1 for p in out if p['wt'])}, kl-quotes {sum(1 for p in out if p['klProb'])}")
    return out

def write_actuals(year, actual, pool):
    ids = {p["id"] for p in pool}
    m = {}
    for a in actual:
        pid = re.sub(r"[^a-z0-9]+", "-", norm(a["name"]) + "-" + a["pos"].lower()).strip("-")
        if pid in ids: m[pid] = a["pts"]
    # censoring: drafted players missing from top-N actuals scored ~0
    for p in pool: m.setdefault(p["id"], 0.0)
    json.dump(m, open(f"bt_actuals_{year}.json", "w"))
    matched = sum(1 for p in pool if m[p["id"]] > 0)
    print(f"bt_actuals_{year}.json: {matched}/{len(pool)} pool players have nonzero actuals")

o21 = json.load(open("data2/oos2021.json"))
o22 = json.load(open("data2/oos2022.json"))
bt = json.load(open("data2/backtest.json"))
gm = json.load(open("data2/games.json"))
kl25 = json.load(open("data2/kalshi2025.json"))

p21 = build(2021, o21["adp2021"], o21["proj2021"], o21["games2019"], 16, o21["games2020"], 16)
write_actuals(2021, o21["actual2021"], p21)
p22 = build(2022, o22["adp2022"], o22["proj2022"], o22["games2020"], 16, o22["games2021"], 17)
write_actuals(2022, o22["actual2022"], p22)
# sensitivity variant: TE calibration off
build(2022, o22["adp2022"], o22["proj2022"], o22["games2020"], 16, o22["games2021"], 17, te_cal=False, out_suffix="notecal")
build(2021, o21["adp2021"], o21["proj2021"], o21["games2019"], 16, o21["games2020"], 16, te_cal=False, out_suffix="notecal")
# ---- holdout seasons (fresh, untouched by any development) ----
o18 = json.load(open("data2/oos2018.json"))
o19 = json.load(open("data2/oos2019.json"))
o23 = json.load(open("data2/oos2023.json"))
o24 = json.load(open("data2/oos2024.json"))
gm_all = json.load(open("data2/games.json"))

p18 = build(2018, o18["adp2018"], o18["proj2018"], o18["gamesA"], 16, o18["gamesB"], 16)
write_actuals(2018, o18["actual2018"], p18)
p19 = build(2019, o19["adp2019"], o19["proj2019"], o19["gamesA"], 16, o19["gamesB"], 16)
write_actuals(2019, o19["actual2019"], p19)
p23 = build(2023, o23["adpY"], o23["projY"], o22["games2021"], 17, o23["gamesPrev"], 17)
write_actuals(2023, o23["actualY"], p23)
p24 = build(2024, o24["adpY"], o24["projY"], o23["gamesPrev"], 17, gm_all["y2023"], 17)
write_actuals(2024, o24["actualY"], p24)
# durability-neutral variants for contamination bounds (2023/24 dur inputs overlap the fit years)
for yr, (adp, proj) in {2023: (o23["adpY"], o23["projY"]), 2024: (o24["adpY"], o24["projY"])}.items():
    pool = build(yr, adp, proj, [], 17, [], 17, out_suffix="nodur")

# 2025 secondary: base (no kalshi) and kalshi variants share identical everything else
teams25 = {(norm(t["name"]), t["pos"]): t["team"] for t in json.load(open("data2/teams2025.json"))}
adp25 = [dict(a, team=teams25.get((norm(a["name"]), a["pos"]), "UNK")) for a in bt["adp2025"]]
bt["adp2025"] = adp25
proj25 = bt["proj2025"]
p25b = build(2025, bt["adp2025"], proj25, gm["y2023"], 17, gm["y2024"], 17, out_suffix="base")
build(2025, bt["adp2025"], proj25, gm["y2023"], 17, gm["y2024"], 17, kalshi=kl25, out_suffix="kalshi")
write_actuals(2025, bt["actual2025"], p25b)
print("done")
