'use strict';
const fs = require('fs');
const Engine = require('./engine.js');
const PLAYERS = JSON.parse(fs.readFileSync('players.json', 'utf8'));

// board rows, columns T1..T4, YOU(5), T6..T8 — exact dataset names
const ROWS = [
  ['Jahmyr Gibbs','Bijan Robinson',"Ja'Marr Chase",'Puka Nacua','Jaxon Smith-Njigba','Christian McCaffrey','Jonathan Taylor','Amon-Ra St. Brown'],
  ['Chase Brown','Drake London','Kenneth Walker III',"De'Von Achane",'James Cook III','Justin Jefferson','CeeDee Lamb','Saquon Barkley'],
  ['Brock Bowers','Malik Nabers','Ashton Jeanty','Derrick Henry','Trey McBride','Omarion Hampton','Jeremiyah Love','A.J. Brown'],
  ['Chris Olave','Lamar Jackson','Kyren Williams','Nico Collins','George Pickens','Josh Allen','Rashee Rice','Josh Jacobs'],
  ['DeVonta Smith','Javonte Williams','Jaylen Waddle','Tetairoa McMillan','Breece Hall','Emeka Egbuka','Garrett Wilson','Ladd McConkey'],
  ['Bucky Irving','Davante Adams','DJ Moore','Cam Skattebo','Tee Higgins','Quinshon Judkins','Zay Flowers','Travis Etienne Jr.'],
  ['David Montgomery','Colston Loveland','Rome Odunze','Drake Maye','Luther Burden III','Jadarian Price','Tyler Warren','Jayden Daniels'],
  ['Joe Burrow','Jameson Williams','Terry McLaurin','Courtland Sutton','Bhayshul Tuten',"D'Andre Swift",'Jalen Hurts','TreVeyon Henderson'],
  ['Mike Evans','Rhamondre Stevenson','Matthew Stafford','DK Metcalf','Christian Watson','Michael Wilson','Carnell Tate','Parker Washington'],
  ['Brian Thomas Jr.','Alec Pierce','Deebo Samuel','Jakobi Meyers','Tony Pollard','Sam LaPorta','Michael Pittman Jr.','Harold Fannin Jr.'],
  ['Trevor Lawrence','Jaxson Dart','Tucker Kraft','Bo Nix','Dak Prescott','Brandon Aubrey','Marvin Harrison Jr.','Justin Herbert'],
  ['George Kittle','Broncos DST','Rams DST','Dallas Goedert','Jaylen Warren','Texans DST','Kyle Pitts','Patrick Mahomes'],
  ["Ka'imi Fairbairn",'Rico Dowdle','Jordyn Tyson','Steelers DST','Mark Andrews','Travis Kelce','Matthew Golden','Jonathon Brooks'],
  ['Quentin Johnston','Kenneth Gainwell','Stefon Diggs','Kyle Monangai','J.K. Dobbins','Rachaad White','Brock Purdy','Ravens DST'],
  ['Seahawks DST','Cameron Dicker','Jason Myers','Cam Little','Trey Smack','Caleb Williams','Chuba Hubbard','Jake Bates'],
  ['Jacory Croskey-Merritt','Hunter Henry','RJ Harvey','Patriots DST','Vikings DST','Makai Lemon','Eagles DST','Jake Ferguson'],
  ['Chargers DST',"Wan'Dale Robinson",'Isaiah Likely','Daniel Jones','Josh Downs','Blake Corum','Harrison Mevis','Jordan Mason'],
];

function makeEngine(slot) {
  return Engine.create(PLAYERS, {
    teams: 8, mySlot: slot, rounds: 17, scoring: 'half',
    slots: { QB: 1, RB: 2, WR: 2, TE: 1, FLEX: 1, K: 1, DST: 1, BENCH: 8 },
    playoffTeams: 4,
  });
}
const probe = makeEngine(5);
const byName = new Map(probe.players.map(p => [p.name, p.id]));
const missing = [];
ROWS.flat().forEach(n => { if (!byName.has(n)) missing.push(n); });
if (missing.length) { console.log('UNRESOLVED:', missing); process.exit(1); }

function loadPicks(e) {
  for (let r = 1; r <= 17; r++) {
    const row = ROWS[r - 1];
    const order = r % 2 === 1 ? [0,1,2,3,4,5,6,7] : [7,6,5,4,3,2,1,0];
    for (const c of order) {
      const res = e.makePick(byName.get(row[c]), c + 1);
      if (!res.ok) { console.log('PICK FAIL', r, c, row[c], res.err); process.exit(1); }
    }
  }
}

// league table: each seat's odds on the fixed rosters (draft over -> 1 draft, many seasons)
console.log('== League playoff odds (4 of 8 spots, 2000 simulated seasons each) ==');
const table = [];
for (let t = 1; t <= 8; t++) {
  const e = makeEngine(t);
  loadPicks(e);
  const o = e.playoffOddsFor(null, 1, 2000, 4242)['__current__'];
  table.push({ t, playoff: o.playoffPct, wins: o.expWins, pts: o.expPts / 14 });
}
table.sort((a, b) => b.playoff - a.playoff);
table.forEach((r, i) => console.log(
  `  ${i + 1}. ${r.t === 5 ? 'YOU ' : 'T' + r.t + '  '}  playoff ${(r.playoff * 100).toFixed(1)}%  expWins ${r.wins.toFixed(2)}  pts/wk ${r.pts.toFixed(1)}`));

// my details
const me = makeEngine(5);
loadPicks(me);
const roster = me.rosterOf(5);
const lu = me.lineup(roster);
console.log('\n== Your lineup (half-PPR blended values) ==');
lu.starters.forEach(s => console.log(`  ${s.slot.padEnd(5)} ${s.p.name.padEnd(24)} ${s.p.val.toFixed(0)} (bye ${s.p.bye})`));
console.log('  bench:', lu.bench.map(p => p.name + ' (' + p.pos + ', bye ' + p.bye + ')').join(', '));
console.log('  bye-stack penalty charged:', lu.byePen, 'pts');

console.log('\n== Bye exposure (starters out per week) ==');
const weeks = {};
lu.starters.forEach(s => { if (s.p.bye) (weeks[s.p.bye] = weeks[s.p.bye] || []).push(s.p.name.split(' ').slice(-1)[0] + '(' + s.p.pos + ')'); });
Object.keys(weeks).sort((a, b) => a - b).forEach(w =>
  console.log(`  wk ${w}: ${weeks[w].length} — ${weeks[w].join(', ')}`));

console.log('\n== Best available on waivers (undrafted, by value) ==');
me.available().sort((a, b) => b.val - a.val).slice(0, 14).forEach(p =>
  console.log(`  ${p.pos.padEnd(3)} ${p.name.padEnd(24)} val ${p.val.toFixed(0)}${p.pos === 'QB' ? '  <- wk-14 QB cover' : ''}`));
