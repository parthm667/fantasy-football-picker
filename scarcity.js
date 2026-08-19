'use strict';
const fs = require('fs');
const Engine = require('./engine.js');
const PLAYERS = JSON.parse(fs.readFileSync('players.json', 'utf8'));
const e = Engine.create(PLAYERS, { teams: 8, mySlot: 5, rounds: 16, scoring: 'half', playoffTeams: 4 });

const val = pos => e.byPos[pos].map(p => p.val);
console.log('== Half-PPR blended value by positional rank (8-team) ==');
console.log('rank :   RB    WR    TE    QB');
for (const r of [1, 3, 5, 8, 10, 12, 15, 20, 25, 30]) {
  const row = ['RB', 'WR', 'TE', 'QB'].map(pos => (val(pos)[r - 1] || 0).toFixed(0).padStart(5));
  console.log(String(r).padStart(4) + ' :' + row.join(' '));
}
console.log('\nDrop-offs (points lost):');
for (const pos of ['RB', 'WR', 'TE']) {
  const v = val(pos);
  console.log(`  ${pos}: 1->5 ${(v[0]-v[4]).toFixed(0)} | 5->10 ${(v[4]-v[9]).toFixed(0)} | 10->15 ${(v[9]-v[14]).toFixed(0)} | 15->25 ${(v[14]-v[24]).toFixed(0)}`);
}
console.log('\n8-team replacement levels (freely available quality):', JSON.stringify(
  Object.fromEntries(Object.entries(e.repl).map(([k, v]) => [k, Math.round(v)]))));

// elite-RB tier: engine tier breaks
const rbs = e.byPos.RB.slice(0, 16);
console.log('\nRB tiers (engine):', rbs.map(p => `${p.posRank}.${p.name.split(' ').slice(-1)[0]}(T${p.tier})`).join(' '));

// market pricing check: are early RBs cheap or expensive vs model value?
console.log('\nMarket vs model (top 24 by 8-team half ADP):');
const byAdp = e.players.filter(p => p.adpF < 25).sort((a, b) => a.adpF - b.adpF);
const posCount = { RB: 0, WR: 0, TE: 0, QB: 0 };
byAdp.forEach(p => posCount[p.pos]++);
console.log('  first 3 rounds by ADP:', JSON.stringify(posCount));
// value-over-replacement per ADP dollar: mean vorp of RBs vs WRs taken in picks 1-16
const early = e.players.filter(p => p.adpF <= 16);
for (const pos of ['RB', 'WR']) {
  const g = early.filter(p => p.pos === pos);
  if (g.length) console.log(`  picks 1-16 ${pos}s: n=${g.length}, mean VOR ${ (g.reduce((s,p)=>s+p.vorp,0)/g.length).toFixed(0)}`);
}
