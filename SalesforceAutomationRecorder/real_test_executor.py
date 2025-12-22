"""
Real Test Executor with Learning & Playback
Executes real browser tests, learns selectors, and reuses them
Enhanced with Gemini AI for intelligent selector generation and learning
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Page
import re

# Import Gemini AI
from gemini_locator import get_gemini_locator

class TestExecutor:
    def __init__(self):
        self.browser = None
        self.page = None
        self.learning_db = Path("test_learning.json")
        self.learned_selectors = self.load_learning()
        self.execution_log = []
        self.performance_metrics = {
            'total_time': 0,
            'selectors_tried': 0,
            'selectors_reused': 0,
            'selectors_learned': 0,
            'step_timings': []
        }
        self.last_failure_screenshot = None
        
    def load_learning(self):
        """Load previously learned selectors"""
        if self.learning_db.exists():
            with open(self.learning_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_learning(self):
        """Save learned selectors for reuse"""
        with open(self.learning_db, 'w', encoding='utf-8') as f:
            json.dump(self.learned_selectors, f, indent=2)
    
    async def start_browser(self, url: str, headless: bool = False, browser: str = "chromium"):
        """Start browser and navigate to URL"""
        playwright = await async_playwright().start()

        browser_name = (browser or "chromium").lower()

        if browser_name == "firefox":
            self.browser = await playwright.firefox.launch(headless=headless)
        elif browser_name in ("chrome", "chrome-headless"):
            try:
                self.browser = await playwright.chromium.launch(channel="chrome", headless=headless)
            except Exception:
                # Fallback to default Chromium if Chrome channel is not available
                self.browser = await playwright.chromium.launch(headless=headless)
        elif browser_name == "edge":
            try:
                self.browser = await playwright.chromium.launch(channel="msedge", headless=headless)
            except Exception:
                # Fallback to default Chromium if Edge channel is not available
                self.browser = await playwright.chromium.launch(headless=headless)
        else:
            # Default to Chromium
            self.browser = await playwright.chromium.launch(headless=headless)

        self.page = await self.browser.new_page()
        
        self.log('info', f'Navigating to {url}')
        await self.page.goto(url)
        await self.page.wait_for_load_state('networkidle')
        self.log('success', 'Page loaded successfully')
    
    async def stop_browser(self):
        """Stop browser"""
        if self.browser:
            await self.browser.close()
            self.log('info', 'Browser closed')
    
    def log(self, level: str, message: str, details: dict = None):
        """Add log entry"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'details': details or {}
        }
        self.execution_log.append(entry)
        print(f"[{level.upper()}] {message}")
    
    def parse_plain_text_step(self, step_text: str):
        """Parse plain text step into action and target"""
        step_text = step_text.strip().lower()
        
        # Click patterns
        if 'click' in step_text:
            target = step_text.replace('click', '').strip()
            return {'action': 'click', 'target': target}
        
        # Fill/Type patterns
        if 'fill' in step_text or 'type' in step_text or 'enter' in step_text:
            # Extract target and value
            # e.g., "fill username with john@example.com"
            match = re.search(r'(fill|type|enter)\s+(.+?)\s+(with|as)\s+(.+)', step_text)
            if match:
                target = match.group(2).strip()
                value = match.group(4).strip()
                return {'action': 'fill', 'target': target, 'value': value}
        
        # Select patterns
        if 'select' in step_text:
            match = re.search(r'select\s+(.+?)\s+(from|in)\s+(.+)', step_text)
            if match:
                value = match.group(1).strip()
                target = match.group(3).strip()
                return {'action': 'select', 'target': target, 'value': value}
        
        return None
    
    async def find_element_smart(self, target: str, action: str = 'click'):
        """Find element using learned selectors or AI strategies"""
        target_key = target.lower().replace(' ', '_')
        start_time = datetime.now()
        
        # Check if we have learned selector
        if target_key in self.learned_selectors:
            learned = self.learned_selectors[target_key]
            self.log('info', f'Using learned selector for "{target}"', 
                    {'selector': learned['selector'], 'success_count': learned['success_count']})
            
            try:
                element = await self.page.wait_for_selector(learned['selector'], timeout=5000)
                if element:
                    # Verify element is visible and correct type
                    is_visible = await element.is_visible()
                    if is_visible:
                        # For fill action, avoid file inputs / readonly / disabled elements.
                        if action == 'fill':
                            try:
                                is_bad_fill_target = await element.evaluate('''el => {
                                    const tag = (el.tagName || '').toLowerCase();
                                    if (tag !== 'input' && tag !== 'textarea') {
                                        return true;
                                    }
                                    if (tag === 'input') {
                                        const t = (el.getAttribute('type') || 'text').toLowerCase();
                                        if (t === 'file' || t === 'hidden' || t === 'checkbox' || t === 'radio' || t === 'button' || t === 'submit') {
                                            return true;
                                        }
                                    }
                                    const ariaDisabled = (el.getAttribute('aria-disabled') || '').toLowerCase();
                                    const ariaReadonly = (el.getAttribute('aria-readonly') || '').toLowerCase();
                                    const hasReadonlyAttr = el.hasAttribute('readonly');
                                    const hasDisabledAttr = el.hasAttribute('disabled');
                                    const className = (el.className || '').toString().toLowerCase();
                                    return ariaDisabled === 'true' || ariaReadonly === 'true' || hasReadonlyAttr || hasDisabledAttr || className.includes('readonly');
                                }''')
                                if is_bad_fill_target:
                                    self.log('warning', f'Learned selector points to non-editable/file input; removing and retrying...')
                                    del self.learned_selectors[target_key]
                                    self.save_learning()
                                    element = None
                            except Exception:
                                pass

                            if element:
                                learned['success_count'] += 1
                                learned['last_used'] = datetime.now().isoformat()
                                self.save_learning()
                                self.performance_metrics['selectors_reused'] += 1
                                return element, learned['selector'], True

                        # For select action, avoid readonly/disabled combobox inputs (OmniStudio often renders both)
                        if action == 'select':
                            try:
                                is_disabled_or_readonly = await element.evaluate('''el => {
                                    const ariaDisabled = (el.getAttribute('aria-disabled') || '').toLowerCase();
                                    const ariaReadonly = (el.getAttribute('aria-readonly') || '').toLowerCase();
                                    const hasReadonlyAttr = el.hasAttribute('readonly');
                                    const hasDisabledAttr = el.hasAttribute('disabled');
                                    const className = (el.className || '').toString().toLowerCase();
                                    return ariaDisabled === 'true' || ariaReadonly === 'true' || hasReadonlyAttr || hasDisabledAttr || className.includes('readonly');
                                }''')
                                if is_disabled_or_readonly:
                                    self.log('warning', f'Learned selector points to readonly/disabled dropdown input; removing and retrying...')
                                    del self.learned_selectors[target_key]
                                    self.save_learning()
                                    element = None
                            except Exception:
                                pass

                            if not element:
                                # Continue to try other strategies
                                pass
                            else:
                                learned['success_count'] += 1
                                learned['last_used'] = datetime.now().isoformat()
                                self.save_learning()
                                self.performance_metrics['selectors_reused'] += 1
                                return element, learned['selector'], True

                        # For textarea action, ensure we are pointing to a real <textarea>
                        if action == 'textarea':
                            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                            if tag_name != 'textarea':
                                self.log('warning', f'Learned selector is {tag_name}, not textarea; removing and retrying...')
                                del self.learned_selectors[target_key]
                                self.save_learning()
                                # Continue to try other strategies
                                element = None
                            else:
                                # Update success count
                                learned['success_count'] += 1
                                learned['last_used'] = datetime.now().isoformat()
                                self.save_learning()
                                
                                # Track metrics
                                self.performance_metrics['selectors_reused'] += 1
                                return element, learned['selector'], True

                        # For form actions, verify the element contains Edit/Start
                        if action == 'click' and 'form' in target.lower() and ':' in target:
                            element_text = await element.evaluate('''el => {
                                return (el.innerText || el.textContent || '').trim().toLowerCase();
                            }''')
                            if 'edit' not in element_text and 'start' not in element_text:
                                self.log('warning', f'Learned selector does not point to Edit/Start button, removing...')
                                del self.learned_selectors[target_key]
                                self.save_learning()
                                # Continue to try other strategies
                            else:
                                # Update success count
                                learned['success_count'] += 1
                                learned['last_used'] = datetime.now().isoformat()
                                self.save_learning()
                                
                                # Track metrics
                                self.performance_metrics['selectors_reused'] += 1
                                return element, learned['selector'], True
                        else:
                            # Update success count
                            learned['success_count'] += 1
                            learned['last_used'] = datetime.now().isoformat()
                            self.save_learning()
                            
                            # Track metrics
                            self.performance_metrics['selectors_reused'] += 1
                            return element, learned['selector'], True
                    else:
                        self.log('warning', f'Learned selector found element but not visible, trying other strategies...')
            except:
                self.log('warning', f'Learned selector failed for "{target}", trying other strategies...')
                # Delete bad learned selector
                del self.learned_selectors[target_key]
                self.save_learning()
                self.log('info', f'Removed bad learned selector for "{target}"')
        
        # Generate multiple selector strategies
        selectors = self.generate_selectors(target, action)
        
        self.log('info', f'Trying {len(selectors)} selector strategies for "{target}"')
        self.performance_metrics['selectors_tried'] += len(selectors)
        
        for i, selector in enumerate(selectors, 1):
            try:
                self.log('info', f'Strategy {i}/{len(selectors)}: {selector}')
                element = await self.page.wait_for_selector(selector, timeout=2000)
                
                if element:
                    # Verify element is visible and enabled
                    is_visible = await element.is_visible()
                    if not is_visible:
                        self.log('warning', f'Element found but not visible: {selector}')
                        continue

                    # For select action, avoid readonly/disabled combobox inputs
                    if action == 'select':
                        try:
                            is_disabled_or_readonly = await element.evaluate('''el => {
                                const ariaDisabled = (el.getAttribute('aria-disabled') || '').toLowerCase();
                                const ariaReadonly = (el.getAttribute('aria-readonly') || '').toLowerCase();
                                const hasReadonlyAttr = el.hasAttribute('readonly');
                                const hasDisabledAttr = el.hasAttribute('disabled');
                                const className = (el.className || '').toString().toLowerCase();
                                return ariaDisabled === 'true' || ariaReadonly === 'true' || hasReadonlyAttr || hasDisabledAttr || className.includes('readonly');
                            }''')
                            if is_disabled_or_readonly:
                                self.log('warning', f'Element is readonly/disabled, skipping for select action: {selector}')
                                continue
                        except Exception:
                            pass
                    
                    # Verify element type matches action
                    tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                    if action == 'fill' and tag_name not in ['input', 'textarea']:
                        self.log('warning', f'Element is {tag_name}, not input/textarea for fill action: {selector}')
                        continue

                    if action == 'fill':
                        try:
                            is_bad_fill_target = await element.evaluate('''el => {
                                const tag = (el.tagName || '').toLowerCase();
                                if (tag === 'input') {
                                    const t = (el.getAttribute('type') || 'text').toLowerCase();
                                    if (t === 'file' || t === 'hidden' || t === 'checkbox' || t === 'radio' || t === 'button' || t === 'submit') {
                                        return true;
                                    }
                                }
                                const ariaDisabled = (el.getAttribute('aria-disabled') || '').toLowerCase();
                                const ariaReadonly = (el.getAttribute('aria-readonly') || '').toLowerCase();
                                const hasReadonlyAttr = el.hasAttribute('readonly');
                                const hasDisabledAttr = el.hasAttribute('disabled');
                                const className = (el.className || '').toString().toLowerCase();
                                return ariaDisabled === 'true' || ariaReadonly === 'true' || hasReadonlyAttr || hasDisabledAttr || className.includes('readonly');
                            }''')
                            if is_bad_fill_target:
                                self.log('warning', f'Element is not a valid fill target, skipping: {selector}')
                                continue
                        except Exception:
                            pass

                    if action == 'select' and tag_name not in ['select', 'input', 'button']:
                        self.log('warning', f'Element is {tag_name}, not select/input/button for select action: {selector}')
                        continue

                    if action == 'textarea' and tag_name != 'textarea':
                        self.log('warning', f'Element is {tag_name}, not textarea for textarea action: {selector}')
                        continue
                    
                    if action == 'click' and tag_name == 'textarea' and 'search' not in target.lower():
                        self.log('warning', f'Element is textarea, not suitable for click action: {selector}')
                        continue
                    
                    # For form clicks, ensure we're clicking a link or button with Edit/Start text
                    if action == 'click' and 'form' in target.lower() and ':' in target:
                        # Check if element is clickable (link/button)
                        is_clickable = await element.evaluate('''el => {
                            const tag = el.tagName.toLowerCase();
                            return tag === 'a' || tag === 'button' || el.onclick !== null || el.getAttribute('role') === 'button';
                        }''')
                        if not is_clickable:
                            self.log('warning', f'Element is {tag_name}, not a clickable link/button for form: {selector}')
                            continue
                        
                        # CRITICAL: Verify the element or its children contain "Edit" or "Start" text
                        element_text = await element.evaluate('''el => {
                            return (el.innerText || el.textContent || '').trim().toLowerCase();
                        }''')
                        if 'edit' not in element_text and 'start' not in element_text:
                            self.log('warning', f'Element text "{element_text}" does not contain Edit/Start: {selector}')
                            continue
                        
                        self.log('info', f'✓ Found Edit/Start button with text: "{element_text}"')
                    
                    # For fill actions, avoid header/navigation search boxes
                    if action == 'fill':
                        is_in_header = await element.evaluate('''el => {
                            let current = el;
                            while (current) {
                                const tag = current.tagName ? current.tagName.toLowerCase() : '';
                                const className = current.className || '';
                                const id = current.id || '';
                                // Check if in header, nav, or search area
                                if (tag === 'header' || tag === 'nav' || 
                                    className.includes('header') || className.includes('nav') || 
                                    className.includes('search-box') || className.includes('global-search') ||
                                    id.includes('header') || id.includes('nav') || id.includes('search')) {
                                    return true;
                                }
                                current = current.parentElement;
                            }
                            return false;
                        }''')
                        if is_in_header:
                            self.log('warning', f'Element is in header/nav area, skipping: {selector}')
                            continue
                    
                    self.log('success', f'✅ Found element with: {selector}')
                    
                    # Learn this selector
                    self.learned_selectors[target_key] = {
                        'selector': selector,
                        'target': target,
                        'action': action,
                        'success_count': 1,
                        'first_learned': datetime.now().isoformat(),
                        'last_used': datetime.now().isoformat()
                    }
                    self.save_learning()
                    self.log('success', f'🧠 Learned selector for "{target}" (action: {action})')
                    
                    # Track metrics
                    self.performance_metrics['selectors_learned'] += 1
                    
                    return element, selector, False
            except Exception as e:
                self.log('warning', f'Strategy failed: {selector}')
                continue

        # OmniStudio dropdown fallback: label text can be in a separate text-block, and there may be
        # multiple combobox inputs (editable + readonly). Prefer the first visible non-readonly combobox input.
        if action == 'select':
            try:
                fieldset_candidates = [
                    f"fieldset:has-text('{target}')",
                    f"fieldset:has-text('{target.replace('.', '')}')" if '.' in target else None,
                    f"fieldset:has-text('{target[:60]}')" if len(target) > 60 else None,
                ]
                for fs_sel in [s for s in fieldset_candidates if s]:
                    fs = self.page.locator(fs_sel).first
                    if await fs.is_visible(timeout=1500):
                        combobox_candidates = [
                            "input[role='combobox']:not([readonly]):not([disabled]):not([aria-readonly='true']):not([aria-disabled='true'])",
                            "[role='combobox']:not([readonly]):not([disabled]):not([aria-readonly='true']):not([aria-disabled='true'])",
                        ]
                        for cb_sel in combobox_candidates:
                            cb = fs.locator(cb_sel).first
                            if await cb.is_visible(timeout=1500):
                                self.log('success', f'✅ Found dropdown via OmniStudio fallback: {fs_sel} >> {cb_sel}')

                                learned_selector = f"{fs_sel} >> {cb_sel}"
                                self.learned_selectors[target_key] = {
                                    'selector': learned_selector,
                                    'target': target,
                                    'action': action,
                                    'success_count': 1,
                                    'first_learned': datetime.now().isoformat(),
                                    'last_used': datetime.now().isoformat(),
                                }
                                self.save_learning()
                                self.performance_metrics['selectors_learned'] += 1
                                return cb, learned_selector, False
            except Exception:
                pass

        # OmniStudio fallback: label text can be in a separate text-block, and there may be multiple
        # textareas (editable + readonly). Prefer the first visible non-readonly textarea.
        if action == 'textarea':
            try:
                fieldset_candidates = [
                    f"fieldset:has-text('{target}')",
                    f"fieldset:has-text('{target.replace('.', '')}')" if '.' in target else None,
                    f"fieldset:has-text('{target[:60]}')" if len(target) > 60 else None,
                ]
                for fs_sel in [s for s in fieldset_candidates if s]:
                    fs = self.page.locator(fs_sel).first
                    if await fs.is_visible(timeout=1500):
                        textarea_candidates = [
                            'textarea:not([readonly]):not([aria-readonly="true"])',
                            'textarea[aria-readonly="false"]',
                            'textarea',
                        ]
                        for ta_sel in textarea_candidates:
                            ta = fs.locator(ta_sel).first
                            if await ta.is_visible(timeout=1500):
                                self.log('success', f'✅ Found textarea via OmniStudio fallback: {fs_sel} >> {ta_sel}')

                                learned_selector = f"{fs_sel} >> {ta_sel}"
                                self.learned_selectors[target_key] = {
                                    'selector': learned_selector,
                                    'target': target,
                                    'action': action,
                                    'success_count': 1,
                                    'first_learned': datetime.now().isoformat(),
                                    'last_used': datetime.now().isoformat(),
                                }
                                self.save_learning()
                                self.performance_metrics['selectors_learned'] += 1
                                return ta, learned_selector, False
            except Exception:
                pass
        
        self.log('error', f'❌ Could not find element "{target}" with any strategy')
        
        # Take a screenshot for debugging and remember it as the last failure screenshot
        try:
            screenshot_path = f"debug_not_found_{target.replace(' ', '_')[:30]}.png"
            await self.page.screenshot(path=screenshot_path)
            self.last_failure_screenshot = screenshot_path
            self.log('info', f'📸 Debug screenshot saved: {screenshot_path}')
        except:
            pass
        
        # Try to get page content for debugging
        try:
            page_text = await self.page.evaluate('() => document.body.innerText')
            # Check if target text exists anywhere on page
            if target.lower() in page_text.lower():
                self.log('warning', f'⚠️ Text "{target}" exists on page but element not clickable')
                self.log('info', f'💡 Try adding more wait time or check if element is in iframe')
            else:
                self.log('warning', f'⚠️ Text "{target}" not found anywhere on page')
                self.log('info', f'💡 Check spelling or wait for page to load completely')
                # Show similar text
                words = target.lower().split()
                if words:
                    first_word = words[0]
                    if first_word in page_text.lower():
                        self.log('info', f'💡 Found similar word "{first_word}" on page')
        except:
            pass
        
        return None, None, False
    
    def generate_selectors(self, target: str, action: str = 'click'):
        """Generate multiple selector strategies based on target and action"""
        target_lower = target.lower()
        target_title = target.title()
        target_clean = target_lower.replace(' ', '')
        
        selectors = []

        prefer_textarea = action in ('fill', 'textarea') and any(
            kw in target_lower
            for kw in ['describe', 'explain', 'comment', 'comments', 'details', 'detail', 'narrative', 'statement', 'reason', 'specify']
        )

        # Fast path for dropdown/select-like fields (Salesforce Lightning combobox)
        if action == 'select':
            selectors.extend([
                # Lightning combobox patterns near label text
                f"label:has-text('{target}') >> xpath=following::*[self::input or self::button][1]",
                f"text='{target}' >> xpath=following::*[self::input or self::button][1]",
                f"text='*{target}' >> xpath=following::*[self::input or self::button][1]",
                # Common combobox input/button roles
                f"[role='combobox'][aria-label*='{target}' i]",
                f"input[role='combobox'][aria-label*='{target}' i]",
                f"button[role='combobox'][aria-label*='{target}' i]",
                # Lightning base combobox markup
                f"lightning-combobox:has-text('{target}') input",
                f"lightning-combobox:has-text('{target}') button",
                f"lightning-base-combobox:has-text('{target}') input",
                f"lightning-base-combobox:has-text('{target}') button",
                # ARIA-haspopup listbox indicates dropdown
                f"[aria-haspopup='listbox'][aria-label*='{target}' i]",
            ])
        
        # For search/input fields
        # Treat textarea actions the same as fill for selector generation.
        if action in ('fill', 'textarea') or any(word in target_lower for word in ['search', 'username', 'email', 'password', 'name', 'field', 'input', 'text']):
            
            # SPECIAL HANDLING FOR PASSWORD FIELDS (HIGHEST PRIORITY)
            if 'password' in target_lower:
                selectors.extend([
                    # Type-based (most reliable for password)
                    f"input[type='password']",
                    # Placeholder-based
                    f"input[placeholder*='Password' i]",
                    f"input[placeholder*='Pass' i]",
                    # ARIA label
                    f"input[aria-label*='Password' i]",
                    # Name attribute
                    f"input[name*='password' i]",
                    f"input[name*='pass' i]",
                    # ID attribute
                    f"input[id*='password' i]",
                    f"input[id*='pass' i]",
                ])
            
            # SPECIAL HANDLING FOR USERNAME/EMAIL FIELDS
            elif 'username' in target_lower or 'email' in target_lower:
                selectors.extend([
                    # Placeholder-based (most reliable)
                    f"input[placeholder*='Username' i]",
                    f"input[placeholder*='User' i]",
                    f"input[placeholder*='Email' i]",
                    # Type-based
                    f"input[type='email']",
                    f"input[type='text'][placeholder*='User' i]",
                    # ARIA label
                    f"input[aria-label*='Username' i]",
                    f"input[aria-label*='Email' i]",
                    # Name attribute
                    f"input[name*='username' i]",
                    f"input[name*='user' i]",
                    f"input[name*='email' i]",
                    # ID attribute
                    f"input[id*='username' i]",
                    f"input[id*='user' i]",
                    f"input[id*='email' i]",
                ])
            
            # Generic field selectors (for other fields)
            # Specific selectors based on label/placeholder (HIGHEST PRIORITY)
            selectors.extend([
                # Placeholder-based (exact match first)
                f"input[placeholder='{target}']",
                f"textarea[placeholder='{target}']",
                f"input[placeholder*='{target}' i]",
                f"textarea[placeholder*='{target}' i]",
                # ARIA label-based
                f"input[aria-label='{target}']",
                f"textarea[aria-label='{target}']",
                f"input[aria-label*='{target}' i]",
                f"textarea[aria-label*='{target}' i]",
                # Label-based (most reliable for forms)
                f"label:has-text('{target}') >> xpath=following::textarea[1]" if prefer_textarea else f"label:has-text('{target}') >> xpath=following::input[1]",
                f"label:has-text('{target}') >> xpath=following::input[1]" if prefer_textarea else f"label:has-text('{target}') >> xpath=following::textarea[1]",
                # Text near input (for Salesforce forms where label is not a <label> tag)
                f"text='{target}' >> xpath=following::textarea[1]" if prefer_textarea else f"text='{target}' >> xpath=following::input[1]",
                f"text='{target}' >> xpath=following::input[1]" if prefer_textarea else f"text='{target}' >> xpath=following::textarea[1]",
                # With asterisk (required fields in Salesforce)
                f"text='*{target}' >> xpath=following::textarea[1]" if prefer_textarea else f"text='*{target}' >> xpath=following::input[1]",
                f"text='*{target}' >> xpath=following::input[1]" if prefer_textarea else f"text='*{target}' >> xpath=following::textarea[1]",
                # Ancestor navigation
                f"text='{target}' >> xpath=ancestor::*[1] >> input",
                f"text='{target}' >> xpath=ancestor::*[1] >> textarea",
                f"text='*{target}' >> xpath=ancestor::*[1] >> input",
                f"text='*{target}' >> xpath=ancestor::*[1] >> textarea",
                # Name attribute
                f"input[name*='{target_clean}']",
                f"textarea[name*='{target_clean}']",
                # Data attributes
                f"[data-field*='{target_lower.replace(' ', '-')}'] >> input",
                f"[data-field*='{target_lower.replace(' ', '-')}'] >> textarea",
                # ID and class based
                f"#{target_clean}",
                f".{target_clean}",
            ])
            
            # Google search specific (only for "search" keyword)
            if 'search' in target_lower and len(target_lower) < 20:
                selectors.extend([
                    "textarea[name='q']",
                    "input[name='q']",
                    "textarea[title*='Search' i]",
                    "input[title*='Search' i]",
                ])
        
        # For buttons and clickable elements
        if action == 'click' or any(word in target_lower for word in ['button', 'btn', 'submit', 'save', 'login', 'next', 'search']):
            selectors.extend([
                # Google search button specific
                "input[value='Google Search']",
                "input[name='btnK']",
                "button[name='btnK']",
                "input[type='submit'][value*='Search' i]",
                # Generic button selectors
                f"button:has-text('{target}')",
                f"input[type='submit'][value*='{target}' i]",
                f"button:has-text('{target_title}')",
                f"[role='button']:has-text('{target}')",
                f"button[aria-label*='{target}' i]",
                f"input[type='button'][value*='{target}' i]",
                f"a:has-text('{target}')",
                f"[data-action*='{target_clean}']"
            ])
        
        # Salesforce Lightning selectors
        selectors.extend([
            f"lightning-button:has-text('{target}')",
            f"lightning-input[data-field*='{target_clean}'] >> input",
            f"[data-label='{target}']",
            f"[title='{target}']"
        ])
        
        # Generic selectors (last resort)
        selectors.extend([
            f"[aria-label='{target}']",
            f"[data-testid*='{target_lower.replace(' ', '-')}']",
            f"text={target}",
            f"text={target_title}"
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_selectors = []
        for sel in selectors:
            if sel not in seen:
                seen.add(sel)
                unique_selectors.append(sel)
        
        return unique_selectors
    
    async def execute_step(self, step_text: str):
        """Execute a single test step"""
        self.log('info', f'Executing: {step_text}')
        
        parsed = self.parse_plain_text_step(step_text)
        if not parsed:
            self.log('error', f'Could not parse step: {step_text}')
            return False
        
        action = parsed['action']
        target = parsed['target']

        element = None
        selector = None
        was_learned = False

        if action == 'fill':
            try:
                prefer_textarea = any(
                    kw in (target or '').lower()
                    for kw in ['describe', 'explain', 'comment', 'comments', 'details', 'detail', 'narrative', 'statement', 'reason', 'specify']
                )
                if prefer_textarea:
                    element, selector, was_learned = await self.find_element_smart(target, 'textarea')
            except Exception:
                pass
        
        # Find element
        if not element:
            element, selector, was_learned = await self.find_element_smart(target, action)
        
        if not element:
            self.log('error', f'Could not find element: {target}')
            return False
        
        # Perform action
        try:
            if action == 'click':
                await element.click()
                self.log('success', f'Clicked: {target}', {'selector': selector})
                
            elif action == 'fill':
                value = parsed.get('value', '')
                try:
                    await element.fill(value)
                    self.log('success', f'Filled {target} with: {value}', {'selector': selector})
                except Exception as e_fill:
                    # Fallback 1: use locator fill with force to bypass pointer interception overlays
                    try:
                        loc = self.page.locator(selector).first if selector else None
                        if loc:
                            await loc.fill(value, force=True)
                            self.log('success', f'Filled {target} with: {value}', {'selector': selector, 'fallback': 'locator_fill_force'})
                        else:
                            raise e_fill
                    except Exception:
                        # Fallback 2: direct JS value set + events (works well for LWC/OmniStudio)
                        try:
                            await element.evaluate(f'''el => {{
                                el.value = {json.dumps(value)};
                                try {{ el.focus(); }} catch (e) {{}}
                                el.dispatchEvent(new Event("input", {{ bubbles: true, composed: true }}));
                                el.dispatchEvent(new Event("change", {{ bubbles: true, composed: true }}));
                                el.dispatchEvent(new Event("blur", {{ bubbles: true, composed: true }}));
                            }}''')
                            self.log('success', f'Filled {target} with: {value}', {'selector': selector, 'fallback': 'js_value_set'})
                        except Exception:
                            raise e_fill
                
            elif action == 'select':
                value = parsed.get('value', '')
                await element.select_option(value)
                self.log('success', f'Selected {value} in: {target}', {'selector': selector})
            
            await asyncio.sleep(0.5)  # Small delay between actions
            return True
            
        except Exception as e:
            self.log('error', f'Action failed: {str(e)}')
            return False
    
    async def execute_test(self, url: str, steps: list, headless: bool = False):
        """Execute complete test"""
        self.execution_log = []
        test_start_time = datetime.now()
        
        try:
            await self.start_browser(url, headless)
            
            success_count = 0
            for i, step in enumerate(steps, 1):
                step_start_time = datetime.now()
                self.log('info', f'Step {i}/{len(steps)}')
                success = await self.execute_step(step)
                step_elapsed = (datetime.now() - step_start_time).total_seconds()
                
                self.performance_metrics['step_timings'].append({
                    'step': step,
                    'time': step_elapsed,
                    'success': success
                })
                
                if success:
                    success_count += 1
            
            # Calculate total time
            total_elapsed = (datetime.now() - test_start_time).total_seconds()
            self.performance_metrics['total_time'] = total_elapsed
            
            # Take screenshot
            screenshot_path = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.page.screenshot(path=screenshot_path)
            self.log('info', f'Screenshot saved: {screenshot_path}')
            
            await self.stop_browser()
            
            # Summary with performance metrics
            self.log('info', f'Test completed: {success_count}/{len(steps)} steps successful')
            self.log('info', f'⏱️  Total time: {total_elapsed:.2f}s')
            self.log('info', f'🔄 Selectors reused: {self.performance_metrics["selectors_reused"]}')
            self.log('info', f'🧠 Selectors learned: {self.performance_metrics["selectors_learned"]}')
            
            return {
                'success': success_count == len(steps),
                'total_steps': len(steps),
                'successful_steps': success_count,
                'execution_log': self.execution_log,
                'learned_selectors': len(self.learned_selectors),
                'performance_metrics': self.performance_metrics
            }
            
        except Exception as e:
            self.log('error', f'Test execution failed: {str(e)}')
            if self.browser:
                await self.stop_browser()
            return {
                'success': False,
                'error': str(e),
                'execution_log': self.execution_log
            }
    
    def get_learned_selectors_summary(self):
        """Get summary of learned selectors"""
        return {
            'total_learned': len(self.learned_selectors),
            'selectors': [
                {
                    'target': data['target'],
                    'selector': data['selector'],
                    'success_count': data['success_count'],
                    'last_used': data['last_used']
                }
                for key, data in self.learned_selectors.items()
            ]
        }


# Example usage
async def example_test():
    """Example test execution"""
    executor = TestExecutor()
    
    # Define test in plain text
    test_steps = [
        "fill username with test@example.com",
        "fill password with password123",
        "click login button"
    ]
    
    # Execute test
    result = await executor.execute_test(
        url="https://example.com/login",
        steps=test_steps,
        headless=False
    )
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Success: {result['success']}")
    print(f"Steps: {result['successful_steps']}/{result['total_steps']}")
    print(f"Learned Selectors: {result['learned_selectors']}")
    
    # Show learned selectors
    summary = executor.get_learned_selectors_summary()
    print("\n" + "="*60)
    print("LEARNED SELECTORS")
    print("="*60)
    for sel in summary['selectors']:
        print(f"Target: {sel['target']}")
        print(f"Selector: {sel['selector']}")
        print(f"Used: {sel['success_count']} times")
        print()


if __name__ == "__main__":
    asyncio.run(example_test())
