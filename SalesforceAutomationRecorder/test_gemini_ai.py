"""
Test script to demonstrate Gemini AI integration
Run this to see AI-enhanced element finding in action
"""

import asyncio
import os
from gemini_enhanced_executor import GeminiEnhancedExecutor


async def test_basic_login():
    """Test basic login flow with AI assistance"""
    print("=" * 70)
    print("🤖 GEMINI AI-ENHANCED TEST EXECUTION")
    print("=" * 70)
    print()
    
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print("✅ Gemini API Key found")
    else:
        print("⚠️  No Gemini API Key found")
        print("   Set GEMINI_API_KEY environment variable to enable AI features")
        print("   Tests will run with traditional selectors only")
    print()
    
    # Initialize executor
    executor = GeminiEnhancedExecutor()
    
    # Define test
    url = "https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/"
    steps = [
        'Wait for 2 seconds',
        'Type "sarokiasamy2@dmigs.com.dcp.dcpuat" into "Username"',
        'Type "Grantee@123" into "Password"',
        'Click "Log in"',
        'Wait for 3 seconds',
        'Click "I Disagree"',
        'Click "Next"',
        'Wait for 2 seconds',
    ]
    
    print("📋 Test Configuration:")
    print(f"   URL: {url}")
    print(f"   Steps: {len(steps)}")
    print()
    
    # Execute test
    print("🚀 Starting test execution...")
    print()
    
    result = await executor.execute_test(url, steps, headless=False)
    
    # Print detailed report
    print()
    print(executor.get_report())
    
    # Print AI learning summary if available
    if executor.gemini_ai.is_available():
        print("\n🧠 AI LEARNING SUMMARY:")
        summary = executor.gemini_ai.get_learning_summary()
        print(f"   • Total AI Queries: {summary['total_queries']}")
        print(f"   • Cached Responses: {summary['cache_size']}")
        
        if summary['recent_queries']:
            print(f"\n   Recent AI Consultations:")
            for query in summary['recent_queries'][-3:]:
                print(f"   - {query['target']} ({query['action']})")
        
        # Save learning history
        executor.gemini_ai.save_learning_history()
        print("\n💾 Learning history saved to: gemini_learning_history.json")
    
    print("\n" + "=" * 70)
    print("✅ Test execution completed!")
    print("=" * 70)
    
    return result


async def test_difficult_elements():
    """Test with intentionally difficult elements to showcase AI"""
    print("\n" + "=" * 70)
    print("🎯 TESTING DIFFICULT ELEMENTS (AI Showcase)")
    print("=" * 70)
    print()
    
    executor = GeminiEnhancedExecutor()
    
    # Test with Google search (complex dynamic elements)
    url = "https://www.google.com"
    steps = [
        'Wait for 2 seconds',
        'Type "Playwright automation" into "Search"',
        'Wait for 1 seconds',
        'Click "Google Search"',
        'Wait for 3 seconds',
    ]
    
    print("📋 Testing Google Search (complex dynamic elements)")
    print()
    
    result = await executor.execute_test(url, steps, headless=False)
    
    print()
    print(executor.get_report())
    
    return result


async def demo_ai_features():
    """Demonstrate specific AI features"""
    print("\n" + "=" * 70)
    print("🔬 AI FEATURES DEMONSTRATION")
    print("=" * 70)
    print()
    
    from gemini_selector_ai import get_gemini_ai
    
    ai = get_gemini_ai()
    
    if not ai.is_available():
        print("⚠️  Gemini AI not available. Set GEMINI_API_KEY to see this demo.")
        return
    
    # Demo 1: Alternative descriptions
    print("Demo 1: Alternative Element Descriptions")
    print("-" * 70)
    
    sample_html = """
    <div class="login-form">
        <button class="btn-primary">Sign In</button>
        <button class="btn-secondary">Create Account</button>
    </div>
    """
    
    alternatives = await ai.suggest_alternative_descriptions(
        "Login Button",
        sample_html
    )
    
    print(f"Original: 'Login Button'")
    print(f"AI Suggestions: {alternatives}")
    print()
    
    # Demo 2: Selector analysis
    print("\nDemo 2: AI Selector Analysis")
    print("-" * 70)
    
    result = await ai.analyze_page_and_suggest_selectors(
        target_description="Submit button",
        page_html=sample_html,
        action_type='click'
    )
    
    print(f"Target: 'Submit button'")
    print(f"AI Reasoning: {result.get('reasoning', 'N/A')}")
    print(f"\nTop 3 Suggestions:")
    for i, suggestion in enumerate(result['selectors'][:3], 1):
        print(f"  {i}. {suggestion['selector']}")
        print(f"     Strategy: {suggestion['strategy']}")
        print(f"     Confidence: {suggestion['confidence']:.0%}")
    print()


async def main():
    """Run all tests"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     GEMINI AI-ENHANCED AUTOMATION TEST SUITE                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Check prerequisites
    print("🔍 Checking Prerequisites...")
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package installed")
    except ImportError:
        print("❌ google-generativeai package not found")
        print("   Run: pip install google-generativeai")
        return
    
    try:
        from playwright.async_api import async_playwright
        print("✅ playwright package installed")
    except ImportError:
        print("❌ playwright package not found")
        print("   Run: pip install playwright")
        print("   Then: playwright install")
        return
    
    print()
    
    # Run tests
    try:
        # Test 1: Basic login
        await test_basic_login()
        
        # Test 2: Difficult elements (optional)
        # Uncomment to test with Google search
        # await test_difficult_elements()
        
        # Demo AI features
        await demo_ai_features()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
