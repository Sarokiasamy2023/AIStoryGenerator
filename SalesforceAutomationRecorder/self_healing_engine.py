"""
Self-Healing Test Execution Engine
Automatically detects and fixes broken selectors during test execution
"""

import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from ai_selector_engine import get_selector_engine


class SelfHealingEngine:
    """
    Automatically heals broken selectors by finding similar elements
    Uses AI-powered similarity matching and DOM analysis
    """
    
    def __init__(self, storage_path: str = "healing_history.json"):
        self.storage_path = storage_path
        self.healing_history = []
        self.selector_engine = get_selector_engine()
        self.dom_cache = {}
        self.healing_stats = defaultdict(int)
        self.load_history()
    
    def load_history(self):
        """Load healing history from disk"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.healing_history = data.get('history', [])
                self.healing_stats = defaultdict(int, data.get('stats', {}))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️ Could not load healing history: {e}")
    
    def save_history(self):
        """Save healing history to disk"""
        try:
            data = {
                'history': self.healing_history[-1000:],  # Keep last 1000 entries
                'stats': dict(self.healing_stats),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save healing history: {e}")
    
    async def heal_selector(
        self,
        page,
        old_selector: str,
        element_context: Dict,
        max_attempts: int = 10
    ) -> Optional[Dict]:
        """
        Attempt to heal a broken selector
        
        Args:
            page: Playwright page object
            old_selector: The selector that failed
            element_context: Context about the element (text, type, etc.)
            max_attempts: Maximum healing attempts
            
        Returns:
            Dictionary with new selector and healing metadata, or None if healing failed
        """
        print(f"🔧 Attempting to heal selector: {old_selector}")
        start_time = time.time()
        
        try:
            # Get current page DOM
            current_dom = await self._capture_dom(page)
            
            # Parse DOM to extract all elements
            current_elements = await self._parse_dom_elements(page)
            
            if not current_elements:
                print("⚠️ No elements found in current DOM")
                return None
            
            # Find best matching element
            best_match = await self._find_best_match(
                element_context,
                current_elements,
                old_selector
            )
            
            if not best_match:
                print("❌ No suitable replacement element found")
                self.healing_stats['failed'] += 1
                return None
            
            # Generate new selector for matched element
            new_selector_result = self.selector_engine.generate_selectors(
                best_match['element_data']
            )
            
            if not new_selector_result['selectors']:
                print("❌ Could not generate new selector")
                self.healing_stats['failed'] += 1
                return None
            
            # Get best new selector
            new_selector = new_selector_result['selectors'][0]['selector']
            
            # Verify new selector works
            try:
                element = await page.wait_for_selector(new_selector, timeout=2000)
                if not element:
                    raise Exception("Selector verification failed")
            except Exception as e:
                print(f"⚠️ New selector verification failed: {e}")
                # Try next best selector
                if len(new_selector_result['selectors']) > 1:
                    new_selector = new_selector_result['selectors'][1]['selector']
                else:
                    self.healing_stats['failed'] += 1
                    return None
            
            # Record successful healing
            healing_time = time.time() - start_time
            healing_record = {
                'timestamp': datetime.now().isoformat(),
                'old_selector': old_selector,
                'new_selector': new_selector,
                'confidence': best_match['similarity'],
                'healing_method': best_match['method'],
                'healing_time_ms': round(healing_time * 1000, 2),
                'element_context': element_context,
                'success': True
            }
            
            self.healing_history.append(healing_record)
            self.healing_stats['success'] += 1
            self.healing_stats['total_time_ms'] += healing_time * 1000
            self.save_history()
            
            print(f"✅ Selector healed successfully in {healing_time:.2f}s")
            print(f"   Old: {old_selector}")
            print(f"   New: {new_selector}")
            print(f"   Confidence: {best_match['similarity']:.2%}")
            
            return healing_record
            
        except Exception as e:
            print(f"❌ Healing failed with error: {e}")
            self.healing_stats['failed'] += 1
            return None
    
    async def _capture_dom(self, page) -> str:
        """Capture current page DOM"""
        try:
            dom = await page.content()
            return dom
        except Exception as e:
            print(f"⚠️ DOM capture failed: {e}")
            return ""
    
    async def _parse_dom_elements(self, page) -> List[Dict]:
        """
        Parse DOM and extract all interactive elements
        
        Returns:
            List of element data dictionaries
        """
        try:
            # JavaScript to extract all interactive elements
            js_code = """
            () => {
                const elements = [];
                const selectors = [
                    'input', 'button', 'a', 'select', 'textarea',
                    '[role="button"]', '[role="link"]', '[role="textbox"]',
                    'lightning-input', 'lightning-button', 'lightning-combobox',
                    '[data-omnistudio-field]', '[class*="slds-"]'
                ];
                
                const allElements = document.querySelectorAll(selectors.join(','));
                
                allElements.forEach((el, index) => {
                    const rect = el.getBoundingClientRect();
                    
                    // Only include visible elements
                    if (rect.width > 0 && rect.height > 0) {
                        const attrs = {};
                        for (let attr of el.attributes) {
                            attrs[attr.name] = attr.value;
                        }
                        
                        elements.push({
                            tagName: el.tagName.toLowerCase(),
                            innerText: el.innerText?.substring(0, 200) || '',
                            attributes: attrs,
                            position: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height
                            },
                            index: index
                        });
                    }
                });
                
                return elements;
            }
            """
            
            elements = await page.evaluate(js_code)
            return elements
            
        except Exception as e:
            print(f"⚠️ DOM parsing failed: {e}")
            return []
    
    async def _find_best_match(
        self,
        element_context: Dict,
        current_elements: List[Dict],
        old_selector: str
    ) -> Optional[Dict]:
        """
        Find the best matching element from current DOM
        
        Args:
            element_context: Original element context
            current_elements: List of current page elements
            old_selector: The failed selector
            
        Returns:
            Best match with similarity score and method
        """
        if not self.selector_engine.model:
            # Fallback to rule-based matching
            return self._rule_based_matching(element_context, current_elements)
        
        try:
            # Extract context text
            context_text = self._extract_context_text(element_context)
            
            # Generate embedding for target element
            target_embedding = self.selector_engine.model.encode(context_text)
            
            # Calculate similarity for all current elements
            matches = []
            for element in current_elements:
                element_text = self.selector_engine._extract_element_text(element)
                
                if not element_text:
                    continue
                
                # Generate embedding
                element_embedding = self.selector_engine.model.encode(element_text)
                
                # Calculate similarity
                similarity = cosine_similarity(
                    [target_embedding],
                    [element_embedding]
                )[0][0]
                
                # Additional scoring factors
                type_match = element.get('tagName') == element_context.get('element_type')
                structural_score = self._calculate_structural_similarity(
                    element_context,
                    element
                )
                
                # Combined score
                combined_score = (
                    similarity * 0.6 +
                    (1.0 if type_match else 0.5) * 0.2 +
                    structural_score * 0.2
                )
                
                matches.append({
                    'element_data': element,
                    'similarity': float(combined_score),
                    'semantic_similarity': float(similarity),
                    'type_match': type_match,
                    'method': 'ai_semantic'
                })
            
            # Sort by similarity
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return best match if confidence is high enough
            if matches and matches[0]['similarity'] >= 0.75:
                return matches[0]
            
            # Try rule-based as fallback
            print("⚠️ AI matching confidence too low, trying rule-based")
            return self._rule_based_matching(element_context, current_elements)
            
        except Exception as e:
            print(f"⚠️ AI matching failed: {e}, falling back to rules")
            return self._rule_based_matching(element_context, current_elements)
    
    def _rule_based_matching(
        self,
        element_context: Dict,
        current_elements: List[Dict]
    ) -> Optional[Dict]:
        """
        Fallback rule-based matching when AI is not available
        """
        context_text = self._extract_context_text(element_context).lower()
        context_type = element_context.get('element_type', '').lower()
        
        best_match = None
        best_score = 0
        
        for element in current_elements:
            score = 0
            element_text = self.selector_engine._extract_element_text(element).lower()
            element_type = element.get('tagName', '').lower()
            
            # Type match
            if element_type == context_type:
                score += 0.3
            
            # Text similarity (simple word overlap)
            context_words = set(context_text.split())
            element_words = set(element_text.split())
            
            if context_words and element_words:
                overlap = len(context_words & element_words)
                total = len(context_words | element_words)
                score += (overlap / total) * 0.5 if total > 0 else 0
            
            # Attribute matching
            attrs = element.get('attributes', {})
            for key in ['name', 'placeholder', 'aria-label', 'title']:
                if key in attrs and context_text in attrs[key].lower():
                    score += 0.2
            
            if score > best_score:
                best_score = score
                best_match = {
                    'element_data': element,
                    'similarity': score,
                    'method': 'rule_based'
                }
        
        if best_match and best_score >= 0.5:
            return best_match
        
        return None
    
    def _calculate_structural_similarity(
        self,
        element_context: Dict,
        current_element: Dict
    ) -> float:
        """
        Calculate structural similarity between elements
        Based on attributes, position, etc.
        """
        score = 0.0
        
        # Compare attributes
        context_attrs = element_context.get('attributes', {})
        current_attrs = current_element.get('attributes', {})
        
        # Check for matching data attributes
        for key in context_attrs:
            if key.startswith('data-') and key in current_attrs:
                if context_attrs[key] == current_attrs[key]:
                    score += 0.3
                else:
                    score += 0.1
        
        # Check for matching classes
        if 'class' in context_attrs and 'class' in current_attrs:
            context_classes = set(context_attrs['class'].split())
            current_classes = set(current_attrs['class'].split())
            
            overlap = len(context_classes & current_classes)
            if overlap > 0:
                score += min(overlap * 0.1, 0.3)
        
        return min(score, 1.0)
    
    def _extract_context_text(self, element_context: Dict) -> str:
        """Extract meaningful text from element context"""
        text_parts = []
        
        if 'element_text' in element_context:
            text_parts.append(element_context['element_text'])
        
        if 'label' in element_context:
            text_parts.append(element_context['label'])
        
        if 'attributes' in element_context:
            attrs = element_context['attributes']
            for key in ['aria-label', 'placeholder', 'title', 'name']:
                if key in attrs:
                    text_parts.append(attrs[key])
        
        return ' '.join(text_parts).strip()
    
    def get_healing_statistics(self) -> Dict:
        """Get healing performance statistics"""
        total = self.healing_stats['success'] + self.healing_stats['failed']
        
        return {
            'total_healing_attempts': total,
            'successful_healings': self.healing_stats['success'],
            'failed_healings': self.healing_stats['failed'],
            'success_rate': round(
                (self.healing_stats['success'] / total * 100) if total > 0 else 0,
                2
            ),
            'average_healing_time_ms': round(
                (self.healing_stats['total_time_ms'] / self.healing_stats['success'])
                if self.healing_stats['success'] > 0 else 0,
                2
            ),
            'recent_healings': len(self.healing_history),
            'last_healing': self.healing_history[-1] if self.healing_history else None
        }
    
    def get_healing_suggestions(
        self,
        test_steps: List[Dict]
    ) -> List[Dict]:
        """
        Analyze test steps and suggest potential improvements
        based on healing history
        """
        suggestions = []
        
        for step in test_steps:
            selector = step.get('selector', '')
            
            # Check if this selector has been healed before
            healed_versions = [
                h for h in self.healing_history
                if h['old_selector'] == selector
            ]
            
            if healed_versions:
                most_recent = healed_versions[-1]
                suggestions.append({
                    'step': step,
                    'current_selector': selector,
                    'suggested_selector': most_recent['new_selector'],
                    'reason': 'Previously healed selector',
                    'confidence': most_recent['confidence'],
                    'last_healed': most_recent['timestamp']
                })
        
        return suggestions
    
    def export_healing_report(self, filepath: str):
        """Export detailed healing report"""
        report = {
            'statistics': self.get_healing_statistics(),
            'healing_history': self.healing_history[-100:],  # Last 100
            'generated_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Healing report exported to {filepath}")


# Singleton instance
_healing_engine = None

def get_healing_engine() -> SelfHealingEngine:
    """Get or create SelfHealingEngine instance"""
    global _healing_engine
    if _healing_engine is None:
        _healing_engine = SelfHealingEngine()
    return _healing_engine
