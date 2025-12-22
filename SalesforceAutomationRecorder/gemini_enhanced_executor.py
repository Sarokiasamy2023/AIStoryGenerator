"""
Enhanced Test Executor with Gemini AI Integration
Combines traditional selector strategies with AI-powered intelligence
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from playwright.async_api import async_playwright, Page
from gemini_selector_ai import get_gemini_ai
from enhanced_test_executor import EnhancedTestExecutor


class GeminiEnhancedExecutor(EnhancedTestExecutor):
    """
    Test executor that uses Gemini AI to enhance element finding
    Falls back to traditional strategies if AI is unavailable
    Inherits all functionality from EnhancedTestExecutor
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        # Initialize parent class
        super().__init__()
        
        # Initialize Gemini AI
        self.gemini_ai = get_gemini_ai(gemini_api_key)
        
        # Add AI-specific metrics (parent already has performance_metrics)
        self.performance_metrics['ai_suggestions_used'] = 0
        self.performance_metrics['traditional_selectors_used'] = 0
        self.performance_metrics['total_steps'] = 0
        self.performance_metrics['successful_steps'] = 0
        self.performance_metrics['failed_steps'] = 0
        
        self.use_ai = True  # Toggle AI usage
        self.logs = []  # Additional logging for AI
    
    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Log message with timestamp"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': data or {}
        }
        self.logs.append(log_entry)
        
        # Also log to parent class if available
        if hasattr(super(), 'log'):
            super().log(level, message, data)
    
    async def find_element_with_ai(
        self,
        target: str,
        action: str = 'click'
    ) -> Tuple[Optional[any], Optional[str], bool]:
        """
        Find element using AI-enhanced strategies
        
        Returns:
            (element, selector, was_ai_used)
        """
        target_key = target.lower().replace(' ', '_')
        
        # Check learned selectors first
        if target_key in self.learned_selectors:
            learned = self.learned_selectors[target_key]
            self.log('info', f'Using learned selector for "{target}"')
            
            try:
                element = await self.page.wait_for_selector(learned['selector'], timeout=5000)
                if element and await element.is_visible():
                    learned['success_count'] += 1
                    self.performance_metrics['selectors_reused'] += 1
                    return element, learned['selector'], False
            except:
                self.log('warning', f'Learned selector failed, trying AI...')
                del self.learned_selectors[target_key]
        
        # Try traditional strategies first (fast)
        traditional_selectors = self._generate_traditional_selectors(target, action)
        self.log('info', f'Trying {len(traditional_selectors)} traditional selectors...')
        
        for i, selector in enumerate(traditional_selectors[:10], 1):  # Try first 10
            try:
                element = await self.page.wait_for_selector(selector, timeout=2000)
                if element and await element.is_visible():
                    self.log('success', f'✅ Found with traditional selector: {selector}')
                    self._learn_selector(target_key, selector, target, action)
                    self.performance_metrics['traditional_selectors_used'] += 1
                    return element, selector, False
            except:
                continue
        
        # Traditional strategies failed, use AI if available
        if self.use_ai and self.gemini_ai.is_available():
            self.log('ai', f'Traditional strategies failed. Consulting Gemini AI...')
            
            try:
                # Get page HTML for AI analysis
                page_html = await self.page.content()
                
                # Get AI suggestions
                ai_result = await self.gemini_ai.analyze_page_and_suggest_selectors(
                    target_description=target,
                    page_html=page_html,
                    action_type=action,
                    failed_selectors=traditional_selectors[:10]
                )
                
                self.log('ai', f"🤖 Gemini AI suggested {len(ai_result['selectors'])} strategies")
                if ai_result.get('reasoning'):
                    self.log('ai', f"💡 AI Reasoning: {ai_result['reasoning']}")
                
                # Try AI-suggested selectors
                for suggestion in ai_result['selectors']:
                    selector = suggestion['selector']
                    confidence = suggestion.get('confidence', 0.5)
                    strategy = suggestion.get('strategy', 'unknown')
                    
                    self.log('ai', f"Trying AI selector (confidence: {confidence:.0%}): {selector}")
                    
                    try:
                        element = await self.page.wait_for_selector(selector, timeout=3000)
                        if element and await element.is_visible():
                            self.log('success', f'✅ Found with AI selector: {selector}')
                            self.log('ai', f'🎯 AI Strategy: {strategy}')
                            self._learn_selector(target_key, selector, target, action)
                            self.performance_metrics['ai_suggestions_used'] += 1
                            return element, selector, True
                    except Exception as e:
                        self.log('warning', f'AI selector failed: {str(e)[:100]}')
                        continue
                
                # AI suggestions also failed, try alternative descriptions
                self.log('ai', '🔄 Trying alternative element descriptions...')
                alternatives = await self.gemini_ai.suggest_alternative_descriptions(
                    target,
                    page_html
                )
                
                for alt_target in alternatives:
                    self.log('ai', f'Trying alternative: "{alt_target}"')
                    alt_selectors = self._generate_traditional_selectors(alt_target, action)
                    
                    for selector in alt_selectors[:5]:
                        try:
                            element = await self.page.wait_for_selector(selector, timeout=2000)
                            if element and await element.is_visible():
                                self.log('success', f'✅ Found with alternative description: "{alt_target}"')
                                self._learn_selector(target_key, selector, target, action)
                                return element, selector, True
                        except:
                            continue
                
            except Exception as e:
                self.log('error', f'AI analysis failed: {e}')
        
        # Everything failed
        self.log('error', f'❌ Could not find element: {target}')
        await self._debug_element_not_found(target)
        
        return None, None, False
    
    def _generate_traditional_selectors(self, target: str, action: str) -> List[str]:
        """Generate traditional selector strategies (non-AI)"""
        target_lower = target.lower()
        target_clean = target_lower.replace(' ', '')
        selectors = []
        
        if action == 'fill':
            selectors.extend([
                f"input[placeholder*='{target}' i]",
                f"input[aria-label*='{target}' i]",
                f"label:has-text('{target}') >> input",
                f"text='{target}' >> xpath=following::input[1]",
                f"[data-field*='{target.replace(' ', '-').lower()}'] >> input",
                f"input[name*='{target_clean}']",
                f"textarea[placeholder*='{target}' i]",
                f"input[type='text']",
                f"input[type='email']",
                f"input[type='password']",
            ])
        else:  # click
            selectors.extend([
                f"button:has-text('{target}')",
                f"a:has-text('{target}')",
                f"[role='button']:has-text('{target}')",
                f"input[type='submit'][value*='{target}' i]",
                f"[aria-label*='{target}' i]",
                f"text={target}",
            ])
        
        # Salesforce-specific
        selectors.extend([
            f"lightning-button:has-text('{target}')",
            f"lightning-input[data-field*='{target_clean}'] >> input",
            f"[data-label='{target}']",
        ])
        
        return selectors
    
    def _learn_selector(self, target_key: str, selector: str, target: str, action: str):
        """Learn successful selector for future use"""
        self.learned_selectors[target_key] = {
            'selector': selector,
            'target': target,
            'action': action,
            'success_count': 1,
            'learned_at': datetime.now().isoformat()
        }
        self.performance_metrics['selectors_learned'] += 1
        self.log('success', f'🧠 Learned selector for "{target}"')
    
    async def _debug_element_not_found(self, target: str):
        """Debug helper when element not found"""
        try:
            # Take screenshot
            screenshot_path = f"debug_{target.replace(' ', '_')[:30]}_{datetime.now().strftime('%H%M%S')}.png"
            await self.page.screenshot(path=screenshot_path)
            self.log('info', f'📸 Debug screenshot: {screenshot_path}')
            
            # Check if text exists on page
            page_text = await self.page.evaluate('() => document.body.innerText')
            if target.lower() in page_text.lower():
                self.log('warning', f'Text "{target}" exists on page but element not clickable')
            else:
                self.log('warning', f'Text "{target}" not found on page')
        except:
            pass
    
    def parse_step(self, step_text: str) -> Optional[Dict]:
        """Parse natural language test step"""
        step_lower = step_text.lower().strip()
        
        # Wait
        if step_lower.startswith('wait'):
            import re
            match = re.search(r'(\d+)', step_lower)
            seconds = int(match.group(1)) if match else 2
            return {'action': 'wait', 'seconds': seconds}
        
        # Navigate
        if step_lower.startswith('navigate') or step_lower.startswith('go to'):
            url = step_text.split()[-1]
            return {'action': 'navigate', 'url': url}
        
        # Type/Fill
        if 'type' in step_lower or 'fill' in step_lower or 'enter' in step_lower:
            import re
            # Pattern: Type "value" into "field"
            match = re.search(r'["\']([^"\']+)["\'].*["\']([^"\']+)["\']', step_text)
            if match:
                return {'action': 'fill', 'value': match.group(1), 'target': match.group(2)}
        
        # Click
        if 'click' in step_lower:
            import re
            match = re.search(r'click[^"\']*["\']([^"\']+)["\']', step_text, re.IGNORECASE)
            if match:
                return {'action': 'click', 'target': match.group(1)}
        
        # Select
        if 'select' in step_lower:
            import re
            match = re.search(r'select[^"\']*["\']([^"\']+)["\'].*["\']([^"\']+)["\']', step_text, re.IGNORECASE)
            if match:
                return {'action': 'select', 'value': match.group(1), 'target': match.group(2)}
        
        return None
    
    async def execute_step(self, step_text: str) -> bool:
        """Execute a single test step"""
        self.performance_metrics['total_steps'] += 1
        self.log('info', f'Executing: {step_text}')
        
        # Use parent's enhanced parser which supports more formats
        parsed = self.parse_plain_text_step(step_text)
        if not parsed:
            self.log('error', f'Could not parse step: {step_text}')
            self.performance_metrics['failed_steps'] += 1
            return False
        
        action = parsed['action']
        
        try:
            if action == 'wait':
                # Parent parser uses 'duration', old parser used 'seconds'
                duration = parsed.get('duration') or parsed.get('seconds', 2)
                await asyncio.sleep(duration)
                self.log('success', f'Waited {duration} seconds')
                self.performance_metrics['successful_steps'] += 1
                return True
            
            elif action == 'navigate':
                await self.page.goto(parsed['url'])
                self.log('success', f'Navigated to {parsed["url"]}')
                self.performance_metrics['successful_steps'] += 1
                return True
            
            elif action in ['click', 'fill', 'select']:
                target = parsed['target']
                element, selector, was_ai = await self.find_element_with_ai(target, action)
                
                if not element:
                    self.performance_metrics['failed_steps'] += 1
                    return False
                
                if action == 'click':
                    await element.click()
                    self.log('success', f'Clicked: {target}')
                
                elif action == 'fill':
                    value = parsed['value']
                    await element.fill(value)
                    self.log('success', f'Filled {target} with: {value}')
                
                elif action == 'select':
                    value = parsed['value']
                    await element.select_option(value)
                    self.log('success', f'Selected {value} in: {target}')
                
                self.performance_metrics['successful_steps'] += 1
                await asyncio.sleep(0.5)
                return True
        
        except Exception as e:
            self.log('error', f'Step failed: {str(e)}')
            self.performance_metrics['failed_steps'] += 1
            return False
    
    async def execute_test(
        self,
        url: str,
        steps: List[str],
        headless: bool = False
    ) -> Dict:
        """Execute complete test"""
        start_time = datetime.now()
        
        try:
            await self.setup(headless)
            
            # Navigate to URL
            self.log('info', f'Navigating to {url}')
            await self.page.goto(url)
            await asyncio.sleep(2)
            
            # Execute steps
            for step in steps:
                success = await self.execute_step(step)
                if not success:
                    self.log('warning', f'Step failed but continuing...')
            
            await asyncio.sleep(2)
            
        finally:
            await self.teardown()
        
        # Calculate metrics
        duration = (datetime.now() - start_time).total_seconds()
        success_rate = (self.performance_metrics['successful_steps'] / 
                       self.performance_metrics['total_steps'] * 100 
                       if self.performance_metrics['total_steps'] > 0 else 0)
        
        return {
            'duration': duration,
            'metrics': self.performance_metrics,
            'success_rate': success_rate,
            'logs': self.logs,
            'ai_summary': self.gemini_ai.get_learning_summary() if self.gemini_ai.is_available() else None
        }
    
    def get_report(self) -> str:
        """Generate test execution report"""
        metrics = self.performance_metrics
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           GEMINI AI-ENHANCED TEST EXECUTION REPORT           ║
╚══════════════════════════════════════════════════════════════╝

