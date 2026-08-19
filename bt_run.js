/* Lookahead-safe draft backtest on the real engine.
   Usage: node bt_run.js <playersFile> <actualsFile> <seeds> <label> [outFile]
   - engine seat: picks via eng.recommendations(1) (the shipped product path)
   - control seat + all opponents: need-aware ADP drafting (no engine value signal)
   - scoring: rosters scored with ACTUAL season points; lineups set by preseason
     ADP order (no hindsight); hindsight-optimal lineup reported as upper bound   */
'use strict';
const fs = require('fs');
const Engine = require('./engine.js');

const [playersFile, actualsFile, seedsArg, label, outFile, wScaleArg, qbStreamArg, anchorArg, rbFloorArg, teGateArg] = process.argv.slice(2);
const WSCALE = wScaleArg != null ? parseFloat(wScaleArg) : 1;
const QBSTREAM = qbStreamArg != null ? parseFloat(qbStreamArg) : 1.3;
const HEDGE = (anchorArg || rbFloorArg || teGateArg)
  ? { anchor: parseFloat(anchorArg || '0'), anchorSlack: 8, rbFloor: parseInt(rbFloorArg || '0', 10), teGate: parseInt(teGateArg || '0', 10) }
  : null;
const PLAYERS = JSON.parse(fs.readFileSync(playersFile, 'utf8'));
const ACTUAL = JSON.parse(fs.readFileSync(actualsFile, 'utf8'));
const SEEDS = parseInt(seedsArg || '20', 10);
const SLOTS = { QB: 1, RB: 2, WR: 2, TE: 1, FLEX: 1, K: 0, DST: 0, BENCH: 6 };
const TEAMS = 10, ROUNDS = 13, PLAYOFF = 6;

function mkEngine(mySlot) {
  return Engine.create(PLAYERS, { teams: TEAMS, mySlot, rounds: ROUNDS, scoring: 'ppr', slots: Object.assign({}, SLOTS), playoffTeams: PLAYOFF, wScale: WSCALE, qbStream: QBSTREAM, hedge: HEDGE });
}

// need-aware ADP drafter: right position at roughly the right time, no value model
function adpNeedPick(e, slot, rng) {
  const roster = e.rosterOf(slot);
  const counts = { QB: 0, RB: 0, WR: 0, TE: 0 };
  roster.forEach(p => counts[p.pos]++);
  const round = e.pickRound(e.currentPick());
  const roundsLeft = ROUNDS - round;
  // starting slots still empty (flex counts once, fillable by RB/WR/TE surplus)
  const needQB = Math.max(0, SLOTS.QB - counts.QB);
  const skillStarters = SLOTS.RB + SLOTS.WR + SLOTS.TE + SLOTS.FLEX;
  const needRB = Math.max(0, SLOTS.RB - counts.RB), needWR = Math.max(0, SLOTS.WR - counts.WR), needTE = Math.max(0, SLOTS.TE - counts.TE);
  const skillHave = counts.RB + counts.WR + counts.TE;
  const needFlex = Math.max(0, skillStarters - Math.max(skillHave, SLOTS.RB - needRB + SLOTS.WR - needWR + SLOTS.TE - needTE + (skillHave > (SLOTS.RB + SLOTS.WR + SLOTS.TE) ? 1 : 0)));
  const emptyStarters = needQB + needRB + needWR + needTE + Math.max(0, Math.min(1, needFlex));
  const mustFill = roundsLeft + 1 <= emptyStarters;
  const avail = e.available().sort((a, b) => a.adpF - b.adpF);
  const pool = [];
  for (const p of avail) {
    if (mustFill) {
      const needed = (p.pos === 'QB' && needQB) || (p.pos === 'RB' && (needRB || needFlex)) ||
                     (p.pos === 'WR' && (needWR || needFlex)) || (p.pos === 'TE' && (needTE || needFlex));
      if (!needed) continue;
    }
    if (p.pos === 'QB' && counts.QB >= SLOTS.QB + 1) continue;                      // hard cap 2 QBs
    if (p.pos === 'TE' && counts.TE >= SLOTS.TE + 1) continue;                      // hard cap 2 TEs
    if (p.pos === 'QB' && counts.QB >= SLOTS.QB && roundsLeft > 3 && rng() < 0.75) continue; // right time for QB2
    pool.push(p);
    if (pool.length >= 18) break;
  }
  const cands = pool.length ? pool : avail.slice(0, 10);
  let best = null, bestKey = -Infinity;
  for (const p of cands) {
    const g = -Math.log(-Math.log(Math.max(1e-9, rng())));
    const key = -p.adpF / 5.5 + g;
    if (key > bestKey) { bestKey = key; best = p; }
  }
  return best;
}

