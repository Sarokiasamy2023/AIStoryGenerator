"""
Google Gemini Smart Locator Generator - FREE with generous limits
Generates intelligent Playwright selectors using Google Gemini API with Vision Detection
"""

import json
import os
import base64
from typing import List, Optional

class GeminiLocatorGenerator:
    def __init__(self, api_key=None):
        """
        Initialize Gemini Locator Generator
        
        Args:
            api_key: Google Gemini API key (or set GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.enabled = False
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                # Use current model name
                self.model = genai.GenerativeModel('models/gemini-2.5-flash')
                self.enabled = True
                print("[OK] Google Gemini enabled!")
            except ImportError:
                print("[WARNING] google-generativeai not installed. Run: pip install google-generativeai")
            except Exception as e:
                print(f"[WARNING] Gemini initialization error: {e}")
        else:
            print("[INFO] Gemini API key not found. Set GEMINI_API_KEY environment variable.")
    
    def generate_selector(self, action, element_description, page_context="", screenshot_path=None):
        """
        Generate smart Playwright selectors using Gemini (with optional vision detection)
        
        Args:
            action: The action to perform (click, fill, select)
            element_description: Natural language description of the element
            page_context: Optional context about the page
            screenshot_path: Optional path to screenshot for vision detection
        
        Returns:
            List of selector strategies to try
        """
        if not self.enabled:
            return self._fallback_selectors(action, element_description)
        
        try:
            # Use vision detection if screenshot is provided
            if screenshot_path and os.path.exists(screenshot_path):
                return self._generate_with_vision(action, element_description, page_context, screenshot_path)
            else:
                return self._generate_text_only(action, element_description, page_context)
                
        except Exception as e:
            print(f"⚠️ Gemini error: {e}. Using fallback selectors.")
            return self._fallback_selectors(action, element_description)
    
    def _generate_with_vision(self, action, element_description, page_context, screenshot_path):
        """Generate selectors using vision detection"""
        try:
            # Read and encode image
            with open(screenshot_path, 'rb') as f:
                image_data = f.read()
            
            # Create multimodal prompt
            prompt = f"""You are a Playwright test automation expert specializing in Salesforce Lightning. 
Analyze this screenshot and generate the best CSS/Playwright selectors for the highlighted element.

Action: {action}
Element to find: "{element_description}"
Context: {page_context or "Salesforce Lightning Web Component"}

Look at the screenshot and identify the element that matches the description. Then generate 8-10 different selector strategies in order of reliability:
- Text-based selectors (has-text, text-is) 
- XPath following-sibling and following selectors
- ARIA labels and roles
- Salesforce Lightning components
- Visual positioning selectors
- Attribute-based selectors

Return ONLY a valid JSON array of selectors. Format:
["selector1", "selector2", "selector3"]

Example for "Save" button:
["button:has-text('Save')", "lightning-button:has-text('Save')", "[role='button']:has-text('Save')"]"""

            # Send multimodal request
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/png", "data": image_data}
            ])
            
            return self._parse_response(response.text, element_description, "vision")
            
        except Exception as e:
            print(f"⚠️ Vision generation failed: {e}. Falling back to text-only.")
            return self._generate_text_only(action, element_description, page_context)
    
    def _generate_text_only(self, action, element_description, page_context):
        """Generate selectors using text only"""
        prompt = f"""You are a Playwright test automation expert. Generate the best CSS/Playwright selectors for this element.

Action: {action}
Element: "{element_description}"
Context: {page_context or "Salesforce Lightning Web Component"}

Generate 8-10 different selector strategies in order of reliability. Include:
- Text-based selectors (has-text, text-is)
- XPath following-sibling and following selectors
- ARIA labels and roles
- Salesforce Lightning components (lightning-input, lightning-combobox)
- Partial matching with case insensitivity

Return ONLY a valid JSON array of selectors. Format:
["selector1", "selector2", "selector3"]

Example for "Edit" button:
["button:has-text('Edit')", "a:has-text('Edit')", "[role='button']:has-text('Edit')"]"""

        response = self.model.generate_content(prompt)
        return self._parse_response(response.text, element_description, "text")
    
    def _parse_response(self, response_text, element_description, mode):
        """Parse Gemini response and extract selectors"""
        selectors_text = response_text.strip()
        
        try:
            # Sometimes Gemini adds extra text, try to extract JSON
            if '[' in selectors_text and ']' in selectors_text:
                start = selectors_text.index('[')
                end = selectors_text.rindex(']') + 1
                json_str = selectors_text[start:end]
                selectors = json.loads(json_str)
                
                if isinstance(selectors, list) and len(selectors) > 0:
                    print(f"🤖 Gemini ({mode}) generated {len(selectors)} selectors for '{element_description}'")
                    return selectors
        except json.JSONDecodeError:
            pass
        
        print(f"⚠️ Gemini response wasn't valid JSON, using fallback")
        return self._fallback_selectors("click", element_description)
    
    def _fallback_selectors(self, action, element_description):
        """Fallback selectors when Gemini is not available"""
        text = element_description.strip('"\'')
        clean_text = text.lower().replace(" ", "")
        
        if action == 'click':
            return [
                f'a:has-text("{text}")',
                f'button:has-text("{text}")',
                f'span:has-text("{text}")',
                f'nav a:has-text("{text}")',
                f'[role="button"]:has-text("{text}")',
                f'lightning-button:has-text("{text}")',
                f'div:has-text("{text}")',
            ]
        elif action == 'fill':
            return [
                f'text="{text}" >> xpath=following::input[1]',
                f'label:has-text("{text}") >> xpath=following::input[1]',
                f'input[placeholder*="{text}" i]',
                f'input[name*="{clean_text}" i]',
                f'input[aria-label*="{text}" i]',
                f'lightning-input:has-text("{text}") >> input',
            ]
        elif action == 'select':
            return [
                f'label:has-text("{text}") >> xpath=following::select[1]',
                f'text="{text}" >> xpath=following::select[1]',
                f'select[aria-label*="{text}" i]',
            ]
        else:
            return [f'text={text}']


# Singleton instance
_gemini_locator = None

def get_gemini_locator(api_key=None):
    """Get or create GeminiLocatorGenerator instance"""
    global _gemini_locator
    if _gemini_locator is None:
        _gemini_locator = GeminiLocatorGenerator(api_key)
    return _gemini_locator
