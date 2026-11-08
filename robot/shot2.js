const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1500, height: 900 }, deviceScaleFactor: 2 });
  await page.goto('file://' + process.argv[2]);
  await page.waitForTimeout(2500);
  await page.click('button[data-p="25,25,45"]');
  await page.click('#v-iso');
  await page.waitForTimeout(800);
  await page.locator('#view').screenshot({ path: process.argv[3] });
  await page.click('#v-close');
  await page.waitForTimeout(800);
  await page.locator('#view').screenshot({ path: process.argv[4] });
  await browser.close();
})();
