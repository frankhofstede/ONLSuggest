import { test, expect } from '@playwright/test';

test('Quick full stack test', async ({ page }) => {
  console.log('Going to frontend...');
  await page.goto('https://frontend-rust-iota-49.vercel.app');

  console.log('Waiting for page load...');
  await page.waitForLoadState('networkidle');

  console.log('Looking for search input...');
  const searchInput = page.locator('input[type="text"].search-box__input');
  await searchInput.waitFor({ state: 'visible', timeout: 10000 });

  console.log('Typing parkeer...');
  await searchInput.fill('parkeer');

  console.log('Clicking submit...');
  const submitButton = page.locator('button[type="submit"]');
  await submitButton.click();

  console.log('Waiting 10 seconds for response...');
  await page.waitForTimeout(10000);

  console.log('Taking screenshot...');
  await page.screenshot({ path: 'test-results/manual-test.png' });

  // Check what's on the page
  const html = await page.content();
  console.log('Page contains:', html.substring(0, 500));
});
