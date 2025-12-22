"""
Quick script to check if Gemini AI is working
"""

import os
import sys


def check_gemini_status():
    """Check Gemini AI integration status"""
    
    print("=" * 70)
    print("  GEMINI AI STATUS CHECK")
    print("=" * 70)
    print()
    
    # Check 1: API Key
    print("1. Checking API Key...")
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"   ✅ API Key found: {api_key[:20]}...{api_key[-4:]}")
    else:
        print("   ❌ API Key NOT found")
        print("   → Set with: $env:GEMINI_API_KEY = 'your-key'")
        print()
    
    # Check 2: Package Installation
    print()
    print("2. Checking google-generativeai package...")
    try:
        import google.generativeai as genai
        print("   ✅ Package installed")
        
        # Try to configure
        if api_key:
            try:
                genai.configure(api_key=api_key)
                print("   ✅ API Key is valid")
                
                # Try to create model
                model = genai.GenerativeModel('gemini-pro')
                print("   ✅ Model initialized successfully")
                
                # Try a simple test
                print()
                print("3. Testing AI Response...")
                response = model.generate_content("Say 'Hello' in one word")
                print(f"   ✅ AI Response: {response.text.strip()}")
                print()
                print("=" * 70)
                print("  🎉 GEMINI AI IS FULLY WORKING!")
                print("=" * 70)
                return True
                
            except Exception as e:
                print(f"   ❌ API Error: {e}")
                print("   → Check if API key is valid")
                print("   → Check internet connection")
        else:
            print("   ⚠️  Cannot test without API key")
            
    except ImportError:
        print("   ❌ Package NOT installed")
        print("   → Install with: pip install google-generativeai")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 70)
    print("  ⚠️  GEMINI AI IS NOT WORKING")
    print("=" * 70)
    return False


def check_existing_integration():
    """Check if existing gemini_locator is working"""
    print()
    print("=" * 70)
    print("  CHECKING EXISTING INTEGRATION")
    print("=" * 70)
    print()
    
    try:
        from gemini_locator import GeminiLocatorGenerator
        
        locator = GeminiLocatorGenerator()
        
        if locator.enabled:
            print("✅ Existing gemini_locator.py is ENABLED")
            print(f"   Model: {locator.model._model_name if hasattr(locator, 'model') else 'N/A'}")
        else:
            print("❌ Existing gemini_locator.py is DISABLED")
            print("   Reason: API key not found or initialization failed")
            
    except ImportError:
        print("ℹ️  gemini_locator.py not found (using new integration)")
    except Exception as e:
        print(f"⚠️  Error checking existing integration: {e}")


def show_restart_instructions():
    """Show how to restart the server"""
    print()
    print("=" * 70)
    print("  HOW TO RESTART SERVER WITH GEMINI AI")
    print("=" * 70)
    print()
    print("Option 1: Use the startup script (Recommended)")
    print("-" * 70)
    print("  PowerShell:")
    print("    .\\start_server_with_gemini.ps1")
    print()
    print("  Command Prompt:")
    print("    start_server_with_gemini.bat")
    print()
    
    print("Option 2: Manual restart")
    print("-" * 70)
    print("  1. Stop current server (Ctrl+C in terminal)")
    print("  2. Set API key:")
    print("     $env:GEMINI_API_KEY = 'AIzaSyCPRLzHy2fmpjWX_n7odENX3K5U3hbUUnQ'")
    print("  3. Start server:")
    print("     python ui_real_test_server.py")
    print()
    
    print("Option 3: Set permanently (one-time)")
    print("-" * 70)
    print("  PowerShell (as Administrator):")
    print("    [System.Environment]::SetEnvironmentVariable(")
    print("      'GEMINI_API_KEY',")
    print("      'AIzaSyCPRLzHy2fmpjWX_n7odENX3K5U3hbUUnQ',")
    print("      'User'")
    print("    )")
    print("  Then restart your terminal/IDE")
    print()


def show_how_to_verify_in_ui():
    """Show how to verify in the UI"""
    print()
    print("=" * 70)
    print("  HOW TO VERIFY IN UI")
    print("=" * 70)
    print()
    print("After starting the server:")
    print()
    print("1. Open browser to: http://localhost:8888")
    print()
    print("2. Check server startup logs for:")
    print("   ✅ Google Gemini enabled!")
    print()
    print("3. In the UI, look for:")
    print("   • AI-suggested selectors")
    print("   • Gemini status indicator")
    print("   • Vision detection features")
    print()
    print("4. When a test runs, logs should show:")
    print("   🤖 Using Gemini AI to generate selectors...")
    print("   ✅ AI suggested: [selector]")
    print()


if __name__ == '__main__':
    # Run all checks
    is_working = check_gemini_status()
    check_existing_integration()
    show_restart_instructions()
    show_how_to_verify_in_ui()
    
    print()
    if is_working:
        print("🎉 You're all set! Gemini AI is ready to use.")
    else:
        print("⚠️  Follow the instructions above to enable Gemini AI.")
    print()
