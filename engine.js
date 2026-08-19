/* ============================================================
   Draft Engine v2
   - Scoring formats: PPR / half-PPR / standard (reception-derived)
   - Player value = blend of site projections and analyst consensus
     (blend weights fitted on a 2025 preseason->results backtest)
   - Monte Carlo: draft completion + 14-week season with
     empirically-fitted season outcome mixture (bust rate + lognormal
     dispersion from 2025 residuals) and NFL-team correlation.
   Works in browser (window.Engine) and Node (module.exports).
   ============================================================ */
(function (global) {
  'use strict';

  // ---------- fitted model parameters ----------
  // Backtest: 2025 preseason ADP/ECR + FFToday projections vs actual 2025 PPR results
  // (n=191 joined). Blend weights = 0.5*fitted + 0.5*0.45 prior, clamped [0.25,0.65].
  // Bust = season < 50% of rank-expected points; probabilities shrunk 60/40 toward
  // the 0.20 league-wide prior. sigma = sd of log residuals among non-bust seasons.
  // wProj: fitted on 2025 then SHRUNK 5x after the 2021/2022 out-of-sample draft
  // backtest showed market-heavy value won BOTH years (lower projection weight beat
  // higher in every tested config). Projections keep full control of sims/variance/tiers.
  const MODEL = {
    wProj: { QB: 0.05, RB: 0.12, WR: 0.06, TE: 0.13, K: 0.50, DST: 0.50 },
    bust: {
      QB: { early: 0.13, late: 0.13 }, RB: { early: 0.10, late: 0.30 },
      WR: { early: 0.17, late: 0.23 }, TE: { early: 0.08, late: 0.14 },
      K:  { early: 0.05, late: 0.05 }, DST: { early: 0.08, late: 0.08 },
    },
    sigma: { QB: 0.33, RB: 0.30, WR: 0.33, TE: 0.30, K: 0.12, DST: 0.18 },
    teamSigma: 0.06,          // NFL-team season factor (offense-wide correlation)
    earlyRankCut: 18,         // posRank <= 18 uses the 'early' bust rate
  };

  // ---------- RNG ----------
  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function randn(rng) {
    let u = 0, v = 0;
    while (u === 0) u = rng();
    while (v === 0) v = rng();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }
  function phi(x) {
    const t = 1 / (1 + 0.2316419 * Math.abs(x));
    const d = 0.3989422804014327 * Math.exp(-x * x / 2);
    let p = d * t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
    return x > 0 ? 1 - p : p;
  }

  const POSITIONS = ['QB', 'RB', 'WR', 'TE', 'K', 'DST'];
  const FLEX_ELIG = { RB: 1, WR: 1, TE: 1 };
  const REG_WEEKS = 14;

  function create(playersRaw, config) {
    const cfg = Object.assign({
      teams: 10, mySlot: 5, rounds: 16, scoring: 'ppr',
      slots: { QB: 1, RB: 2, WR: 2, TE: 1, FLEX: 1, K: 1, DST: 1, BENCH: 7 },
      playoffTeams: 6,
    }, config);
    const T = cfg.teams;
    cfg.rounds = cfg.rounds || Object.entries(cfg.slots).reduce((s, [k, v]) => s + v, 0);
    const disc = { ppr: 0, half: 0.5, std: 1 }[cfg.scoring] || 0;

    // ----- derive per-format numbers -----
    const players = playersRaw.map((p, i) => Object.assign({}, p, { idx: i }));
    const byId = new Map(players.map(p => [p.id, p]));
    players.forEach(p => {
      p.fmtProj = FLEX_ELIG[p.pos] ? Math.max(5, p.proj - disc * (p.rec || 0)) : p.proj;
      const a = cfg.scoring === 'half' ? p.adpHalf : cfg.scoring === 'std' ? p.adpStd : p.adp;
      p.adpF = (a && a > 0) ? a : p.adp;
      p.adpSd = Math.min(28, 3 + 0.14 * p.adpF);
    });

    // positional ranks: by projection, by market ADP, by analyst consensus
    const byPos = {}, curve = {};
    POSITIONS.forEach(pos => {
      const grp = players.filter(p => p.pos === pos);
      grp.slice().sort((a, b) => a.adpF - b.adpF).forEach((p, i) => { p.adpPosRank = i + 1; });
      const withEcr = grp.filter(p => p.ecr != null).sort((a, b) => a.ecr - b.ecr);
      withEcr.forEach((p, i) => { p.ecrPosRank = i + 1; });
      const byProj = grp.slice().sort((a, b) => b.fmtProj - a.fmtProj);
      byProj.forEach((p, i) => { p.projPosRank = i + 1; });
      curve[pos] = byProj.map(p => p.fmtProj);
      byPos[pos] = byProj;
    });
    function curveAt(pos, rank) {
      const c = curve[pos];
      if (!c.length) return 0;
      return c[Math.max(0, Math.min(c.length - 1, Math.round(rank) - 1))];
    }

    // Kalshi fantasy-leader implied positional rank (renormalized quotes; top names only)
    POSITIONS.forEach(pos => {
      players.filter(p => p.pos === pos && p.klProb != null)
        .sort((a, b) => b.klProb - a.klProb)
        .forEach((p, i) => { p.kalshiPosRank = i + 1; });
    });

    // Kalshi team environment: effective win totals -> capped multipliers
    const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));
    const wtByTeam = {};
    players.forEach(p => { if (p.wt != null && p.team) wtByTeam[p.team] = p.wt; });
    const wtTeams = Object.keys(wtByTeam);
    const wtMean = wtTeams.length ? wtTeams.reduce((s, t) => s + wtByTeam[t], 0) / wtTeams.length : 8.5;
    const envMult = {};   // sims: team season-factor mean, capped ±4%
    wtTeams.forEach(t => { envMult[t] = clamp(1 + 0.012 * (wtByTeam[t] - wtMean), 0.96, 1.04); });

    // blended value: fitted weights; market rank = analyst ECR, averaged with the
    // Kalshi leaders-implied rank where a real quote exists (top of board only)
    const wScale = cfg.wScale != null ? cfg.wScale : 1;   // backtest/ablation knob: scales projection weight
    players.forEach(p => {
      const w = Math.max(0, Math.min(1, (MODEL.wProj[p.pos] != null ? MODEL.wProj[p.pos] : 0.5) * wScale));
      // Kalshi leaders demoted to a 25% minority voice after the 2025 backtest with real
      // Aug-2025 quotes showed a full-replacement leaders signal HURT draft outcomes
      // (thin favorite-only books); never used alone.
      let mRank;
      if (p.ecrPosRank != null && p.kalshiPosRank != null) mRank = 0.75 * p.ecrPosRank + 0.25 * p.kalshiPosRank;
      else if (p.ecrPosRank != null) mRank = p.ecrPosRank;
      else if (p.kalshiPosRank != null) mRank = 0.5 * p.kalshiPosRank + 0.5 * p.adpPosRank;
      else mRank = p.adpPosRank;
      p.mktRank = mRank;
      p.mktPts = curveAt(p.pos, mRank);
      p.val = w * p.fmtProj + (1 - w) * p.mktPts;
      // DST/K: market team strength is sharper than projections here — capped tilt
      p.envTilt = 1;
      if (p.wt != null) {
        if (p.pos === 'DST') p.envTilt = clamp(1 + 0.020 * (p.wt - wtMean), 0.90, 1.10);
        if (p.pos === 'K') p.envTilt = clamp(1 + 0.012 * (p.wt - wtMean), 0.94, 1.06);
        p.val *= p.envTilt;
      }
    });

    // model-vs-market team disagreement (projected offense strength rank vs win-total rank)
    const teamProj = {};
    wtTeams.forEach(t => {
      const tops = players.filter(p => p.team === t && FLEX_ELIG[p.pos] || p.team === t && p.pos === 'QB')
        .sort((a, b) => b.fmtProj - a.fmtProj).slice(0, 5);
      teamProj[t] = tops.reduce((s, p) => s + p.fmtProj, 0);
    });
    const projOrder = wtTeams.slice().sort((a, b) => teamProj[b] - teamProj[a]);
    const wtOrder = wtTeams.slice().sort((a, b) => wtByTeam[b] - wtByTeam[a]);
    const teamDisagree = {};  // positive = Kalshi likes the team MORE than projections do
    wtTeams.forEach(t => { teamDisagree[t] = projOrder.indexOf(t) - wtOrder.indexOf(t); });

    // value-based ranks + tiers
    const TIER_THR = { QB: 16, RB: 14, WR: 14, TE: 15, K: 6, DST: 6 };
    POSITIONS.forEach(pos => {
      const grp = players.filter(p => p.pos === pos).sort((a, b) => b.val - a.val);
      byPos[pos] = grp;
      let tier = 1, prev = null, n = 1;
      grp.forEach((p, i) => {
        p.posRank = i + 1;
        if (prev !== null && (prev - p.val) >= TIER_THR[pos] && n < 9) { tier++; n++; }
        p.tier = tier; prev = p.val;
      });
    });
    players.forEach(p => {
      p.ppg = p.val / 17;
      p.sd = p.pos === 'K' ? 4.0 : p.pos === 'DST' ? 5.5 : Math.min(11, Math.max(3, 1.8 + 0.42 * p.ppg));
    });

    // ----- replacement levels on blended value -----
    const flexShare = { RB: 0.45, WR: 0.50, TE: 0.05 };
    function demandFor(pos) {
      const s = cfg.slots;
      if (pos === 'QB') return T * (s.QB * (cfg.qbStream || 1.3));
      if (pos === 'K') return T * s.K + 1;
      if (pos === 'DST') return T * s.DST + 1;
      const flexN = (s.FLEX || 0) * (flexShare[pos] || 0);
      const benchDepth = { RB: 1.0, WR: 1.0, TE: 0.15 }[pos] || 0;
      return T * (s[pos] + flexN + benchDepth);
    }
    const repl = {};
    POSITIONS.forEach(pos => {
      const rank = Math.max(1, Math.round(demandFor(pos)));
      const grp = byPos[pos];
      repl[pos] = grp.length ? grp[Math.min(rank - 1, grp.length - 1)].val : 0;
    });
    const flexRepl = 0.45 * repl.RB + 0.50 * repl.WR + 0.05 * repl.TE;
    players.forEach(p => {
      p.vorp = Math.max(-20, p.val - repl[p.pos]);
      p.flexVorp = FLEX_ELIG[p.pos] ? Math.max(-20, p.val - flexRepl) : p.vorp;
      p.benchVorp = Math.max(0, p.val - (FLEX_ELIG[p.pos] ? Math.min(repl[p.pos], flexRepl) : repl[p.pos]));
    });

    // ----- snake math -----
    const totalPicks = T * cfg.rounds;
    function pickRound(p) { return Math.ceil(p / T); }
    function pickTeam(p) {
      const r = pickRound(p), i = p - (r - 1) * T;
      return (r % 2 === 1) ? i : T - i + 1;
    }
    function teamPickNumbers(slot) {
      const out = [];
      for (let r = 1; r <= cfg.rounds; r++) out.push((r - 1) * T + ((r % 2 === 1) ? slot : T - slot + 1));
      return out;
    }
    function nextPickOf(slot, afterPick) {
      for (const p of teamPickNumbers(slot)) if (p > afterPick) return p;
      return null;
    }

    // ----- draft state -----
    const state = { picks: [], taken: new Set() };
    function currentPick() { return state.picks.length + 1; }
    function draftOver() { return state.picks.length >= totalPicks; }
    function onClock() { return draftOver() ? null : pickTeam(currentPick()); }
    function rosterOf(slot, picksArr) {
      const src = picksArr || state.picks;
      const out = [];
      for (let i = 0; i < src.length; i++) if (src[i].team === slot) out.push(byId.get(src[i].playerId));
      return out;
    }
    function makePick(playerId, team) {
      const t = team || onClock();
      if (draftOver()) return { ok: false, err: 'Draft complete' };
      if (state.taken.has(playerId)) return { ok: false, err: 'Already drafted' };
      if (!byId.has(playerId)) return { ok: false, err: 'Unknown player' };
      state.picks.push({ playerId, team: t });
      state.taken.add(playerId);
      return { ok: true, pick: state.picks.length, team: t };
    }
    function undo() {
      const last = state.picks.pop();
      if (last) state.taken.delete(last.playerId);
      return last || null;
    }
    function available() { return players.filter(p => !state.taken.has(p.id)); }

    // ----- roster valuation -----
    const BENCH_W = [0.25, 0.18, 0.13, 0.09, 0.06, 0.04, 0.02, 0.01, 0.01, 0.01];
    const BENCH_TGT = { QB: 1, RB: 3, WR: 3, TE: 1, K: 0, DST: 0 };

    function lineup(roster) {
      const pool = { QB: [], RB: [], WR: [], TE: [], K: [], DST: [] };
      roster.forEach(p => pool[p.pos] && pool[p.pos].push(p));
      POSITIONS.forEach(pos => pool[pos].sort((a, b) => b.val - a.val));
      const starters = [], used = new Set();
      ['QB', 'RB', 'WR', 'TE', 'K', 'DST'].forEach(pos => {
        for (let i = 0; i < (cfg.slots[pos] || 0); i++) {
          const p = pool[pos][i];
          if (p) { starters.push({ p, slot: pos }); used.add(p.id); }
        }
      });
      const flexN = cfg.slots.FLEX || 0;
      const flexPool = roster.filter(p => FLEX_ELIG[p.pos] && !used.has(p.id)).sort((a, b) => b.val - a.val);
      const flexIds = new Set();
      for (let i = 0; i < flexN && i < flexPool.length; i++) {
        starters.push({ p: flexPool[i], slot: 'FLEX' }); used.add(flexPool[i].id); flexIds.add(flexPool[i].id);
      }
      const bench = roster.filter(p => !used.has(p.id)).sort((a, b) => b.benchVorp - a.benchVorp);
      let value = 0;
      starters.forEach(s => { value += Math.max(0, flexIds.has(s.p.id) ? s.p.flexVorp : s.p.vorp); });
      const benchCnt = { QB: 0, RB: 0, WR: 0, TE: 0, K: 0, DST: 0 };
      bench.forEach((p, i) => {
        const over = benchCnt[p.pos] >= (BENCH_TGT[p.pos] || 0);
        value += p.benchVorp * (BENCH_W[i] || 0.01) * (over ? 0.12 : 1);
        benchCnt[p.pos]++;
      });
      // bye-stacking cost: one starter on bye is covered by the bench at little cost
      // (already in season totals); each ADDITIONAL starter sharing that bye forces a
      // deeper replacement. k same-week byes cost ~5 * C(k,2) season points.
      const byeCnt = {};
      starters.forEach(s => {
        if (s.p.bye && s.p.pos !== 'K' && s.p.pos !== 'DST') byeCnt[s.p.bye] = (byeCnt[s.p.bye] || 0) + 1;
      });
      let byePen = 0;
      Object.values(byeCnt).forEach(k => { if (k >= 2) byePen += 5 * k * (k - 1) / 2; });
      value -= byePen;
      return { starters, bench, value, byePen };
    }
    function marginal(p, roster) {
      return lineup(roster.concat([p])).value - lineup(roster).value;
    }

    // ----- availability -----
    function survivalProb(p, c, k) {
      if (k <= c) return 1;
      const Sk = 1 - phi((k - p.adpF) / p.adpSd);
      const Sc = 1 - phi((c - p.adpF) / p.adpSd);
      if (Sc <= 1e-9) return 0.05;
      return Math.max(0.02, Math.min(1, Sk / Sc));
    }
    function expectedBestAtNext(pos, roster, c, nextP) {
      if (nextP == null) return { ev: 0, likely: null };
      const avail = available().filter(p => p.pos === pos).sort((a, b) => b.val - a.val).slice(0, 14);
      let probNoneBetter = 1, ev = 0, likely = null, likelyP = 0;
      for (const q of avail) {
        const s = survivalProb(q, c, nextP);
        const pBest = probNoneBetter * s;
        const m = marginal(q, roster);
        ev += pBest * m;
        if (pBest > likelyP) { likelyP = pBest; likely = q; }
        probNoneBetter *= (1 - s);
        if (probNoneBetter < 1e-4) break;
      }
      return { ev, likely };
    }

    // ----- opponent model -----
    function oppRosterCounts(roster) {
      const c = { QB: 0, RB: 0, WR: 0, TE: 0, K: 0, DST: 0 };
      roster.forEach(p => c[p.pos]++);
      return c;
    }
    function oppPick(slot, avail, pickNo, rng, picksArr) {
      const roster = rosterOf(slot, picksArr);
      const counts = oppRosterCounts(roster);
      const round = pickRound(pickNo);
      const roundsLeft = cfg.rounds - round;
      const s = cfg.slots;
      const needK = counts.K < s.K, needD = counts.DST < s.DST;
      const mustSlots = (needK ? 1 : 0) + (needD ? 1 : 0);
      if (roundsLeft < mustSlots) {
        const pos = needK ? 'K' : 'DST';
        const cands = avail.filter(p => p.pos === pos);
        if (cands.length) return cands.sort((a, b) => a.adpF - b.adpF)[0];
      }
      const pool = [];
      for (const p of avail) {
        if (pool.length >= 40 && p.adpF > pickNo + 60) break;
        if (p.pos === 'QB' && counts.QB >= s.QB + 1) continue;
        if (p.pos === 'TE' && counts.TE >= s.TE + 1) continue;
        if (p.pos === 'K' && (counts.K >= s.K || roundsLeft > 2 && rng() < 0.93)) continue;
        if (p.pos === 'DST' && (counts.DST >= s.DST || roundsLeft > 3 && rng() < 0.9)) continue;
        if (p.pos === 'QB' && counts.QB >= s.QB && roundsLeft > 3 && rng() < 0.75) continue;
        pool.push(p);
        if (pool.length >= 18) break;
      }
      const cands = pool.length ? pool : avail.slice(0, 10);
      // ~40% of league drafts on value, the rest follow ADP with noise
      if (rng() < 0.4) {
        let bv = null, bs = -Infinity;
        for (const p of cands) {
          const v = Math.max(p.vorp, p.flexVorp != null ? p.flexVorp : -1e9);
          if (v > bs) { bs = v; bv = p; }
        }
        if (bv) return bv;
      }
      let best = null, bestKey = -Infinity;
      for (let i = 0; i < cands.length; i++) {
        const p = cands[i];
        const gumbel = -Math.log(-Math.log(Math.max(1e-9, rng())));
        const key = -(p.adpF) / 5.5 + gumbel;
        if (key > bestKey) { bestKey = key; best = p; }
      }
      return best;
    }

    function myAutoPick(avail, roster, pickNo, rng) {
      let best = null, bestScore = -Infinity;
      const round = pickRound(pickNo);
      const roundsLeft = cfg.rounds - round;
      const counts = oppRosterCounts(roster);
      const s = cfg.slots;
      const needK = counts.K < s.K, needD = counts.DST < s.DST;
      const mustSlots = (needK ? 1 : 0) + (needD ? 1 : 0);
      if (roundsLeft < mustSlots) {
        const pos = needK ? 'K' : 'DST';
        const cands = avail.filter(p => p.pos === pos);
        if (cands.length) return cands.sort((a, b) => b.val - a.val)[0];
      }
      const top = avail.slice(0, 40);
      for (const p of top) {
        if (p.pos === 'K' && (counts.K >= s.K || roundsLeft > 1)) continue;
        if (p.pos === 'DST' && (counts.DST >= s.DST || roundsLeft > 2)) continue;
        if (p.pos === 'QB' && counts.QB >= s.QB + 1) continue;
        if (p.pos === 'TE' && counts.TE >= s.TE + 2) continue;
        if (FLEX_ELIG[p.pos] && counts[p.pos] + 1 > s[p.pos] + 1 + (BENCH_TGT[p.pos] || 0)) continue;
        const m = marginal(p, roster);
        const jitter = (rng ? rng() : 0.5) * 0.8;
        if (m + jitter > bestScore) { bestScore = m + jitter; best = p; }
      }
      return best || avail[0];
    }

    // ----- season simulation with fitted outcome mixture -----
    function drawFactors(rosters, rng) {
      const teamF = {};
      const playerF = new Map();
      for (let t = 1; t <= T; t++) {
        for (const p of rosters[t]) {
          if (!teamF[p.team]) teamF[p.team] = (envMult[p.team] || 1) * Math.exp(MODEL.teamSigma * randn(rng) - 0.5 * MODEL.teamSigma * MODEL.teamSigma);
          const b = MODEL.bust[p.pos] || { early: 0.15, late: 0.2 };
          // per-player durability multiplier (fitted 2023-25: RR 1.71 for prior 4+ missed)
          const pB = clamp((p.posRank <= MODEL.earlyRankCut ? b.early : b.late) * (p.dur || 1), 0.02, 0.6);
          let f;
          if (rng() < pB) f = 0.15 + 0.4 * rng();               // bust/injury season
          else {
            const sg = MODEL.sigma[p.pos] || 0.3;
            f = Math.exp(sg * randn(rng) - 0.5 * sg * sg);       // healthy dispersion
            f = Math.min(2.2, f);
          }
          playerF.set(p.id, f * teamF[p.team]);
        }
      }
      return playerF;
    }

    function weekMeanOf(roster, week, factors) {
      const active = roster.filter(p => p.bye !== week);
      const pool = { QB: [], RB: [], WR: [], TE: [], K: [], DST: [] };
      active.forEach(p => pool[p.pos] && pool[p.pos].push(p));
      const eff = p => p.ppg * (factors ? (factors.get(p.id) || 1) : 1);
      POSITIONS.forEach(pos => pool[pos].sort((a, b) => eff(b) - eff(a)));
      let mean = 0, varsum = 0;
      const used = new Set();
      ['QB', 'RB', 'WR', 'TE', 'K', 'DST'].forEach(pos => {
        for (let i = 0; i < (cfg.slots[pos] || 0); i++) {
          const p = pool[pos][i];
          if (p) { mean += eff(p); varsum += p.sd * p.sd; used.add(p.id); }
        }
      });
      const flexN = cfg.slots.FLEX || 0;
      const flexPool = active.filter(p => FLEX_ELIG[p.pos] && !used.has(p.id)).sort((a, b) => eff(b) - eff(a));
      for (let i = 0; i < flexN && i < flexPool.length; i++) {
        mean += eff(flexPool[i]); varsum += flexPool[i].sd * flexPool[i].sd;
      }
      return { mean, sd: Math.sqrt(varsum) * 0.92 };
    }

    function roundRobinOpponent(t, week, n) {
      const w = (week - 1) % (n - 1);
      if (n % 2 !== 0) return null;
      const pos = [];
      for (let i = 0; i < n - 1; i++) pos.push(((i + w) % (n - 1)) + 1);
      if (t === n) return pos[0];
      const idx = pos.indexOf(t);
      if (idx === 0) return n;
      return pos[(n - 1) - idx];
    }

    function simulateSeasons(rosters, nSeasons, rng) {
      let playoffCount = 0, winSum = 0, ptsSum = 0;
      for (let sIdx = 0; sIdx < nSeasons; sIdx++) {
        const factors = drawFactors(rosters, rng);
        const wins = new Array(T + 1).fill(0);
        const pts = new Array(T + 1).fill(0);
        for (let w = 1; w <= REG_WEEKS; w++) {
          const scores = new Array(T + 1);
          for (let t = 1; t <= T; t++) {
            const m = weekMeanOf(rosters[t], w, factors);
            scores[t] = m.mean + randn(rng) * m.sd;
            pts[t] += scores[t];
          }
          const seen = new Set();
          for (let t = 1; t <= T; t++) {
            if (seen.has(t)) continue;
            const opp = roundRobinOpponent(t, w, T);
            if (!opp) {
              const sorted = scores.slice(1).sort((a, b) => a - b);
              const med = sorted[Math.floor(sorted.length / 2)];
              if (scores[t] > med) wins[t]++;
              seen.add(t); continue;
            }
            seen.add(t); seen.add(opp);
            if (scores[t] > scores[opp]) wins[t]++; else wins[opp]++;
          }
        }
        const order = [];
        for (let t = 1; t <= T; t++) order.push(t);
        order.sort((a, b) => (wins[b] - wins[a]) || (pts[b] - pts[a]));
        if (order.indexOf(cfg.mySlot) + 1 <= cfg.playoffTeams) playoffCount++;
        winSum += wins[cfg.mySlot]; ptsSum += pts[cfg.mySlot];
      }
      return { playoffPct: playoffCount / nSeasons, expWins: winSum / nSeasons, expPts: ptsSum / nSeasons };
    }

    function simulateRestOfDraft(rng, forcedId) {
      const picksArr = state.picks.slice();
      const takenSim = new Set(state.taken);
      let availSorted = players.filter(p => !takenSim.has(p.id)).sort((a, b) => a.adpF - b.adpF);
      let forcedPending = forcedId || null;
      for (let c = picksArr.length + 1; c <= totalPicks; c++) {
        const t = pickTeam(c);
        let chosen = null;
        if (t === cfg.mySlot) {
          if (forcedPending && !takenSim.has(forcedPending)) {
            chosen = byId.get(forcedPending); forcedPending = null;
          } else {
            chosen = myAutoPick(availSorted, rosterOf(cfg.mySlot, picksArr), c, rng);
          }
        } else {
          chosen = oppPick(t, availSorted, c, rng, picksArr);
        }
        if (!chosen) chosen = availSorted[0];
        if (!chosen) break;
        picksArr.push({ playerId: chosen.id, team: t });
        takenSim.add(chosen.id);
        const ix = availSorted.indexOf(chosen);
        if (ix >= 0) availSorted.splice(ix, 1);
      }
      const rosters = [];
      for (let t = 1; t <= T; t++) rosters[t] = rosterOf(t, picksArr);
      return rosters;
    }

    function playoffOddsFor(candidateIds, nDrafts, nSeasons, seed) {
      const results = {};
      const list = candidateIds && candidateIds.length ? candidateIds : [null];
      list.forEach((cid, ci) => {
        const rng = mulberry32((seed || 42) * 7919 + ci * 104729 + state.picks.length * 31);
        let agg = { playoffPct: 0, expWins: 0, expPts: 0 };
        for (let d = 0; d < nDrafts; d++) {
          const rosters = simulateRestOfDraft(rng, cid);
          const r = simulateSeasons(rosters, nSeasons, rng);
          agg.playoffPct += r.playoffPct; agg.expWins += r.expWins; agg.expPts += r.expPts;
        }
        results[cid || '__current__'] = {
          playoffPct: agg.playoffPct / nDrafts, expWins: agg.expWins / nDrafts, expPts: agg.expPts / nDrafts,
        };
      });
      return results;
    }

    // ----- recommendations -----
    function detectRun() {
      const recent = state.picks.slice(-6);
      const counts = {};
      recent.forEach(pk => { const p = byId.get(pk.playerId); counts[p.pos] = (counts[p.pos] || 0) + 1; });
      let runPos = null;
      Object.entries(counts).forEach(([pos, n]) => {
        if (n >= 4 && ['RB', 'WR', 'TE', 'QB'].includes(pos)) runPos = pos;
      });
      return runPos;
    }

    function recommendations(topN) {
      const c = currentPick();
      const roster = rosterOf(cfg.mySlot);
      const nextP = nextPickOf(cfg.mySlot, c);
      const avail = available().sort((a, b) => b.vorp - a.vorp);
      const round = pickRound(c);
      const roundsLeft = cfg.rounds - round;
      const counts = oppRosterCounts(roster);
      const s = cfg.slots;
      const run = detectRun();
      const lu0 = lineup(roster);

      const nextBest = {};
      POSITIONS.forEach(pos => { nextBest[pos] = expectedBestAtNext(pos, roster, c, nextP); });

      const cands = [];
      const seen = new Set();
      POSITIONS.forEach(pos => {
        avail.filter(p => p.pos === pos).slice(0, pos === 'K' || pos === 'DST' ? 3 : 10)
          .forEach(p => { if (!seen.has(p.id)) { seen.add(p.id); cands.push(p); } });
      });

      const needK = counts.K < s.K, needD = counts.DST < s.DST;
      const mustSlots = (needK ? 1 : 0) + (needD ? 1 : 0);

      const scored = cands.map(p => {
        const m = marginal(p, roster);
        const nb = nextBest[p.pos];
        const urg = Math.max(0, m - (nb ? nb.ev : 0));
        const surv = nextP ? survivalProb(p, c, nextP) : 1;
        let score = m + 0.6 * urg;
        if (p.pos === 'K' && counts.K >= s.K) score -= 999;
        if (p.pos === 'DST' && counts.DST >= s.DST) score -= 999;
        if (p.pos === 'QB' && counts.QB >= s.QB + 1) score -= 999;
        if (p.pos === 'TE' && counts.TE >= s.TE + 2) score -= 999;
        if (p.pos === 'K' && roundsLeft > 1 && !(roundsLeft <= mustSlots)) score -= 60;
        if (p.pos === 'DST' && roundsLeft > 2 && !(roundsLeft <= mustSlots)) score -= 55;
        if ((p.pos === 'K' && needK || p.pos === 'DST' && needD) && roundsLeft < mustSlots + 1) score += 80;
        if (p.pos === 'QB' && counts.QB >= s.QB) score -= 25;
        if (p.pos === 'TE' && counts.TE >= s.TE + 1) score -= 25;
        // roster-composition caps: don't hoard one position past realistic depth
        if (FLEX_ELIG[p.pos]) {
          const cap = s[p.pos] + 1 + (BENCH_TGT[p.pos] || 0);
          const after = counts[p.pos] + 1;
          if (after > cap) score -= 15;
          else if (after === cap) score -= 3;
        }
        // hedged-structure controls (validated on dev years, evaluated on holdout)
        if (cfg.hedge) {
          const h = cfg.hedge;
          if (h.anchor) score -= h.anchor * Math.max(0, (p.adpF - c) - (h.anchorSlack != null ? h.anchorSlack : 8));
          if (h.rbFloor && p.pos === 'RB' && counts.RB < s.RB && round >= 3) score += 5 * Math.min(4, round - 2);
          if (h.teGate && p.pos === 'TE' && counts.TE >= s.TE && round < 8) score -= 12;
        }
        const byeClash = lu0.starters.filter(x => x.p.bye === p.bye).length;
        // (bye-stack cost now lives inside lineup(), so marginal() prices it directly)
        if (run && p.pos === run && (counts[run] || 0) < (s[run] || 0) + 1) score += 2;

        const reasons = [];
        if (p.news) reasons.push({ t: 'news', txt: '⚠ ' + p.news });
        const gonePct = Math.round((1 - surv) * 100);
        if (nextP && gonePct >= 45) reasons.push({ t: 'gone', txt: gonePct + '% gone by your next pick' });
        const tierMates = avail.filter(q => q.pos === p.pos && q.tier === p.tier && q.id !== p.id).length;
        if (tierMates === 0 && p.tier < 8) {
          const nxt = avail.find(q => q.pos === p.pos && q.tier > p.tier);
          const drop = nxt ? Math.round(p.val - nxt.val) : 0;
          if (drop >= 8) reasons.push({ t: 'cliff', txt: 'Last of ' + p.pos + ' tier ' + p.tier + ' — next tier −' + drop + ' pts' });
        } else if (tierMates === 1) {
          reasons.push({ t: 'tier', txt: 'Only 2 left in ' + p.pos + ' tier ' + p.tier });
        }
        // analyst context
        if (p.ecr != null) {
          if (p.ecr <= c - 8) reasons.push({ t: 'value', txt: 'Falling: analysts rank him #' + p.ecr + ', still here at #' + c });
          else if (p.ecr >= c + 16 && round <= 9) reasons.push({ t: 'reach', txt: 'Analysts have him ~#' + p.ecr + ' — you can likely wait' });
        }
        // durability context (only the fitted, significant effect)
        if (p.dur >= 1.15) reasons.push({ t: 'injury', txt: 'Injury history — elevated bust risk in sims' });
        else if (p.dur <= 0.91 && p.posRank <= 40 && p.durM != null) reasons.push({ t: 'durable', txt: 'Durable — near-full seasons in 2024-25' });
        // Kalshi context
        if (p.klProb != null && p.klProb >= 0.06) {
          reasons.push({ t: 'kalshi', txt: 'Kalshi: ' + Math.round(p.klProb * 100) + '% to lead ' + p.pos + 's' });
        }
        if (FLEX_ELIG[p.pos] || p.pos === 'QB') {
          const dg = teamDisagree[p.team];
          if (dg != null && Math.abs(dg) >= 10) {
            reasons.push({ t: 'kalshiTeam', txt: 'Kalshi ' + (dg > 0 ? 'higher' : 'lower') + ' on ' + p.team + ' than projections (O/U ' + p.wtLine + ')' });
          }
        }
        const mGap = (p.ecrPosRank != null ? p.ecrPosRank : p.adpPosRank) - p.projPosRank;
        if (mGap >= 5 && p.projPosRank <= 40) reasons.push({ t: 'model', txt: 'Projections ' + p.pos + p.projPosRank + ' vs analysts ' + p.pos + (p.ecrPosRank || p.adpPosRank) });
        const slotFit = fitLabel(p, roster, lu0, counts);
        if (slotFit) reasons.push({ t: 'fit', txt: slotFit });
        if (nb && nb.likely && nb.likely.id !== p.id && nextP) {
          reasons.push({ t: 'wait', txt: 'If you wait: likely ' + nb.likely.name + ' (−' + Math.max(0, Math.round(m - nb.ev)) + ' pts)' });
        }
        if (byeClash >= 3) reasons.push({ t: 'bye', txt: 'Careful: ' + byeClash + ' starters already on bye wk ' + p.bye });
        if (run && p.pos === run) reasons.push({ t: 'run', txt: run + ' run in progress' });

        return { p, m: round2(m), urgency: round2(urg), surv, score: round2(score), reasons };
      }).sort((a, b) => b.score - a.score);

      return { candidates: scored.slice(0, topN || 8), nextPick: nextP, run, nextBest };
    }

    function fitLabel(p, roster, lu, counts) {
      const s = cfg.slots;
      if (p.pos === 'K' || p.pos === 'DST') return counts[p.pos] < s[p.pos] ? 'Fills ' + p.pos : null;
      if (counts[p.pos] < s[p.pos]) return 'Fills starting ' + p.pos + (counts[p.pos] + 1);
      const flexUsed = lu.starters.filter(x => x.slot === 'FLEX').length;
      if (FLEX_ELIG[p.pos] && flexUsed < (s.FLEX || 0)) return 'Fills FLEX';
      if (FLEX_ELIG[p.pos]) {
        const worstFlex = lu.starters.filter(x => x.slot === 'FLEX').map(x => x.p.val);
        if (worstFlex.length && p.val > Math.min(...worstFlex)) return 'Upgrades FLEX';
      }
      if (p.pos === 'QB' && counts.QB >= s.QB) return 'Backup QB';
      return 'Bench depth';
    }

    function round2(x) { return Math.round(x * 100) / 100; }

    return {
      cfg, players, byId, byPos, repl, totalPicks, MODEL, envMult, teamDisagree, wtMean,
      pickTeam, pickRound, teamPickNumbers, nextPickOf,
      state, currentPick, draftOver, onClock, rosterOf, makePick, undo, available,
      lineup, marginal, survivalProb, recommendations,
      simulateRestOfDraft, simulateSeasons, playoffOddsFor, drawFactors,
      mulberry32, detectRun,
      exportState: () => JSON.stringify({
        cfg: { teams: cfg.teams, mySlot: cfg.mySlot, rounds: cfg.rounds, scoring: cfg.scoring, slots: cfg.slots, playoffTeams: cfg.playoffTeams },
        picks: state.picks,
      }),
      importState: (json) => {
        const d = JSON.parse(json);
        state.picks.length = 0; state.taken.clear();
        (d.picks || []).forEach(pk => { state.picks.push(pk); state.taken.add(pk.playerId); });
        return d.cfg;
      },
    };
  }

  const Engine = { create, phi, mulberry32, MODEL: null };
  if (typeof module !== 'undefined' && module.exports) module.exports = Engine;
  global.Engine = Engine;
})(typeof window !== 'undefined' ? window : globalThis);
