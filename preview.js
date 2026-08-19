/* Slot-5-of-8, half-PPR opening preview: engine picks vs need-aware ADP room. */
'use strict';
const fs = require('fs');
const Engine = require('./engine.js');
const PLAYERS = JSON.parse(fs.readFileSync('players.json', 'utf8'));

function adpNeedPick(e, slot, rng) {
  const roster = e.rosterOf(slot);
  const counts = { QB: 0, RB: 0, WR: 0, TE: 0, K: 0, DST: 0 };
  roster.forEach(p => counts[p.pos]++);
  const round = e.pickRound(e.currentPick());
  const roundsLeft = e.cfg.rounds - round;
  const avail = e.available().sort((a, b) => a.adpF - b.adpF);
  const pool = [];
  for (const p of avail) {
    if (p.pos === 'K' && (counts.K >= 1 || roundsLeft > 1)) continue;
    if (p.pos === 'DST' && (counts.DST >= 1 || roundsLeft > 2)) continue;
    if (p.pos === 'QB' && counts.QB >= 2) continue;
    if (p.pos === 'TE' && counts.TE >= 2) continue;
    if (p.pos === 'QB' && counts.QB >= 1 && roundsLeft > 3 && rng() < 0.75) continue;
    pool.push(p);
    if (pool.length >= 14) break;
  }
  let best = null, bestKey = -Infinity;
  for (const p of (pool.length ? pool : avail.slice(0, 8))) {
    const g = -Math.log(-Math.log(Math.max(1e-9, rng())));
    if (-p.adpF / 5.5 + g > bestKey) { bestKey = -p.adpF / 5.5 + g; best = p; }
  }
  return best;
}

const tally = {};   // round -> {playerName: count}
for (let seed = 1; seed <= 12; seed++) {
  const e = Engine.create(PLAYERS, { teams: 8, mySlot: 5, rounds: 16, scoring: 'half', playoffTeams: 4 });
  const rng = Engine.mulberry32(seed * 7919);
  while (!e.draftOver() && e.pickRound(e.currentPick()) <= 8) {
    const clock = e.onClock();
    if (clock === 5) {
      const r = e.pickRound(e.currentPick());
      const rec = e.recommendations(3);
      const top = rec.candidates[0].p;
      tally[r] = tally[r] || {};
      const key = top.name + ' (' + top.pos + top.posRank + ')';
      tally[r][key] = (tally[r][key] || 0) + 1;
      e.makePick(top.id, 5);
    } else {
      e.makePick(adpNeedPick(e, clock, rng).id, clock);
    }
  }
}
console.log('Slot 5 of 8, half-PPR — engine pick frequency across 12 simulated rooms (rounds 1-8):');
for (let r = 1; r <= 8; r++) {
  const t = Object.entries(tally[r] || {}).sort((a, b) => b[1] - a[1]).slice(0, 3)
    .map(([k, v]) => k + ' ×' + v).join(', ');
  console.log('  R' + r + ' (pick ' + ((r % 2 === 1) ? (r - 1) * 8 + 5 : r * 8 - 4) + '): ' + t);
}
