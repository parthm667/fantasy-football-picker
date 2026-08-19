# Draft Command

A single-file, offline-capable fantasy football draft assistant with a statistically validated recommendation engine. Built for the 2026 season; battle-tested in a live draft (finished #2 of 8 by simulated playoff odds).

**Open `draft-command-2026.html` in any browser — that's the whole app.** No server, no dependencies. Configure league (PPR / half-PPR / standard, 8–14 teams, custom lineups), log picks as they happen, and get live recommendations with prose explanations, Monte-Carlo playoff odds per candidate, and crash-proof autosave.

## Does it actually work?

It was backtested the hard way: development on 2021–2022, config locked, then evaluated **once per season** on four untouched holdout years, against a need-aware ADP-drafting control (a deliberately competent baseline). Change in P(top-6 by points), paired by draft slot and seed:

| Season | dTop6 | t |
|---|---|---|
| 2018 (holdout) | **+32.0 pp** | 9.1 |
| 2019 (holdout) | **+36.4 pp** | 10.4 |
| 2021 (dev) | −12.0 pp | −2.4 |
| 2022 (dev) | +9.0 pp | 1.9 |
| 2023 (holdout) | **+16.0 pp** | 4.1 |
| 2024 (holdout) | **+9.6 pp** | 2.3 |

Holdout: 4/4 positive, mean +23.5 pp, year-level t(3)=3.7. The edge is *structural positional allocation* (when/where draft capital is spent), it was largest before the market repriced elite QB/TE scarcity, and one dev year (2021) shows the failure mode. Full methodology, lookahead-bias controls, and honest caveats: [`backtest_report.md`](backtest_report.md).

## How the engine works

- **Value** = market-led blend: expert consensus (ECR) + format-specific ADP + Kalshi prediction-market prices (demoted to a 25% minority voice after a paired 2025 backtest with recovered Aug-2025 quotes), with a small projection tilt (weights shrunk 5× after the OOS backtest showed market-heavy wins).
- **Projections govern the simulation layer**: bust-probability mixture fitted on 2025 preseason→results residuals (RB ~27%, WR ~23% bust rates), per-player durability multipliers fitted on 2023–25 games-missed persistence (RR 1.71, p=0.0025), weekly variance, byes, and NFL-team environments from Kalshi win totals.
- **Recommendations** = value-over-replacement + next-pick wait-cost asymmetry + tier cliffs + roster/bye-aware marginal value, explained in prose by a live "Decision panel"; per-candidate playoff odds from simulated draft completions × 14-week seasons, auto-deepened on close calls.
- Features were significance-gated: a handcuff-boost effect was tested (60 starter/backup pairs) and **rejected** (p=0.36); durability passed and shipped.

## Repo layout

```
draft-command-2026.html   the app (built artifact — open this)
app_shell.html / app.js   UI source (assembled into the artifact)
engine.js                 recommendation + simulation engine (browser + Node)
assemble.py               builds the single-file app
build_players.py          data pipeline: merge projections/ADP/ECR/Kalshi/news → players.json
build_model.py            2025 backtest fit (blend weights, bust mixture)
significance.py           durability + handcuff hypothesis tests
data/, data2/             research snapshots (projections, ADP by format/era, ECR,
                          Kalshi quotes incl. recovered Aug-2025 candles, games played
                          2016–2025, news corrections)
bt_build.py / bt_run.js   lookahead-safe backtest harness (2018–2025 seasons)
bt_inspect.js, bt_diag.py backtest diagnostics
calibrate.js              per-slot recommendation calibration vs analyst boards
test_engine.js            engine unit tests (41)
verify.mjs                Playwright end-to-end suite
trade_eval.js             in-season trade simulator (2,000-season paired deltas)
final_roster.js           post-draft league table + roster analysis
backtest_report.md        full validation writeup
ROADMAP.md                improvement backlog from the live-draft field test
shots/                    UI verification screenshots
```

## Rebuilding / running

```bash
python3 build_players.py     # data → players.json
python3 assemble.py          # → draft-command-2026.html
node test_engine.js          # engine tests
node calibrate.js            # analyst-alignment check
python3 bt_build.py          # backtest inputs
node bt_run.js bt_players_2023.json bt_actuals_2023.json 25 LABEL out.json
node verify.mjs              # E2E (needs Playwright + Chromium; this repo's copy
                             # resolves playwright from a global install — for local
                             # use: npm i -D playwright && npx playwright install chromium,
                             # and change the createRequire path in verify.mjs)
```

Node ≥ 18 and Python 3 (stdlib only). The app itself needs neither.

## Data provenance & disclaimers

Data files are point-in-time research snapshots (Aug 2026 build; historical archives 2016–2025) drawn from FFToday, FantasyPros, FantasyFootballCalculator, CBS Sports, Kalshi's public API, and dated news reports — collected for personal research; respect the original sources' terms if you redistribute. Kalshi data is used as a market-information signal only; nothing here is gambling or financial advice. Past backtest performance does not guarantee your league's future; 2021 is in the table on purpose.

Built collaboratively with Claude (Anthropic). Code: MIT — do whatever, keep the disclaimer.
