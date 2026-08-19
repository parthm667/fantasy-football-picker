#!/usr/bin/env python3
"""Diagnose: per-year, per-position predictive power of projections vs market (ADP)."""
import json, math

def spearman(pairs):
    n = len(pairs)
    if n < 6: return None
    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0]*n
        for rk, i in enumerate(order): r[i] = rk+1
        return r
    ra, rb = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs])
    d2 = sum((a-b)**2 for a, b in zip(ra, rb))
    return 1 - 6*d2/(n*(n*n-1))

for year in [2021, 2022, 2025]:
    suffix = 'base' if year == 2025 else ''
    players = json.load(open(f"bt_players_{year}{suffix}.json"))
    actual = json.load(open(f"bt_actuals_{year}.json"))
    pool = [p for p in players if p["adp"] <= 150]
    print(f"\n== {year} (pool: ADP<=150, n={len(pool)}) ==")
    print(f"{'pos':<5}{'n':>4} {'rho(proj)':>10} {'rho(ADP)':>9}  better")
    for pos in ["QB", "RB", "WR", "TE", "ALL"]:
        grp = pool if pos == "ALL" else [p for p in pool if p["pos"] == pos]
        pp = [(p["proj"], actual[p["id"]]) for p in grp]
        pa = [(-p["adp"], actual[p["id"]]) for p in grp]
        rp, ra = spearman(pp), spearman(pa)
        if rp is None: continue
        print(f"{pos:<5}{len(grp):>4} {rp:>10.3f} {ra:>9.3f}  {'PROJ' if rp > ra else 'ADP'} ({abs(rp-ra):.3f})")
