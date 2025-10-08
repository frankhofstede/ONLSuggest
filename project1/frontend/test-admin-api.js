/**
 * Test script to verify admin API endpoints work correctly
 */

const API_URL = 'https://project1-drv91r5fa-frankhofstedes-projects.vercel.app';
const USERNAME = 'admin';
const PASSWORD = 'admin123';

const auth = Buffer.from(`${USERNAME}:${PASSWORD}`).toString('base64');

async function testEndpoint(path, method = 'GET', body = null) {
  console.log(`\nTesting ${method} ${path}...`);

  const options = {
    method,
    headers: {
      'Authorization': `Basic ${auth}`,
      'Content-Type': 'application/json'
    }
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_URL}${path}`, options);
    console.log(`Status: ${response.status} ${response.statusText}`);

    const text = await response.text();

    // Check if it's HTML (Vercel auth page)
    if (text.includes('<!doctype html>') || text.includes('Authentication Required')) {
      console.log('❌ Got Vercel authentication page');
      return false;
    }

    // Try to parse as JSON
    try {
      const data = JSON.parse(text);
      console.log('✅ Response:', JSON.stringify(data, null, 2));
      return true;
    } catch (e) {
      console.log('Response text:', text.substring(0, 200));
      return false;
    }
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
    return false;
  }
}

async function runTests() {
  console.log('=== Admin API Test Suite ===');
  console.log(`API URL: ${API_URL}`);

  let passed = 0;
  let failed = 0;

  // Test 1: Get stats
  if (await testEndpoint('/api/admin/stats')) {
    passed++;
  } else {
    failed++;
  }

  // Test 2: Get gemeentes
  if (await testEndpoint('/api/admin/gemeentes')) {
    passed++;
  } else {
    failed++;
  }

  // Test 3: Get services
  if (await testEndpoint('/api/admin/services')) {
    passed++;
  } else {
    failed++;
  }

  console.log(`\n=== Results ===`);
  console.log(`✅ Passed: ${passed}`);
  console.log(`❌ Failed: ${failed}`);

  process.exit(failed > 0 ? 1 : 0);
}

runTests();
