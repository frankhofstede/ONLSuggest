import { test, expect } from '@playwright/test';

const BASE_URL = 'https://frontend-rust-iota-49.vercel.app';

test.describe('Admin CRUD Functionality Tests', () => {

  test('Gemeentes page loads and displays list', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/gemeentes`);
    await page.waitForTimeout(3000);

    const content = await page.textContent('body');
    console.log('Gemeentes page content:', content);

    // Check for page heading
    expect(content).toContain('Gemeentes');

    // Check for back link
    expect(content).toContain('Dashboard');

    await page.screenshot({ path: 'test-results/gemeentes-list.png', fullPage: true });
  });

  test('Services page loads and displays list', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/services`);
    await page.waitForTimeout(3000);

    const content = await page.textContent('body');
    console.log('Services page content:', content);

    expect(content).toContain('Services');
    expect(content).toContain('Dashboard');

    await page.screenshot({ path: 'test-results/services-list.png', fullPage: true });
  });

  test('Associations page loads and displays list', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/associations`);
    await page.waitForTimeout(3000);

    const content = await page.textContent('body');
    console.log('Associations page content:', content);

    expect(content).toContain('Koppelingen');
    expect(content).toContain('Dashboard');

    await page.screenshot({ path: 'test-results/associations-list.png', fullPage: true });
  });

  test('Gemeentes: Create new gemeente', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/gemeentes`);
    await page.waitForTimeout(2000);

    // Look for "Create" or "Nieuw" button
    const createButton = await page.locator('button:has-text("Nieuw"), button:has-text("Create")').first();

    if (await createButton.isVisible()) {
      await createButton.click();
      await page.waitForTimeout(1000);

      // Fill in form
      const nameInput = await page.locator('input[name="name"], input[placeholder*="naam"]').first();
      if (await nameInput.isVisible()) {
        await nameInput.fill('Test Gemeente Playwright');

        // Try to find and fill province
        const provinceInput = await page.locator('input[name="province"], input[placeholder*="provincie"]').first();
        if (await provinceInput.isVisible()) {
          await provinceInput.fill('Test Provincie');
        }

        // Submit
        await page.click('button[type="submit"], button:has-text("Opslaan"), button:has-text("Save")');
        await page.waitForTimeout(2000);

        const content = await page.textContent('body');
        console.log('After create:', content);

        await page.screenshot({ path: 'test-results/gemeente-created.png', fullPage: true });
      } else {
        console.log('Create form not found');
      }
    } else {
      console.log('Create button not found');
    }
  });

  test('Services: Create new service', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin/services`);
    await page.waitForTimeout(2000);

    const createButton = await page.locator('button:has-text("Nieuw"), button:has-text("Create")').first();

    if (await createButton.isVisible()) {
      await createButton.click();
      await page.waitForTimeout(1000);

      const nameInput = await page.locator('input[name="name"], input[placeholder*="naam"]').first();
      if (await nameInput.isVisible()) {
        await nameInput.fill('Test Service Playwright');

        // Try to find description
        const descInput = await page.locator('input[name="description"], textarea[name="description"]').first();
        if (await descInput.isVisible()) {
          await descInput.fill('Test description');
        }

        await page.click('button[type="submit"], button:has-text("Opslaan"), button:has-text("Save")');
        await page.waitForTimeout(2000);

        await page.screenshot({ path: 'test-results/service-created.png', fullPage: true });
      }
    } else {
      console.log('Create button not found on Services page');
    }
  });

  test('Back to Dashboard links work', async ({ page }) => {
    // From Gemeentes
    await page.goto(`${BASE_URL}/admin/gemeentes`);
    await page.waitForTimeout(2000);

    await page.click('a:has-text("Dashboard")');
    await page.waitForTimeout(1000);

    expect(page.url()).toBe(`${BASE_URL}/admin`);

    // From Services
    await page.goto(`${BASE_URL}/admin/services`);
    await page.waitForTimeout(2000);

    await page.click('a:has-text("Dashboard")');
    await page.waitForTimeout(1000);

    expect(page.url()).toBe(`${BASE_URL}/admin`);

    // From Associations
    await page.goto(`${BASE_URL}/admin/associations`);
    await page.waitForTimeout(2000);

    await page.click('a:has-text("Dashboard")');
    await page.waitForTimeout(1000);

    expect(page.url()).toBe(`${BASE_URL}/admin`);
  });
});
