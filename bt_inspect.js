'use strict';
const fs = require('fs');
const Engine = require('./engine.js');
const year = process.argv[2] || '2021';
const W = parseFloat(process.argv[3] || '0');
const PLAYERS = JSON.parse(fs.readFileSync(`bt_players_${year}.json`, 'utf8'));
const ACTUAL = JSON.parse(fs.readFileSync(`bt_actuals_${year}.json`, 'utf8'));
const SLOTS = { QB: 1, RB: 2, WR: 2, TE: 1, FLEX: 1, K: 0, DST: 0, BENCH: 6 };

function adpNeedPick(e, slot, rng) {
  const roster = e.rosterOf(slot);
  const counts = { QB: 0, RB: 0, WR: 0, TE: 0 };
  roster.forEach(p => counts[p.pos]++);
  const roundsLeft = 13 - e.pickRound(e.currentPick());
  const avail = e.available().sort((a, b) => a.adpF - b.adpF);
  const pool = [];
  for (const p of avail) {
    if (p.pos === 'QB' && counts.QB >= 2) continue;
    if (p.pos === 'TE' && counts.TE >= 2) continue;
    if (p.pos === 'QB' && counts.QB >= 1 && roundsLeft > 3 && rng() < 0.75) continue;
    pool.push(p);
    if (pool.length >= 18) break;
  }
  let best = null, bestKey = -Infinity;
  for (const p of (pool.length ? pool : avail.slice(0, 10))) {
    const g = -Math.log(-Math.log(Math.max(1e-9, rng())));
    const key = -p.adpF / 5.5 + g;
    if (key > bestKey) { bestKey = key; best = p; }
  }
  return best;
}

// aggregate: where do engine points come from vs control, by position + by round
const posPts = { engine: {}, control: {} }, posCnt = { engine: {}, control: {} };
const roundPos = { engine: {}, control: {} };
const qbRound = { engine: [], control: [] };
for (let seed = 1; seed <= 20; seed++) {
  for (let slot = 1; slot <= 10; slot++) {
    for (const policy of ['engine', 'control']) {
      const e = Engine.create(PLAYERS, { teams: 10, mySlot: slot, rounds: 13, scoring: 'ppr', slots: Object.assign({}, SLOTS), playoffTeams: 6, wScale: W });
      const rng = Engine.mulberry32(seed * 1000003 + slot * 997 + (policy === 'engine' ? 0 : 421));
      while (!e.draftOver()) {
        const clock = e.onClock();
        const pick = (clock === slot && policy === 'engine') ? e.recommendations(1).candidates[0].p : adpNeedPick(e, clock, rng);
        if (clock === slot) {
          const r = e.pickRound(e.currentPick());
          roundPos[policy][r] = roundPos[policy][r] || {};
          roundPos[policy][r][pick.pos] = (roundPos[policy][r][pick.pos] || 0) + 1;
          if (pick.pos === 'QB' && !e.rosterOf(slot).some(p => p.pos === 'QB')) qbRound[policy].push(r);
        }
        e.makePick(pick.id, clock);
      }
      // starters by preseason ADP, actual pts by position
      const roster = e.rosterOf(slot).slice().sort((a, b) => a.adpF - b.adpF);
      const used = new Set(); const take = (pos, n) => {
        let c = 0;
        for (const p of roster) if (!used.has(p.id) && p.pos === pos && c < n) {
          used.add(p.id); posPts[policy][pos] = (posPts[policy][pos] || 0) + (ACTUAL[p.id] || 0); c++;
        }
      };
      take('QB', 1); take('RB', 2); take('WR', 2); take('TE', 1);
      let c = 0;
      for (const p of roster) if (!used.has(p.id) && p.pos !== 'QB' && c < 1) {
        used.add(p.id); posPts[policy]['FLEX_' + p.pos] = (posPts[policy]['FLEX_' + p.pos] || 0) + (ACTUAL[p.id] || 0); c++;
      }
      e.rosterOf(slot).forEach(p => posCnt[policy][p.pos] = (posCnt[policy][p.pos] || 0) + 1);
    }
  }
}
const N = 200;
console.log(`== ${year} wScale=${W} — starter actual pts by slot group (avg per league, engine − control) ==`);
const keys = [...new Set([...Object.keys(posPts.engine), ...Object.keys(posPts.control)])].sort();
for (const k of keys) {
  const a = (posPts.engine[k] || 0) / N, b = (posPts.control[k] || 0) / N;
  console.log(`  ${k.padEnd(9)} engine ${a.toFixed(0).padStart(4)}  control ${b.toFixed(0).padStart(4)}  diff ${(a - b >= 0 ? '+' : '')}${(a - b).toFixed(0)}`);
}
console.log('roster pos counts/league:', JSON.stringify({ engine: Object.fromEntries(Object.entries(posCnt.engine).map(([k, v]) => [k, +(v / N).toFixed(1)])), control: Object.fromEntries(Object.entries(posCnt.control).map(([k, v]) => [k, +(v / N).toFixed(1)])) }));
const avg = a => a.reduce((s, x) => s + x, 0) / a.length;
console.log('first-QB round: engine', avg(qbRound.engine).toFixed(1), 'control', avg(qbRound.control).toFixed(1));
console.log('rounds 1-4 position mix (engine vs control):');
for (let r = 1; r <= 4; r++) console.log(`  R${r}: engine ${JSON.stringify(roundPos.engine[r])} | control ${JSON.stringify(roundPos.control[r])}`);
