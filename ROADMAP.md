# Draft Command — Improvement Roadmap (post live-draft field test)
*Compiled Aug 18, 2026, after the first real draft (8-team half-PPR, finished #2 by sims at 55.3%). Every scoring change below goes through the standing gate: implement → six-season backtest on identical seeds → keep only if the alpha holds. Display-layer changes ship without the gate but never carry score weight until validated.*

## Shipped during/after the draft round
Prose Decision panel · bye-stacking inside pick scoring (re-verified, holdout mean +23.5pp) · crash-proof autosave (URL + storage) · auto-deepening sims on close calls · Aug-16 news chips · true 8-team half-PPR ADP · **board CSV export (menu → "Download board as CSV": full pick log + your flags + top-120 available with value/ADP/analyst/Kalshi/durability columns)**.

## Tier 1 — engine correctness (before the next draft)

**1. Supply-vs-demand survival & wait-costs** *(the Purdy-at-76 / Pollard seam).* The tool tracks all rosters but "% gone" and wait-costs read only ADP curves, and the sims' opponents draft backups at a flat generic rate. The correct model, formalized from the user's live arbitrage: per position per window, compare **expected demand before my next pick** (opponents with unfilled starters at a high rate, plus backup demand as a *time-varying, roster-state-dependent* curve — near zero right after starters fill league-wide, igniting once opponents exhaust their own skill needs) against **acceptable supply depth** (how many remaining players sit within tolerance of the best one). Canonical test case this must reproduce: at pick 76, three backup QBs (Lawrence 81, Dart 82, Nix 84) went inside the wait window and waiting was STILL right, because an 8-deep plateau absorbs a 3-QB run — while Pollard's pool (RB4s with standalone value) was ~2-deep under live demand. Ratio, not headline. Panel lines and sims share this one model so the tool can never disagree with itself again.

**2. Deadline-aware self-continuation in candidate sims.** When a sim tests "wait on X," simulated-you currently completes the draft greedily and sometimes procrastinates into the basement, inflating take-now urgency. Fix: continuation policy fills each remaining starter slot by a computed deadline (the same survival math), like actual-you does.

**3. Flex-scoped urgency** *(the Loveland case).* Urgency for a candidate whose roster home is FLEX must compare against the best flex-eligible player at the next pick, not the best same-position player — owning McBride means missing a TE2 costs a flex-replacement, not a tier cliff.

**4. Bench-aware bye logic** *(user request, merged with the QB2-insurance gap).* Two sides of one fix: (a) the bye-stack penalty should shrink when a position-eligible bench player with a different bye covers the stacked slot (cover ≈ 60% discount — you start a worse player, not a zero: the Andrews-covers-McBride effect); (b) bench players whose bye differs from their slot's starter at one-deep positions (QB, TE) earn an insurance bonus in bench value — the reason drafting Goff at 133 was right and the ledger said ~0. The weekly season sims already price all of this; the fix is making draft-time scoring see what the sims see. Validation: six-season suite must stay flat-or-better.

## Tier 2 — new signal layers (display-first)

**5. Social/beat-writer sentiment sweep** *(user request).* At build/refresh time, agents sweep r/fantasyfootball, X beat writers, and camp reports into per-player buzz chips (direction + one-liner + source), extending the news layer. Design constraints stated up front: crowd sentiment is mostly an ADP echo (ADP *is* aggregated sentiment), so the orthogonal value is narrow — early role/usage reporting that hasn't moved ADP yet, and injury-rumor velocity. Ships at **zero scoring weight**; there is no historical sentiment archive to backtest against, so it likely remains a permanent display layer — chips for the human, not points for the machine. Astroturf/recency guards required.

**6. Confidence bands on playoff odds** *(the 66%→49% scare).* Display ± bands derived from sim counts; label movements inside the band as noise; never render a quick-sim number next to a deep-sim number without marking the depth.

## Tier 3 — product surface

**7. In-app trade evaluator.** Tonight's Cook/Pickens offers were adjudicated by hand-run sims (−10.4pp fleece detected; +4.7pp win-win found; the 3-WR "sweetener" priced at −11.3pp). Port to UI: select players both directions → paired 2,000-season delta for *both* teams, with drop-slot handling and the streaming-baseline caveat auto-stated.

**8. In-season companion.** Weekly odds tracker seeded with the live roster, start/sit via the same sims, waiver targets ranked by playoff-odds impact, and a bye/streaming planner (the week-14 Goff plan, automated).

**9. Weekly-level backtest.** The one methodological upgrade that unlocks proper validation of items 4 and 8: weekly game logs, lineups set week-by-week, bench/bye/streaming value finally measurable. Season-total scoring — the current suite's known blind spot — systematically understates exactly the depth-and-coverage effects this roster was built on.

*Standing rule unchanged: nothing enters the score without surviving out-of-sample evidence; everything that informs the human ships as a chip first.*
