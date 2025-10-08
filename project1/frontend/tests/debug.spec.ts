import { test } from '@playwright/test';

test('Debug console errors', async ({ page }) => {
  const errors: string[] = [];
  const logs: string[] = [];

  page.on('console', msg => {
    const text = msg.text();
    logs.push(`[${msg.type()}] ${text}`);
    if (msg.type() === 'error') {
      errors.push(text);
    }
  });

  page.on('pageerror', error => {
    errors.push(`PAGE ERROR: ${error.message}\n${error.stack}`);
  });

  console.log('Loading page...');
  await page.goto('https://frontend-rust-iota-49.vercel.app', { waitUntil: 'networkidle' });

  console.log('\n=== CONSOLE LOGS ===');
  logs.forEach(log => console.log(log));

  console.log('\n=== ERRORS ===');
  if (errors.length > 0) {
    errors.forEach(err => console.log('ERROR:', err));
  } else {
    console.log('No errors found');
  }

  console.log('\n=== PAGE STATE ===');
  const html = await page.content();
  console.log('Page HTML length:', html.length);
  console.log('Root div exists:', html.includes('id="root"'));

  const rootContent = await page.locator('#root').innerHTML().catch(() => 'ERROR getting root content');
  console.log('Root content length:', rootContent.length);
  console.log('Root content:', rootContent.substring(0, 200));

  await page.screenshot({ path: 'test-results/debug-screenshot.png', fullPage: true });
  console.log('\n✓ Screenshot saved to test-results/debug-screenshot.png');
});
