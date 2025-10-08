import { test, expect } from '@playwright/test';

test('Admin cog icon appears and links to admin page', async ({ page }) => {
  // Go to homepage
  await page.goto('http://localhost:3000');

  // Wait for app to load
  await page.waitForSelector('.app');

  // Check if cog icon exists
  const cogLink = page.locator('a[href="/admin"]');
  await expect(cogLink).toBeVisible();

  console.log('✅ Cog icon is visible');

  // Click the cog icon
  await cogLink.click();

  // Wait for navigation to admin page
  await page.waitForURL('**/admin');

  console.log('✅ Successfully navigated to admin page');

  // Check if admin dashboard loads
  const adminTitle = page.locator('h1');
  await expect(adminTitle).toContainText('Admin');

  console.log('✅ Admin page loaded successfully');
});
