// Reproducible checks for the static simulation only; no production acceptance.
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const assert = require('node:assert/strict');
const modulePath = process.env.PLAYWRIGHT_MODULE;
if (!modulePath) throw new Error('Set PLAYWRIGHT_MODULE to an existing Playwright package. No installation is performed.');
const { chromium } = require(modulePath);
const base = __dirname;
const captures = path.join(base, 'screenshots');
fs.mkdirSync(captures, { recursive: true });
(async () => {
  const browser = await chromium.launch({ headless: true, ...(process.env.CHROMIUM_EXECUTABLE ? { executablePath: process.env.CHROMIUM_EXECUTABLE } : {}) });
  const evidence = { scope: 'Static browser simulation only; no inference or API', viewports: ['1440x1000', '390x844'], results: [] };
  try {
    for (const direction of ['desk', 'casebook']) {
      const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(pathToFileURL(path.join(base, direction + '.html')).href);
      await page.screenshot({ path: path.join(captures, direction + '-desktop.png'), fullPage: true });
      const runs = () => page.locator('[data-run]').count();
      assert.equal(await runs(), 1);
      if(direction==='casebook')assert.equal(await page.locator('.workspace > :first-child').getAttribute('class'), 'decision-column', 'visual and DOM order agree');
      await page.selectOption('#outcome-filter', 'needs_review');
      await page.locator('#outcome-filter').focus();
      await page.selectOption('#outcome-filter', 'all');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'outcome-filter', 'focus preserved after filter update');
      await page.selectOption('#model', 'qwen35-4b');
      assert.equal(await runs(), 1, 'controls must not submit');
      await page.click('#edit-text');
      await page.fill('#transcript-input', 'Caller: Please call me back tomorrow.\nRepresentative: I have your message.');
      await page.screenshot({ path: path.join(captures, direction + '-editing.png'), fullPage: true });
      await page.click('#save-text');
      assert.equal(await runs(), 1, 'saving must not submit');
      assert.match(await page.locator('.transcript-meta').innerText(), /v1/, 'old result keeps old text');
      await page.click('#classify');
      await page.waitForFunction(() => document.querySelectorAll('[data-run]').length === 2);
      assert.equal(await page.locator('mark').count(), 1, 'edited output highlights its exact body quote');
      await page.click('[data-run="SIM-101"]');
      assert.match(await page.locator('.conversation').innerText(), /Please still call me tomorrow/);
      assert.equal(await page.locator('mark').count(), 1);
      await page.selectOption('#review-choice', 'no_callback');
      await page.fill('#review-note', 'Separate simulated disagreement.');
      await page.locator('#review-form button').click();
      assert.match(await page.locator('.result').innerText(), /Callback required/);
      await page.reload();
      assert.equal(await runs(), 2, 'history survives reload');
      await page.locator('.provenance summary').click();
      await page.screenshot({ path: path.join(captures, direction + '-provenance.png'), fullPage: true });
      await page.click('#reset');
      for (const scenario of ['loading', 'timeout', 'malformed']) {
        await page.selectOption('#scenario', scenario);
        await page.click('#classify');
        if (scenario === 'loading') {
          assert.equal(await page.locator('#classify').isDisabled(), true);
          await page.click('[data-run="SIM-101"]');
          assert.match(await page.locator('.result').innerText(), /Callback required/, 'history visible while loading');
          await page.screenshot({ path: path.join(captures, direction + '-loading.png'), fullPage: true });
          await page.click('#end-loading');
        } else {
          await page.waitForFunction(() => !document.querySelector('#classify').disabled);
          assert.equal(await page.locator('.result .outcome').count(), 0);
          await page.screenshot({ path: path.join(captures, direction + '-' + scenario + '.png'), fullPage: true });
        }
      }
      await page.selectOption('#scenario', 'unavailable');
      assert.equal(await page.locator('#classify').isDisabled(), true);
      await page.click('[data-run="SIM-101"]');
      assert.match(await page.locator('.result').innerText(), /Callback required/, 'history visible while unavailable');
      await page.screenshot({ path: path.join(captures, direction + '-unavailable.png'), fullPage: true });
      await page.click('#reset');
      await page.click('#new-case');
      await page.click('#cancel-edit');
      await page.screenshot({ path: path.join(captures, direction + '-empty.png'), fullPage: true });
      await page.click('#empty-load');
      await page.selectOption('#outcome-filter', 'needs_review');
      await page.selectOption('#status-filter', 'reviewed');
      assert.equal(await page.locator('[data-case]').count(), 0);
      await page.click('#reset');
      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({ path: path.join(captures, direction + '-narrow.png'), fullPage: true });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'no document overflow at 390px');
      await page.click('#new-case');
      await page.fill('#transcript-input', 'Caller: ' + 'long-unbroken-text'.repeat(600));
      await page.click('#save-text');
      await page.click('#classify');
      await page.waitForFunction(() => document.querySelectorAll('[data-run]').length === 1);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'long text must wrap');
      assert.deepEqual(errors, []);
      evidence.results.push({ direction, passed: true, checks: ['explicit submit only', 'new transcript version', 'original text/highlight retained', 'separate review', 'reload history', 'loading', 'timeout', 'malformed', 'unavailable', 'empty', 'no filter results', '390px overflow', 'long text', 'edited quote highlight', 'history visible while busy/unavailable', 'focus preserved', 'casebook DOM order', 'no JS exceptions'] });
      await context.close();
    }
    fs.writeFileSync(path.join(base, 'verification.json'), JSON.stringify(evidence, null, 2) + '\n');
    console.log(JSON.stringify(evidence));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
