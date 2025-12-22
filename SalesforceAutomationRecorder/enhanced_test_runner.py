"""
Enhanced Test Runner with AI-Powered Self-Healing
Integrates selector intelligence and self-healing into test execution
"""

import asyncio
import time
from typing import Dict, List, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser

from ai_selector_engine import get_selector_engine
from self_healing_engine import get_healing_engine
from learning_feedback_system import get_learning_system


class EnhancedTestRunner:
    """
    Test runner with built-in self-healing and intelligent selector management
    """
    
    def __init__(
        self,
        headless: bool = False,
        enable_healing: bool = True,
        enable_learning: bool = True
    ):
        self.headless = headless
        self.enable_healing = enable_healing
        self.enable_learning = enable_learning
        
        self.selector_engine = get_selector_engine()
        self.healing_engine = get_healing_engine()
        self.learning_system = get_learning_system()
        
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.test_stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'healed_actions': 0,
            'failed_actions': 0,
            'total_time_ms': 0
        }
    
    async def start(self, url: str):
        """Start browser and navigate to URL"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        
        print(f"🌐 Navigating to {url}")
        await self.page.goto(url)
        await self.page.wait_for_load_state('networkidle')
        
        print("✅ Page loaded successfully")
    
    async def stop(self):
        """Stop browser and cleanup"""
        if self.browser:
            await self.browser.close()
        
        print("\n📊 Test Execution Summary:")
        print(f"   Total Actions: {self.test_stats['total_actions']}")
        print(f"   Successful: {self.test_stats['successful_actions']}")
        print(f"   Self-Healed: {self.test_stats['healed_actions']}")
        print(f"   Failed: {self.test_stats['failed_actions']}")
        print(f"   Success Rate: {self._calculate_success_rate():.1f}%")
        print(f"   Total Time: {self.test_stats['total_time_ms']:.0f}ms")
    
    async def smart_click(
        self,
        selector: str,
        element_context: Optional[Dict] = None,
        timeout: int = 5000
    ) -> bool:
        """
        Click with automatic self-healing
        
        Args:
            selector: Element selector
            element_context: Optional context for healing
            timeout: Timeout in milliseconds
            
        Returns:
            True if successful, False otherwise
        """
        return await self._smart_action(
            'click',
            selector,
            element_context,
            timeout
        )
    
    async def smart_fill(
        self,
        selector: str,
        value: str,
        element_context: Optional[Dict] = None,
        timeout: int = 5000
    ) -> bool:
        """
        Fill input with automatic self-healing
        """
        return await self._smart_action(
            'fill',
            selector,
            element_context,
            timeout,
            value=value
        )
    
    async def smart_select(
        self,
        selector: str,
        value: str,
        element_context: Optional[Dict] = None,
        timeout: int = 5000
    ) -> bool:
        """
        Select option with automatic self-healing
        """
        return await self._smart_action(
            'select',
            selector,
            element_context,
            timeout,
            value=value
        )
    
    async def _smart_action(
        self,
        action: str,
        selector: str,
        element_context: Optional[Dict],
        timeout: int,
        **kwargs
    ) -> bool:
        """
        Execute action with self-healing capability
        """
        self.test_stats['total_actions'] += 1
        start_time = time.time()
        
        try:
            # Try original selector first
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            
            if not element:
                raise Exception(f"Element not found: {selector}")
            
            # Perform action
            if action == 'click':
                await element.click()
            elif action == 'fill':
                await element.fill(kwargs.get('value', ''))
            elif action == 'select':
                await element.select_option(kwargs.get('value', ''))
            
            # Record success
            execution_time = (time.time() - start_time) * 1000
            self.test_stats['successful_actions'] += 1
            self.test_stats['total_time_ms'] += execution_time
            
            if self.enable_learning:
                self.learning_system.record_selector_execution(
                    selector,
                    element_context.get('element_type', 'unknown') if element_context else 'unknown',
                    success=True,
                    execution_time_ms=execution_time
                )
            
            print(f"✅ {action.upper()}: {selector} ({execution_time:.0f}ms)")
            return True
            
        except Exception as e:
            print(f"⚠️ {action.upper()} failed: {selector}")
            print(f"   Error: {str(e)}")
            
            # Attempt self-healing if enabled
            if self.enable_healing and element_context:
                print(f"🔧 Attempting self-healing...")
                
                healing_result = await self.healing_engine.heal_selector(
                    self.page,
                    selector,
                    element_context
                )
                
                if healing_result:
                    # Retry with healed selector
                    new_selector = healing_result['new_selector']
                    print(f"🔄 Retrying with healed selector: {new_selector}")
                    
                    try:
                        element = await self.page.wait_for_selector(new_selector, timeout=timeout)
                        
                        if action == 'click':
                            await element.click()
                        elif action == 'fill':
                            await element.fill(kwargs.get('value', ''))
                        elif action == 'select':
                            await element.select_option(kwargs.get('value', ''))
                        
                        execution_time = (time.time() - start_time) * 1000
                        self.test_stats['successful_actions'] += 1
                        self.test_stats['healed_actions'] += 1
                        self.test_stats['total_time_ms'] += execution_time
                        
                        print(f"✅ {action.upper()} succeeded after healing ({execution_time:.0f}ms)")
                        return True
                        
                    except Exception as retry_error:
                        print(f"❌ Healing retry failed: {retry_error}")
            
            # Record failure
            self.test_stats['failed_actions'] += 1
            
            if self.enable_learning:
                self.learning_system.record_selector_execution(
                    selector,
                    element_context.get('element_type', 'unknown') if element_context else 'unknown',
                    success=False
                )
            
            return False
    
    async def generate_smart_selector(
        self,
        element_description: str,
        element_type: str = 'input'
    ) -> str:
        """
        Generate intelligent selector for an element
        
        Args:
            element_description: Natural language description
            element_type: Type of element (input, button, etc.)
            
        Returns:
            Best selector string
        """
        # Create element data from description
        element_data = {
            'tagName': element_type,
            'innerText': element_description,
            'attributes': {}
        }
        
        result = self.selector_engine.generate_selectors(element_data)
        
        if result['selectors']:
            best_selector = result['selectors'][0]['selector']
            confidence = result['selectors'][0]['confidence']
            
            print(f"🤖 Generated selector: {best_selector} (confidence: {confidence:.2%})")
            return best_selector
        
        return f"text={element_description}"
    
    async def verify_element_exists(
        self,
        selector: str,
        timeout: int = 5000
    ) -> bool:
        """
        Verify element exists without interaction
        """
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            return element is not None
        except:
            return False
    
    async def take_screenshot(self, filepath: str):
        """Take screenshot of current page"""
        await self.page.screenshot(path=filepath)
        print(f"📸 Screenshot saved: {filepath}")
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        total = self.test_stats['total_actions']
        if total == 0:
            return 0.0
        
        successful = self.test_stats['successful_actions']
        return (successful / total) * 100
    
    async def run_test_from_recording(
        self,
        recording_file: str,
        url: str
    ):
        """
        Run test from a recording file with self-healing
        
        Args:
            recording_file: Path to recording JSON
            url: Starting URL
        """
        import json
        
        # Load recording
        with open(recording_file, 'r') as f:
            interactions = json.load(f)
        
        print(f"📋 Loaded {len(interactions)} interactions from {recording_file}")
        
        # Start browser
        await self.start(url)
        
        # Execute each interaction
        for i, interaction in enumerate(interactions, 1):
            action = interaction.get('action', 'click')
            selector = interaction.get('selector', '')
            label = interaction.get('label', 'Unknown')
            
            print(f"\n[{i}/{len(interactions)}] {action.upper()}: {label}")
            
            # Create element context for healing
            element_context = {
                'element_text': label,
                'element_type': interaction.get('componentType', 'unknown'),
                'framework': interaction.get('framework', 'unknown'),
                'attributes': interaction.get('attributes', {})
            }
            
            # Execute action
            if action == 'click':
                await self.smart_click(selector, element_context)
            elif action == 'input' or action == 'fill':
                # In real scenario, you'd have the value to fill
                await self.smart_fill(selector, "Test Value", element_context)
            
            # Small delay between actions
            await asyncio.sleep(0.5)
        
        # Stop browser
        await self.stop()


# Example usage function
async def example_usage():
    """Example of using the enhanced test runner"""
    
    runner = EnhancedTestRunner(
        headless=False,
        enable_healing=True,
        enable_learning=True
    )
    
    try:
        # Start browser
        await runner.start("https://login.salesforce.com")
        
        # Use smart actions with self-healing
        await runner.smart_fill(
            "input#username",
            "test@example.com",
            element_context={
                'element_text': 'Username',
                'element_type': 'input',
                'attributes': {'id': 'username', 'type': 'text'}
            }
        )
        
        await runner.smart_fill(
            "input#password",
            "password123",
            element_context={
                'element_text': 'Password',
                'element_type': 'input',
                'attributes': {'id': 'password', 'type': 'password'}
            }
        )
        
        await runner.smart_click(
            "input#Login",
            element_context={
                'element_text': 'Log In',
                'element_type': 'button',
                'attributes': {'id': 'Login', 'type': 'submit'}
            }
        )
        
        # Take screenshot
        await runner.take_screenshot("test_result.png")
        
    finally:
        await runner.stop()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
