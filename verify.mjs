import { createRequire } from 'module';
import path from 'path';
const require = createRequire('/usr/lib/node_modules/');
const { chromium } = require('playwright');

const file = 'file://' + path.resolve('draft-command-2026.html');
const errors = [];
const browser = await chromium.launch();

function watch(page, tag) {
  page.on('console', m => { if (m.type() === 'error') errors.push(tag + ' console: ' + m.text()); });
  page.on('pageerror', e => errors.push(tag + ' pageerror: ' + e.message));
}

// ============ A. PPR interactive flow (phone) ============
{
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage(); watch(page, 'A');
  await page.goto(file);
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shots/v2-01-setup.png' });
  await page.click('#startBtn');
  await page.waitForTimeout(300);

  async function logPick(q) {
    await page.fill('#searchInput', q);
    await page.waitForTimeout(220);
    await page.click('#searchResults .prow');
    await page.waitForTimeout(150);
    await page.click('#confirmYes');
    await page.waitForTimeout(200);
  }
  await logPick('gibbs'); await logPick('bijan'); await logPick('chase'); await logPick('nacua');

  await page.waitForFunction(() => {
    const v = document.querySelector('.oddsVal');
    return v && v.textContent.includes('%');
  }, null, { timeout: 20000 }).catch(() => errors.push('A: sims never completed'));
  await page.waitForTimeout(1500);
  const stars = await page.evaluate(() => [...document.querySelectorAll('.oddsVal')].filter(v => v.textContent.includes('★')).length);
  if (stars !== 1) errors.push('A: expected exactly 1 starred card, got ' + stars);
  const meta = await page.textContent('.recCard .recMeta');
  if (!meta.includes('analysts #')) errors.push('A: rec card missing analyst rank: ' + meta);
  if (!meta.includes('O/U')) errors.push('A: rec card missing Kalshi O/U: ' + meta);
  const hasKalshiChip = await page.evaluate(() =>
    [...document.querySelectorAll('.reasons .chip')].some(c => c.textContent.includes('Kalshi')));
  if (!hasKalshiChip) errors.push('A: no Kalshi chips rendered');
  const dp = await page.evaluate(() => {
    const d = document.querySelector('.decision');
    const v = document.getElementById('simVerdict');
    return { exists: !!d, txt: d ? d.textContent : '', sims: v ? v.textContent : '' };
  });
  if (!dp.exists) errors.push('A: decision panel missing');
  else {
    if (!dp.txt.includes('waiting costs')) errors.push('A: decision panel missing wait-cost lines: ' + dp.txt.slice(0, 120));
    if (!dp.sims.includes('%')) errors.push('A: sim verdict never populated: ' + dp.sims);
  }
  await page.screenshot({ path: 'shots/v2-02-myturn.png', fullPage: true });

  const s1 = await page.textContent('#statusLine1');
  if (!s1.includes('YOUR PICK')) errors.push('A: not my turn at pick 5: ' + s1);
  await page.click('.recCard .draftBtn');
  await page.waitForTimeout(350);
  if (!(await page.textContent('#statusLine1')).includes('Pick 6')) errors.push('A: pick did not advance');
  await page.click('#undoBtn');
  await page.waitForTimeout(300);
  if (!(await page.textContent('#statusLine1')).includes('Pick 5')) errors.push('A: undo failed');

  // CSV export generates a full board
  const csvCheck = await page.evaluate(() => {
    const csv = window.__dc.csv();
    const lines = csv.split('\n');
    return { lines: lines.length, header: lines[0].includes('analyst_rank'), avail: csv.includes('available'), drafted: csv.includes('drafted') };
  });
  if (csvCheck.lines < 100 || !csvCheck.header || !csvCheck.avail || !csvCheck.drafted) errors.push('A: CSV export bad: ' + JSON.stringify(csvCheck));

  // crash-proofing: hash restore after reload
  const hash1 = await page.evaluate(() => location.hash);
  if (!hash1.includes('d=')) errors.push('A: no autosave hash: ' + hash1.slice(0, 40));
  await page.reload();
  await page.waitForTimeout(700);
  const r1 = await page.evaluate(() => ({
    main: !document.getElementById('mainView').classList.contains('hidden'),
    picks: window.__dc.eng() ? window.__dc.eng().state.picks.length : -1,
  }));
  if (!r1.main || r1.picks !== 4) errors.push('A: hash restore failed: ' + JSON.stringify(r1));
  // storage restore with hash stripped
  await page.evaluate(() => history.replaceState(null, '', location.pathname));
  await page.reload();
  await page.waitForTimeout(700);
  const r2 = await page.evaluate(() => window.__dc.eng() ? window.__dc.eng().state.picks.length : -1);
  if (r2 !== 4) errors.push('A: storage restore failed: ' + r2);
  await ctx.close();
}

