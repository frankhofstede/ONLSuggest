import { test } from '@playwright/test';

test('Test search with parkeer', async ({ page }) => {
  const errors: string[] = [];
  const networkRequests: any[] = [];

  page.on('console', msg => {
    console.log(`[${msg.type()}] ${msg.text()}`);
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  page.on('pageerror', error => {
    console.log('PAGE ERROR:', error.message);
    errors.push(error.message);
  });

  page.on('request', request => {
    if (request.url().includes('suggestions')) {
      networkRequests.push({
        url: request.url(),
        method: request.method(),
        postData: request.postData()
      });
      console.log('REQUEST:', request.method(), request.url());
    }
  });

  page.on('response', async response => {
    if (response.url().includes('suggestions')) {
      console.log('RESPONSE:', response.status(), response.url());
      try {
        const body = await response.text();
        console.log('RESPONSE BODY:', body.substring(0, 500));
      } catch (e) {
        console.log('Could not read response body');
      }
    }
  });

  console.log('1. Loading page...');
  await page.goto('https://frontend-rust-iota-49.vercel.app');
  await page.waitForLoadState('networkidle');

  console.log('2. Taking initial screenshot...');
  await page.screenshot({ path: 'test-results/before-search.png' });

  console.log('3. Entering search query...');
  const input = page.locator('input[type="text"]');
  await input.fill('parkeer');

  console.log('4. Clicking search button...');
  const button = page.locator('button[type="submit"]');
  await button.click();

  console.log('5. Waiting for response...');
  await page.waitForTimeout(5000);

  console.log('6. Taking after-search screenshot...');
  await page.screenshot({ path: 'test-results/after-search.png', fullPage: true });

  console.log('7. Checking page state...');
  const rootContent = await page.locator('#root').innerHTML();
  console.log('Root content length:', rootContent.length);
  console.log('Root content preview:', rootContent.substring(0, 300));

  console.log('\n=== NETWORK REQUESTS ===');
  console.log('Total requests to suggestions:', networkRequests.length);
  networkRequests.forEach(req => {
    console.log('- URL:', req.url);
    console.log('  Method:', req.method);
    console.log('  Body:', req.postData);
  });

  console.log('\n=== ERRORS ===');
  if (errors.length > 0) {
    errors.forEach(err => console.log('ERROR:', err));
  } else {
    console.log('No errors');
  }
});
