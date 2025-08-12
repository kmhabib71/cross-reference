#!/usr/bin/env python3
"""
Cross-Language Section ID Unification System for Phase 2.5 - Task 2.5.3
========================================================================

Standardize section references across Bengali/English with canonical IDs.

Critical Problem Addressed:
- Bengali query mentions "ধারা ৭৫"
- English legal text has "Section 75"  
- System fails to match -> FIXED with unified canonical IDs

Core Features:
- Bilingual section mapping (Bengali ↔ English)
- Canonical ID system for consistent reference
- Variation handling for multiple formats
- Integration with Phase 2 Knowledge Graph
- Fuzzy matching for partial references

Author: Phase 2.5 Implementation
Date: August 10, 2025
"""

import json
import re
import logging
from typing import Dict, List, Tuple, Optional, Any, Set, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import difflib
from collections import defaultdict
import sys

# Import Phase 2 components for integration
sys.path.append(str(Path(__file__).parent.parent / "phase_2_knowledge_graph"))
from legal_entity_extractor import LegalEntityExtractor

# Import Phase 2.5 components  
from temporal_law_manager import TemporalLawManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SectionMapping:
    """Unified section mapping with bilingual support"""
    canonical_id: str
    document_source: str
    section_number: str
    bengali_variations: List[str]
    english_variations: List[str]
    canonical_text_bengali: str
    canonical_text_english: str
    topic_keywords: List[str]
    related_sections: List[str]
    effective_date: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class UnificationMatch:
    """Result of section unification matching"""
    query_text: str
    matched_section: Optional[SectionMapping]
    confidence_score: float
    match_type: str  # "exact", "fuzzy", "semantic", "numeric"
    alternative_matches: List[SectionMapping]
    normalization_applied: List[str]

