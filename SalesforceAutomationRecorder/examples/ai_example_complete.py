"""
Complete AI-Powered Test Example
Demonstrates all AI features: selector generation, self-healing, and learning
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_test_runner import EnhancedTestRunner
from ai_selector_engine import get_selector_engine
from learning_feedback_system import get_learning_system
from self_healing_engine import get_healing_engine


async def demo_selector_generation():
    """Demo: Generate intelligent selectors"""
    print("\n" + "="*60)
    print("DEMO 1: Intelligent Selector Generation")
    print("="*60)
    
    engine = get_selector_engine()
    
    # Example 1: Email input
    print("\n📧 Email Input Field:")
    email_element = {
        'tagName': 'input',
        'innerText': '',
        'attributes': {
            'type': 'email',
            'name': 'email',
            'placeholder': 'Enter your email',
            'class': 'form-control email-input',
            'aria-label': 'Email address'
        }
    }
    
    result = engine.generate_selectors(email_element)
    print(f"Generated {len(result['selectors'])} selectors:\n")
    
    for i, sel in enumerate(result['selectors'][:5], 1):
        print(f"{i}. {sel['selector']}")
        print(f"   Strategy: {sel['strategy']}, Confidence: {sel['confidence']:.1%}\n")
    
    # Example 2: Lightning button
    print("\n⚡ Salesforce Lightning Button:")
    lightning_button = {
        'tagName': 'lightning-button',
        'innerText': 'Save',
        'attributes': {
            'class': 'slds-button slds-button_brand',
            'data-field': 'save-button',
            'label': 'Save'
        }
    }
    
    result = engine.generate_selectors(lightning_button, page_context="Salesforce Lightning")
    print(f"Generated {len(result['selectors'])} selectors:\n")
    
    for i, sel in enumerate(result['selectors'][:5], 1):
        print(f"{i}. {sel['selector']}")
        print(f"   Strategy: {sel['strategy']}, Confidence: {sel['confidence']:.1%}\n")


async def demo_self_healing_test():
    """Demo: Self-healing test execution"""
    print("\n" + "="*60)
    print("DEMO 2: Self-Healing Test Execution")
    print("="*60)
    
    runner = EnhancedTestRunner(
        headless=False,
        enable_healing=True,
        enable_learning=True
    )
    
    try:
        print("\n🌐 Starting browser...")
        await runner.start("https://www.google.com")
        
        # Test 1: Search box (should work)
        print("\n✅ Test 1: Working selector")
        await runner.smart_fill(
            "textarea[name='q']",
            "Playwright automation",
            element_context={
                'element_text': 'Search',
                'element_type': 'textarea',
                'attributes': {'name': 'q', 'title': 'Search'}
            }
        )
        
        await asyncio.sleep(1)
        
        # Test 2: Simulate broken selector (will trigger healing)
        print("\n🔧 Test 2: Broken selector (will attempt healing)")
        await runner.smart_click(
            "button.old-search-button",  # This doesn't exist
            element_context={
                'element_text': 'Google Search',
                'element_type': 'button',
                'attributes': {'name': 'btnK'}
            }
        )
        
        await asyncio.sleep(2)
        
        # Take screenshot
        await runner.take_screenshot("demo_result.png")
        
    finally:
        await runner.stop()


async def demo_learning_feedback():
    """Demo: Learning from feedback"""
    print("\n" + "="*60)
    print("DEMO 3: Learning System & Feedback")
    print("="*60)
    
    learning = get_learning_system()
    
    # Simulate user corrections
    print("\n📝 Recording user feedback...")
    
    feedback_examples = [
        {
            'incorrect': 'button.submit',
            'correct': 'button[data-action="submit"]',
            'element': {
                'tagName': 'button',
                'innerText': 'Submit',
                'attributes': {'data-action': 'submit'}
            },
            'reason': 'Data attributes are more stable'
        },
        {
            'incorrect': 'input.email',
            'correct': 'input[name="email"]',
            'element': {
                'tagName': 'input',
                'innerText': '',
                'attributes': {'name': 'email', 'type': 'email'}
            },
            'reason': 'Name attribute is more reliable'
        },
        {
            'incorrect': 'div.modal button:nth-child(2)',
            'correct': 'button[aria-label="Confirm"]',
            'element': {
                'tagName': 'button',
                'innerText': 'Confirm',
                'attributes': {'aria-label': 'Confirm'}
            },
            'reason': 'ARIA labels provide better accessibility'
        }
    ]
    
    for i, feedback in enumerate(feedback_examples, 1):
        print(f"\n{i}. Recording correction:")
        print(f"   ❌ Incorrect: {feedback['incorrect']}")
        print(f"   ✅ Correct: {feedback['correct']}")
        
        result = learning.record_feedback(
            feedback['incorrect'],
            feedback['correct'],
            feedback['element'],
            reason=feedback['reason']
        )
        
        print(f"   💡 Learned: {result['learning_insights']['key_insight']}")
    
    # Show statistics
    print("\n" + "-"*60)
    print("📊 Learning Statistics:")
    print("-"*60)
    
    stats = learning.get_learning_statistics()
    print(f"Total feedback records: {stats['total_feedback_records']}")
    print(f"Patterns learned: {stats['pattern_library']['total_patterns']}")
    print(f"Average confidence: {stats['pattern_library']['average_confidence']:.2%}")
    
    # Get improvement suggestions
    print("\n" + "-"*60)
    print("💡 Improvement Suggestions:")
    print("-"*60)
    
    suggestions = learning.get_improvement_suggestions()
    if suggestions:
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"\n{i}. {suggestion['type'].upper()}")
            print(f"   Priority: {suggestion['priority']}")
            print(f"   Selector: {suggestion['selector']}")
            print(f"   Reason: {suggestion['reason']}")
    else:
        print("No suggestions yet (need more data)")


async def demo_similarity_search():
    """Demo: Find similar elements"""
    print("\n" + "="*60)
    print("DEMO 4: Similarity Search")
    print("="*60)
    
    engine = get_selector_engine()
    
    # First, add some elements to the database
    print("\n📥 Adding sample elements to database...")
    
    sample_elements = [
        {
            'tagName': 'input',
            'innerText': '',
            'attributes': {
                'type': 'email',
                'placeholder': 'Email Address',
                'name': 'user_email'
            }
        },
        {
            'tagName': 'input',
            'innerText': '',
            'attributes': {
                'type': 'email',
                'placeholder': 'Your Email',
                'name': 'email'
            }
        },
        {
            'tagName': 'input',
            'innerText': '',
            'attributes': {
                'type': 'text',
                'placeholder': 'Username',
                'name': 'username'
            }
        }
    ]
    
    for elem in sample_elements:
        engine.generate_selectors(elem)
    
    print(f"Added {len(sample_elements)} elements")
    
    # Now search for similar elements
    print("\n🔍 Searching for similar email inputs...")
    
    query_element = {
        'tagName': 'input',
        'innerText': '',
        'attributes': {
            'type': 'email',
            'placeholder': 'Enter email',
            'name': 'contact_email'
        }
    }
    
    similar = engine.find_similar_elements(query_element, threshold=0.7)
    
    if similar:
        print(f"\nFound {len(similar)} similar elements:\n")
        for i, match in enumerate(similar, 1):
            print(f"{i}. Similarity: {match['similarity']:.1%}")
            print(f"   Element: {match['element_data']['tagName']}")
            attrs = match['element_data'].get('attributes', {})
            print(f"   Placeholder: {attrs.get('placeholder', 'N/A')}")
            print()
    else:
        print("No similar elements found (AI model may not be loaded)")


async def demo_healing_statistics():
    """Demo: View healing statistics"""
    print("\n" + "="*60)
    print("DEMO 5: Healing Statistics")
    print("="*60)
    
    healing = get_healing_engine()
    
    stats = healing.get_healing_statistics()
    
    print("\n📊 Self-Healing Performance:")
    print(f"   Total attempts: {stats['total_healing_attempts']}")
    print(f"   Successful: {stats['successful_healings']}")
    print(f"   Failed: {stats['failed_healings']}")
    print(f"   Success rate: {stats['success_rate']}%")
    print(f"   Avg healing time: {stats['average_healing_time_ms']:.0f}ms")
    
    if stats['last_healing']:
        print(f"\n🔧 Last Healing Action:")
        last = stats['last_healing']
        print(f"   Time: {last['timestamp']}")
        print(f"   Old selector: {last['old_selector']}")
        print(f"   New selector: {last['new_selector']}")
        print(f"   Confidence: {last['confidence']:.1%}")


async def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("AI-POWERED TEST AUTOMATION - COMPLETE DEMO")
    print("="*60)
    
    demos = [
        ("Selector Generation", demo_selector_generation),
        ("Self-Healing Test", demo_self_healing_test),
        ("Learning & Feedback", demo_learning_feedback),
        ("Similarity Search", demo_similarity_search),
        ("Healing Statistics", demo_healing_statistics)
    ]
    
    for name, demo_func in demos:
        try:
            await demo_func()
            await asyncio.sleep(1)
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETED")
    print("="*60)
    
    print("\n📚 Next Steps:")
    print("1. Review generated selectors and healing logs")
    print("2. Check learning_feedback.db for stored patterns")
    print("3. View healing_history.json for healing actions")
    print("4. Integrate into your test suite")
    print("5. Start MCP server: python mcp_server.py --http")


if __name__ == "__main__":
    asyncio.run(main())
