import { test, expect } from '@playwright/test';

test('Verify cog icon exists on production site', async ({ page }) => {
  console.log('Loading production site...');
  await page.goto('https://frontend-rust-iota-49.vercel.app/');

  console.log('Waiting for app to load...');
  await page.waitForSelector('.app', { timeout: 10000 });

  console.log('Taking screenshot of homepage...');
  await page.screenshot({ path: 'test-results/production-homepage.png', fullPage: true });

  console.log('Looking for admin link...');
  const adminLink = page.locator('a[href="/admin"]');

  const count = await adminLink.count();
  console.log(`Found ${count} admin link(s)`);

  if (count > 0) {
    const isVisible = await adminLink.isVisible();
    console.log(`Admin link visible: ${isVisible}`);

    if (isVisible) {
      console.log('✅ Cog icon is present and visible!');

      // Click it to verify navigation works
      console.log('Clicking admin link...');
      await adminLink.click();

      await page.waitForURL('**/admin', { timeout: 5000 });
      console.log('✅ Successfully navigated to admin page!');

      await page.screenshot({ path: 'test-results/production-admin.png', fullPage: true });
    } else {
      throw new Error('Admin link exists but is not visible');
    }
  } else {
    // Get page content to debug
    const html = await page.content();
    console.log('Page HTML length:', html.length);
    console.log('Contains "admin":', html.includes('admin'));
    throw new Error('No admin link found on page');
  }
});
