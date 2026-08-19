const fs = require('fs');
const Engine = require('./engine.js');
const players = JSON.parse(fs.readFileSync('players.json', 'utf8'));

let pass = 0, fail = 0;
function ok(cond, msg) { if (cond) pass++; else { fail++; console.log('  FAIL:', msg); } }
const find = (e, n) => e.players.find(p => p.name === n);

// ---------- 1. snake math ----------
{
  const e = Engine.create(players, { teams: 10, mySlot: 5, rounds: 16 });
  ok(e.pickTeam(1) === 1 && e.pickTeam(10) === 10 && e.pickTeam(11) === 10 && e.pickTeam(20) === 1 && e.pickTeam(21) === 1, 'snake order');
  ok(e.nextPickOf(5, 5) === 16, 'next pick math');
}

// ---------- 2. scoring formats ----------
{
  const ep = Engine.create(players, { teams: 10, mySlot: 5, scoring: 'ppr' });
  const eh = Engine.create(players, { teams: 10, mySlot: 5, scoring: 'half' });
  const es = Engine.create(players, { teams: 10, mySlot: 5, scoring: 'std' });
  const n = [find(ep, 'Puka Nacua'), find(eh, 'Puka Nacua'), find(es, 'Puka Nacua')];
  console.log('Nacua fmtProj ppr/half/std:', n.map(p => p.fmtProj.toFixed(1)).join('/'),
              'adpF:', n.map(p => p.adpF).join('/'));
  ok(Math.abs(n[0].fmtProj - 339.8) < 0.1, 'ppr proj unchanged');
  ok(Math.abs(n[1].fmtProj - (339.8 - 58.5)) < 0.1, 'half = ppr - rec/2');
  ok(Math.abs(n[2].fmtProj - (339.8 - 117)) < 0.1, 'std = ppr - rec');
  ok(n[1].adpF === 2.9 && n[2].adpF === 3.1, 'format ADP used');
  const q = [find(ep, 'Josh Allen'), find(es, 'Josh Allen')];
  ok(Math.abs(q[0].fmtProj - q[1].fmtProj) < 0.1, 'QB proj format-invariant');
  // std should value early-down RBs relatively higher: Derrick Henry (16 rec) vs Nacua
  const hpr = find(ep, 'Derrick Henry').val / find(ep, 'Puka Nacua').val;
  const hst = find(es, 'Derrick Henry').val / find(es, 'Puka Nacua').val;
  ok(hst > hpr, 'low-reception RB gains relative value in standard: ' + hpr.toFixed(2) + ' -> ' + hst.toFixed(2));
}

// ---------- 3. analyst blend ----------
{
  const e = Engine.create(players, { teams: 10, mySlot: 5 });
  const a = find(e, "De'Von Achane");
  console.log('Achane: fmtProj', a.fmtProj.toFixed(1), 'mktPts', a.mktPts.toFixed(1), 'val', a.val.toFixed(1), 'ecr', a.ecr);
  ok(a.val > a.fmtProj, 'Achane pulled up toward analyst rank');
  const jsn = find(e, 'Jaxon Smith-Njigba');
  ok(Math.abs(jsn.val - jsn.fmtProj) < 12, 'JSN val stays near proj (analysts agree)');
  // board alignment: Spearman(val rank, ecr) over ECR-ranked players
  const withEcr = e.players.filter(p => p.ecr != null && p.ecr <= 150);
  const byVal = e.players.slice().sort((x, y) => y.vorp - x.vorp);   // overall board = value over replacement
  const valRank = new Map(byVal.map((p, i) => [p.id, i + 1]));
  const pairs = withEcr.map(p => [valRank.get(p.id), p.ecr]);
  const nn = pairs.length;
  const rk = vals => { const ord = vals.map((v, i) => [v, i]).sort((x, y) => x[0] - y[0]); const r = []; ord.forEach(([v, i], j) => r[i] = j + 1); return r; };
  const ra = rk(pairs.map(p => p[0])), rb = rk(pairs.map(p => p[1]));
  let d2 = 0; for (let i = 0; i < nn; i++) d2 += (ra[i] - rb[i]) ** 2;
  const rho = 1 - 6 * d2 / (nn * (nn * nn - 1));
  console.log('Spearman(board value, analyst ECR) over', nn, 'players:', rho.toFixed(3));
  ok(rho > 0.8, 'board tracks analyst consensus (rho > 0.8): ' + rho.toFixed(3));
  // top-24 overlap
  const top24 = new Set(byVal.slice(0, 24).map(p => p.id));
  const ecr24 = e.players.filter(p => p.ecr != null && p.ecr <= 24);
  const overlap = ecr24.filter(p => top24.has(p.id)).length;
  console.log('Top-24 overlap with analysts:', overlap + '/24');
  ok(overlap >= 15, 'top-24 mostly matches analysts: ' + overlap);
}

