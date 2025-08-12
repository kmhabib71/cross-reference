#!/usr/bin/env python3
"""
Legal Entity Extractor for Phase 2 - Task 2.1
===============================================

Comprehensive entity recognition system for Bangladesh tax laws.
Integrates Phase 1.5 Bengali NER with enhanced entity categorization.

Entity Types:
- Sections: ধারা/Section + number  
- Schedules: তফসিল/Schedule + number + part
- Rules: বিধি/Rule + number
- Financial Years: অর্থবছর/FY format
- Tax Rates: Percentage values with context
- Amounts: Monetary values with context

Author: Phase 2 Implementation
Date: August 10, 2025
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import sys

# Import Phase 1.5 NER components (placeholder for now)
# sys.path.append(str(Path(__file__).parent.parent / "phase_1_5_bengali_ner"))
# from bengali_legal_ner_trainer import BengaliLegalNER

class MockBengaliLegalNER:
    """Mock Bengali NER for testing Phase 2 without dependencies"""
    def extract_entities(self, text: str) -> List[Dict]:
        # Basic mock implementation
        entities = []
        if 'ধারা' in text:
            entities.append({
                'type': 'SECTION_DIRECT',
                'text': 'ধারা ১৬৩',
                'confidence': 0.95,
                'context': 'mock context'
            })
        return entities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LegalEntity:
    """Structured legal entity with metadata"""
    entity_type: str
    text: str
    normalized_form: str
    confidence: float
    context: str
    document_source: str
    section_context: Optional[str] = None
    bengali_equivalent: Optional[str] = None
    english_equivalent: Optional[str] = None
    numerical_value: Optional[float] = None
    
class LegalEntityExtractor:
    """
    Advanced legal entity extraction system for Bangladesh tax laws.
    
    Features:
    - Bengali/English bilingual entity recognition
    - Integration with Phase 1.5 Bengali NER
    - Context-aware entity categorization
    - Cross-reference relationship detection
    - Confidence scoring and validation
    """
    
    def __init__(self):
        """Initialize entity extractor with patterns and NER model"""
        self.bengali_ner = MockBengaliLegalNER()  # Using mock for testing
        self.entity_patterns = self._init_entity_patterns()
        self.bilingual_mappings = self._init_bilingual_mappings()
        self.context_analyzers = self._init_context_analyzers()
        
        logger.info("Legal Entity Extractor initialized")
    
    def _init_entity_patterns(self) -> Dict[str, List[str]]:
        """Initialize comprehensive regex patterns for entity recognition"""
        return {
            # Section patterns (Bengali + English)
            "sections": [
                r'ধারা\s*(\d+[ক-ঙ]?)',  # ধারা ১৬৩, ধারা ৭৫ক
                r'Section\s*(\d+[A-Z]?)',  # Section 163, Section 75A
                r'Sec\.\s*(\d+[A-Z]?)',   # Sec. 163
                r's\.\s*(\d+[A-Z]?)',     # s. 163
                r'§\s*(\d+[A-Z]?)',       # § 163
                r'(\d+)\s*নং\s*ধারা',     # ১৬৩ নং ধারা
            ],
            
            # Schedule patterns
            "schedules": [
                r'তফসিল\s*(\d+(?:ম|য়)?)\s*(?:অংশ\s*(\d+))?',  # তফসিল ৪র্থ অংশ ২
                r'Schedule\s*(\d+(?:st|nd|rd|th)?)\s*(?:Part\s*(\d+))?',  # Schedule 4th Part 2
                r'(\d+)(?:ম|য়)?\s*তফসিল(?:\s*অংশ\s*(\d+))?',  # ৪র্থ তফসিল অংশ ২
                r'(\d+)(?:st|nd|rd|th)?\s*Schedule(?:\s*Part\s*(\d+))?',  # 4th Schedule Part 2
            ],
            
            # Rules patterns  
            "rules": [
                r'বিধি\s*(\d+[ক-ঙ]?)',    # বিধি ৩
                r'Rule\s*(\d+[A-Z]?)',     # Rule 3
                r'(\d+)\s*নং\s*বিধি',      # ৩ নং বিধি
            ],
            
            # Financial Year patterns
            "financial_years": [
                r'(\d{4})-(\d{2,4})\s*অর্থবছর',          # ২০২৪-২৫ অর্থবছর
                r'FY\s*(\d{4})-(\d{2,4})',               # FY 2024-25
                r'অর্থবছর\s*(\d{4})-(\d{2,4})',          # অর্থবছর ২০২৪-২৫
                r'Financial\s*Year\s*(\d{4})-(\d{2,4})', # Financial Year 2024-25
            ],
            
            # Tax Rate patterns
            "tax_rates": [
                r'(\d+(?:\.\d+)?)\s*%',                    # 15%, 2.5%
                r'(\d+(?:\.\d+)?)\s*শতাংশ',               # ১৫ শতাংশ
                r'শতকরা\s*(\d+(?:\.\d+)?)',               # শতকরা ১৫
                r'percent\s*(\d+(?:\.\d+)?)',             # percent 15
                r'(\d+(?:\.\d+)?)\s*per\s*cent',          # 15 per cent
            ],
            
            # Amount patterns (Bengali numerals + English)
            "amounts": [
                r'(\d+(?:,\d+)*)\s*টাকা',                 # ১,৫০,০০০ টাকা
                r'(\d+(?:,\d+)*)\s*taka',                 # 150000 taka
                r'BDT\s*(\d+(?:,\d+)*)',                  # BDT 150,000
                r'৳\s*(\d+(?:,\d+)*)',                    # ৳ ১,৫০,০০০
                r'(\d+)\s*লক্ষ(?:\s*টাকা)?',             # ৫ লক্ষ টাকা
                r'(\d+)\s*কোটি(?:\s*টাকা)?',             # ২ কোটি টাকা
                r'(\d+)\s*হাজার(?:\s*টাকা)?',           # ৫০ হাজার টাকা
                r'(\d+)\s*lakh(?:\s*taka)?',              # 5 lakh taka
                r'(\d+)\s*crore(?:\s*taka)?',             # 2 crore taka
            ],
        }
    
    def _init_bilingual_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize Bengali-English equivalent mappings"""
        return {
            "section_terms": {
                "ধারা": "Section",
                "Section": "ধারা", 
                "Sec": "ধারা",
                "s": "ধারা",
                "§": "ধারা"
            },
            "schedule_terms": {
                "তফসিল": "Schedule",
                "Schedule": "তফসিল",
                "অংশ": "Part",
                "Part": "অংশ"
            },
            "rule_terms": {
                "বিধি": "Rule",
                "Rule": "বিধি"
            },
            "ordinal_numbers": {
                "১ম": "1st", "২য়": "2nd", "৩য়": "3rd", "৪র্থ": "4th",
                "৫ম": "5th", "৬ষ্ঠ": "6th", "৭ম": "7th", "৮ম": "8th",
                "1st": "১ম", "2nd": "২য়", "3rd": "৩য়", "4th": "৪র্থ",
                "5th": "৫ম", "6th": "৬ষ্ঠ", "7th": "৭ম", "8th": "৮ম"
            },
            "bengali_numerals": {
                "০": "0", "১": "1", "২": "2", "৩": "3", "৪": "4",
                "৫": "5", "৬": "6", "৭": "7", "৮": "8", "৯": "9"
            }
        }
    
    def _init_context_analyzers(self) -> Dict[str, callable]:
        """Initialize context analysis functions for entity validation"""
        return {
            "sections": self._analyze_section_context,
            "schedules": self._analyze_schedule_context,
            "rules": self._analyze_rule_context,
            "financial_years": self._analyze_fy_context,
            "tax_rates": self._analyze_rate_context,
            "amounts": self._analyze_amount_context
        }
    
    def extract_entities(self, text: str, document_source: str = "") -> List[LegalEntity]:
        """
        Extract all legal entities from given text
        
        Args:
            text: Input text (Bengali/English mixed)
            document_source: Source document identifier
            
        Returns:
            List of structured legal entities with metadata
        """
        entities = []
        
        # Phase 1: Use Phase 1.5 Bengali NER for initial extraction
        bengali_entities = self._extract_with_bengali_ner(text, document_source)
        entities.extend(bengali_entities)
        
        # Phase 2: Pattern-based extraction for comprehensive coverage
        pattern_entities = self._extract_with_patterns(text, document_source)
        entities.extend(pattern_entities)
        
        # Phase 3: Cross-reference detection
        crossref_entities = self._extract_cross_references(text, document_source)
        entities.extend(crossref_entities)
        
        # Phase 4: Entity normalization and deduplication
        normalized_entities = self._normalize_and_deduplicate(entities)
        
        # Phase 5: Confidence scoring and validation
        validated_entities = self._validate_entities(normalized_entities, text)
        
        logger.info(f"Extracted {len(validated_entities)} entities from {document_source}")
        return validated_entities
    
    def _extract_with_bengali_ner(self, text: str, document_source: str) -> List[LegalEntity]:
        """Extract entities using Phase 1.5 Bengali NER system"""
        entities = []
        
        try:
            # Use Bengali NER for entity extraction
            ner_results = self.bengali_ner.extract_entities(text)
            
            for entity in ner_results:
                legal_entity = LegalEntity(
                    entity_type=entity.get('type', 'unknown'),
                    text=entity.get('text', ''),
                    normalized_form=self._normalize_entity_text(entity.get('text', '')),
                    confidence=entity.get('confidence', 0.0),
                    context=entity.get('context', ''),
                    document_source=document_source,
                    bengali_equivalent=entity.get('text', '') if self._is_bengali(entity.get('text', '')) else None,
                    english_equivalent=self._get_english_equivalent(entity.get('text', ''))
                )
                entities.append(legal_entity)
                
        except Exception as e:
            logger.warning(f"Bengali NER extraction failed: {e}")
        
        return entities
    
    def _extract_with_patterns(self, text: str, document_source: str) -> List[LegalEntity]:
        """Extract entities using regex patterns"""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entity_text = match.group(0).strip()
                    context = self._get_entity_context(text, match.span())
                    
                    # Analyze context for validation
                    context_analysis = self.context_analyzers[entity_type](entity_text, context)
                    
                    if context_analysis['is_valid']:
                        legal_entity = LegalEntity(
                            entity_type=entity_type,
                            text=entity_text,
                            normalized_form=self._normalize_entity_text(entity_text),
                            confidence=context_analysis['confidence'],
                            context=context,
                            document_source=document_source,
                            bengali_equivalent=self._get_bengali_equivalent(entity_text),
                            english_equivalent=self._get_english_equivalent(entity_text),
                            numerical_value=context_analysis.get('numerical_value')
                        )
                        entities.append(legal_entity)
        
        return entities
    
    def _extract_cross_references(self, text: str, document_source: str) -> List[LegalEntity]:
        """Extract indirect references and cross-references"""
        crossref_entities = []
        
        # Indirect reference patterns
        indirect_patterns = [
            r'উক্ত\s*ধারা',         # "the said section"
            r'সংশ্লিষ্ট\s*তফসিল',   # "related schedule"
            r'প্রযোজ্য\s*বিধি',     # "applicable rule"
            r'পূর্বোক্ত\s*বিধান',   # "aforementioned provision"
            r'এই\s*আইন',          # "this Act"
            r'this\s*section',     # English indirect reference
            r'such\s*provision',   # English indirect reference
        ]
        
        for pattern in indirect_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                entity_text = match.group(0).strip()
                context = self._get_entity_context(text, match.span(), window_size=100)
                
                # Try to resolve indirect reference
                resolved_reference = self._resolve_indirect_reference(entity_text, context)
                
                legal_entity = LegalEntity(
                    entity_type="cross_reference",
                    text=entity_text,
                    normalized_form=resolved_reference if resolved_reference else entity_text,
                    confidence=0.7 if resolved_reference else 0.4,
                    context=context,
                    document_source=document_source,
                    section_context=resolved_reference
                )
                crossref_entities.append(legal_entity)
        
        return crossref_entities
    
    def _normalize_and_deduplicate(self, entities: List[LegalEntity]) -> List[LegalEntity]:
        """Normalize entity representations and remove duplicates"""
        seen_entities = set()
        normalized_entities = []
        
        for entity in entities:
            # Create normalized key for deduplication
            normalized_key = (
                entity.entity_type,
                entity.normalized_form,
                entity.document_source
            )
            
            if normalized_key not in seen_entities:
                seen_entities.add(normalized_key)
                normalized_entities.append(entity)
            else:
                # Merge confidence scores for duplicates
                for existing_entity in normalized_entities:
                    if (existing_entity.entity_type == entity.entity_type and 
                        existing_entity.normalized_form == entity.normalized_form):
                        existing_entity.confidence = max(existing_entity.confidence, entity.confidence)
                        break
        
        return normalized_entities
    
    def _validate_entities(self, entities: List[LegalEntity], original_text: str) -> List[LegalEntity]:
        """Validate extracted entities and assign final confidence scores"""
        validated_entities = []
        
        for entity in entities:
            # Validation checks
            is_valid = True
            confidence_adjustments = 0.0
            
            # Check 1: Text length validation
            if len(entity.text.strip()) < 2:
                is_valid = False
            
            # Check 2: Context validation
            if not self._has_legal_context(entity.context):
                confidence_adjustments -= 0.2
            
            # Check 3: Cross-validation with other entities
            supporting_entities = self._find_supporting_entities(entity, entities)
            if supporting_entities:
                confidence_adjustments += 0.1
            
            # Apply confidence adjustments
            final_confidence = min(1.0, max(0.0, entity.confidence + confidence_adjustments))
            
            if is_valid and final_confidence > 0.3:  # Minimum confidence threshold
                entity.confidence = final_confidence
                validated_entities.append(entity)
        
        return validated_entities
    
    # Context Analysis Methods
    def _analyze_section_context(self, entity_text: str, context: str) -> Dict[str, Any]:
        """Analyze section entity context"""
        legal_indicators = ['আইন', 'বিধি', 'তফসিল', 'Act', 'Rule', 'Schedule']
        confidence = 0.6
        
        # Boost confidence if legal terms are nearby
        for indicator in legal_indicators:
            if indicator in context:
                confidence += 0.1
        
        return {
            'is_valid': True,
            'confidence': min(confidence, 0.95)
        }
    
    def _analyze_schedule_context(self, entity_text: str, context: str) -> Dict[str, Any]:
        """Analyze schedule entity context"""
        schedule_indicators = ['আইন', 'ধারা', 'Act', 'Section', 'provision']
        confidence = 0.7
        
        for indicator in schedule_indicators:
            if indicator in context:
                confidence += 0.05
        
        return {
            'is_valid': True,
            'confidence': min(confidence, 0.95)
        }
    
    def _analyze_rule_context(self, entity_text: str, context: str) -> Dict[str, Any]:
        """Analyze rule entity context"""
        return {
            'is_valid': True,
            'confidence': 0.8
        }
    
    def _analyze_fy_context(self, entity_text: str, context: str) -> Dict[str, Any]:
        """Analyze financial year context"""
        return {
            'is_valid': True,
            'confidence': 0.9
        }
    
    def _analyze_rate_context(self, entity_text: str, context: str) -> Dict[str, Any]:
        """Analyze tax rate context"""
        rate_match = re.search(r'(\d+(?:\.\d+)?)', entity_text)
        numerical_value = float(rate_match.group(1)) if rate_match else None
        
        return {
            'is_valid': True,
            'confidence': 0.85,
            'numerical_value': numerical_value
        }
    
    def _analyze_amount_context(self, entity_text: str, context: str) -> Dict[str, Any]:
        """Analyze amount entity context"""
        # Extract numerical value
        numerical_value = self._extract_amount_value(entity_text)
        
        return {
            'is_valid': True,
            'confidence': 0.8,
            'numerical_value': numerical_value
        }
    
    # Utility Methods
    def _normalize_entity_text(self, text: str) -> str:
        """Normalize entity text for consistent representation"""
        # Convert Bengali numerals to English
        normalized = text
        for bengali, english in self.bilingual_mappings['bengali_numerals'].items():
            normalized = normalized.replace(bengali, english)
        
        # Standardize spacing
        normalized = re.sub(r'\s+', ' ', normalized.strip())
        
        return normalized
    
    def _get_entity_context(self, text: str, span: Tuple[int, int], window_size: int = 50) -> str:
        """Extract context around entity mention"""
        start, end = span
        context_start = max(0, start - window_size)
        context_end = min(len(text), end + window_size)
        
        return text[context_start:context_end].strip()
    
    def _is_bengali(self, text: str) -> bool:
        """Check if text contains Bengali characters"""
        bengali_pattern = r'[\u0980-\u09FF]'
        return bool(re.search(bengali_pattern, text))
    
    def _get_bengali_equivalent(self, text: str) -> Optional[str]:
        """Get Bengali equivalent of English entity"""
        # Implementation for bilingual mapping
        return None  # Placeholder
    
    def _get_english_equivalent(self, text: str) -> Optional[str]:
        """Get English equivalent of Bengali entity"""
        # Implementation for bilingual mapping  
        return None  # Placeholder
    
    def _resolve_indirect_reference(self, entity_text: str, context: str) -> Optional[str]:
        """Resolve indirect reference to specific entity"""
        # Implementation for indirect reference resolution
        return None  # Placeholder
    
    def _has_legal_context(self, context: str) -> bool:
        """Check if context indicates legal document"""
        legal_terms = ['আইন', 'বিধি', 'তফসিল', 'ধারা', 'Act', 'Rule', 'Schedule', 'Section']
        return any(term in context for term in legal_terms)
    
    def _find_supporting_entities(self, target_entity: LegalEntity, all_entities: List[LegalEntity]) -> List[LegalEntity]:
        """Find entities that support the target entity"""
        supporting = []
        
        for entity in all_entities:
            if (entity != target_entity and 
                entity.document_source == target_entity.document_source and
                self._entities_are_related(target_entity, entity)):
                supporting.append(entity)
        
        return supporting
    
    def _entities_are_related(self, entity1: LegalEntity, entity2: LegalEntity) -> bool:
        """Check if two entities are semantically related"""
        # Simple proximity check
        return abs(len(entity1.context) - len(entity2.context)) < 100
    
    def _extract_amount_value(self, amount_text: str) -> Optional[float]:
        """Extract numerical value from amount text"""
        # Handle Bengali amount formats
        if 'লক্ষ' in amount_text:
            match = re.search(r'(\d+(?:\.\d+)?)\s*লক্ষ', amount_text)
            return float(match.group(1)) * 100000 if match else None
        elif 'কোটি' in amount_text:
            match = re.search(r'(\d+(?:\.\d+)?)\s*কোটি', amount_text)
            return float(match.group(1)) * 10000000 if match else None
        elif 'হাজার' in amount_text:
            match = re.search(r'(\d+(?:\.\d+)?)\s*হাজার', amount_text)
            return float(match.group(1)) * 1000 if match else None
        else:
            # Extract basic number
            match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', amount_text.replace(',', ''))
            return float(match.group(1)) if match else None
    
    def export_entities(self, entities: List[LegalEntity], output_path: str) -> None:
        """Export entities to JSON format"""
        entities_data = [asdict(entity) for entity in entities]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'entities': entities_data,
                'total_count': len(entities),
                'entity_types': self._get_entity_type_distribution(entities),
                'extraction_metadata': {
                    'version': '2.1.0',
                    'phase': 'Phase 2 - Task 2.1',
                    'features': [
                        'Bengali NER Integration',
                        'Pattern-based Extraction',
                        'Cross-reference Detection',
                        'Bilingual Mapping',
                        'Context Analysis',
                        'Confidence Scoring'
                    ]
                }
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exported {len(entities)} entities to {output_path}")
    
    def _get_entity_type_distribution(self, entities: List[LegalEntity]) -> Dict[str, int]:
        """Get distribution of entity types"""
        distribution = {}
        for entity in entities:
            distribution[entity.entity_type] = distribution.get(entity.entity_type, 0) + 1
        return distribution

