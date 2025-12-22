"""
Gemini AI Test Generator - Optional Enhancement
Adds natural language test generation without affecting existing code
"""

import os
import json
import re
from pathlib import Path

class GeminiTestGenerator:
    def __init__(self, api_key=None):
        """Initialize Gemini (optional - existing code works without it)"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.enabled = False
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                
                # Try different model names in order of preference (updated for 2025)
                model_names = [
                    'models/gemini-2.5-flash',
                    'models/gemini-2.0-flash',
                    'models/gemini-flash-latest',
                    'models/gemini-2.5-pro',
                    'models/gemini-pro-latest'
                ]
                
                model_loaded = False
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        # Test if model works
                        self.model.generate_content("test")
                        self.enabled = True
                        print(f"✅ Gemini AI enabled! (Using {model_name})")
                        model_loaded = True
                        break
                    except:
                        continue
                
                if not model_loaded:
                    print("ℹ️  Could not load Gemini model. Listing available models...")
                    try:
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                print(f"   Available: {m.name}")
                    except:
                        pass
                    print("   Your existing code still works perfectly!")
                    
            except ImportError:
                print("ℹ️  Gemini not available. Install: pip install google-generativeai")
                print("   Your existing code still works perfectly!")
            except Exception as e:
                print(f"ℹ️  Gemini setup skipped: {e}")
                print("   Your existing code still works perfectly!")
        else:
            print("ℹ️  Gemini not configured (optional feature)")
            print("   Your existing code works perfectly without it!")
    
    def generate_test_from_description(self, description, test_name=None):
        """
        Generate test from natural language description
        Falls back to manual mode if Gemini not available
        """
        if not self.enabled:
            print("\n⚠️  Gemini not available - use manual test creation")
            print("   Your existing text file method still works!")
            return None
        
        try:
            # Simpler, more focused prompt
            prompt = f"""Create a Playwright test for: {description}

Return ONLY a JSON object (no markdown, no code blocks) with this structure:
{{
  "name": "Test_Name",
  "description": "Brief description",
  "steps": [
    {{"action": "click", "selector": "button:has-text('Button')", "description": "Click button"}},
    {{"action": "fill", "selector": "input[name='field']", "value": "value", "description": "Fill field"}},
    {{"action": "wait", "value": "1", "description": "Wait"}}
  ]
}}

Actions: click, fill, select, wait
Selectors: Use button:has-text("Text") or input[name="field"]
Keep it simple and focused."""

            print("🤖 Generating test with Gemini AI...")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            response_text = response_text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                test_json = json.loads(json_match.group())
                
                # Set test name if provided
                if test_name:
                    test_json['name'] = test_name
                
                # Ensure steps exist
                if 'steps' not in test_json or not test_json['steps']:
                    print("⚠️  No steps generated")
                    return None
                
                print(f"✅ Generated {len(test_json.get('steps', []))} test steps")
                return test_json
            else:
                print("⚠️  Could not parse AI response")
                print(f"Response: {response_text[:200]}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed: {e}")
            print(f"Response: {response_text[:200]}")
            return None
        except Exception as e:
            print(f"⚠️  AI generation failed: {e}")
            return None
    
    def enhance_existing_test(self, test_steps):
        """
        Enhance existing test with better selectors and error handling
        Optional - doesn't modify original if Gemini unavailable
        """
        if not self.enabled:
            return test_steps  # Return original unchanged
        
        try:
            prompt = f"""Improve this test by adding:
1. Better error handling
2. More reliable selectors
3. Proper assertions
4. Better waits

Original test:
{json.dumps(test_steps, indent=2)}

Return improved test in same JSON format."""

            response = self.model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            
            if json_match:
                enhanced = json.loads(json_match.group())
                print("✅ Test enhanced with AI suggestions")
                return enhanced.get('steps', test_steps)
            else:
                return test_steps  # Return original if enhancement fails
                
        except:
            return test_steps  # Return original if error
    
    def suggest_selectors(self, element_description):
        """
        Suggest multiple selector options for an element
        Optional feature - doesn't affect existing code
        """
        if not self.enabled:
            # Fallback to basic selectors
            return [
                f'text={element_description}',
                f'button:has-text("{element_description}")',
                f'a:has-text("{element_description}")'
            ]
        
        try:
            prompt = f"""Generate 5 different Playwright selectors for: "{element_description}"

Return as JSON array:
["selector1", "selector2", "selector3", "selector4", "selector5"]

Use various strategies: text matching, CSS, XPath, ARIA, etc."""

            response = self.model.generate_content(prompt)
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            
            if json_match:
                selectors = json.loads(json_match.group())
                return selectors
            else:
                # Fallback to basic selectors
                return [
                    f'text={element_description}',
                    f'button:has-text("{element_description}")',
                    f'a:has-text("{element_description}")'
                ]
        except:
            # Fallback to basic selectors
            return [
                f'text={element_description}',
                f'button:has-text("{element_description}")',
                f'a:has-text("{element_description}")'
            ]


def get_gemini_generator(api_key=None):
    """Get Gemini generator instance (optional)"""
    return GeminiTestGenerator(api_key)


# Standalone script for natural language test generation
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("""
╔════════════════════════════════════════════════════════════╗
║  Gemini AI Test Generator (Optional Enhancement)          ║
╚════════════════════════════════════════════════════════════╝

Usage:
  python gemini_test_generator.py "Your test description"

Example:
  python gemini_test_generator.py "Test the login flow with valid credentials"

Setup (if not done):
  1. Get free API key: https://ai.google.dev/
  2. Set environment variable:
     $env:GEMINI_API_KEY = "your-key-here"

Note: Your existing test methods still work without Gemini!
      This is just an optional enhancement.
""")
        sys.exit(0)
    
    description = ' '.join(sys.argv[1:])
    
    print(f"\n{'='*60}")
    print(f"🤖 Gemini AI Test Generator")
    print(f"{'='*60}\n")
    
    generator = GeminiTestGenerator()
    
    if not generator.enabled:
        print("\n⚠️  Gemini not configured")
        print("\nTo enable AI test generation:")
        print("1. Get free API key: https://ai.google.dev/")
        print("2. Set: $env:GEMINI_API_KEY = 'your-key'")
        print("3. Install: pip install google-generativeai")
        print("\n✅ Your existing test methods still work perfectly!")
        sys.exit(1)
    
    test_json = generator.generate_test_from_description(description)
    
    if test_json:
        # Save to file
        test_name = test_json.get('name', 'Generated_Test')
        output_file = f"tests/{test_name}.json"
        
        Path("tests").mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(test_json, f, indent=2)
        
        print(f"\n✅ Test saved: {output_file}")
        print(f"📊 Steps: {len(test_json.get('steps', []))}")
        print(f"\nRun with:")
        print(f"  python run_tests_cli.py {output_file} --headless --batch")
        print(f"\nOr use your existing text file method - both work!")
    else:
        print("\n⚠️  AI generation failed")
        print("✅ Use your existing text file method instead!")