// ---------- 3b. Kalshi layers ----------
{
  const e = Engine.create(players, { teams: 10, mySlot: 5 });
  const ems = Object.values(e.envMult);
  ok(ems.every(v => v >= 0.96 && v <= 1.04), 'env multipliers capped [0.96,1.04]');
  ok(e.envMult.MIA === 0.96, 'MIA env capped at floor: ' + e.envMult.MIA);
  ok(e.envMult.LAR > 1.02, 'LAR env boosted: ' + e.envMult.LAR.toFixed(3));
  const hou = find(e, 'Texans DST'), cle = find(e, 'Browns DST');
  ok(hou.envTilt > 1.01 && cle.envTilt < 0.99, 'DST tilts follow win totals: HOU ' + hou.envTilt.toFixed(3) + ' CLE ' + cle.envTilt.toFixed(3));
  const bow = find(e, 'Brock Bowers'), mcb = find(e, 'Trey McBride');
  ok(bow.kalshiPosRank === 1 && mcb.kalshiPosRank === 2, 'Kalshi TE board: Bowers 1, McBride 2');
  ok(bow.klProb > mcb.klProb, 'Bowers leader prob > McBride');
  const rec = Engine.create(players, { teams: 10, mySlot: 1 }).recommendations(3);
  ok(rec.candidates[0].reasons.some(r => r.t === 'kalshi'), 'pick-1 top rec carries a Kalshi chip');
}

// ---------- 3c. durability layer ----------
{
  const e = Engine.create(players, { teams: 10, mySlot: 5 });
  const allen = find(e, 'Josh Allen'), burrow = find(e, 'Joe Burrow');
  ok(allen.dur <= 0.91, 'Allen (17g x2) durable mult: ' + allen.dur);
  ok(burrow.dur >= 1.15, 'Burrow (8g in 2025) elevated mult: ' + burrow.dur);
  const love = find(e, 'Jeremiyah Love');
  ok(love.dur === 1.0 && love.durM == null, 'rookie neutral durability');
  // bust-rate differential in actual draws
  const rng = Engine.mulberry32(21);
  const rosters = [];
  for (let t = 1; t <= 10; t++) rosters[t] = [];
  rosters[1] = [allen, burrow];
  let bA = 0, bB = 0, N = 6000;
  for (let i = 0; i < N; i++) {
    const f = e.drawFactors(rosters, rng);
    if (f.get(allen.id) < 0.5) bA++;     // <0.5 isolates true bust draws (healthy tail ~2.6%)
    if (f.get(burrow.id) < 0.5) bB++;
  }
  console.log('sim bust rates (<0.5): Allen', (bA/N*100).toFixed(1) + '%', 'Burrow', (bB/N*100).toFixed(1) + '%');
  ok(bB/N > bA/N + 0.015, 'Burrow busts materially more often than Allen in sims');
}

// ---------- 3d. bye-aware roster valuation ----------
{
  const e = Engine.create(players, { teams: 8, mySlot: 5, scoring: 'half' });
  const nacua = find(e, 'Puka Nacua');            // bye 11
  const jsn = find(e, 'Jaxon Smith-Njigba');      // bye 11
  const adams = find(e, 'Davante Adams');         // bye 11
  const stacked = [nacua, jsn, adams];
  const spread = [nacua, Object.assign({}, jsn, { bye: 6 }), Object.assign({}, adams, { bye: 9 })];
  const vStack = e.lineup(stacked).value, vSpread = e.lineup(spread).value;
  ok(vSpread > vStack, 'same players, spread byes > stacked byes: ' + vSpread.toFixed(1) + ' vs ' + vStack.toFixed(1));
  ok(Math.abs((vSpread - vStack) - 15) < 0.01, '3-stack penalty = 15 pts: ' + (vSpread - vStack).toFixed(1));
  // marginal() prices it: same-bye candidate worth less than a different-bye twin
  const roster = [nacua, jsn];                    // two bye-11 starters
  const twinSame = Object.assign({}, adams);      // bye 11
  const twinDiff = Object.assign({}, adams, { bye: 9, id: 'twin-diff' });
  const mSame = e.marginal(twinSame, roster), mDiff = e.marginal(twinDiff, roster);
  ok(mDiff > mSame, 'picking algo penalizes joining a bye stack: ' + mSame.toFixed(1) + ' vs ' + mDiff.toFixed(1));
}

// ---------- 4. season outcome mixture ----------
{
  const e = Engine.create(players, { teams: 10, mySlot: 5 });
  const rng = Engine.mulberry32(11);
  // fake full rosters via a quick sim
  const rosters = e.simulateRestOfDraft(rng, null);
  let sum = 0, cnt = 0, busts = 0;
  for (let i = 0; i < 30; i++) {
    const f = e.drawFactors(rosters, rng);
    f.forEach(v => { sum += v; cnt++; if (v < 0.55) busts++; });
  }
  const mean = sum / cnt, bustRate = busts / cnt;
  console.log('season factor mean', mean.toFixed(3), 'bust-ish rate', (bustRate * 100).toFixed(1) + '%');
  ok(mean > 0.78 && mean < 1.02, 'factor mean sane: ' + mean.toFixed(3));
  ok(bustRate > 0.08 && bustRate < 0.32, 'bust rate in empirical range: ' + bustRate.toFixed(3));
}

