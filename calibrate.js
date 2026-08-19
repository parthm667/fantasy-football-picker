/* Per-slot calibration: what does the tool recommend from every draft slot in
   rounds 1-3 (opponents drafting straight ADP), and does it track analyst boards? */
const fs = require('fs');
const Engine = require('./engine.js');
const players = JSON.parse(fs.readFileSync('players.json', 'utf8'));

let fail = 0;
for (const scoring of ['ppr', 'half', 'std']) {
  console.log('\n========== ' + scoring.toUpperCase() + ' — 10-team, rounds 1-3 by slot ==========');
  for (let slot = 1; slot <= 10; slot++) {
    const e = Engine.create(players, { teams: 10, mySlot: slot, rounds: 16, scoring });
    const picksTxt = [];
    for (let round = 1; round <= 3; round++) {
      while (!e.draftOver() && e.onClock() !== slot) {
        const bestAdp = e.available().sort((a, b) => a.adpF - b.adpF)[0];
        e.makePick(bestAdp.id, e.onClock());
      }
      if (e.draftOver()) break;
      const pickNo = e.currentPick();
      const rec = e.recommendations(3).candidates[0];
      e.makePick(rec.p.id, slot);
      const ecr = rec.p.ecr;
      picksTxt.push(`R${round} #${pickNo}: ${rec.p.name} (${rec.p.pos}${rec.p.posRank}, ECR ${ecr ?? '—'})`);
      // tolerance: recommended player's analyst rank shouldn't be wildly past the pick
      if (scoring === 'ppr' && ecr != null && ecr > pickNo + 17) {
        console.log(`   !! reach vs analysts at slot ${slot} R${round}: ECR ${ecr} at pick ${pickNo}`);
        fail++;
      }
    }
    console.log(`slot ${String(slot).padStart(2)}: ` + picksTxt.join('  |  '));
  }
}
console.log(fail ? `\n${fail} reach warnings` : '\nAll slot recommendations within analyst tolerance');
process.exit(fail ? 1 : 0);
