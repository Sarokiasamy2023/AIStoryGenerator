"""
AI-Powered Selector Intelligence Engine
Generates, learns, and optimizes UI element selectors using ML/NLP
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import hashlib

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ sentence-transformers not installed. Run: pip install sentence-transformers")


class SelectorIntelligenceEngine:
    """
    AI-powered selector generation and learning system
    Uses semantic embeddings to understand UI elements
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with a lightweight sentence transformer model
        
        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2 - 80MB, fast)
        """
        self.model_name = model_name
        self.model = None
        self.selector_cache = {}
        self.element_embeddings = {}
        self.selector_success_rates = defaultdict(lambda: {'success': 0, 'failure': 0})
        
        if TRANSFORMERS_AVAILABLE:
            try:
                print(f"🤖 Loading AI model: {model_name}...")
                self.model = SentenceTransformer(model_name)
                print(f"✅ AI Selector Engine initialized!")
            except Exception as e:
                print(f"⚠️ Could not load model: {e}")
                self.model = None
        else:
            print("ℹ️ Running in fallback mode without AI features")
    
    def generate_selectors(
        self,
        element_data: Dict,
        page_context: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate multiple selector strategies with confidence scores
        
        Args:
            element_data: DOM element information
            page_context: Optional page/app context
            
        Returns:
            Dictionary with ranked selectors and metadata
        """
        # Extract element features
        element_text = self._extract_element_text(element_data)
        element_type = element_data.get('tagName', '').lower()
        attributes = element_data.get('attributes', {})
        
        # Generate semantic embedding
        embedding = None
        if self.model:
            try:
                semantic_text = f"{element_text} {element_type} {' '.join(attributes.values())}"
                embedding = self.model.encode(semantic_text)
            except Exception as e:
                print(f"⚠️ Embedding generation failed: {e}")
        
        # Generate multiple selector strategies
        selectors = {
            'css': self._generate_css_selectors(element_data),
            'xpath': self._generate_xpath_selectors(element_data),
            'semantic': self._generate_semantic_selectors(element_data),
            'aria': self._generate_aria_selectors(element_data),
            'visual': self._generate_visual_selectors(element_data),
            'salesforce': self._generate_salesforce_selectors(element_data)
        }
        
        # Flatten and rank all selectors
        all_selectors = []
        for strategy, selector_list in selectors.items():
            for selector in selector_list:
                all_selectors.append({
                    'selector': selector,
                    'strategy': strategy,
                    'confidence': self._calculate_confidence(selector, element_data, strategy)
                })
        
        # Sort by confidence
        all_selectors.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Store embedding for future similarity matching
        element_id = self._generate_element_id(element_data)
        if embedding is not None:
            self.element_embeddings[element_id] = {
                'embedding': embedding,
                'element_data': element_data,
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'selectors': all_selectors[:15],  # Top 15 selectors
            'element_id': element_id,
            'embedding': embedding.tolist() if embedding is not None else None,
            'element_text': element_text,
            'element_type': element_type
        }
    
    def _generate_css_selectors(self, element_data: Dict) -> List[str]:
        """Generate CSS selector strategies"""
        selectors = []
        tag = element_data.get('tagName', '').lower()
        attrs = element_data.get('attributes', {})
        text = element_data.get('innerText', '').strip()
        
        # ID-based (highest priority)
        if 'id' in attrs:
            selectors.append(f"#{attrs['id']}")
        
        # Name attribute
        if 'name' in attrs:
            selectors.append(f"{tag}[name='{attrs['name']}']")
            selectors.append(f"[name='{attrs['name']}']")
        
        # Placeholder
        if 'placeholder' in attrs:
            selectors.append(f"{tag}[placeholder='{attrs['placeholder']}']")
            selectors.append(f"{tag}[placeholder*='{attrs['placeholder']}' i]")
        
        # Data attributes
        for key, value in attrs.items():
            if key.startswith('data-'):
                selectors.append(f"{tag}[{key}='{value}']")
                selectors.append(f"[{key}='{value}']")
        
        # Class-based
        if 'class' in attrs:
            classes = attrs['class'].split()
            if classes:
                # Single most specific class
                selectors.append(f"{tag}.{classes[0]}")
                # All classes
                selectors.append(f"{tag}.{'.'.join(classes)}")
        
        # Type attribute (for inputs)
        if 'type' in attrs:
            selectors.append(f"{tag}[type='{attrs['type']}']")
        
        # ARIA attributes
        if 'aria-label' in attrs:
            selectors.append(f"{tag}[aria-label='{attrs['aria-label']}']")
            selectors.append(f"[aria-label*='{attrs['aria-label']}' i]")
        
        # Text content
        if text and len(text) < 50:
            selectors.append(f"{tag}:has-text('{text}')")
            selectors.append(f"text='{text}'")
        
        return selectors
    
    def _generate_xpath_selectors(self, element_data: Dict) -> List[str]:
        """Generate XPath selector strategies"""
        selectors = []
        tag = element_data.get('tagName', '').lower()
        attrs = element_data.get('attributes', {})
        text = element_data.get('innerText', '').strip()
        
        # ID-based
        if 'id' in attrs:
            selectors.append(f"//{tag}[@id='{attrs['id']}']")
        
        # Name-based
        if 'name' in attrs:
            selectors.append(f"//{tag}[@name='{attrs['name']}']")
        
        # Text-based
        if text and len(text) < 50:
            selectors.append(f"//{tag}[text()='{text}']")
            selectors.append(f"//{tag}[contains(text(), '{text}')]")
        
        # Placeholder
        if 'placeholder' in attrs:
            selectors.append(f"//{tag}[@placeholder='{attrs['placeholder']}']")
        
        # Following sibling (for label + input patterns)
        if 'aria-label' in attrs or 'placeholder' in attrs:
            label_text = attrs.get('aria-label', attrs.get('placeholder', ''))
            selectors.append(f"//label[contains(text(), '{label_text}')]/following::input[1]")
            selectors.append(f"//label[contains(text(), '{label_text}')]/following-sibling::input[1]")
        
        # Data attributes
        for key, value in attrs.items():
            if key.startswith('data-'):
                selectors.append(f"//{tag}[@{key}='{value}']")
        
        return selectors
    
    def _generate_semantic_selectors(self, element_data: Dict) -> List[str]:
        """Generate semantic/text-based selectors"""
        selectors = []
        text = element_data.get('innerText', '').strip()
        attrs = element_data.get('attributes', {})
        
        # Playwright text selectors
        if text and len(text) < 100:
            selectors.append(f"text={text}")
            selectors.append(f"text=/{re.escape(text)}/i")
            
            # Partial text match
            words = text.split()
            if len(words) > 1:
                selectors.append(f"text=/{words[0]}/i")
        
        # Label-based
        label_text = attrs.get('aria-label', attrs.get('placeholder', ''))
        if label_text:
            selectors.append(f"label:has-text('{label_text}') >> input")
            selectors.append(f"text='{label_text}' >> xpath=following::input[1]")
        
        return selectors
    
    def _generate_aria_selectors(self, element_data: Dict) -> List[str]:
        """Generate ARIA and accessibility-based selectors"""
        selectors = []
        attrs = element_data.get('attributes', {})
        
        # ARIA role
        if 'role' in attrs:
            selectors.append(f"[role='{attrs['role']}']")
            
            # Role + name
            if 'aria-label' in attrs:
                selectors.append(f"[role='{attrs['role']}'][aria-label='{attrs['aria-label']}']")
        
        # ARIA label
        if 'aria-label' in attrs:
            selectors.append(f"[aria-label='{attrs['aria-label']}']")
            selectors.append(f"[aria-label*='{attrs['aria-label']}' i]")
        
        # ARIA described by
        if 'aria-describedby' in attrs:
            selectors.append(f"[aria-describedby='{attrs['aria-describedby']}']")
        
        return selectors
    
    def _generate_visual_selectors(self, element_data: Dict) -> List[str]:
        """Generate position/visual-based selectors"""
        selectors = []
        tag = element_data.get('tagName', '').lower()
        
        # Nth-child patterns (use cautiously)
        # These are less stable but can be useful as fallbacks
        
        return selectors  # Visual selectors are less reliable, keep minimal
    
    def _generate_salesforce_selectors(self, element_data: Dict) -> List[str]:
        """Generate Salesforce Lightning/OmniScript specific selectors"""
        selectors = []
        tag = element_data.get('tagName', '').lower()
        attrs = element_data.get('attributes', {})
        
        # Lightning components
        if tag.startswith('lightning-'):
            selectors.append(tag)
            
            # Lightning input with label
            if 'data-field' in attrs:
                selectors.append(f"{tag}[data-field='{attrs['data-field']}']")
            
            # Lightning with inner input
            selectors.append(f"{tag} >> input")
            selectors.append(f"{tag} >> button")
        
        # OmniScript components
        if 'data-omnistudio-' in str(attrs):
            for key, value in attrs.items():
                if key.startswith('data-omnistudio-'):
                    selectors.append(f"[{key}='{value}']")
        
        # Salesforce Lightning Design System (SLDS) classes
        if 'class' in attrs:
            classes = attrs['class']
            if 'slds-' in classes:
                slds_classes = [c for c in classes.split() if c.startswith('slds-')]
                for cls in slds_classes[:3]:  # Top 3 SLDS classes
                    selectors.append(f".{cls}")
        
        # Vlocity/OmniStudio
        if 'vlocity' in str(attrs).lower() or 'omnistudio' in str(attrs).lower():
            for key, value in attrs.items():
                if 'vlocity' in key.lower() or 'omnistudio' in key.lower():
                    selectors.append(f"[{key}='{value}']")
        
        return selectors
    
    def _calculate_confidence(
        self,
        selector: str,
        element_data: Dict,
        strategy: str
    ) -> float:
        """
        Calculate confidence score for a selector (0-1)
        Based on:
        - Selector specificity
        - Historical success rate
        - Strategy reliability
        - Element characteristics
        """
        confidence = 0.5  # Base confidence
        
        # Strategy weights
        strategy_weights = {
            'css': 0.9,
            'xpath': 0.7,
            'semantic': 0.8,
            'aria': 0.85,
            'visual': 0.4,
            'salesforce': 0.95
        }
        confidence *= strategy_weights.get(strategy, 0.5)
        
        # Selector specificity bonus
        if '#' in selector:  # ID selector
            confidence += 0.3
        elif 'data-' in selector:  # Data attribute
            confidence += 0.25
        elif 'aria-' in selector:  # ARIA attribute
            confidence += 0.2
        elif '[name=' in selector:  # Name attribute
            confidence += 0.15
        
        # Historical success rate
        if selector in self.selector_success_rates:
            stats = self.selector_success_rates[selector]
            total = stats['success'] + stats['failure']
            if total > 0:
                success_rate = stats['success'] / total
                confidence = confidence * 0.7 + success_rate * 0.3
        
        # Salesforce-specific bonus
        if 'lightning-' in selector or 'slds-' in selector:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def find_similar_elements(
        self,
        query_element: Dict,
        threshold: float = 0.85
    ) -> List[Dict]:
        """
        Find similar elements from past recordings using semantic similarity
        
        Args:
            query_element: Element to find matches for
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar elements with similarity scores
        """
        if not self.model or not self.element_embeddings:
            return []
        
        try:
            # Generate embedding for query element
            query_text = self._extract_element_text(query_element)
            query_embedding = self.model.encode(query_text)
            
            # Compare with stored embeddings
            similar_elements = []
            for element_id, stored_data in self.element_embeddings.items():
                stored_embedding = stored_data['embedding']
                
                # Calculate cosine similarity
                similarity = cosine_similarity(
                    [query_embedding],
                    [stored_embedding]
                )[0][0]
                
                if similarity >= threshold:
                    similar_elements.append({
                        'element_id': element_id,
                        'similarity': float(similarity),
                        'element_data': stored_data['element_data'],
                        'timestamp': stored_data['timestamp']
                    })
            
            # Sort by similarity
            similar_elements.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similar_elements
            
        except Exception as e:
            print(f"⚠️ Similarity search failed: {e}")
            return []
    
    def record_selector_result(
        self,
        selector: str,
        success: bool,
        execution_time: float = 0
    ):
        """
        Record selector execution result for learning
        
        Args:
            selector: The selector that was used
            success: Whether it successfully found the element
            execution_time: Time taken to find element
        """
        if success:
            self.selector_success_rates[selector]['success'] += 1
        else:
            self.selector_success_rates[selector]['failure'] += 1
    
    def get_best_selector(
        self,
        element_data: Dict,
        page_context: Optional[str] = None
    ) -> str:
        """
        Get the single best selector for an element
        
        Args:
            element_data: Element information
            page_context: Optional page context
            
        Returns:
            Best selector string
        """
        result = self.generate_selectors(element_data, page_context)
        if result['selectors']:
            return result['selectors'][0]['selector']
        
        # Fallback to simple text selector
        text = self._extract_element_text(element_data)
        return f"text={text}" if text else "body"
    
    def _extract_element_text(self, element_data: Dict) -> str:
        """Extract meaningful text from element data"""
        text_parts = []
        
        # Inner text
        if 'innerText' in element_data:
            text_parts.append(element_data['innerText'].strip())
        
        # ARIA label
        attrs = element_data.get('attributes', {})
        if 'aria-label' in attrs:
            text_parts.append(attrs['aria-label'])
        
        # Placeholder
        if 'placeholder' in attrs:
            text_parts.append(attrs['placeholder'])
        
        # Title
        if 'title' in attrs:
            text_parts.append(attrs['title'])
        
        return ' '.join(text_parts).strip()
    
    def _generate_element_id(self, element_data: Dict) -> str:
        """Generate unique ID for element"""
        text = self._extract_element_text(element_data)
        tag = element_data.get('tagName', '')
        attrs_str = json.dumps(element_data.get('attributes', {}), sort_keys=True)
        
        unique_string = f"{tag}:{text}:{attrs_str}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def export_learned_data(self, filepath: str):
        """Export learned selector patterns to file"""
        data = {
            'selector_success_rates': dict(self.selector_success_rates),
            'element_count': len(self.element_embeddings),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Exported learned data to {filepath}")
    
    def import_learned_data(self, filepath: str):
        """Import previously learned selector patterns"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.selector_success_rates = defaultdict(
                lambda: {'success': 0, 'failure': 0},
                data.get('selector_success_rates', {})
            )
            
            print(f"✅ Imported learned data from {filepath}")
        except Exception as e:
            print(f"⚠️ Could not import learned data: {e}")


# Singleton instance
_selector_engine = None

def get_selector_engine() -> SelectorIntelligenceEngine:
    """Get or create SelectorIntelligenceEngine instance"""
    global _selector_engine
    if _selector_engine is None:
        _selector_engine = SelectorIntelligenceEngine()
    return _selector_engine
