const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1400, height: 860 }, deviceScaleFactor: 1 });
  const errs = [];
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', e => errs.push(String(e)));
  await page.goto('file://' + process.argv[2]);
  await page.waitForTimeout(2500);
  for (const [name, preset, viewBtn] of JSON.parse(process.argv[3])) {
    if (preset) await page.click(`button[data-p="${preset}"]`);
    if (viewBtn) await page.click('#v-' + viewBtn);
    await page.waitForTimeout(600);
    await page.screenshot({ path: name });
  }
  console.log('errors:', JSON.stringify(errs));
  await browser.close();
})();