def main():
    """Test the Legal Entity Extractor"""
    extractor = LegalEntityExtractor()
    
    # Test with sample Bengali legal text
    test_text = """
    আয়কর আইন ২০২৩ এর ধারা ১৬৩ অনুযায়ী ন্যূনতম কর প্রযোজ্য হবে।
    ৬ষ্ঠ তফসিলের ৪র্থ অংশে কর অবকাশের বিধান রয়েছে। 
    ২০২৪-২৫ অর্থবছরে ৩.৫ লক্ষ টাকা পর্যন্ত আয় করমুক্ত।
    Section 75 of Income Tax Act 2023 requires return filing.
    """
    
    entities = extractor.extract_entities(test_text, "test_document")
    
    print(f"\n🎯 Extracted {len(entities)} entities:")
    print("=" * 60)
    
    for entity in entities:
        print(f"Type: {entity.entity_type}")
        print(f"Text: {entity.text}")
        print(f"Normalized: {entity.normalized_form}")
        print(f"Confidence: {entity.confidence:.2f}")
        print(f"Context: {entity.context[:50]}...")
        print("-" * 40)
    
    # Export results
    output_path = Path(__file__).parent / "test_entities_extraction.json"
    extractor.export_entities(entities, str(output_path))

if __name__ == "__main__":
    main()