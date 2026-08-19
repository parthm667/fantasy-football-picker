'use strict';
const fs = require('fs');
const Engine = require('./engine.js');
const PLAYERS = JSON.parse(fs.readFileSync('players.json', 'utf8'));
const e = Engine.create(PLAYERS, { teams: 8, mySlot: 5, rounds: 16, scoring: 'half', playoffTeams: 4 });
const take = (frag, team) => {
  const p = e.players.find(x => x.name.includes(frag));
  e.makePick(p.id, team);
};
take('Gibbs', 1); take('Bijan', 2); take('Nacua', 3); take("Ja'Marr", 4);

const rec = e.recommendations(8);
console.log('Engine board at pick 5 (top 6 by score):');
rec.candidates.slice(0, 6).forEach((c, i) => {
  const p = c.p;
  console.log(`  ${i + 1}. ${p.name} ${p.pos}${p.posRank} val ${p.val.toFixed(0)} vorp ${p.vorp.toFixed(0)} score ${c.score.toFixed(1)} dur ${p.dur} | ${c.reasons.map(r => r.txt).join(' · ')}`);
});

const ids = {};
for (const frag of ['McCaffrey', 'St. Brown', 'Smith-Njigba', 'Jonathan Taylor']) {
  ids[frag] = e.players.find(x => x.name.includes(frag)).id;
}
console.log('\nDeep sims (40 drafts x 10 seasons each):');
const t0 = Date.now();
const odds = e.playoffOddsFor(Object.values(ids), 40, 10, 777);
for (const [frag, id] of Object.entries(ids)) {
  const o = odds[id];
  console.log(`  ${frag.padEnd(16)} playoff ${(o.playoffPct * 100).toFixed(1)}%  expWins ${o.expWins.toFixed(2)}  expPts/wk ${(o.expPts / 14).toFixed(0)}`);
}
console.log('  (' + (Date.now() - t0) + 'ms, baseline 4/8 = 50%)');

// what's likely back at pick 12 by position
console.log('\nLikely best available at your next pick (#12):');
for (const pos of ['RB', 'WR']) {
  const nb = rec.nextBest[pos];
  if (nb && nb.likely) console.log(`  ${pos}: ${nb.likely.name} (val ${nb.likely.val.toFixed(0)})`);
}
