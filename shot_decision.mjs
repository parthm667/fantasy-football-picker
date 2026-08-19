import { createRequire } from 'module';
import path from 'path';
const require = createRequire('/usr/lib/node_modules/');
const { chromium } = require('playwright');

const b = await chromium.launch();
const p = await (await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })).newPage();
await p.goto('file://' + path.resolve('draft-command-2026.html'));
await p.click('#scoringSeg button:has-text("Half PPR")');
await p.click('#teamsSeg button:has-text("8")');
await p.waitForTimeout(150);
await p.click('#slotGrid button:has-text("5")');
await p.click('#startBtn');
await p.waitForTimeout(250);
async function log(q) {
  await p.fill('#searchInput', q); await p.waitForTimeout(220);
  await p.click('#searchResults .prow'); await p.waitForTimeout(120);
  await p.click('#confirmYes'); await p.waitForTimeout(180);
}
await log('gibbs'); await log('bijan'); await log('nacua'); await log("ja'marr");
await p.waitForFunction(() => {
  const v = document.getElementById('simVerdict');
  return v && v.textContent.includes('%');
}, null, { timeout: 25000 });
await p.waitForTimeout(800);
const el = await p.locator('.decision');
await el.screenshot({ path: 'shots/decision.png' });
await b.close();
console.log('screenshot saved');
