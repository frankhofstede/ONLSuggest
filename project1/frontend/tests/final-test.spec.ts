import { test } from '@playwright/test';

test('Final admin test with fresh deployment', async ({ page }) => {
  const consoleMessages: string[] = [];
  const errors: string[] = [];

  page.on('console', msg => consoleMessages.push(`${msg.type()}: ${msg.text()}`));
  page.on('pageerror', error => errors.push(`PAGE ERROR: ${error.message}`));
  page.on('requestfailed', request => errors.push(`FAILED: ${request.url()}`));

  console.log('Loading fresh deployment admin page...');
  await page.goto('https://frontend-7lprr7be6-frankhofstedes-projects.vercel.app/admin');

  await page.waitForTimeout(5000);

  const content = await page.locator('body').textContent();
  console.log('\n=== PAGE CONTENT ===');
  console.log(content);

  console.log('\n=== CONSOLE MESSAGES ===');
  consoleMessages.forEach(msg => console.log(msg));

  console.log('\n=== ERRORS ===');
  errors.forEach(err => console.log(err));

  await page.screenshot({ path: 'test-results/final-admin.png', fullPage: true });

  if (content?.includes('Total Gemeentes') || content?.includes('Total Services')) {
    console.log('\n✅✅✅ SUCCESS! Admin dashboard is working!');
  } else if (content?.includes('Error')) {
    console.log('\n❌ Still showing error');
  } else {
    console.log('\n⏳ Unknown state');
  }
});