// lineup by a given ordering metric; scored with actual points
function scoreRoster(e, roster, metric) {
  const by = m => roster.slice().sort((a, b) => m(b) - m(a));
  const ord = metric === 'hindsight' ? by(p => ACTUAL[p.id] || 0) : by(p => -p.adpF);
  const used = new Set(); let pts = 0;
  const fill = (pos, n) => {
    let c = 0;
    for (const p of ord) if (!used.has(p.id) && p.pos === pos && c < n) { used.add(p.id); pts += ACTUAL[p.id] || 0; c++; }
  };
  fill('QB', SLOTS.QB); fill('RB', SLOTS.RB); fill('WR', SLOTS.WR); fill('TE', SLOTS.TE);
  let c = 0;
  for (const p of ord) if (!used.has(p.id) && (p.pos === 'RB' || p.pos === 'WR' || p.pos === 'TE') && c < SLOTS.FLEX) { used.add(p.id); pts += ACTUAL[p.id] || 0; c++; }
  return pts;
}

function runLeague(mySlot, seed, policy) {
  const e = mkEngine(mySlot);
  const rng = Engine.mulberry32(seed * 1000003 + mySlot * 997 + (policy === 'engine' ? 0 : 421));
  while (!e.draftOver()) {
    const clock = e.onClock();
    let pick;
    if (clock === mySlot && policy === 'engine') {
      pick = e.recommendations(1).candidates[0].p;
    } else {
      pick = adpNeedPick(e, clock, rng);
    }
    e.makePick(pick.id, clock);
  }
  const res = { exp: [], hind: [] };
  for (let t = 1; t <= TEAMS; t++) {
    const r = e.rosterOf(t);
    res.exp[t] = scoreRoster(e, r, 'exp');
    res.hind[t] = scoreRoster(e, r, 'hindsight');
  }
  const rankOf = (arr) => arr.slice(1).filter(x => x > arr[mySlot]).length + 1;
  return {
    slot: mySlot, seed, policy,
    pts: Math.round(res.exp[mySlot]), rank: rankOf(res.exp),
    top6: rankOf(res.exp) <= PLAYOFF ? 1 : 0,
    margin: Math.round(res.exp[mySlot] - median(res.exp.slice(1))),
    hindRank: rankOf(res.hind), hindTop6: rankOf(res.hind) <= PLAYOFF ? 1 : 0,
  };
}
function median(a) { const s = a.slice().sort((x, y) => x - y); return (s[4] + s[5]) / 2; }

const rows = [];
for (let seed = 1; seed <= SEEDS; seed++)
  for (let slot = 1; slot <= TEAMS; slot++)
    for (const policy of ['engine', 'control'])
      rows.push(runLeague(slot, seed, policy));

const agg = {};
for (const pol of ['engine', 'control']) {
  const r = rows.filter(x => x.policy === pol);
  agg[pol] = {
    n: r.length,
    meanRank: avg(r.map(x => x.rank)), top6: avg(r.map(x => x.top6)),
    meanMargin: avg(r.map(x => x.margin)), meanPts: avg(r.map(x => x.pts)),
    hindTop6: avg(r.map(x => x.hindTop6)), hindMeanRank: avg(r.map(x => x.hindRank)),
  };
}
// paired diffs by (slot, seed)
const diffs = [];
for (let seed = 1; seed <= SEEDS; seed++) for (let slot = 1; slot <= TEAMS; slot++) {
  const a = rows.find(x => x.policy === 'engine' && x.seed === seed && x.slot === slot);
  const b = rows.find(x => x.policy === 'control' && x.seed === seed && x.slot === slot);
  diffs.push({ dRank: a.rank - b.rank, dTop6: a.top6 - b.top6, dMargin: a.margin - b.margin });
}
function avg(a) { return a.reduce((s, x) => s + x, 0) / a.length; }
function tstat(a) { const m = avg(a); const v = a.reduce((s, x) => s + (x - m) ** 2, 0) / (a.length - 1); return m / Math.sqrt(v / a.length); }
agg.paired = {
  n: diffs.length,
  dRank: avg(diffs.map(d => d.dRank)), tRank: tstat(diffs.map(d => d.dRank)),
  dTop6: avg(diffs.map(d => d.dTop6)), tTop6: tstat(diffs.map(d => d.dTop6)),
  dMargin: avg(diffs.map(d => d.dMargin)), tMargin: tstat(diffs.map(d => d.dMargin)),
};
console.log(label, JSON.stringify(agg, null, 1));
if (outFile) fs.writeFileSync(outFile, JSON.stringify({ label, agg, rows }, null, 0));
