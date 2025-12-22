"""
Smart Locator Generator using GPT-4
Generates intelligent Playwright selectors based on natural language descriptions
"""

import os

# Try to import OpenAI, but make it optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

class SmartLocatorGenerator:
    def __init__(self, api_key=None):
        """Initialize with OpenAI API key"""
        if not OPENAI_AVAILABLE:
            self.enabled = False
            print("ℹ️ OpenAI not installed. Smart locators disabled. Run: pip install openai")
            return
            
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
            print("✅ GPT-4 Smart Locators enabled!")
        else:
            self.enabled = False
            print("ℹ️ OpenAI API key not found. Smart locators disabled.")
    
    def generate_selector(self, action, element_description, page_context=""):
        """
        Generate a smart Playwright selector using GPT-4
        
        Args:
            action: The action to perform (click, fill, select)
            element_description: Natural language description of the element
            page_context: Optional context about the page
        
        Returns:
            List of selector strategies to try
        """
        if not self.enabled:
            return self._fallback_selectors(action, element_description)
        
        try:
            prompt = f"""You are a Playwright test automation expert specializing in Salesforce Lightning and modern web frameworks.

Action: {action}
Element Description: "{element_description}"
Page Context: {page_context or "Salesforce Lightning Web Component"}

Generate 10-12 different selector strategies in order of reliability. Include:
- Salesforce Lightning specific selectors (lightning-input, lightning-combobox, etc.)
- XPath following-sibling and following selectors
- ARIA labels and data attributes
- Partial text matching with case insensitivity
- Multiple fallback strategies

For INPUT fields, try:
1. Direct input selectors with partial name/placeholder matching
2. Label + following input (XPath)
3. Lightning-input components
4. Data attributes
5. ARIA labels

For DROPDOWNS, try:
1. Standard select elements
2. Lightning-combobox components
3. Input elements with role="combobox" (LWC comboboxes) - PRIORITIZE THESE
4. Div elements with role="combobox"
5. Button triggers with following options (LOWEST PRIORITY)

Return ONLY a JSON array of valid Playwright selectors. Format:
["selector1", "selector2", "selector3", ...]

Examples:
- Input: ["input[name*='email' i]", "label:has-text('Email') >> xpath=following::input[1]", "lightning-input[data-field='email'] >> input"]
- Dropdown: ["select[name*='status']", "label:has-text('Status') >> xpath=following::select[1]", "text='Status' >> xpath=following-sibling::div[1]"]
"""

            # Use GPT-3.5-turbo by default (much cheaper, still effective)
            # Change to "gpt-4" if you need maximum accuracy
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # 20x cheaper than GPT-4!
                messages=[
                    {"role": "system", "content": "You are a Playwright selector expert. Return only valid JSON arrays of selectors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            selectors_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            try:
                selectors = json.loads(selectors_text)
            except json.JSONDecodeError:
                # If response isn't valid JSON, try to extract selectors
                print(f"⚠️ GPT response wasn't valid JSON, using fallback")
                return self._fallback_selectors(action, element_description)
            
            if not isinstance(selectors, list) or len(selectors) == 0:
                print(f"⚠️ GPT returned invalid selectors, using fallback")
                return self._fallback_selectors(action, element_description)
            
            print(f"🤖 GPT-3.5 generated {len(selectors)} selectors for '{element_description}'")
            return selectors
            
        except Exception as e:
            print(f"⚠️ GPT-3.5 error: {e}. Using fallback selectors.")
            return self._fallback_selectors(action, element_description)
    
    def _fallback_selectors(self, action, element_description):
        """Fallback selectors when GPT-3.5 is not available"""
        text = element_description.strip('"\'')
        
        if action == 'click':
            return [
                # Basic text selectors
                f'text={text}',
                f'a:has-text("{text}")',
                f'button:has-text("{text}")',
                # Navigation
                f'nav a:has-text("{text}")',
                f'header a:has-text("{text}")',
                # ARIA and roles
                f'[role="button"]:has-text("{text}")',
                f'[role="link"]:has-text("{text}")',
                # Salesforce Lightning specific
                f'lightning-button:has-text("{text}")',
                f'lightning-formatted-text:has-text("{text}")',
                f'a.slds-button:has-text("{text}")',
                f'span:has-text("{text}")',
                f'div:has-text("{text}")',
                # Case insensitive
                f'a:text-is("{text}")',
                f'button:text-is("{text}")',
            ]
        elif action == 'fill':
            clean_text = text.lower().replace(" ", "")
            return [
                # Direct input selectors
                f'input[placeholder*="{text}" i]',
                f'input[name*="{clean_text}" i]',
                f'input[aria-label*="{text}" i]',
                f'input[title*="{text}" i]',
                # Label-based with XPath
                f'label:has-text("{text}") >> xpath=following::input[1]',
                f'text="{text}" >> xpath=following::input[1]',
                f'label:has-text("{text}") >> xpath=following-sibling::input[1]',
                # Lightning components
                f'lightning-input:has-text("{text}") >> input',
                f'lightning-input[data-label*="{text}" i] >> input',
                # Partial text matching
                f'label:text-is("{text}") + input',
                f'div:has-text("{text}") >> input',
                # Data attributes
                f'input[data-field*="{clean_text}" i]',
                f'input[data-name*="{clean_text}" i]',
                # ID-based
                f'input[id*="{clean_text}" i]'
            ]
        elif action == 'select':
            clean_text = text.lower().replace(" ", "")
            return [
                # Standard select elements
                f'select[name*="{clean_text}" i]',
                f'select[aria-label*="{text}" i]',
                f'label:has-text("{text}") >> xpath=following::select[1]',
                f'text="{text}" >> xpath=following::select[1]',
                # Lightning combobox components
                f'lightning-combobox[data-label*="{text}" i]',
                f'text="{text}" >> xpath=following::lightning-combobox[1]',
                # Input-based combobox (LWC) - HIGHER PRIORITY than buttons
                f'text="{text}" >> xpath=following::input[@role="combobox"][1]',
                f'input[role="combobox"][aria-label*="{text}" i]',
                f'input[role="combobox"][placeholder*="{text}" i]',
                # Div-based combobox
                f'text="{text}" >> xpath=following::div[@role="combobox"][1]',
                f'div[role="combobox"][aria-label*="{text}" i]',
                # Button-based dropdowns (LOWER PRIORITY)
                f'text="{text}" >> xpath=following::button[1]',
            ]
        else:
            return [f'text={text}']
    
    def analyze_page_structure(self, page_html):
        """
        Use GPT-4 to analyze page structure and suggest better selectors
        
        Args:
            page_html: HTML content of the page
        
        Returns:
            Dictionary of insights about the page
        """
        if not self.enabled:
            return {"insights": "GPT-4 not enabled"}
        
        try:
            # Limit HTML to first 3000 chars to avoid token limits
            html_sample = page_html[:3000]
            
            prompt = f"""Analyze this HTML and identify key patterns for test automation:

{html_sample}

Identify:
1. Framework used (React, Angular, Salesforce Lightning, etc.)
2. Common class patterns
3. Navigation structure
4. Form patterns
5. Recommended selector strategies

Return as JSON."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a web automation expert. Analyze HTML structure."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            import json
            insights = json.loads(response.choices[0].message.content)
            return insights
            
        except Exception as e:
            print(f"⚠️ Page analysis error: {e}")
            return {"error": str(e)}


# Singleton instance
_smart_locator = None

def get_smart_locator(api_key=None):
    """Get or create SmartLocatorGenerator instance"""
    global _smart_locator
    if _smart_locator is None:
        _smart_locator = SmartLocatorGenerator(api_key)
    return _smart_locator
