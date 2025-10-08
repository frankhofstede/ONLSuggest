import { test } from '@playwright/test';

test('Check admin page error', async ({ page }) => {
  // Capture console messages and errors
  const consoleMessages: string[] = [];
  const errors: string[] = [];

  page.on('console', msg => {
    consoleMessages.push(`${msg.type()}: ${msg.text()}`);
  });

  page.on('pageerror', error => {
    errors.push(`PAGE ERROR: ${error.message}`);
  });

  page.on('requestfailed', request => {
    errors.push(`REQUEST FAILED: ${request.url()} - ${request.failure()?.errorText}`);
  });

  console.log('Loading admin page...');
  await page.goto('https://frontend-rust-iota-49.vercel.app/admin');

  // Wait a bit for the page to load and try to fetch data
  await page.waitForTimeout(5000);

  // Take screenshot
  await page.screenshot({ path: 'test-results/admin-error-check.png', fullPage: true });

  // Get the page content
  const bodyText = await page.locator('body').textContent();
  console.log('\n=== PAGE CONTENT ===');
  console.log(bodyText);

  console.log('\n=== CONSOLE MESSAGES ===');
  consoleMessages.forEach(msg => console.log(msg));

  console.log('\n=== ERRORS ===');
  errors.forEach(err => console.log(err));

  // Check for specific error message
  const errorElement = page.locator('.error, [class*="error"]');
  const errorCount = await errorElement.count();
  if (errorCount > 0) {
    console.log('\n=== ERROR ELEMENTS FOUND ===');
    for (let i = 0; i < errorCount; i++) {
      const text = await errorElement.nth(i).textContent();
      console.log(`Error ${i + 1}: ${text}`);
    }
  }
});
