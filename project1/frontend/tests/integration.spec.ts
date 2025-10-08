import { test, expect } from '@playwright/test';

const PRODUCTION_URL = 'https://frontend-rust-iota-49.vercel.app';

test.describe('Full Stack Integration', () => {
  test('should search for parkeer and get results from backend', async ({ page }) => {
    await page.goto(PRODUCTION_URL);

    // Enter search query
    const searchInput = page.locator('input[type="text"].search-box__input');
    await searchInput.fill('parkeer');

    // Submit search
    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    // Wait for results (not error message)
    await page.waitForSelector('.suggestion-card', { timeout: 10000 });

    // Check that we got suggestions
    const suggestions = page.locator('.suggestion-card');
    const count = await suggestions.count();
    expect(count).toBeGreaterThan(0);

    // Check first suggestion contains expected text
    const firstSuggestion = suggestions.first();
    await expect(firstSuggestion).toContainText('parkeer');
  });

  test('should search for paspoort and get results', async ({ page }) => {
    await page.goto(PRODUCTION_URL);

    const searchInput = page.locator('input[type="text"].search-box__input');
    await searchInput.fill('paspoort');

    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    await page.waitForSelector('.suggestion-card', { timeout: 10000 });

    const suggestions = page.locator('.suggestion-card');
    const count = await suggestions.count();
    expect(count).toBeGreaterThan(0);

    const firstSuggestion = suggestions.first();
    await expect(firstSuggestion).toContainText('paspoort');
  });

  test('should handle unknown queries gracefully', async ({ page }) => {
    await page.goto(PRODUCTION_URL);

    const searchInput = page.locator('input[type="text"].search-box__input');
    await searchInput.fill('xyzabc123unknown');

    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    // Should either show generic suggestions or proper message
    await page.waitForTimeout(3000);

    // Check that we don't have an error
    const errorMessage = page.locator('text=Er is iets misgegaan');
    await expect(errorMessage).not.toBeVisible();
  });
});
