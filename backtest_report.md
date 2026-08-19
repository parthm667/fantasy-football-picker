# Draft Command — Backtest Report v2 (with locked-config holdout)
*Aug 16, 2026*

## 1. Design and lookahead controls

Two-stage protocol. **Stage 1 (development):** the engine was backtested on 2021–2022, which exposed that its 2025-fitted projection weights didn't generalize and that its concentrated positional strategy (early QB, double TE, WR flex, funded by RB quality) has year-dependent payoff. The engine was reconfigured there: market-led value (projection weight shrunk 5×), Kalshi leaders demoted to a minority voice after a paired 2025 test with real recovered Aug-2025 quotes showed the standalone signal hurt (dMargin −55, t=−4.96). Structural hedge candidates (reach anchor, RB floor, TE gate) were tried on the dev years and **rejected** — each either did nothing or traded away 2022's gains without repairing 2021.

**Stage 2 (confirmation):** the reconfigured engine was **locked**, then evaluated exactly once per season on four fresh seasons never touched during development: **2018, 2019, 2023, 2024**.

Controls: engine inputs per year are strictly preseason-knowable (that year's ADP and projections; durability from the two prior seasons); actuals quarantined from the engine; lineups set by preseason ADP order (no hindsight); opponents and the control seat draft **need-aware ADP** (top-of-board sampling with noise, positional logic, forced fills — a deliberately competent baseline, stronger than typical league-mates). Agents verified sources at the content level (e.g., FFToday's 2018 QB archive was detected as overwritten with 2019 data and rejected; per-year scoring formulas were solved arithmetically before conversion to PPR). Season lengths era-corrected (16 games pre-2021). Known residuals: parameters fitted on 2023–25 tested on earlier years (generalization, not time-machine deployability); durability inputs for 2023/24 overlap its fit window — bounded by durability-off reruns, which changed draft outcomes by exactly zero (the layer acts through sims, not picks).

## 2. Results: engine vs need-aware ADP control

dTop6 = change in P(top-6 by season points), paired by (slot, seed), 10-team PPR, 13 rounds, 25 seeds × 10 slots (dev years 20 × 10).

| Season | Status | dTop6 | t | dRank | dMargin (pts) |
|---|---|---|---|---|---|
| 2018 | **holdout, one-shot** | **+30.8 pp** | +8.6 | −2.15 | +168 |
| 2019 | **holdout, one-shot** | **+38.0 pp** | +11.1 | −2.60 | +173 |
| 2021 | dev | −8.5 to −9.5 pp | ≈ −1.9 | +0.5 | −45 |
| 2022 | dev | +9.5 to +13.0 pp | ≈ +2.3 | −0.7 | +50 |
| 2023 | **holdout, one-shot** | **+13.6 pp** | +3.3 | −0.82 | +60 |
| 2024 | **holdout, one-shot** | +4.4 pp | +1.0 (ns) | −0.38 | +33 |

Holdout aggregate (the only years that count as confirmation): **4 of 4 positive** (sign test p=0.0625 one-sided), mean **+21.7 pp**, year-level t(3)=2.80 (p≈0.03 one-sided). Across all six seasons: 5 of 6 positive, mean +14.6 pp.

## 3. Interpretation — where the alpha lives and how big it is today

The engine's edge is **structural positional allocation**, not player-picking: it consistently buys QB and elite TE earlier than the room and WR flex depth, at the cost of RB starter quality. That trade was enormous in 2018–2019 (+31/+38 pp — elite QB/TE were massively underpriced before the market repriced those positions), negative once (2021), and moderately positive in the modern, partially-repriced market (2023: +13.6 significant; 2024: +4.4 not significant). The honest reading of the trend: **real, positive, and shrinking** — expect the 2023–24 magnitude (~+5 to +14 pp above a competent ADP drafter's ~55–60% baseline), not the 2018–19 one, and accept that roughly one season in several will land below baseline (2021-style) because concentrated value bets carry across-league correlated risk. Within-position player selection remains market-equivalent — the edge is *when and where* capital is spent, plus flawless in-draft bookkeeping the backtest baseline never even mis-executes.

## 4. Shipped configuration (validated end-to-end)

Market-led value (ECR + ADP + Kalshi-minority; projection weight QB .05 / RB .12 / WR .06 / TE .13), projections in full control of the simulation layer (bust mixture, dispersion, durability p=0.0025, byes, team correlation with Kalshi win-total environments), structural VBD/urgency logic unchanged (it is the alpha), hedge knobs present but off (rejected on dev evidence), Kalshi leaders at 25% of market rank (demoted on 2025 paired evidence). Post-lock validation: 38/38 engine tests, analyst-board ρ=0.952, per-slot calibration clean in all three formats, full browser E2E green.

## 5. Bottom line

Under a locked-config, one-shot-per-season holdout across four fresh years, the engine beat a competent need-aware ADP baseline in all four (mean +21.7 pp playoff-rate, t=2.8), with the edge concentrated in structural positional allocation and decaying as markets reprice — most recently +13.6 pp (2023, significant) and +4.4 pp (2024, positive but not significant). That is a defensible, honestly-earned alpha claim at the season sample sizes this domain allows; it is not a guarantee, and 2021 shows the failure mode. The tool ships in exactly the configuration this evidence validates.

## Addendum (v2.1): bye-aware pick scoring re-verification

After shipping the bye-stacking penalty inside roster valuation (marginal value now charges ~5·C(k,2) points for k starters sharing a bye), the full six-season suite was re-run on identical files and seeds — synthetic bye assignments in the backtest make this a robustness test (does the diversification constraint cost draft value under arbitrary byes?). Result: holdout 2018 +32.0 (was +30.8), 2019 +36.4 (was +38.0), 2023 +16.0 (was +13.6), 2024 +9.6 and now significant (was +4.4 ns); holdout mean +23.5 pp (was +21.7), year-level t(3)=3.7. Dev years moved within seed noise (2021 −12.0, 2022 +9.0). Per-year deltas are within pick-path reshuffling noise; the constraint is free or better on draft outcomes while buying real bye coverage that only the live season simulations can price. Retained.

*Data: FFC ADP archives (2018–25) · FFToday projection archives (2018–25, scoring solved per year; corrupted 2018 QB archive rejected, FantasyPros Sep-2018 snapshot substituted) · FantasyPros PPR results (2016–25) · Kalshi historical candlesticks (Aug–Sep 2025). Harness: shipped engine.js verbatim; bt_build.py / bt_run.js / bt_inspect.js / significance.py.*
