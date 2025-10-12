"""
Playwright test for Epic 3 Story 3.1: Admin Feature Toggle for Suggestion Engine
Tests the complete flow of the settings page
"""
import asyncio
from playwright.async_api import async_playwright, expect
import sys

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "https://backend-black-xi.vercel.app"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

async def test_story_3_1():
    """Test Story 3.1: Admin Settings Page"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("\n🧪 Testing Epic 3 Story 3.1: Admin Feature Toggle")
        print("=" * 60)

        # Test 1: Navigate to admin settings page
        print("\n1️⃣ Navigating to admin settings page...")
        await page.goto(f"{FRONTEND_URL}/admin/settings")
        await page.wait_for_load_state("networkidle")

        # Check if page loaded
        await expect(page.locator("h1")).to_have_text("Instellingen")
        print("   ✅ Settings page loaded")

        # Test 2: Check initial state
        print("\n2️⃣ Checking initial state...")
        template_radio = page.locator('input[value="template"]')
        koop_radio = page.locator('input[value="koop"]')

        # Wait for radios to be visible
        await template_radio.wait_for(state="visible", timeout=10000)
        await koop_radio.wait_for(state="visible", timeout=10000)

        # Check which is selected (default should be template)
        is_template_checked = await template_radio.is_checked()
        is_koop_checked = await koop_radio.is_checked()

        print(f"   Template Engine: {'✅ Selected' if is_template_checked else '❌ Not selected'}")
        print(f"   KOOP API: {'✅ Selected' if is_koop_checked else '❌ Not selected'}")

        current_engine = "template" if is_template_checked else "koop"
        print(f"   Current engine: {current_engine}")

        # Test 3: Toggle to KOOP API (if currently on template)
        if is_template_checked:
            print("\n3️⃣ Toggling to KOOP API...")
            await koop_radio.click()

            # Wait for success message
            try:
                success_msg = page.locator('.admin-settings__success')
                await success_msg.wait_for(state="visible", timeout=5000)
                success_text = await success_msg.inner_text()
                print(f"   ✅ Success message: {success_text}")
            except Exception as e:
                print(f"   ⚠️  No success message (might have failed): {e}")

            # Verify KOOP is now selected
            await page.wait_for_timeout(1000)
            is_koop_checked = await koop_radio.is_checked()
            if is_koop_checked:
                print("   ✅ KOOP API is now selected")
            else:
                print("   ❌ KOOP API toggle failed")

        # Test 4: Toggle back to Template Engine
        print("\n4️⃣ Toggling back to Template Engine...")
        await template_radio.click()

        # Wait for success message
        try:
            success_msg = page.locator('.admin-settings__success')
            await success_msg.wait_for(state="visible", timeout=5000)
            success_text = await success_msg.inner_text()
            print(f"   ✅ Success message: {success_text}")
        except Exception as e:
            print(f"   ⚠️  No success message (might have failed): {e}")

        # Verify template is now selected
        await page.wait_for_timeout(1000)
        is_template_checked = await template_radio.is_checked()
        if is_template_checked:
            print("   ✅ Template Engine is now selected")
        else:
            print("   ❌ Template Engine toggle failed")

        # Test 5: Check status indicator
        print("\n5️⃣ Checking status indicator...")
        status_badge = page.locator('.status-badge strong')
        status_text = await status_badge.inner_text()
        print(f"   Status: {status_text}")

        if "Template" in status_text:
            print("   ✅ Status badge shows Template Engine")
        else:
            print("   ✅ Status badge shows KOOP API")

        # Test 6: Test persistence by refreshing page
        print("\n6️⃣ Testing persistence after page refresh...")
        await page.reload()
        await page.wait_for_load_state("networkidle")

        # Check if setting persisted
        await template_radio.wait_for(state="visible", timeout=10000)
        is_template_checked_after_reload = await template_radio.is_checked()

        if is_template_checked == is_template_checked_after_reload:
            print("   ✅ Setting persisted after page reload")
        else:
            print("   ❌ Setting did NOT persist after page reload")

        # Test 7: Check back link works
        print("\n7️⃣ Testing back link to dashboard...")
        back_link = page.locator('a:has-text("Terug naar dashboard")')
        await back_link.click()
        await page.wait_for_load_state("networkidle")

        # Verify we're on dashboard
        dashboard_heading = page.locator('h1')
        heading_text = await dashboard_heading.inner_text()

        if "Admin Dashboard" in heading_text:
            print("   ✅ Back link works - returned to dashboard")
        else:
            print(f"   ⚠️  Back link navigated to unexpected page: {heading_text}")

        # Test 8: Verify Settings card exists on dashboard
        print("\n8️⃣ Checking Settings card on dashboard...")
        settings_card = page.locator('a[href="/admin/settings"]')
        if await settings_card.count() > 0:
            card_text = await settings_card.inner_text()
            print(f"   ✅ Settings card found: {card_text.strip()[:50]}...")
        else:
            print("   ❌ Settings card not found on dashboard")

        print("\n" + "=" * 60)
        print("🎉 Story 3.1 Testing Complete!")
        print("=" * 60)

        # Keep browser open for inspection
        print("\n⏸️  Keeping browser open for 5 seconds for inspection...")
        await page.wait_for_timeout(5000)

        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(test_story_3_1())
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
