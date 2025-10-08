import { test, expect } from '@playwright/test';

const PRODUCTION_URL = 'https://frontend-rust-iota-49.vercel.app';

test.describe('ONLSuggest Application', () => {
  test('should load the homepage successfully', async ({ page }) => {
    await page.goto(PRODUCTION_URL);

    // Check page title
    await expect(page).toHaveTitle(/ONLSuggest/);

    // Check main heading
    await expect(page.locator('h1')).toContainText('ONLSuggest');

    // Check subtitle
    await expect(page.locator('.app__subtitle')).toContainText('Vind snel de gemeentelijke dienst die u zoekt');
  });

  test('should display search interface with examples', async ({ page }) => {
    await page.goto(PRODUCTION_URL);

    // Check for search input placeholder or description
    const description = page.locator('text=Voer een zoekterm in om relevante gemeentelijke diensten te vinden');
    await expect(description).toBeVisible();

    // Check examples are shown
    await expect(page.locator('text=Voorbeelden')).toBeVisible();
    await expect(page.locator('text=parkeervergunning')).toBeVisible();
    await expect(page.locator('text=paspoort aanvragen')).toBeVisible();
    await expect(page.locator('text=verhuizen doorgeven')).toBeVisible();
    await expect(page.locator('text=trouwen')).toBeVisible();
  });

  test('should have a working search input field', async ({ page }) => {
    await page.goto(PRODUCTION_URL);

    // Find and interact with search input
    const searchInput = page.locator('input[type="text"].search-box__input');
    await expect(searchInput).toBeVisible();

    // Type in search field
    await searchInput.fill('parkeervergunning');
    await expect(searchInput).toHaveValue('parkeervergunning');

    // Check submit button
    const submitButton = page.locator('button[type="submit"]');
    await expect(submitButton).toBeEnabled();
  });

  test('should be responsive and mobile-friendly', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(PRODUCTION_URL);

    await expect(page.locator('h1')).toBeVisible();

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(PRODUCTION_URL);

    await expect(page.locator('h1')).toBeVisible();
  });

  test('should have proper Dutch language content', async ({ page }) => {
    await page.goto(PRODUCTION_URL);

    // Check for Dutch content
    const htmlLang = await page.locator('html').getAttribute('lang');
    expect(htmlLang).toBe('nl');
  });
});
