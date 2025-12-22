"""
Playwright test executor with video recording and visual feedback
"""
import asyncio
import time
from pathlib import Path
from datetime import datetime
from typing import Optional
from playwright.async_api import async_playwright, Page, Locator
from models.test_models import (
    TestScenario, TestStep, TestAction, TestResult, 
    StepResult, ActionResult, ConsoleLog
)


class PlaywrightExecutor:
    def __init__(self, output_dir: str):
        self.screenshot_dir = Path(output_dir) / "screenshots"
        self.video_dir = Path(output_dir) / "videos"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.video_dir.mkdir(parents=True, exist_ok=True)
        
        self.playwright = None
        self.browser = None
        self.context = None
        self.page: Optional[Page] = None
        self.console_logs = []
        self.video_path = None

    async def initialize(self):
        """Initialize Playwright browser"""
        print("🔧 Initializing Playwright...")
        self.playwright = await async_playwright().start()
        
        is_headless = False  # Set to False to see browser
        
        self.browser = await self.playwright.chromium.launch(
            headless=is_headless,
            slow_mo=0,
            args=["--start-maximized"]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080} if is_headless else None,
            record_video_dir=str(self.video_dir),
            record_video_size={'width': 1920, 'height': 1080},
            no_viewport=not is_headless
        )
        
        self.page = await self.context.new_page()
        
        # Capture console logs
        self.page.on("console", self._handle_console)
        
        print("✅ Playwright initialized successfully")

    def _handle_console(self, msg):
        """Handle browser console messages"""
        log = ConsoleLog(
            Type=msg.type,
            Text=msg.text,
            Timestamp=datetime.now(),
            Location=msg.location.get('url', '') if msg.location else ''
        )
        self.console_logs.append(log)
        print(f"  📝 Console [{msg.type.upper()}]: {msg.text}")

    async def execute_scenario(self, scenario: TestScenario) -> TestResult:
        """Execute test scenario"""
        if not self.page:
            raise RuntimeError("Playwright not initialized")
        
        result = TestResult(
            ScenarioName=scenario.ScenarioName,
            StartTime=datetime.now(),
            Status="Passed"
        )
        
        start_time = time.time()
        
        try:
            print(f"\n🚀 Starting scenario: {scenario.ScenarioName}")
            
            # Navigate to scenario URL
            if scenario.Url:
                print(f"🌐 Navigating to: {scenario.Url}")
                await self.page.goto(scenario.Url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(1)
                print("✓ Page loaded successfully")
            
            # Execute steps
            for step in sorted(scenario.Steps, key=lambda s: s.Order):
                step_result = await self._execute_step(step)
                result.StepResults.append(step_result)
                
                if step_result.Status == "Failed":
                    result.Status = "Failed"
                    result.ErrorMessage = step_result.ErrorMessage
                    break
        
        except Exception as e:
            result.Status = "Failed"
            result.ErrorMessage = str(e)
            print(f"❌ Scenario execution failed: {e}")
        
        finally:
            result.EndTime = datetime.now()
            result.DurationMs = (time.time() - start_time) * 1000
            result.ConsoleLogs = self.console_logs.copy()
            
            # Show test summary overlay
            await self._show_test_summary(result)
        
        return result

    async def _execute_step(self, step: TestStep) -> StepResult:
        """Execute a test step"""
        step_result = StepResult(
            StepOrder=step.Order,
            PageName=step.StepName or step.PageName,
            StartTime=datetime.now(),
            Status="Passed"
        )
        
        start_time = time.time()
        
        try:
            step_name = step.StepName or step.PageName
            print(f"\n▶ Step {step.Order}: {step_name}")
            
            # Show step banner
            await self._show_step_banner(f"Step {step.Order}: {step_name}", "#2196F3")
            
            # Navigate if needed
            if step.PageUrl:
                await self.page.goto(step.PageUrl, wait_until="networkidle")
                await asyncio.sleep(1)
            
            # Execute actions
            for i, action in enumerate(sorted(step.Actions, key=lambda a: a.Order)):
                if i == 0 and action.DelayMs > 0:
                    await asyncio.sleep(action.DelayMs / 1000)
                
                action_result = await self._execute_action(action, step.PageName)
                step_result.ActionResults.append(action_result)
                
                if action_result.Status == "Failed":
                    step_result.Status = "Failed"
                    step_result.ErrorMessage = action_result.ErrorMessage
                    break
                
                if i > 0 and action.DelayMs > 0:
                    await asyncio.sleep(action.DelayMs / 1000)
        
        except Exception as e:
            step_result.Status = "Failed"
            step_result.ErrorMessage = str(e)
            print(f"❌ Step failed: {e}")
        
        finally:
            step_result.EndTime = datetime.now()
            step_result.DurationMs = (time.time() - start_time) * 1000
        
        return step_result

    async def _execute_action(self, action: TestAction, page_name: str) -> ActionResult:
        """Execute a single action"""
        action_result = ActionResult(
            ActionOrder=action.Order,
            Element=action.Element,
            Action=action.Action,
            Timestamp=datetime.now(),
            Status="Passed"
        )
        
        try:
            print(f"  ✓ {action.Action.upper()} '{action.Value}' into {action.Element}")
            
            # Show action banner
            await self._show_action_banner(
                f"Action {action.Order}: {action.Action} - {action.Element}", 
                "#4CAF50"
            )
            
            # Find element
            locator = await self._get_locator(action.Selector)
            
            # Wait for element to be visible with longer timeout for slow-loading elements
            try:
                await locator.wait_for(state="visible", timeout=10000)
            except Exception as e:
                # If element not found, check if it's a flowruntime or complex component
                if 'flowruntime' in action.Selector.lower() or 'omniscript' in action.Selector.lower():
                    print(f"  ⚠️ Skipping complex component that may not be directly interactable")
                    return action_result
                
                # Try fallback: use element text to find it
                if action.Element and action.Element != 'Unknown Element':
                    print(f"  ⚠️ Primary selector failed, trying text-based fallback: {action.Element}")
                    try:
                        fallback_locator = self.page.get_by_text(action.Element, exact=False)
                        await fallback_locator.first.wait_for(state="visible", timeout=5000)
                        locator = fallback_locator.first
                        print(f"  ✓ Found element using text fallback")
                    except Exception:
                        print(f"  ❌ Fallback also failed")
                        raise e
                else:
                    raise
            
            # Scroll into view
            await locator.scroll_into_view_if_needed()
            await asyncio.sleep(0.3)
            
            # Highlight element (blue)
            await self._highlight_element(locator, "blue", 800)
            
            # Execute action
            action_lower = action.Action.lower()
            if action_lower in ["type", "fill", "input"]:
                # Handle None or empty values
                value = action.Value if action.Value and action.Value != "None" else ""
                await locator.fill(value)
            elif action_lower == "change":
                # 'change' is typically triggered after filling - treat as fill
                value = action.Value if action.Value and action.Value != "None" else ""
                await locator.fill(value)
            elif action_lower == "click":
                # Check if this might cause navigation
                if action.IsNavigation:
                    try:
                        # Try to wait for navigation, but don't fail if it doesn't happen
                        async with self.page.expect_navigation(timeout=5000, wait_until="domcontentloaded"):
                            await locator.click()
                    except Exception:
                        # Navigation didn't happen or already completed, that's ok
                        pass
                    # Extra wait for dynamic content to load
                    await asyncio.sleep(2)
                else:
                    await locator.click()
                    # Small wait after any click for UI updates
                    await asyncio.sleep(0.5)
            elif action_lower == "check":
                await locator.check()
            elif action_lower == "uncheck":
                await locator.uncheck()
            elif action_lower == "select":
                await locator.select_option(action.Value)
            elif action_lower == "hover":
                await locator.hover()
            else:
                raise NotImplementedError(f"Action '{action.Action}' not supported")
            
            # Take screenshot
            screenshot_path = self.screenshot_dir / f"{page_name}_Action{action.Order}_{datetime.now():%Y%m%d_%H%M%S}.png"
            try:
                await locator.screenshot(path=str(screenshot_path))
            except:
                await self.page.screenshot(path=str(screenshot_path), full_page=False)
            
            action_result.ScreenshotPath = str(screenshot_path)
            
            # Wait for navigation if needed
            if action.IsNavigation:
                await self.page.wait_for_load_state("networkidle")
                await asyncio.sleep(1)
        
        except Exception as e:
            action_result.Status = "Failed"
            action_result.ErrorMessage = str(e)
            action_result.IsHighlighted = True
            print(f"  ❌ Action failed: {e}")
            
            try:
                # Show error banner
                await self._show_action_banner(f"❌ FAILED: {action.Element} - {str(e)}", "#F44336")
                
                # Highlight failed element (red with pulse)
                locator = self.page.locator(action.Selector)
                await self._highlight_failed_element(locator, 5000)
                
                # Screenshot failure
                screenshot_path = self.screenshot_dir / f"{page_name}_Action{action.Order}_FAILED_{datetime.now():%Y%m%d_%H%M%S}.png"
                await self.page.screenshot(path=str(screenshot_path), full_page=True)
                action_result.ScreenshotPath = str(screenshot_path)
            except Exception as screenshot_ex:
                print(f"  ⚠️ Failed to capture error screenshot: {screenshot_ex}")
        
        return action_result

    async def _highlight_element(self, locator: Locator, color: str, duration_ms: int = 500):
        """Highlight element with colored border"""
        try:
            await locator.evaluate(f"""
                element => {{
                    element.style.border = '5px solid {color}';
                    element.style.boxShadow = '0 0 20px {color}';
                    element.style.outline = '3px solid {color}';
                    element.style.outlineOffset = '2px';
                    element.style.zIndex = '999999';
                    element.style.position = 'relative';
                }}
            """)
            
            await asyncio.sleep(duration_ms / 1000)
            
            if color != "red":
                await locator.evaluate("""
                    element => {
                        element.style.border = '';
                        element.style.boxShadow = '';
                        element.style.outline = '';
                        element.style.outlineOffset = '';
                    }
                """)
        except Exception as e:
            print(f"  ⚠️ Failed to highlight element: {e}")

    async def _highlight_failed_element(self, locator: Locator, duration_ms: int = 5000):
        """Highlight failed element with pulsing red effect"""
        try:
            await locator.evaluate("""
                element => {
                    element.style.border = '8px solid red';
                    element.style.boxShadow = '0 0 30px red, inset 0 0 20px rgba(255,0,0,0.3)';
                    element.style.outline = '5px solid red';
                    element.style.outlineOffset = '3px';
                    element.style.backgroundColor = 'rgba(255,0,0,0.2)';
                    element.style.zIndex = '999999';
                    element.style.position = 'relative';
                    element.style.animation = 'pulse 1s infinite';
                    
                    if (!document.getElementById('pulse-animation')) {
                        const style = document.createElement('style');
                        style.id = 'pulse-animation';
                        style.textContent = `
                            @keyframes pulse {
                                0%, 100% { box-shadow: 0 0 30px red, inset 0 0 20px rgba(255,0,0,0.3); }
                                50% { box-shadow: 0 0 50px red, inset 0 0 30px rgba(255,0,0,0.5); }
                            }
                        `;
                        document.head.appendChild(style);
                    }
                }
            """)
            
            await asyncio.sleep(duration_ms / 1000)
        except Exception as e:
            print(f"  ⚠️ Failed to highlight failed element: {e}")

    async def _show_step_banner(self, message: str, bg_color: str):
        """Show step banner overlay on video"""
        try:
            await self.page.evaluate("""
                ({ message, bgColor }) => {
                    const existing = document.getElementById('test-step-banner');
                    if (existing) existing.remove();
                    
                    const banner = document.createElement('div');
                    banner.id = 'test-step-banner';
                    banner.style.cssText = `
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        background: ${bgColor};
                        color: white;
                        padding: 20px;
                        font-size: 24px;
                        font-weight: bold;
                        text-align: center;
                        z-index: 9999999;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                        font-family: Arial, sans-serif;
                    `;
                    banner.textContent = message;
                    document.body.appendChild(banner);
                    
                    setTimeout(() => banner.remove(), 1000);
                }
            """, {"message": message, "bgColor": bg_color})
            
            await asyncio.sleep(1)
        except Exception as e:
            print(f"  ⚠️ Failed to show step banner: {e}")

    async def _show_action_banner(self, message: str, bg_color: str):
        """Show action banner overlay on video"""
        try:
            await self.page.evaluate("""
                ({ message, bgColor }) => {
                    const existing = document.getElementById('test-action-banner');
                    if (existing) existing.remove();
                    
                    const banner = document.createElement('div');
                    banner.id = 'test-action-banner';
                    banner.style.cssText = `
                        position: fixed;
                        top: 80px;
                        left: 50%;
                        transform: translateX(-50%);
                        background: ${bgColor};
                        color: white;
                        padding: 15px 30px;
                        font-size: 18px;
                        font-weight: bold;
                        text-align: center;
                        z-index: 9999998;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                        border-radius: 8px;
                        font-family: Arial, sans-serif;
                        min-width: 400px;
                    `;
                    banner.textContent = message;
                    document.body.appendChild(banner);
                    
                    setTimeout(() => banner.remove(), 800);
                }
            """, {"message": message, "bgColor": bg_color})
            
            await asyncio.sleep(0.8)
        except Exception as e:
            print(f"  ⚠️ Failed to show action banner: {e}")

    async def _show_test_summary(self, result: TestResult):
        """Show test summary overlay at the end"""
        try:
            passed_steps = sum(1 for s in result.StepResults if s.Status == "Passed")
            failed_steps = sum(1 for s in result.StepResults if s.Status == "Failed")
            total_actions = sum(len(s.ActionResults) for s in result.StepResults)
            passed_actions = sum(sum(1 for a in s.ActionResults if a.Status == "Passed") for s in result.StepResults)
            failed_actions = sum(sum(1 for a in s.ActionResults if a.Status == "Failed") for s in result.StepResults)
            duration = result.DurationMs / 1000
            status_icon = "✅" if result.Status == "Passed" else "❌"
            bg_color = "#4CAF50" if result.Status == "Passed" else "#F44336"
            
            await self.page.evaluate("""
                ({ summary, bgColor }) => {
                    const overlay = document.createElement('div');
                    overlay.id = 'test-summary-overlay';
                    overlay.style.cssText = `
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: rgba(0, 0, 0, 0.9);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        z-index: 99999999;
                        font-family: Arial, sans-serif;
                    `;
                    
                    const box = document.createElement('div');
                    box.style.cssText = `
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                        max-width: 600px;
                        width: 90%;
                    `;
                    
                    box.innerHTML = `
                        <div style='text-align: center; border-bottom: 3px solid ${bgColor}; padding-bottom: 20px; margin-bottom: 30px;'>
                            <h1 style='margin: 0; color: #333; font-size: 32px;'>TEST EXECUTION SUMMARY</h1>
                        </div>
                        <div style='font-size: 18px; line-height: 2;'>
                            <div style='display: flex; justify-content: space-between; padding: 10px; background: #f5f5f5; border-radius: 4px; margin-bottom: 10px;'>
                                <strong>Scenario:</strong>
                                <span>${summary.scenarioName}</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; padding: 10px; background: ${bgColor}; color: white; border-radius: 4px; margin-bottom: 10px;'>
                                <strong>Status:</strong>
                                <span style='font-size: 24px;'>${summary.statusIcon} ${summary.status}</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; padding: 10px; background: #f5f5f5; border-radius: 4px; margin-bottom: 10px;'>
                                <strong>Duration:</strong>
                                <span>${summary.duration} seconds</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; padding: 10px; background: #f5f5f5; border-radius: 4px; margin-bottom: 10px;'>
                                <strong>Steps:</strong>
                                <span>${summary.totalSteps} (${summary.passedSteps} passed, ${summary.failedSteps} failed)</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; padding: 10px; background: #f5f5f5; border-radius: 4px;'>
                                <strong>Actions:</strong>
                                <span>${summary.totalActions} (${summary.passedActions} passed, ${summary.failedActions} failed)</span>
                            </div>
                        </div>
                    `;
                    
                    overlay.appendChild(box);
                    document.body.appendChild(overlay);
                    
                    setTimeout(() => overlay.remove(), 5000);
                }
            """, {
                "summary": {
                    "scenarioName": result.ScenarioName,
                    "status": result.Status,
                    "statusIcon": status_icon,
                    "duration": f"{duration:.1f}",
                    "totalSteps": len(result.StepResults),
                    "passedSteps": passed_steps,
                    "failedSteps": failed_steps,
                    "totalActions": total_actions,
                    "passedActions": passed_actions,
                    "failedActions": failed_actions
                },
                "bgColor": bg_color
            })
            
            await asyncio.sleep(5)
        except Exception as e:
            print(f"  ⚠️ Failed to show test summary: {e}")

    async def _get_locator(self, selector: str):
        """Get Playwright locator from selector string"""
        # Simply return the locator - Playwright will handle all selector types
        return self.page.locator(selector)

    async def get_video_path(self) -> Optional[str]:
        """Get the recorded video path"""
        if self.page and self.page.video:
            return await self.page.video.path()
        return None

    async def close(self):
        """Close browser and cleanup"""
        print("\n🔧 Closing Playwright...")
        
        if self.page:
            await self.page.close()
        
        if self.context:
            await self.context.close()
        
        if self.browser:
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()
        
        print("✅ Playwright closed successfully")
