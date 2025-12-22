"""
Google Gemini AI Integration for Intelligent Element Finding
Enhances selector strategies using AI-powered analysis
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import google.generativeai as genai


class GeminiSelectorAI:
    """
    Uses Google Gemini AI to:
    1. Analyze page structure and suggest optimal selectors
    2. Learn from failed attempts and suggest alternatives
    3. Understand semantic context of elements
    4. Generate smart fallback strategies
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini AI
        
        Args:
            api_key: Google Gemini API key (or set GEMINI_API_KEY env variable)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.cache = {}  # Cache AI responses to reduce API calls
        self.learning_history = []  # Track what works and what doesn't
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini AI initialized successfully")
            except Exception as e:
                print(f"⚠️ Gemini AI initialization failed: {e}")
                self.model = None
        else:
            print("⚠️ No Gemini API key found. Set GEMINI_API_KEY environment variable.")
    
    def is_available(self) -> bool:
        """Check if Gemini AI is available"""
        return self.model is not None
    
    async def analyze_page_and_suggest_selectors(
        self,
        target_description: str,
        page_html: str,
        action_type: str = 'click',
        failed_selectors: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze page structure and suggest optimal selectors using Gemini AI
        
        Args:
            target_description: Natural language description of element (e.g., "Login button")
            page_html: HTML content of the page (or relevant section)
            action_type: Type of action (click, fill, select, etc.)
            failed_selectors: List of selectors that already failed
            
        Returns:
            Dictionary with suggested selectors and reasoning
        """
        if not self.is_available():
            return self._fallback_suggestions(target_description, action_type)
        
        # Check cache first
        cache_key = f"{target_description}_{action_type}_{hash(page_html[:500])}"
        if cache_key in self.cache:
            print("📦 Using cached AI suggestions")
            return self.cache[cache_key]
        
        try:
            # Truncate HTML if too large (Gemini has token limits)
            html_snippet = self._extract_relevant_html(page_html, target_description)
            
            # Build prompt
            prompt = self._build_analysis_prompt(
                target_description,
                html_snippet,
                action_type,
                failed_selectors
            )
            
            print(f"🤖 Asking Gemini AI for selector suggestions...")
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            # Parse AI response
            result = self._parse_ai_response(response.text)
            
            # Cache the result
            self.cache[cache_key] = result
            
            # Log to learning history
            self.learning_history.append({
                'timestamp': datetime.now().isoformat(),
                'target': target_description,
                'action': action_type,
                'suggestions': result['selectors'][:5],
                'reasoning': result.get('reasoning', '')
            })
            
            return result
            
        except Exception as e:
            print(f"⚠️ Gemini AI analysis failed: {e}")
            return self._fallback_suggestions(target_description, action_type)
    
    def _build_analysis_prompt(
        self,
        target: str,
        html: str,
        action: str,
        failed_selectors: Optional[List[str]] = None
    ) -> str:
        """Build prompt for Gemini AI"""
        
        failed_info = ""
        if failed_selectors:
            failed_info = f"\n\nThese selectors have already FAILED:\n" + "\n".join(f"- {s}" for s in failed_selectors)
        
        prompt = f"""You are an expert in web automation and CSS/XPath selectors. Analyze the HTML and suggest the BEST selectors to find the target element.

TARGET ELEMENT: "{target}"
ACTION TYPE: {action}
{failed_info}

HTML SNIPPET:
```html
{html}
```

REQUIREMENTS:
1. Suggest 10 different selector strategies (CSS, XPath, Playwright selectors)
2. Prioritize ROBUST selectors that won't break easily
3. Consider Salesforce Lightning, OmniScript, and modern web frameworks
4. For {action} actions, ensure selectors target the right element type
5. Avoid selectors that are too generic or too brittle
6. If failed selectors are provided, suggest DIFFERENT approaches

RESPOND IN THIS EXACT JSON FORMAT:
{{
  "selectors": [
    {{"selector": "css or xpath selector", "strategy": "description", "confidence": 0.95}},
    {{"selector": "another selector", "strategy": "description", "confidence": 0.90}}
  ],
  "reasoning": "Brief explanation of your approach",
  "element_type": "button|input|link|etc",
  "recommendations": ["tip 1", "tip 2"]
}}

Focus on PRACTICAL, WORKING selectors. Be specific and actionable."""

        return prompt
    
    def _extract_relevant_html(self, html: str, target: str, max_length: int = 8000) -> str:
        """
        Extract relevant HTML section around the target element
        Reduces token usage and improves AI accuracy
        """
        if len(html) <= max_length:
            return html
        
        # Try to find relevant section containing target text
        target_lower = target.lower()
        html_lower = html.lower()
        
        # Find position of target text
        pos = html_lower.find(target_lower)
        
        if pos != -1:
            # Extract context around target
            start = max(0, pos - max_length // 2)
            end = min(len(html), pos + max_length // 2)
            return html[start:end]
        
        # If target not found in HTML, return first chunk
        # (might be in attributes, data-*, etc.)
        return html[:max_length]
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse Gemini AI response into structured format"""
        try:
            # Try to extract JSON from response
            # AI might wrap it in markdown code blocks
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Validate structure
            if 'selectors' not in data:
                raise ValueError("No selectors in response")
            
            # Ensure confidence scores
            for selector_obj in data['selectors']:
                if 'confidence' not in selector_obj:
                    selector_obj['confidence'] = 0.7
            
            return data
            
        except Exception as e:
            print(f"⚠️ Failed to parse AI response: {e}")
            print(f"Raw response: {response_text[:200]}...")
            
            # Try to extract selectors from plain text
            selectors = []
            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('.') or line.startswith('#') or 
                           line.startswith('[') or line.startswith('//') or
                           'button' in line or 'input' in line):
                    selectors.append({
                        'selector': line,
                        'strategy': 'extracted',
                        'confidence': 0.6
                    })
            
            return {
                'selectors': selectors[:10],
                'reasoning': 'Parsed from plain text response',
                'element_type': 'unknown',
                'recommendations': []
            }
    
    def _fallback_suggestions(self, target: str, action: str) -> Dict:
        """Provide fallback suggestions when AI is not available"""
        target_lower = target.lower()
        selectors = []
        
        if action == 'fill':
            selectors = [
                {'selector': f"input[placeholder*='{target}' i]", 'strategy': 'placeholder', 'confidence': 0.8},
                {'selector': f"input[aria-label*='{target}' i]", 'strategy': 'aria-label', 'confidence': 0.75},
                {'selector': f"label:has-text('{target}') >> input", 'strategy': 'label-association', 'confidence': 0.85},
                {'selector': f"[data-field*='{target.replace(' ', '-').lower()}']", 'strategy': 'data-attribute', 'confidence': 0.7},
            ]
        else:  # click
            selectors = [
                {'selector': f"button:has-text('{target}')", 'strategy': 'button-text', 'confidence': 0.85},
                {'selector': f"a:has-text('{target}')", 'strategy': 'link-text', 'confidence': 0.8},
                {'selector': f"[role='button']:has-text('{target}')", 'strategy': 'role-button', 'confidence': 0.75},
                {'selector': f"[aria-label='{target}']", 'strategy': 'aria-label', 'confidence': 0.7},
            ]
        
        return {
            'selectors': selectors,
            'reasoning': 'Fallback suggestions (AI not available)',
            'element_type': 'input' if action == 'fill' else 'button',
            'recommendations': ['Consider setting up Gemini API for better suggestions']
        }
    
    async def learn_from_failure(
        self,
        target: str,
        failed_selectors: List[str],
        page_html: str,
        action: str
    ) -> Dict:
        """
        Learn from failed attempts and suggest new strategies
        
        Args:
            target: Element description
            failed_selectors: All selectors that failed
            page_html: Current page HTML
            action: Action type
            
        Returns:
            New suggestions based on failure analysis
        """
        if not self.is_available():
            return self._fallback_suggestions(target, action)
        
        print(f"🧠 Gemini AI analyzing {len(failed_selectors)} failed attempts...")
        
        # Use the main analysis function with failed selectors
        result = await self.analyze_page_and_suggest_selectors(
            target,
            page_html,
            action,
            failed_selectors
        )
        
        # Filter out selectors that already failed
        result['selectors'] = [
            s for s in result['selectors']
            if s['selector'] not in failed_selectors
        ]
        
        return result
    
    async def suggest_alternative_descriptions(
        self,
        original_target: str,
        page_html: str
    ) -> List[str]:
        """
        Suggest alternative ways to describe the target element
        Useful when original description doesn't match anything
        
        Args:
            original_target: Original element description
            page_html: Page HTML
            
        Returns:
            List of alternative descriptions
        """
        if not self.is_available():
            # Simple fallback alternatives
            words = original_target.split()
            alternatives = [
                original_target.title(),
                original_target.upper(),
                ' '.join(words[:-1]) if len(words) > 1 else original_target,
                words[0] if words else original_target
            ]
            return alternatives
        
        try:
            prompt = f"""Given this element description: "{original_target}"

And this HTML snippet:
```html
{page_html[:2000]}
```

The element was NOT found with the original description.
Suggest 5 alternative ways to describe this element that might exist on the page.

Consider:
- Partial matches
- Similar wording
- Abbreviated versions
- Common synonyms
- Related UI elements

Respond with ONLY a JSON array of strings:
["alternative 1", "alternative 2", "alternative 3", "alternative 4", "alternative 5"]"""

            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            # Parse response
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            alternatives = json.loads(text)
            return alternatives
            
        except Exception as e:
            print(f"⚠️ Alternative suggestions failed: {e}")
            return [original_target]
    
    def get_learning_summary(self) -> Dict:
        """Get summary of AI learning history"""
        return {
            'total_queries': len(self.learning_history),
            'cache_size': len(self.cache),
            'recent_queries': self.learning_history[-10:] if self.learning_history else []
        }
    
    def clear_cache(self):
        """Clear AI response cache"""
        self.cache.clear()
        print("🗑️ AI cache cleared")
    
    def save_learning_history(self, filepath: str = 'gemini_learning_history.json'):
        """Save learning history to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.learning_history, f, indent=2)
            print(f"💾 Learning history saved to {filepath}")
        except Exception as e:
            print(f"⚠️ Failed to save learning history: {e}")
    
    def load_learning_history(self, filepath: str = 'gemini_learning_history.json'):
        """Load learning history from file"""
        try:
            with open(filepath, 'r') as f:
                self.learning_history = json.load(f)
            print(f"📂 Loaded {len(self.learning_history)} learning entries")
        except FileNotFoundError:
            print(f"ℹ️ No learning history file found at {filepath}")
        except Exception as e:
            print(f"⚠️ Failed to load learning history: {e}")


# Singleton instance
_gemini_ai_instance = None

def get_gemini_ai(api_key: Optional[str] = None) -> GeminiSelectorAI:
    """Get or create Gemini AI singleton instance"""
    global _gemini_ai_instance
    if _gemini_ai_instance is None:
        _gemini_ai_instance = GeminiSelectorAI(api_key)
    return _gemini_ai_instance
