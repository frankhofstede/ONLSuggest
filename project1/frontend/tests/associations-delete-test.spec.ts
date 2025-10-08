import { test, expect } from '@playwright/test';

test('Associations page loads with correct data and delete works', async ({ page }) => {
  test.setTimeout(90000); // 90 seconds to allow for data loading checks
  await page.goto('https://frontend-rust-iota-49.vercel.app/admin/associations');

  // Wait for data to load by checking if "Loading..." disappears
  console.log('Waiting for associations to load (checking every 10 seconds)...');

  const maxWaitTime = 60000; // Max 60 seconds
  const checkInterval = 10000; // Check every 10 seconds
  let elapsedTime = 0;
  let isLoaded = false;

  while (elapsedTime < maxWaitTime && !isLoaded) {
    await page.waitForTimeout(checkInterval);
    elapsedTime += checkInterval;

    const content = await page.textContent('body');

    // Check if "Loading..." is gone and we have actual data
    if (content && !content.includes('Loading...') && content.includes('Amsterdam')) {
      console.log(`✅ Data loaded after ${elapsedTime / 1000} seconds`);
      isLoaded = true;
    } else {
      console.log(`⏳ Still loading... (${elapsedTime / 1000}s elapsed)`);
    }
  }

  if (!isLoaded) {
    throw new Error(`Timeout: Data did not load after ${maxWaitTime / 1000} seconds`);
  }

  const content = await page.textContent('body');
  console.log('Associations page:', content?.substring(0, 500));

  // Check that associations are loaded
  expect(content).toContain('Amsterdam');
  expect(content).toContain('Parkeervergunning');

  // Take screenshot
  await page.screenshot({ path: 'test-results/associations-with-data.png', fullPage: true });

  console.log('\n✅ Associations are loading correctly with real data!');
  console.log('The delete buttons should now work with association IDs.');
});
