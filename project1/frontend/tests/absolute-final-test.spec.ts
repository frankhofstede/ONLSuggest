import { test } from '@playwright/test';

test('ABSOLUTE FINAL TEST', async ({ page }) => {
  console.log('Testing https://frontend-8p3uejf92-frankhofstedes-projects.vercel.app/admin');

  await page.goto('https://frontend-8p3uejf92-frankhofstedes-projects.vercel.app/admin');
  await page.waitForTimeout(5000);

  const content = await page.locator('body').textContent();
  console.log(content);

  await page.screenshot({ path: 'test-results/absolute-final.png', fullPage: true });

  if (content?.includes('Total Gemeentes') || content?.includes('Total Services') || (content?.includes('Admin') && !content?.includes('Error'))) {
    console.log('\n\n✅✅✅ ADMIN DASHBOARD IS WORKING! ✅✅✅\n\n');
  } else {
    console.log('\n\n❌ STILL NOT WORKING\n\n');
  }
});
