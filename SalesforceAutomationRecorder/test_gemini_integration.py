#!/usr/bin/env python3
"""
Test Google Gemini API Integration
Demo script to test Gemini locator generation with vision detection
"""

import os
import sys
from pathlib import Path

def test_gemini_integration():
    """Test Gemini API integration for selector generation"""
    print("="*60)
    print("  🤖 Testing Google Gemini API Integration")
    print("="*60)
    print()
    
    # Check API key - set it automatically if not found
    if not os.getenv('GEMINI_API_KEY'):
        print("🔧 Setting API key automatically...")
        os.environ['GEMINI_API_KEY'] = "AIzaSyCPRLzHy2fmpjWX_n7odENX3K5U3hbUUnQ"
        print("✅ API key set for this session")
        print()
    
    try:
        # Import and test Gemini locator
        from gemini_locator import get_gemini_locator
        locator = get_gemini_locator()
        
        if not locator.enabled:
            print("❌ Gemini failed to initialize!")
            return False
        
        print("✅ Gemini API connected successfully!")
        print()
        
        # Test 1: Text-based selector generation
        print("🧪 Test 1: Text-based selector generation")
        print("-" * 50)
        test_cases = [
            ("click", "Login button"),
            ("fill", "Username field"),
            ("click", "Save button"),
            ("select", "Country dropdown"),
        ]
        
        for action, description in test_cases:
            print(f"\n📍 Testing: {action} -> '{description}'")
            selectors = locator.generate_selector(action, description)
            
            if selectors and len(selectors) > 0:
                print(f"✅ Generated {len(selectors)} selectors:")
                for i, selector in enumerate(selectors[:3], 1):
                    print(f"   {i}. {selector}")
                if len(selectors) > 3:
                    print(f"   ... and {len(selectors) - 3} more")
            else:
                print("❌ No selectors generated")
        
        print()
        
        # Test 2: Vision-based selector generation (if we have a screenshot)
        print("🧪 Test 2: Vision-based selector generation")
        print("-" * 50)
        
        # Check for any existing screenshots
        screenshot_files = list(Path("test_videos").glob("*.png")) + list(Path(".").glob("*.png"))
        
        if screenshot_files:
            screenshot_path = screenshot_files[0]
            print(f"📸 Using screenshot: {screenshot_path}")
            
            selectors = locator.generate_selector(
                "click", "Submit button", 
                screenshot_path=str(screenshot_path)
            )
            
            if selectors and len(selectors) > 0:
                print(f"✅ Vision mode generated {len(selectors)} selectors:")
                for i, selector in enumerate(selectors[:3], 1):
                    print(f"   {i}. {selector}")
            else:
                print("❌ Vision mode failed")
        else:
            print("ℹ️ No screenshots found for vision test")
            print("   Vision detection will work when you run actual tests")
        
        print()
        
        # Test 3: Salesforce-specific selectors
        print("🧪 Test 3: Salesforce Lightning selectors")
        print("-" * 50)
        
        salesforce_cases = [
            ("click", "New button in Salesforce"),
            ("fill", "Account Name field"),
            ("click", "Save button in lightning component"),
        ]
        
        for action, description in salesforce_cases:
            print(f"\n📍 Salesforce: {action} -> '{description}'")
            selectors = locator.generate_selector(
                action, description, 
                page_context="Salesforce Lightning Web Component"
            )
            
            if selectors and len(selectors) > 0:
                print(f"✅ Generated {len(selectors)} selectors:")
                for i, selector in enumerate(selectors[:2], 1):
                    print(f"   {i}. {selector}")
            else:
                print("❌ No selectors generated")
        
        print()
        print("🎉 All tests completed!")
        print()
        print("📊 Usage Statistics:")
        print(f"   • FREE tier: 1,500 requests/day")
        print(f"   • Rate limit: 60 requests/minute") 
        print(f"   • Vision detection: ✅ Included")
        print(f"   • Response time: ~1-2 seconds")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Run: pip install google-generativeai")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_ui_integration():
    """Test integration with test_builder_ui.py"""
    print("\n" + "="*60)
    print("  🌐 Testing UI Integration")
    print("="*60)
    print()
    
    try:
        # Import the UI module
        import test_builder_ui
        
        # Check if Gemini locator is initialized
        if hasattr(test_builder_ui, 'gemini_locator'):
            locator = test_builder_ui.gemini_locator
            if locator.enabled:
                print("✅ Gemini locator is integrated in UI!")
                print("   Start the UI server with:")
                print("   python test_builder_ui.py")
                print("   Then open: http://localhost:5000")
                return True
            else:
                print("⚠️ Gemini locator integrated but not enabled")
                return False
        else:
            print("❌ Gemini locator not found in UI module")
            return False
            
    except Exception as e:
        print(f"❌ UI integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Gemini API Integration Tests...")
    print()
    
    # Test core functionality
    success = test_gemini_integration()
    
    if success:
        # Test UI integration
        test_ui_integration()
        
        print("\n" + "="*60)
        print("  🎯 Next Steps")
        print("="*60)
        print()
        print("1. Start the web interface:")
        print("   python test_builder_ui.py")
        print()
        print("2. Open browser to: http://localhost:5000")
        print()
        print("3. Create a test and see Gemini in action!")
        print()
        print("4. Check your API usage at:")
        print("   https://makersuite.google.com/app/apikey")
        
    else:
        print("\n❌ Integration tests failed. Please check setup.")
