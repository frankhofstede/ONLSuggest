import { test } from '@playwright/test';

test('Test latest deployment directly', async ({ context }) => {
  // Create new page with cleared cache
  const page = await context.newPage();

  // Capture console and errors
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

  console.log('Loading latest deployment admin page...');
  await page.goto('https://frontend-181aetmx5-frankhofstedes-projects.vercel.app/admin', {
    waitUntil: 'networkidle'
  });

  // Wait for data to load
  await page.waitForTimeout(5000);

  // Take screenshot
  await page.screenshot({ path: 'test-results/latest-admin.png', fullPage: true });

  // Get page content
  const bodyText = await page.locator('body').textContent();
  console.log('\n=== PAGE CONTENT ===');
  console.log(bodyText);

  console.log('\n=== CONSOLE MESSAGES ===');
  consoleMessages.forEach(msg => console.log(msg));

  console.log('\n=== ERRORS ===');
  errors.forEach(err => console.log(err));

  // Check for stats
  if (bodyText?.includes('Total Gemeentes') || bodyText?.includes('Total Services')) {
    console.log('\n✅ SUCCESS: Stats are loading!');
  } else if (bodyText?.includes('Error')) {
    console.log('\n❌ FAILED: Error message present');
  } else if (bodyText?.includes('Loading')) {
    console.log('\n⏳ LOADING: Page is still loading data');
  }
});
