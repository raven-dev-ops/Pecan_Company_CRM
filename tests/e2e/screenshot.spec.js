const fs = require('fs');
const path = require('path');
const { test, expect } = require('@playwright/test');

test('capture responsive preview screenshots', async ({ page }, testInfo) => {
  await page.goto('/index.html');
  await expect(page.locator('h1')).toContainText('Sales Operations Snapshot');

  const shotsDir = path.resolve('docs', 'screenshots');
  fs.mkdirSync(shotsDir, { recursive: true });

  const outName = `web-preview-${testInfo.project.name}.png`;
  const outPath = path.join(shotsDir, outName);
  await page.screenshot({ path: outPath, fullPage: true });
});