"""
DCP
Auto-generated test
"""

import asyncio
from playwright.async_api import async_playwright

async def salesforce_login(page):
    """Reusable login function"""
    print("🔐 Logging in...")
    await page.goto("https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/")
    await asyncio.sleep(2)
    
    await page.fill('input[placeholder="Username"]', 'sarokiasamy2@dmigs.com.dcp.dcpuat')
    await page.fill('input[placeholder="Password"]', 'Grantee@123')
    await page.click('button:has-text("Log in")')
    await asyncio.sleep(5)
    
    # Handle agreement
    print("📋 Handling agreement...")
    try:
        await page.wait_for_selector('input[type="checkbox"][role="switch"]', timeout=10000)
        await page.click('label:has(input[type="checkbox"][role="switch"])', timeout=3000)
        await asyncio.sleep(2)
        
        await page.click('button.slds-button:has-text("Next")', timeout=2000)
        print("   ✓ Clicked Next")
        await asyncio.sleep(3)
        
        await page.click('button.slds-button:has-text("Finish")', timeout=2000)
        print("   ✓ Clicked Finish")
        await asyncio.sleep(5)
        print("✅ Login complete!\n")
    except Exception as e:
        print(f"⚠️ Agreement handling: {e}\n")

async def run_test():
    """Main test function"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   DCP                                                        ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=500)
    page = await browser.new_page(viewport=None)
    
    try:
        await salesforce_login(page)
        
        print("📊 Step 1: click")
        await page.click('text=HSD PERFORMANCE REPORTS')
        await asyncio.sleep(2)

        print("📊 Step 2: wait")
        await asyncio.sleep(2)

        print("📊 Step 3: click")
        await page.click('span:has-text("Recently Viewed"):not(:has(button))')
        await asyncio.sleep(2)

        print("📊 Step 4: wait")
        await asyncio.sleep(1)

        print("📊 Step 5: click")
        await page.click('text=In Progress Reports')
        await asyncio.sleep(2)

        print("📊 Step 6: wait")
        await asyncio.sleep(2)

        print("📊 Step 7: click")
        await page.click('text=HSD-01059')
        await asyncio.sleep(2)

        print("📊 Step 8: wait")
        await asyncio.sleep(2)

        print("📊 Step 9: click")
        await page.click('button:has-text("Edit"), a:has-text("Edit")')
        await asyncio.sleep(2)

        print("📊 Step 10: wait")
        await asyncio.sleep(2)

        print("📊 Step 11: click")
        await page.click('button:has-text("Next")')
        await asyncio.sleep(2)

        print("📊 Step 12: wait")
        await asyncio.sleep(2)

        print("\n✅ Test completed successfully!")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        await page.screenshot(path="test_failure.png")
        print("📸 Screenshot saved to test_failure.png")
        await asyncio.sleep(5)
    
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(run_test())
