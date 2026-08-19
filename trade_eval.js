'use strict';
const fs = require('fs');
const Engine = require('./engine.js');
const PLAYERS = JSON.parse(fs.readFileSync('players.json', 'utf8'));

const BASE = [
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

function clone(rows) { return rows.map(r => r.slice()); }
function runScenario(label, rows) {
  const results = {};
  for (const slot of [5, 3, 8]) {
    const e = Engine.create(PLAYERS, {
      teams: 8, mySlot: slot, rounds: 17, scoring: 'half',
      slots: { QB: 1, RB: 2, WR: 2, TE: 1, FLEX: 1, K: 1, DST: 1, BENCH: 8 }, playoffTeams: 4,
    });
    const byName = new Map(e.players.map(p => [p.name, p.id]));
    for (let r = 1; r <= 17; r++) {
      const row = rows[r - 1];
      const order = r % 2 === 1 ? [0,1,2,3,4,5,6,7] : [7,6,5,4,3,2,1,0];
      for (const c of order) {
        const res = e.makePick(byName.get(row[c]), c + 1);
        if (!res.ok) { console.log('FAIL', label, r, row[c], res.err); process.exit(1); }
      }
    }
    results[slot] = e.playoffOddsFor(null, 1, 2000, 991)['__current__'];
  }
  console.log(`${label.padEnd(26)} YOU ${(results[5].playoffPct*100).toFixed(1)}%  (T3 ${(results[3].playoffPct*100).toFixed(1)}%, T8 ${(results[8].playoffPct*100).toFixed(1)}%)`);
  return results;
}

runScenario('BASELINE (no trade)', BASE);

// Trade 1: send Cook -> T3(pani); receive McLaurin + Odunze; you drop Downs; T3 backfills w/ FA Pacheco
const t1 = clone(BASE);
t1[1][4] = 'Terry McLaurin';        // Cook slot -> McLaurin
t1[16][4] = 'Rome Odunze';          // Downs dropped -> Odunze in
t1[6][2] = 'James Cook III';        // T3 Odunze slot -> Cook
t1[7][2] = 'Isiah Pacheco';         // T3 McLaurin slot -> FA backfill
runScenario('TRADE 1 (Cook out)', t1);

// Trade 2: send Pickens -> T8(Rahul); receive Mahomes + P.Washington + Etienne; drop Downs + Dobbins; T8 backfills 2 FAs
const t2 = clone(BASE);
t2[3][4] = 'Travis Etienne Jr.';    // Pickens slot -> Etienne
t2[13][4] = 'Parker Washington';    // Dobbins dropped -> P.Washington
t2[16][4] = 'Patrick Mahomes';      // Downs dropped -> Mahomes
t2[5][7] = 'George Pickens';        // T8 Etienne slot -> Pickens
t2[8][7] = 'Jayden Reed';           // T8 P.Washington slot -> FA
t2[11][7] = 'Baker Mayfield';       // T8 Mahomes slot -> FA
runScenario('TRADE 2 (Pickens out)', t2);

// Trade 1b (sweetened): Cook -> T3; receive Deebo + McLaurin + Odunze; drop Downs + Dobbins; T3 backfills 2 FAs
const t1b = clone(BASE);
t1b[1][4] = 'Terry McLaurin';
t1b[16][4] = 'Rome Odunze';
t1b[13][4] = 'Deebo Samuel';
t1b[6][2] = 'James Cook III';
t1b[7][2] = 'Isiah Pacheco';
t1b[9][2] = 'Jayden Reed';
runScenario('TRADE 1b (3 WRs for Cook)', t1b);