📊 EXECUTION METRICS:
  • Total Steps: {metrics['total_steps']}
  • Successful: {metrics['successful_steps']} ✅
  • Failed: {metrics['failed_steps']} ❌
  • Success Rate: {metrics['successful_steps']/metrics['total_steps']*100:.1f}%

🤖 AI USAGE:
  • AI Suggestions Used: {metrics['ai_suggestions_used']}
  • Traditional Selectors: {metrics['traditional_selectors_used']}
  • AI Availability: {'✅ Yes' if self.gemini_ai.is_available() else '❌ No'}

🧠 LEARNING:
  • Selectors Learned: {metrics['selectors_learned']}
  • Selectors Reused: {metrics['selectors_reused']}
  • Learning Efficiency: {metrics['selectors_reused']/(metrics['selectors_learned'] or 1):.1f}x

💡 RECOMMENDATIONS:
"""
        if not self.gemini_ai.is_available():
            report += "  • Set GEMINI_API_KEY environment variable for AI features\n"
        
        if metrics['failed_steps'] > 0:
            report += f"  • {metrics['failed_steps']} steps failed - review logs for details\n"
        
        if metrics['ai_suggestions_used'] > 0:
            report += f"  • AI helped find {metrics['ai_suggestions_used']} difficult elements\n"
        
        return report


# Example usage
async def main():
    """Example test execution"""
    
    # Initialize executor (will use GEMINI_API_KEY from environment)
    executor = GeminiEnhancedExecutor()
    
    # Define test
    url = "https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/"
    steps = [
        'Wait for 2 seconds',
        'Type "sarokiasamy2@dmigs.com.dcp.dcpuat" into "Username"',
        'Type "Grantee@123" into "Password"',
        'Click "Log in"',
        'Wait for 2 seconds',
        'Click "I Disagree"',
        'Click "Next"',
    ]
    
    # Execute test
    result = await executor.execute_test(url, steps, headless=False)
    
    # Print report
    print(executor.get_report())
    
    # Save AI learning history
    if executor.gemini_ai.is_available():
        executor.gemini_ai.save_learning_history()


if __name__ == '__main__':
    asyncio.run(main())