// ============ B. Standard scoring correctness ============
{
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage(); watch(page, 'B');
  await page.goto(file);
  await page.click('#scoringSeg button:has-text("Standard")');
  await page.waitForTimeout(150);
  await page.click('#startBtn');
  await page.waitForTimeout(400);
  const check = await page.evaluate(() => {
    const e = window.__dc.eng();
    const n = e.players.find(p => p.name === 'Puka Nacua');
    const q = e.players.find(p => p.name === 'Josh Allen');
    return { scoring: e.cfg.scoring, nacua: n.fmtProj, nacuaAdp: n.adpF, qb: q.fmtProj };
  });
  if (check.scoring !== 'std') errors.push('B: scoring not std: ' + check.scoring);
  if (Math.abs(check.nacua - 222.8) > 0.5) errors.push('B: Nacua std proj wrong: ' + check.nacua);
  if (Math.abs(check.nacuaAdp - 3.1) > 0.01) errors.push('B: Nacua std ADP wrong: ' + check.nacuaAdp);
  if (Math.abs(check.qb - 369.8) > 0.5) errors.push('B: QB proj should be format-invariant: ' + check.qb);
  // half-ppr via restart
  await page.click('#menuBtn'); await page.waitForTimeout(150);
  await page.click('#mSetup'); page.once('dialog', d => d.accept());
  await page.waitForTimeout(100);
  await page.evaluate(() => {}); // let confirm resolve
  await ctx.close();
}

// ============ C. Full 160-pick draft playthrough (PPR) ============
{
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage(); watch(page, 'C');
  await page.goto(file);
  await page.click('#startBtn');
  await page.waitForTimeout(250);
  let guard = 0;
  while (guard++ < 170) {
    const done = await page.evaluate(() => {
      const d = window.__dc; const e = d.eng();
      if (e.draftOver()) return true;
      const clock = e.onClock();
      if (clock === e.cfg.mySlot) {
        d.commit(e.recommendations(1).candidates[0].p.id, clock);
      } else {
        d.commit(e.available().sort((a, b) => a.adpF - b.adpF)[0].id, clock);
      }
      return d.eng().draftOver();
    });
    await page.waitForTimeout(35);
    if (done) break;
  }
  const s1 = await page.textContent('#statusLine1');
  if (!s1.includes('Draft complete')) errors.push('C: draft did not complete: ' + s1);
  const roster = await page.evaluate(() => {
    const e = window.__dc.eng();
    const mine = e.rosterOf(e.cfg.mySlot);
    const counts = {};
    mine.forEach(p => counts[p.pos] = (counts[p.pos] || 0) + 1);
    return { n: mine.length, counts, starters: e.lineup(mine).starters.length };
  });
  if (roster.n !== 16) errors.push('C: roster size ' + roster.n);
  if (roster.starters !== 9) errors.push('C: starters ' + roster.starters);
  if (roster.counts.K !== 1 || roster.counts.DST !== 1) errors.push('C: K/DST wrong: ' + JSON.stringify(roster.counts));
  await page.click('#nav button[data-pane="team"]');
  await page.waitForFunction(() => document.getElementById('oddsHero').textContent.includes('%'), null, { timeout: 20000 })
    .catch(() => errors.push('C: final odds never rendered'));
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shots/v2-03-final-team.png', fullPage: true });
  await page.click('#nav button[data-pane="board"]');
  await page.waitForTimeout(250);
  await page.screenshot({ path: 'shots/v2-04-final-board.png' });
  // export includes scoring + all picks
  const exp = await page.evaluate(() => JSON.parse(window.__dc.eng().exportState()));
  if (exp.picks.length !== 160 || !exp.cfg.scoring) errors.push('C: export bad: ' + exp.picks.length);
  await ctx.close();
}

// ============ D. Import restores a draft ============
{
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage(); watch(page, 'D');
  await page.goto(file);
  await page.click('#scoringSeg button:has-text("Half PPR")');
  await page.click('#startBtn');
  await page.waitForTimeout(250);
  // make 3 picks then export
  await page.evaluate(() => {
    const d = window.__dc;
    for (let i = 0; i < 3; i++) {
      const e = d.eng();
      d.commit(e.available().sort((a, b) => a.adpF - b.adpF)[0].id, e.onClock());
    }
  });
  const exported = await page.evaluate(() => window.__dc.eng().exportState());
  // fresh page, import (may auto-restore from shared context storage — that's intended behavior)
  const page2 = await ctx.newPage(); watch(page2, 'D2');
  await page2.goto(file);
  await page2.waitForTimeout(700);
  const inMain = await page2.evaluate(() => !document.getElementById('mainView').classList.contains('hidden'));
  if (!inMain) { await page2.click('#startBtn'); await page2.waitForTimeout(200); }
  await page2.click('#menuBtn'); await page2.waitForTimeout(150);
  await page2.click('#mImport'); await page2.waitForTimeout(150);
  await page2.fill('#ioArea', exported);
  await page2.click('#ioGo');
  await page2.waitForTimeout(400);
  const st = await page2.evaluate(() => {
    const e = window.__dc.eng();
    return { picks: e.state.picks.length, scoring: e.cfg.scoring };
  });
  if (st.picks !== 3 || st.scoring !== 'half') errors.push('D: import failed: ' + JSON.stringify(st));
  await ctx.close();
}

// ============ E. Desktop render ============
{
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 800 } });
  const page = await ctx.newPage(); watch(page, 'E');
  await page.goto(file);
  await page.click('#startBtn');
  await page.click('#nav button[data-pane="board"]');
  await page.waitForTimeout(250);
  await page.screenshot({ path: 'shots/v2-05-desktop.png' });
  await ctx.close();
}

await browser.close();
console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'CLEAN — all E2E checks passed (formats, full draft, import, star, analyst ranks)');
process.exit(errors.length ? 1 : 0);