class SectionUnificationSystem:
    """
    Cross-language section ID unification system for Bangladesh tax laws.
    
    Capabilities:
    - Bilingual section reference standardization
    - Canonical ID generation and mapping
    - Variation handling (ধারা ৭৫, Section 75, Sec 75, s. 75)
    - Fuzzy matching for partial or misspelled references
    - Semantic matching based on content similarity
    - Integration with temporal law versions
    - Export/import of unified mappings
    """
    
    def __init__(self, temporal_manager: Optional[TemporalLawManager] = None,
                 entity_extractor: Optional[LegalEntityExtractor] = None):
        """Initialize section unification system"""
        self.temporal_manager = temporal_manager
        self.entity_extractor = entity_extractor or LegalEntityExtractor()
        
        # Core mapping data structures
        self.section_mappings: Dict[str, SectionMapping] = {}
        self.canonical_index: Dict[str, str] = {}  # canonical_id -> section_mapping_id
        self.variation_index: Dict[str, List[str]] = defaultdict(list)  # variation -> canonical_ids
        
        # Pattern recognition and normalization
        self.bengali_numerals = self._init_bengali_numerals()
        self.section_patterns = self._init_section_patterns()
        self.normalization_rules = self._init_normalization_rules()
        
        # Pre-built section mappings for common Bangladesh tax law sections
        self._initialize_core_mappings()
        
        logger.info("Section Unification System initialized")
    
    def _init_bengali_numerals(self) -> Dict[str, str]:
        """Initialize Bengali to English numeral mapping"""
        return {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
    
    def _init_section_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for section recognition"""
        return {
            # Bengali section patterns
            "bengali_sections": [
                r'ধারা\s*([০-৯\d]+[ক-ঙাআইউএও]?)',        # ধারা ৭৫, ধারা ১৬৩ক
                r'([০-৯\d]+)\s*নং\s*ধারা',                # ৭৫ নং ধারা
                r'([০-৯\d]+)\s*(?:নম্বর|নং)?\s*ধারা',      # ৭৫ নম্বর ধারা
                r'ধারা\s*([০-৯\d]+)\s*এর',                # ধারা ৭৫ এর
            ],
            
            # English section patterns  
            "english_sections": [
                r'Section\s*(\d+[A-Z]?)',                   # Section 75, Section 75A
                r'Sec\.?\s*(\d+[A-Z]?)',                   # Sec 75, Sec. 75A
                r's\.?\s*(\d+[A-Z]?)',                     # s. 75, s 75A
                r'§\s*(\d+[A-Z]?)',                        # § 75
                r'Section\s*No\.?\s*(\d+[A-Z]?)',          # Section No. 75
            ],
            
            # Mixed/Numeric patterns
            "numeric_sections": [
                r'(\d+)[ক-ঙাআইউএও]?\s*(?:ধারা|section|sec)',  # 75 ধারা, 75 section
                r'(?:ধারা|section|sec)\s*(\d+[A-Z]?)',          # ধারা 75, section 75
            ],
            
            # Schedule patterns (related)
            "schedule_patterns": [
                r'তফসিল\s*([০-৯\d]+(?:ম|য়)?)',           # তফসিল ৪র্থ
                r'Schedule\s*(\d+(?:st|nd|rd|th)?)',        # Schedule 4th
                r'([০-৯\d]+)(?:ম|য়)?\s*তফসিল',           # ৪র্থ তফসিল
            ]
        }
    
    def _init_normalization_rules(self) -> Dict[str, Any]:
        """Initialize text normalization rules"""
        return {
            "bengali_to_english_numerals": self.bengali_numerals,
            "section_term_standardization": {
                "ধারা": "section",
                "Section": "section", 
                "Sec": "section",
                "sec": "section",
                "s": "section",
                "§": "section"
            },
            "ordinal_standardization": {
                "ক": "A", "খ": "B", "গ": "C", "ঘ": "D", "ঙ": "E",
                "চ": "F", "ছ": "G", "জ": "H", "ঝ": "I", "ঞ": "J"
            },
            "whitespace_normalization": r'\s+',  # Multiple spaces to single space
            "punctuation_removal": r'[।,;:!?]'   # Remove Bengali/English punctuation
        }
    
    def _initialize_core_mappings(self) -> None:
        """Initialize core section mappings for Bangladesh tax laws"""
        
        core_sections = [
            # Income Tax Act 2023 - Key Sections
            {
                "canonical_id": "ITA_2023_S44",
                "document_source": "income_tax_act_2023",
                "section_number": "44",
                "bengali_variations": ["ধারা ৪৪", "ধারা চুয়াল্লিশ", "৪ৄ নং ধারা"],
                "english_variations": ["Section 44", "Sec 44", "s. 44", "§ 44"],
                "canonical_text_bengali": "করমুক্ত আয়ের সীমা",
                "canonical_text_english": "Tax-free income limit",
                "topic_keywords": ["tax_free_limit", "exemption_threshold", "করমুক্ত", "সীমা"],
                "related_sections": ["ITA_2023_S43", "ITA_2023_S45"]
            },
            {
                "canonical_id": "ITA_2023_S75",
                "document_source": "income_tax_act_2023", 
                "section_number": "75",
                "bengali_variations": ["ধারা ৭৫", "ধারা পঁচাত্তর", "৭৫ নং ধারা"],
                "english_variations": ["Section 75", "Sec 75", "s. 75", "§ 75"],
                "canonical_text_bengali": "রিটার্ন দাখিল বাধ্যবাধকতা",
                "canonical_text_english": "Obligation to furnish return",
                "topic_keywords": ["return_filing", "filing_obligation", "রিটার্ন", "দাখিল"],
                "related_sections": ["ITA_2023_S76", "ITA_2023_S77"]
            },
            {
                "canonical_id": "ITA_2023_S163",
                "document_source": "income_tax_act_2023",
                "section_number": "163",
                "bengali_variations": ["ধারা ১৬৩", "ধারা একশ তেষট্টি", "১৬৩ নং ধারা"],
                "english_variations": ["Section 163", "Sec 163", "s. 163", "§ 163"],
                "canonical_text_bengali": "ন্যূনতম কর",
                "canonical_text_english": "Minimum tax",
                "topic_keywords": ["minimum_tax", "ন্যূনতম", "কর"],
                "related_sections": ["ITA_2023_S162", "ITA_2023_S164"]
            },
            {
                "canonical_id": "ITA_2023_S102",
                "document_source": "income_tax_act_2023",
                "section_number": "102",
                "bengali_variations": ["ধারা ১০২", "ধারা একশ দুই", "১০২ নং ধারা"],
                "english_variations": ["Section 102", "Sec 102", "s. 102", "§ 102"],
                "canonical_text_bengali": "সঞ্চয় আমানত ও সাবধি আমানতের সুদ থেকে উৎসে কর কর্তন",
                "canonical_text_english": "Deduction at source from interest on savings and fixed deposits",
                "topic_keywords": ["tds", "interest_tax", "সুদ", "কর_কর্তন"],
                "related_sections": ["ITA_2023_S101", "ITA_2023_S103"]
            },
            # Add Schedule mappings
            {
                "canonical_id": "ITA_2023_SCH4",
                "document_source": "income_tax_act_2023",
                "section_number": "schedule_4",
                "bengali_variations": ["তফসিল ৪", "চতুর্থ তফসিল", "৪ নং তফসিল"],
                "english_variations": ["Schedule 4", "4th Schedule", "Fourth Schedule"],
                "canonical_text_bengali": "কর হার তফসিল",
                "canonical_text_english": "Tax rate schedule",
                "topic_keywords": ["tax_rates", "schedule", "হার", "তফসিল"],
                "related_sections": ["ITA_2023_SCH3", "ITA_2023_SCH5"]
            }
        ]
        
        # Create section mappings
        for section_data in core_sections:
            mapping = SectionMapping(**section_data)
            self.section_mappings[mapping.canonical_id] = mapping
            
            # Build indexes
            self.canonical_index[mapping.canonical_id] = mapping.canonical_id
            
            # Index all variations
            all_variations = mapping.bengali_variations + mapping.english_variations
            for variation in all_variations:
                normalized_variation = self._normalize_section_text(variation)
                self.variation_index[normalized_variation].append(mapping.canonical_id)
        
        logger.info(f"Initialized {len(self.section_mappings)} core section mappings")
    
    def normalize_section_reference(self, section_text: str) -> str:
        """
        Normalize section reference to canonical form
        
        Args:
            section_text: Raw section reference in Bengali/English
            
        Returns:
            Normalized section reference
        """
        logger.debug(f"Normalizing: {section_text}")
        
        # Step 1: Convert Bengali numerals to English
        normalized = self._convert_bengali_numerals(section_text)
        
        # Step 2: Normalize whitespace
        normalized = re.sub(self.normalization_rules["whitespace_normalization"], ' ', normalized)
        
        # Step 3: Remove punctuation
        normalized = re.sub(self.normalization_rules["punctuation_removal"], '', normalized)
        
        # Step 4: Standardize section terms
        for bengali_term, english_term in self.normalization_rules["section_term_standardization"].items():
            normalized = re.sub(rf'\b{re.escape(bengali_term)}\b', english_term, normalized, flags=re.IGNORECASE)
        
        # Step 5: Extract and standardize section number
        section_number = self._extract_section_number(normalized)
        if section_number:
            normalized = f"section {section_number}"
        
        return normalized.strip().lower()
    
    def find_section_mapping(self, query: str, confidence_threshold: float = 0.7) -> UnificationMatch:
        """
        Find section mapping for query with confidence scoring
        
        Args:
            query: User query containing section reference
            confidence_threshold: Minimum confidence for valid match
            
        Returns:
            UnificationMatch with best matching section and alternatives
        """
        logger.debug(f"Finding section mapping for: {query[:50]}...")
        
        # Step 1: Extract potential section references from query
        extracted_sections = self._extract_section_references(query)
        
        if not extracted_sections:
            return UnificationMatch(
                query_text=query,
                matched_section=None,
                confidence_score=0.0,
                match_type="no_match",
                alternative_matches=[],
                normalization_applied=[]
            )
        
        best_match = None
        best_confidence = 0.0
        best_match_type = "no_match"
        alternative_matches = []
        normalization_steps = []
        
        # Step 2: Try to match each extracted section reference
        for section_ref in extracted_sections:
            normalized_ref = self.normalize_section_reference(section_ref)
            normalization_steps.append(f"'{section_ref}' -> '{normalized_ref}'")
            
            # Exact match attempt
            exact_match = self._find_exact_match(normalized_ref)
            if exact_match:
                confidence = 0.95
                if confidence > best_confidence:
                    best_match = exact_match
                    best_confidence = confidence
                    best_match_type = "exact"
                elif confidence >= confidence_threshold:
                    alternative_matches.append(exact_match)
            
            # Fuzzy match attempt if no exact match
            if not exact_match:
                fuzzy_matches = self._find_fuzzy_matches(normalized_ref)
                for match, confidence in fuzzy_matches:
                    if confidence >= confidence_threshold:
                        if confidence > best_confidence:
                            if best_match:
                                alternative_matches.append(best_match)
                            best_match = match
                            best_confidence = confidence
                            best_match_type = "fuzzy"
                        else:
                            alternative_matches.append(match)
            
            # Semantic match attempt for broader queries
            semantic_matches = self._find_semantic_matches(query, normalized_ref)
            for match, confidence in semantic_matches:
                if confidence >= confidence_threshold and confidence > best_confidence:
                    if best_match:
                        alternative_matches.append(best_match)
                    best_match = match
                    best_confidence = confidence
                    best_match_type = "semantic"
        
        return UnificationMatch(
            query_text=query,
            matched_section=best_match,
            confidence_score=best_confidence,
            match_type=best_match_type,
            alternative_matches=alternative_matches[:5],  # Limit alternatives
            normalization_applied=normalization_steps
        )
    
    def add_section_mapping(self, mapping_data: Dict[str, Any]) -> SectionMapping:
        """
        Add new section mapping to the system
        
        Args:
            mapping_data: Section mapping data dictionary
            
        Returns:
            Created SectionMapping object
        """
        mapping = SectionMapping(**mapping_data)
        
        # Validate canonical ID is unique
        if mapping.canonical_id in self.section_mappings:
            raise ValueError(f"Canonical ID {mapping.canonical_id} already exists")
        
        # Add to main storage
        self.section_mappings[mapping.canonical_id] = mapping
        
        # Update indexes
        self.canonical_index[mapping.canonical_id] = mapping.canonical_id
        
        all_variations = mapping.bengali_variations + mapping.english_variations
        for variation in all_variations:
            normalized_variation = self._normalize_section_text(variation)
            self.variation_index[normalized_variation].append(mapping.canonical_id)
        
        logger.info(f"Added section mapping: {mapping.canonical_id}")
        return mapping
    
    def get_canonical_id(self, section_reference: str) -> Optional[str]:
        """Get canonical ID for section reference"""
        match = self.find_section_mapping(section_reference)
        return match.matched_section.canonical_id if match.matched_section else None
    
    def get_bilingual_variations(self, canonical_id: str) -> Dict[str, List[str]]:
        """Get all bilingual variations for canonical ID"""
        mapping = self.section_mappings.get(canonical_id)
        if not mapping:
            return {}
        
        return {
            "bengali": mapping.bengali_variations,
            "english": mapping.english_variations,
            "canonical_id": canonical_id,
            "canonical_texts": {
                "bengali": mapping.canonical_text_bengali,
                "english": mapping.canonical_text_english
            }
        }
    
    def resolve_cross_references(self, document_text: str) -> Dict[str, Any]:
        """
        Resolve all section cross-references in a document
        
        Args:
            document_text: Full document text with references
            
        Returns:
            Document with resolved cross-references and mapping metadata
        """
        logger.info("Resolving cross-references in document")
        
        # Find all section references in document
        all_refs = self._extract_section_references(document_text)
        resolved_refs = []
        unresolved_refs = []
        
        for ref in all_refs:
            match = self.find_section_mapping(ref, confidence_threshold=0.6)
            
            if match.matched_section:
                resolved_refs.append({
                    "original_text": ref,
                    "canonical_id": match.matched_section.canonical_id,
                    "section_number": match.matched_section.section_number,
                    "confidence": match.confidence_score,
                    "match_type": match.match_type,
                    "bilingual_text": {
                        "bengali": match.matched_section.canonical_text_bengali,
                        "english": match.matched_section.canonical_text_english
                    }
                })
            else:
                unresolved_refs.append(ref)
        
        return {
            "document_text": document_text,
            "total_references": len(all_refs),
            "resolved_references": resolved_refs,
            "unresolved_references": unresolved_refs,
            "resolution_rate": len(resolved_refs) / len(all_refs) if all_refs else 0.0,
            "metadata": {
                "analysis_date": "2025-08-10",
                "resolution_method": "section_unification_system",
                "version": "2.5.3"
            }
        }
    
    def generate_unification_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive statistics about section unification"""
        stats = {
            "total_mappings": len(self.section_mappings),
            "total_variations": sum(len(mapping.bengali_variations) + len(mapping.english_variations) 
                                  for mapping in self.section_mappings.values()),
            "document_sources": set(mapping.document_source for mapping in self.section_mappings.values()),
            "mapping_distribution": defaultdict(int),
            "coverage_analysis": {
                "bengali_coverage": 0,
                "english_coverage": 0,
                "bilingual_mappings": 0
            },
            "most_common_sections": [],
            "metadata": {
                "generated_date": "2025-08-10",
                "system_version": "2.5.3"
            }
        }
        
        # Distribution by document source
        for mapping in self.section_mappings.values():
            stats["mapping_distribution"][mapping.document_source] += 1
        
        # Coverage analysis
        bilingual_count = 0
        for mapping in self.section_mappings.values():
            if mapping.bengali_variations:
                stats["coverage_analysis"]["bengali_coverage"] += 1
            if mapping.english_variations:
                stats["coverage_analysis"]["english_coverage"] += 1
            if mapping.bengali_variations and mapping.english_variations:
                bilingual_count += 1
        
        stats["coverage_analysis"]["bilingual_mappings"] = bilingual_count
        
        # Most common sections (by number of variations)
        section_popularity = []
        for mapping in self.section_mappings.values():
            variation_count = len(mapping.bengali_variations) + len(mapping.english_variations)
            section_popularity.append((mapping.canonical_id, variation_count))
        
        stats["most_common_sections"] = sorted(section_popularity, key=lambda x: x[1], reverse=True)[:10]
        
        return dict(stats)
    
    # Internal utility methods
    def _normalize_section_text(self, text: str) -> str:
        """Normalize section text for indexing"""
        return self.normalize_section_reference(text)
    
    def _convert_bengali_numerals(self, text: str) -> str:
        """Convert Bengali numerals to English"""
        converted = text
        for bengali, english in self.bengali_numerals.items():
            converted = converted.replace(bengali, english)
        return converted
    
    def _extract_section_number(self, text: str) -> Optional[str]:
        """Extract section number from normalized text"""
        # Try all section patterns
        for pattern_group in self.section_patterns.values():
            for pattern in pattern_group:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        # Try simple number extraction
        number_match = re.search(r'\b(\d+[A-Z]?)\b', text)
        if number_match:
            return number_match.group(1)
        
        return None
    
    def _extract_section_references(self, text: str) -> List[str]:
        """Extract all section references from text"""
        references = []
        
        for pattern_group in self.section_patterns.values():
            for pattern in pattern_group:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    references.append(match.group(0).strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_refs = []
        for ref in references:
            normalized = self.normalize_section_reference(ref)
            if normalized not in seen:
                seen.add(normalized)
                unique_refs.append(ref)
        
        return unique_refs
    
    def _find_exact_match(self, normalized_ref: str) -> Optional[SectionMapping]:
        """Find exact match for normalized reference"""
        canonical_ids = self.variation_index.get(normalized_ref, [])
        
        if canonical_ids:
            # Return first exact match (could be improved with ranking)
            return self.section_mappings.get(canonical_ids[0])
        
        return None
    
    def _find_fuzzy_matches(self, normalized_ref: str) -> List[Tuple[SectionMapping, float]]:
        """Find fuzzy matches for normalized reference"""
        matches = []
        
        for variation, canonical_ids in self.variation_index.items():
            # Use difflib for fuzzy matching
            similarity = difflib.SequenceMatcher(None, normalized_ref, variation).ratio()
            
            if similarity > 0.7:  # Threshold for fuzzy match
                for canonical_id in canonical_ids:
                    mapping = self.section_mappings.get(canonical_id)
                    if mapping:
                        matches.append((mapping, similarity))
        
        # Sort by similarity score
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:5]  # Return top 5 matches
    
    def _find_semantic_matches(self, original_query: str, normalized_ref: str) -> List[Tuple[SectionMapping, float]]:
        """Find semantic matches based on content"""
        matches = []
        query_lower = original_query.lower()
        
        for mapping in self.section_mappings.values():
            # Check topic keyword overlap
            keyword_matches = 0
            for keyword in mapping.topic_keywords:
                if keyword.lower() in query_lower:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                # Simple semantic scoring
                semantic_score = keyword_matches / len(mapping.topic_keywords)
                if semantic_score > 0.3:  # Minimum semantic threshold
                    matches.append((mapping, semantic_score * 0.8))  # Reduced confidence for semantic
        
        # Sort by semantic score
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:3]  # Return top 3 semantic matches
    
    def export_unification_data(self, output_path: str) -> None:
        """Export section unification data to JSON"""
        export_data = {
            "section_mappings": {k: asdict(v) for k, v in self.section_mappings.items()},
            "canonical_index": self.canonical_index,
            "variation_index": dict(self.variation_index),
            "section_patterns": self.section_patterns,
            "normalization_rules": self.normalization_rules,
            "statistics": self.generate_unification_statistics(),
            "metadata": {
                "version": "2.5.3",
                "export_date": "2025-08-10",
                "description": "Cross-Language Section ID Unification Data"
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Section unification data exported to {output_path}")

def main():
    """Test the Section Unification System"""
    unifier = SectionUnificationSystem()
    
    print("🌐 Section Unification System Test")
    print("=" * 50)
    
    # Test various section reference formats
    test_queries = [
        "আয়কর আইনের ধারা ৭৫ অনুযায়ী রিটার্ন দিতে হবে",
        "Section 163 of Income Tax Act deals with minimum tax",
        "তফসিল ৪ অনুসারে কর হার নির্ধারিত",
        "What is mentioned in sec 44 about tax exemption?",
        "ধারা ১০২ এ সুদের উপর কর কর্তনের কথা আছে",
        "Invalid reference to section 999 which does not exist"
    ]
    
    print("📝 Testing Section Reference Matching:")
    print("-" * 40)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        
        match = unifier.find_section_mapping(query)
        
        if match.matched_section:
            print(f"   ✅ Match: {match.matched_section.canonical_id}")
            print(f"   📄 Section: {match.matched_section.section_number}")
            print(f"   🎯 Confidence: {match.confidence_score:.2f}")
            print(f"   🔍 Match Type: {match.match_type}")
            print(f"   🇧🇩 Bengali: {match.matched_section.canonical_text_bengali}")
            print(f"   🇬🇧 English: {match.matched_section.canonical_text_english}")
            
            if match.alternative_matches:
                print(f"   📋 Alternatives: {len(match.alternative_matches)}")
        else:
            print("   ❌ No match found")
            if match.normalization_applied:
                print(f"   🔄 Normalized: {match.normalization_applied[0]}")
    
    # Test cross-reference resolution
    print(f"\n🔗 Testing Cross-Reference Resolution:")
    print("-" * 40)
    
    test_document = """
    আয়কর আইন ২০২৩ এর ধারা ৪৪ অনুযায়ী করমুক্ত আয়ের সীমা নির্ধারিত।
    Section 75 requires return filing for all taxpayers.
    ন্যূনতম কর সংক্রান্ত বিষয় ধারা ১৬৩ এ বর্ণিত আছে।
    তফসিল ৪ এ কর হার উল্লেখ করা হয়েছে।
    """
    
    resolution = unifier.resolve_cross_references(test_document)
    
    print(f"Total References: {resolution['total_references']}")
    print(f"Resolved: {len(resolution['resolved_references'])}")
    print(f"Unresolved: {len(resolution['unresolved_references'])}")
    print(f"Resolution Rate: {resolution['resolution_rate']:.2%}")
    
    for ref in resolution['resolved_references']:
        print(f"  ✅ {ref['original_text']} → {ref['canonical_id']} ({ref['confidence']:.2f})")
    
    for ref in resolution['unresolved_references']:
        print(f"  ❌ {ref} (unresolved)")
    
    # Test statistics generation
    print(f"\n📊 System Statistics:")
    print("-" * 25)
    
    stats = unifier.generate_unification_statistics()
    print(f"Total Mappings: {stats['total_mappings']}")
    print(f"Total Variations: {stats['total_variations']}")
    print(f"Document Sources: {len(stats['document_sources'])}")
    print(f"Bilingual Coverage: {stats['coverage_analysis']['bilingual_mappings']}/{stats['total_mappings']}")
    
    # Export unification data
    output_path = Path(__file__).parent / "section_unification_data.json"
    unifier.export_unification_data(str(output_path))
    print(f"\n✅ Unification data exported to: {output_path}")

if __name__ == "__main__":
    main()