// ---------- 5. recommendations + full mock draft (half-PPR) ----------
{
  const e = Engine.create(players, { teams: 10, mySlot: 1, scoring: 'half' });
  const rec = e.recommendations(8);
  console.log('pick-1 recs (half):', rec.candidates.slice(0, 5).map(c => c.p.name + '(' + c.p.pos + (c.p.ecr ? ' ecr' + c.p.ecr : '') + ')').join(', '));
  ok(['RB', 'WR'].includes(rec.candidates[0].p.pos), 'first rec RB/WR');
  ok(rec.candidates[0].p.ecr <= 8, 'pick-1 rec is an analyst top-8 player: ecr=' + rec.candidates[0].p.ecr);

  const e2 = Engine.create(players, { teams: 10, mySlot: 5, rounds: 16, scoring: 'half' });
  const rng = Engine.mulberry32(7);
  while (!e2.draftOver()) {
    const clock = e2.onClock();
    if (clock === 5) e2.makePick(e2.recommendations(5).candidates[0].p.id, 5);
    else {
      const availSorted = e2.available().sort((a, b) => a.adpF - b.adpF);
      e2.makePick(availSorted[Math.min(availSorted.length - 1, Math.floor(rng() * 6))].id, clock);
    }
  }
  const mine = e2.rosterOf(5);
  const counts = {};
  mine.forEach(p => counts[p.pos] = (counts[p.pos] || 0) + 1);
  console.log('mock roster counts:', JSON.stringify(counts));
  ok(mine.length === 16, '16 players drafted');
  ok(counts.K === 1 && counts.DST === 1, 'exactly one K and one DST');
  ok(counts.QB >= 1 && counts.QB <= 2, 'QB 1-2');
  ok((counts.RB || 0) >= 4 && (counts.RB || 0) <= 8, 'RB 4-8: ' + counts.RB);
  ok((counts.WR || 0) >= 4 && (counts.WR || 0) <= 8, 'WR 4-8: ' + counts.WR);
  ok(e2.lineup(mine).starters.length === 9, 'full lineup');
}

// ---------- 6. playoff odds + perf ----------
{
  const e = Engine.create(players, { teams: 10, mySlot: 5, rounds: 16 });
  const rng = Engine.mulberry32(3);
  for (let i = 0; i < 40; i++) {
    const availSorted = e.available().sort((a, b) => a.adpF - b.adpF);
    e.makePick(availSorted[Math.min(availSorted.length - 1, Math.floor(rng() * 4))].id, e.onClock());
  }
  let t0 = Date.now();
  const rec = e.recommendations(6);
  console.log('mid-draft recs:', rec.candidates.slice(0, 4).map(c =>
    c.p.name + ' s=' + c.score + ' [' + c.reasons.map(r => r.txt).join(' | ') + ']').join('\n   '));
  const tRec = Date.now() - t0;
  ok(tRec < 400, 'recs < 400ms: ' + tRec);
  const cands = rec.candidates.slice(0, 4).map(c => c.p.id);
  t0 = Date.now();
  const odds = e.playoffOddsFor(cands, 12, 6, 99);
  const tOdds = Date.now() - t0;
  Object.entries(odds).forEach(([id, o]) => console.log('  ', id, (o.playoffPct * 100).toFixed(1) + '%', o.expWins.toFixed(2) + 'w'));
  console.log('candidate sims took', tOdds, 'ms');
  const vals = Object.values(odds).map(o => o.playoffPct);
  ok(vals.every(v => v >= 0 && v <= 1) && vals.some(v => v > 0.2 && v < 0.95), 'odds sane');
  ok(tOdds < 8000, 'sims < 8s: ' + tOdds);
  const cur = e.playoffOddsFor(null, 10, 6, 5)['__current__'];
  console.log('current roster:', (cur.playoffPct * 100).toFixed(1) + '%');
  ok(cur.playoffPct > 0.15 && cur.playoffPct < 0.95, 'current odds not degenerate');
}

// ---------- 7. export/import with scoring ----------
{
  const e = Engine.create(players, { teams: 12, mySlot: 3, scoring: 'std' });
  e.makePick(e.players.sort((a, b) => a.adpF - b.adpF)[0].id, 1);
  const exp = JSON.parse(e.exportState());
  ok(exp.cfg.scoring === 'std' && exp.cfg.teams === 12, 'export carries scoring + teams');
}

console.log('\n=== ' + pass + ' passed, ' + fail + ' failed ===');
process.exit(fail ? 1 : 0);
