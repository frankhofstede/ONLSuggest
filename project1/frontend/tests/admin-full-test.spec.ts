import { test, expect } from '@playwright/test';

const ADMIN_URL = 'https://frontend-rust-iota-49.vercel.app/admin';

test.describe('Admin Dashboard Full Functionality Test', () => {

  test('Dashboard loads and shows statistics', async ({ page }) => {
    await page.goto(ADMIN_URL);
    await page.waitForTimeout(3000);

    // Check for stats
    const content = await page.textContent('body');
    console.log('Page content:', content);

    // Verify stats are displayed
    expect(content).toContain('Gemeentes');
    expect(content).toContain('Services');
    expect(content).toContain('Koppelingen');
  });

  test('Navigate to Gemeentes management', async ({ page }) => {
    await page.goto(ADMIN_URL);
    await page.waitForTimeout(2000);

    // Click on Gemeentes navigation card (in Beheer section)
    await page.click('.nav-card:has-text("Gemeentes")');
    await page.waitForTimeout(2000);

    const url = page.url();
    console.log('Current URL after click:', url);
    expect(url).toContain('/admin/gemeentes');

    await page.screenshot({ path: 'test-results/gemeentes-page.png', fullPage: true });
  });

  test('Navigate to Services management', async ({ page }) => {
    await page.goto(ADMIN_URL);
    await page.waitForTimeout(2000);

    // Click on Services navigation card (in Beheer section)
    await page.click('.nav-card:has-text("Services")');
    await page.waitForTimeout(2000);

    const url = page.url();
    console.log('Current URL after click:', url);
    expect(url).toContain('/admin/services');

    await page.screenshot({ path: 'test-results/services-page.png', fullPage: true });
  });

  test('Navigate to Associations management', async ({ page }) => {
    await page.goto(ADMIN_URL);
    await page.waitForTimeout(2000);

    // Click on Koppelingen navigation card (in Beheer section)
    await page.click('.nav-card:has-text("Koppelingen")');
    await page.waitForTimeout(2000);

    const url = page.url();
    console.log('Current URL after click:', url);
    expect(url).toContain('/admin/associations');

    await page.screenshot({ path: 'test-results/associations-page.png', fullPage: true });
  });

  test('Back to frontend link works', async ({ page }) => {
    await page.goto(ADMIN_URL);
    await page.waitForTimeout(2000);

    // Click back to frontend
    await page.click('text=Terug naar frontend');
    await page.waitForTimeout(2000);

    const url = page.url();
    console.log('Current URL after clicking back:', url);
    expect(url).not.toContain('/admin');

    await page.screenshot({ path: 'test-results/back-to-frontend.png', fullPage: true });
  });

  test('Admin cog icon navigation', async ({ page }) => {
    await page.goto('https://frontend-rust-iota-49.vercel.app/');
    await page.waitForTimeout(2000);

    // Look for cog icon
    const cogIcon = await page.locator('[class*="cog"], [class*="settings"], svg').first();
    if (await cogIcon.isVisible()) {
      await cogIcon.click();
      await page.waitForTimeout(2000);

      const url = page.url();
      console.log('URL after clicking cog:', url);
      expect(url).toContain('/admin');
    } else {
      console.log('Cog icon not found on main page');
    }

    await page.screenshot({ path: 'test-results/cog-navigation.png', fullPage: true });
  });
});
