import { test } from '@playwright/test';

test('Test admin dashboard SUCCESS', async ({ page }) => {
  const consoleMessages: string[] = [];

  page.on('console', msg => consoleMessages.push(`${msg.type()}: ${msg.text()}`));

  console.log('Loading admin page...');
  await page.goto('https://frontend-8m7et354o-frankhofstedes-projects.vercel.app/admin');

  await page.waitForTimeout(5000);

  const content = await page.locator('body').textContent();
  console.log('\n=== PAGE CONTENT ===');
  console.log(content);

  console.log('\n=== CONSOLE (last 10) ===');
  consoleMessages.slice(-10).forEach(msg => console.log(msg));

  await page.screenshot({ path: 'test-results/success-admin.png', fullPage: true });

  if (content?.includes('Total Gemeentes') || content?.includes('Total Services') || content?.includes('0')) {
    console.log('\n✅✅✅ SUCCESS! Admin dashboard is displaying data!');
  } else if (content?.includes('Error')) {
    console.log('\n❌ Error still showing');
  } else if (content?.includes('Loading')) {
    console.log('\n⏳ Still loading');
  }
});
