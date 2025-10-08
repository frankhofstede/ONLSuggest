import { test, expect } from '@playwright/test';

test('Admin cog icon appears and links to admin page', async ({ page }) => {
  // Go to homepage
  await page.goto('http://localhost:3000');

  // Wait for app to load
  await page.waitForSelector('.app');

  // Take screenshot
  await page.screenshot({ path: 'test-results/homepage.png' });

  // Check if cog icon exists
  const cogLink = page.locator('a[href="/admin"]');
  const isVisible = await cogLink.isVisible();

  console.log(`Cog icon visible: ${isVisible}`);

  if (!isVisible) {
    throw new Error('Cog icon not visible on homepage');
  }

  // Click the cog icon
  await cogLink.click();

  // Wait for navigation to admin page
  await page.waitForURL('**/admin');

  console.log('✅ Successfully navigated to admin page');

  // Take screenshot of admin page
  await page.screenshot({ path: 'test-results/admin-page.png' });

  // Check if admin dashboard loads
  const hasAdmin = await page.content();
  console.log('Admin page loaded, checking content...');

  if (!hasAdmin.includes('Admin')) {
    throw new Error('Admin page does not contain expected content');
  }

  console.log('✅ Admin page loaded successfully');
});
