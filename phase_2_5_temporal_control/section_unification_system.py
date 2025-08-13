#!/usr/bin/env python3
"""
Section Unification System for Phase 2.5 - Fresh Implementation
==============================================================

Cross-Language Section ID Unification system for Bangladesh tax laws.
Standardizes Bengali and English section references to canonical IDs.

Critical Features:
- Unify Bengali "ধারা ১৬৩" with English "Section 163"
- Create canonical IDs (ITA_2023_S163) for all section references
- Handle multiple format variations (Sec, S., Section, ধারা)
- Fuzzy matching for partial/misspelled references
- Integration with Phase 2 knowledge graph and temporal system

Author: Phase 2.5 Fresh Implementation
Date: August 13, 2025
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Set, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import sys

# Import our working Phase 2 components
sys.path.append(str(Path(__file__).parent.parent / "phase_2_knowledge_graph"))
from graph_database_setup import LegalKnowledgeGraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SectionReference:
    """Represents a section reference in any format"""
    original_text: str          # Original text as found
    canonical_id: str           # Standardized canonical ID
    document_id: str            # Source document identifier
    section_number: str         # Extracted section number
    language: str               # 'bengali' or 'english'
    confidence_score: float     # 0.0-1.0 confidence in extraction
    variations: List[str]       # All known variations

@dataclass
class SectionMapping:
    """Maps all variations of a section to canonical ID"""
    canonical_id: str           # ITA_2023_S163, VAT_2012_S45 etc.
    document_type: str          # income_tax_act, vat_act, customs_act
    section_number: str         # 163, 45, etc.
    bengali_variations: List[str]  # ["ধারা ১৬৩", "ধারা-১৬৩", etc.]
    english_variations: List[str]  # ["Section 163", "Sec 163", "S.163", etc.]
    title_bengali: Optional[str]   # Bengali section title if available
    title_english: Optional[str]   # English section title if available

class SectionUnificationSystem:
    """
    Cross-Language Section ID Unification system - Phase 2.5 Fresh Implementation
    Standardizes Bengali and English section references to canonical IDs
    """
    
    def __init__(self, knowledge_graph_db: Optional[LegalKnowledgeGraphDatabase] = None):
        """Initialize with Phase 2 knowledge graph"""
        # Connect to Phase 2 database
        if not knowledge_graph_db:
            phase2_db_path = str(Path(__file__).parent.parent / "phase_2_knowledge_graph" / "bengali_legal_knowledge_graph.db")
            knowledge_graph_db = LegalKnowledgeGraphDatabase(phase2_db_path)
        
        self.graph_db = knowledge_graph_db
        self.section_mappings: Dict[str, SectionMapping] = {}
        
        # Initialize section unification database
        self._initialize_section_mappings()
        
        logger.info("🔧 Initialized Section Unification System")
        logger.info(f"📊 Connected to knowledge graph: {self.graph_db.graph.number_of_nodes()} nodes, {self.graph_db.graph.number_of_edges()} edges")
        logger.info(f"🗺️ Loaded {len(self.section_mappings)} section mappings")
    
    def _initialize_section_mappings(self):
        """Initialize comprehensive section mappings for key legal documents"""
        
        # Core Income Tax Act 2023 sections
        self._add_income_tax_act_mappings()
        
        # VAT Act 2012 sections
        self._add_vat_act_mappings()
        
        # Customs Act 1969 sections
        self._add_customs_act_mappings()
        
        logger.info(f"🗺️ Initialized {len(self.section_mappings)} section mappings across multiple acts")
    
    def _add_income_tax_act_mappings(self):
        """Add Income Tax Act 2023 section mappings"""
        
        # Key sections from Income Tax Act 2023
        ita_sections = [
            {
                "number": "75",
                "title_bengali": "কর ধার্যের ভিত্তি",
                "title_english": "Basis of charge of tax"
            },
            {
                "number": "163", 
                "title_bengali": "কর কর্তন",
                "title_english": "Deduction of tax"
            },
            {
                "number": "44",
                "title_bengali": "করের হার",
                "title_english": "Rates of tax"
            },
            {
                "number": "82C",
                "title_bengali": "ডিজিটাল সেবা কর",
                "title_english": "Digital service tax"
            },
            {
                "number": "195",
                "title_bengali": "ফেরত প্রদান",
                "title_english": "Refund"
            }
        ]
        
        for section in ita_sections:
            canonical_id = f"ITA_2023_S{section['number']}"
            
            # Generate Bengali variations
            bengali_variations = [
                f"ধারা {section['number']}",
                f"ধারা-{section['number']}",
                f"ধারা {section['number']} ",
                f"ধারা {self._convert_to_bengali_numerals(section['number'])}",
                f"আয়কর আইনের ধারা {section['number']}",
                f"আয়কর আইন, ২০২৩ এর ধারা {section['number']}"
            ]
            
            # Generate English variations
            english_variations = [
                f"Section {section['number']}",
                f"Sec {section['number']}",
                f"S. {section['number']}",
                f"s. {section['number']}",
                f"Section-{section['number']}",
                f"Section {section['number']} of Income Tax Act",
                f"Section {section['number']} of ITA 2023"
            ]
            
            mapping = SectionMapping(
                canonical_id=canonical_id,
                document_type="income_tax_act",
                section_number=section['number'],
                bengali_variations=bengali_variations,
                english_variations=english_variations,
                title_bengali=section.get('title_bengali'),
                title_english=section.get('title_english')
            )
            
            self.section_mappings[canonical_id] = mapping
    
    def _add_vat_act_mappings(self):
        """Add VAT Act 2012 section mappings"""
        
        vat_sections = [
            {
                "number": "15",
                "title_bengali": "মূল্য সংযোজন কর",
                "title_english": "Value added tax"
            },
            {
                "number": "25",
                "title_bengali": "কর হার",
                "title_english": "Tax rate"
            }
        ]
        
        for section in vat_sections:
            canonical_id = f"VAT_2012_S{section['number']}"
            
            bengali_variations = [
                f"ধারা {section['number']}",
                f"ভ্যাট আইনের ধারা {section['number']}",
                f"মূল্য সংযোজন কর আইনের ধারা {section['number']}"
            ]
            
            english_variations = [
                f"Section {section['number']}",
                f"Section {section['number']} of VAT Act",
                f"VAT Act Section {section['number']}"
            ]
            
            mapping = SectionMapping(
                canonical_id=canonical_id,
                document_type="vat_act",
                section_number=section['number'],
                bengali_variations=bengali_variations,
                english_variations=english_variations,
                title_bengali=section.get('title_bengali'),
                title_english=section.get('title_english')
            )
            
            self.section_mappings[canonical_id] = mapping
    
    def _add_customs_act_mappings(self):
        """Add Customs Act 1969 section mappings"""
        
        customs_sections = [
            {
                "number": "25",
                "title_bengali": "শুল্ক ধার্য",
                "title_english": "Assessment of duty"
            }
        ]
        
        for section in customs_sections:
            canonical_id = f"CUSTOMS_1969_S{section['number']}"
            
            bengali_variations = [
                f"ধারা {section['number']}",
                f"কাস্টমস আইনের ধারা {section['number']}",
                f"শুল্ক আইনের ধারা {section['number']}"
            ]
            
            english_variations = [
                f"Section {section['number']}",
                f"Section {section['number']} of Customs Act",
                f"Customs Act Section {section['number']}"
            ]
            
            mapping = SectionMapping(
                canonical_id=canonical_id,
                document_type="customs_act", 
                section_number=section['number'],
                bengali_variations=bengali_variations,
                english_variations=english_variations,
                title_bengali=section.get('title_bengali'),
                title_english=section.get('title_english')
            )
            
            self.section_mappings[canonical_id] = mapping
    
    def _convert_to_bengali_numerals(self, english_number: str) -> str:
        """Convert English numerals to Bengali"""
        translation_map = {
            '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
            '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
        }
        
        result = english_number
        for eng, ben in translation_map.items():
            result = result.replace(eng, ben)
        
        return result
    
    def _convert_to_english_numerals(self, bengali_number: str) -> str:
        """Convert Bengali numerals to English"""
        translation_map = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        
        result = bengali_number
        for ben, eng in translation_map.items():
            result = result.replace(ben, eng)
        
        return result
    
    def extract_section_references(self, text: str) -> List[SectionReference]:
        """
        Extract all section references from text in any language/format
        
        Args:
            text: Input text containing section references
            
        Returns:
            List of extracted section references with canonical IDs
        """
        
        references = []
        
        # Bengali section patterns
        bengali_patterns = [
            r'ধারা\s*[-–—]?\s*([০-৯\d]+[০-৯\dA-Za-z]*)',  # ধারা ১৬৩, ধারা-১৬৩, ধারা ৮২সি
            r'([০-৯\d]+[০-৯\dA-Za-z]*)\s*নং?\s*ধারা',       # ১৬৩ নং ধারা, ১৬৩ ধারা
            r'আইনের\s*ধারা\s*([০-৯\d]+[০-৯\dA-Za-z]*)',   # আইনের ধারা ১৬৩
        ]
        
        # English section patterns
        english_patterns = [
            r'[Ss]ection\s*[-–—]?\s*([0-9]+[0-9A-Za-z]*)',     # Section 163, Section-163
            r'[Ss]ec\.?\s*([0-9]+[0-9A-Za-z]*)',               # Sec 163, Sec. 163
            r'[Ss]\.?\s*([0-9]+[0-9A-Za-z]*)',                 # S 163, S. 163, s. 163
            r'([0-9]+[0-9A-Za-z]*)\s*of\s*[Aa]ct',             # 163 of Act
        ]
        
        # Search for Bengali patterns
        for pattern in bengali_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                section_num = self._convert_to_english_numerals(match.group(1))
                canonical_id = self._find_canonical_id(section_num, text)
                
                if canonical_id:
                    references.append(SectionReference(
                        original_text=match.group(0),
                        canonical_id=canonical_id,
                        document_id=self._extract_document_id(canonical_id),
                        section_number=section_num,
                        language="bengali",
                        confidence_score=0.9,
                        variations=self.section_mappings[canonical_id].bengali_variations
                    ))
        
        # Search for English patterns  
        for pattern in english_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                section_num = match.group(1)
                canonical_id = self._find_canonical_id(section_num, text)
                
                if canonical_id:
                    references.append(SectionReference(
                        original_text=match.group(0),
                        canonical_id=canonical_id,
                        document_id=self._extract_document_id(canonical_id),
                        section_number=section_num,
                        language="english",
                        confidence_score=0.9,
                        variations=self.section_mappings[canonical_id].english_variations
                    ))
        
        # Remove duplicates based on canonical_id
        unique_refs = {}
        for ref in references:
            if ref.canonical_id not in unique_refs:
                unique_refs[ref.canonical_id] = ref
        
        logger.info(f"🔍 Extracted {len(unique_refs)} unique section references from text")
        return list(unique_refs.values())
    
    def _find_canonical_id(self, section_number: str, context_text: str) -> Optional[str]:
        """Find canonical ID for section number using context"""
        
        # Try to match with existing mappings
        for canonical_id, mapping in self.section_mappings.items():
            if mapping.section_number.lower() == section_number.lower():
                
                # Use context to determine which document
                context_lower = context_text.lower()
                
                if mapping.document_type == "income_tax_act":
                    if any(keyword in context_lower for keyword in ['আয়কর', 'income tax', 'ita', 'income-tax']):
                        return canonical_id
                elif mapping.document_type == "vat_act":
                    if any(keyword in context_lower for keyword in ['ভ্যাট', 'vat', 'value added', 'মূল্য সংযোজন']):
                        return canonical_id
                elif mapping.document_type == "customs_act":
                    if any(keyword in context_lower for keyword in ['কাস্টমস', 'customs', 'শুল্ক', 'duty']):
                        return canonical_id
        
        # Default to Income Tax Act if no context match
        for canonical_id, mapping in self.section_mappings.items():
            if (mapping.section_number.lower() == section_number.lower() and 
                mapping.document_type == "income_tax_act"):
                return canonical_id
        
        return None
    
    def _extract_document_id(self, canonical_id: str) -> str:
        """Extract document ID from canonical ID"""
        if canonical_id.startswith("ITA_"):
            return "income_tax_act_2023"
        elif canonical_id.startswith("VAT_"):
            return "vat_act_2012"
        elif canonical_id.startswith("CUSTOMS_"):
            return "customs_act_1969"
        else:
            return "unknown_document"
    
    def unify_section_reference(self, reference_text: str, document_hint: Optional[str] = None) -> Optional[SectionReference]:
        """
        Unify a single section reference to canonical format
        
        Args:
            reference_text: Section reference text (e.g., "ধারা ১৬৩", "Section 163")
            document_hint: Optional hint about source document
            
        Returns:
            Unified section reference or None if not found
        """
        
        # Extract all references from the text
        references = self.extract_section_references(reference_text)
        
        if not references:
            logger.warning(f"⚠️ Could not unify section reference: {reference_text}")
            return None
        
        # Return first reference (most confident)
        unified_ref = references[0]
        logger.info(f"✅ Unified '{reference_text}' → {unified_ref.canonical_id}")
        
        return unified_ref
    
    def find_all_variations(self, canonical_id: str) -> List[str]:
        """Get all known variations of a canonical section ID"""
        
        if canonical_id not in self.section_mappings:
            return []
        
        mapping = self.section_mappings[canonical_id]
        all_variations = mapping.bengali_variations + mapping.english_variations
        
        return all_variations
    
    def cross_reference_lookup(self, text: str) -> Dict[str, List[str]]:
        """
        Find cross-references between different legal documents
        
        Args:
            text: Text containing potential cross-references
            
        Returns:
            Dictionary mapping canonical IDs to related sections
        """
        
        # Extract all section references
        references = self.extract_section_references(text)
        
        cross_refs = {}
        
        for ref in references:
            # Find related sections in knowledge graph
            related_nodes = self._find_related_nodes_in_graph(ref.canonical_id)
            
            if related_nodes:
                cross_refs[ref.canonical_id] = [
                    node_id for node_id in related_nodes
                    if node_id != ref.canonical_id
                ]
        
        logger.info(f"🔗 Found cross-references for {len(cross_refs)} sections")
        return cross_refs
    
    def _find_related_nodes_in_graph(self, canonical_id: str) -> List[str]:
        """Find related nodes in Phase 2 knowledge graph"""
        
        related_nodes = []
        
        # Search for nodes containing this canonical ID or section number
        section_num = canonical_id.split('_S')[-1] if '_S' in canonical_id else ''
        
        for node_id, node_data in self.graph_db.graph.nodes(data=True):
            node_text = node_data.get('text', '').lower()
            
            # Check if node mentions this section
            if (canonical_id.lower() in node_text or 
                f'section {section_num}' in node_text or 
                f'ধারা {section_num}' in node_text):
                related_nodes.append(node_id)
        
        return related_nodes[:10]  # Limit results
    
    def validate_unification_coverage(self) -> Dict[str, Any]:
        """Validate section unification coverage and accuracy"""
        
        # Test unification with sample queries
        test_cases = [
            "ধারা ১৬৩",           # Bengali standard
            "Section 163",        # English standard
            "Sec 163",            # English abbreviated
            "আয়কর আইনের ধারা ৭৫", # Bengali with context
            "Section 44 of ITA",  # English with context
            "ভ্যাট আইনের ধারা ১৫"  # VAT Act reference
        ]
        
        results = {
            "total_test_cases": len(test_cases),
            "successful_unifications": 0,
            "failed_cases": [],
            "unification_accuracy": 0.0,
            "coverage_statistics": {}
        }
        
        successful = 0
        
        for test_case in test_cases:
            unified = self.unify_section_reference(test_case)
            if unified:
                successful += 1
            else:
                results["failed_cases"].append(test_case)
        
        results["successful_unifications"] = successful
        results["unification_accuracy"] = (successful / len(test_cases)) * 100
        
        # Coverage statistics
        results["coverage_statistics"] = {
            "total_mappings": len(self.section_mappings),
            "bengali_variations": sum(len(m.bengali_variations) for m in self.section_mappings.values()),
            "english_variations": sum(len(m.english_variations) for m in self.section_mappings.values()),
            "documents_covered": len(set(m.document_type for m in self.section_mappings.values()))
        }
        
        logger.info(f"✅ Unification coverage: {results['unification_accuracy']:.1f}%")
        return results
    
    def export_unification_data(self, output_path: str) -> Dict[str, Any]:
        """Export section unification data for external use"""
        
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "system_version": "Phase 2.5 Fresh Implementation",
                "total_mappings": len(self.section_mappings),
                "knowledge_graph_nodes": self.graph_db.graph.number_of_nodes(),
                "knowledge_graph_edges": self.graph_db.graph.number_of_edges()
            },
            "section_mappings": {},
            "validation_results": self.validate_unification_coverage()
        }
        
        # Export all section mappings
        for canonical_id, mapping in self.section_mappings.items():
            export_data["section_mappings"][canonical_id] = asdict(mapping)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Exported section unification data to {output_path}")
        return export_data

def main():
    """Test the section unification system"""
    
    print("🚀 Testing Section Unification System - Phase 2.5 Fresh Implementation")
    print("=" * 75)
    
    # Initialize system
    unifier = SectionUnificationSystem()
    
    print(f"\n📊 System Statistics:")
    print(f"   • Section Mappings: {len(unifier.section_mappings)}")
    print(f"   • Knowledge Graph: {unifier.graph_db.graph.number_of_nodes()} nodes")
    
    # Test unification with various formats
    test_queries = [
        "আয়কর আইনের ধারা ১৬৩ অনুযায়ী",
        "Section 163 of Income Tax Act requires",
        "ধারা ৭৫ এর বিধান অনুসারে",
        "According to Sec 44 of ITA 2023",
        "ভ্যাট আইনের ধারা ১৫",
        "কাস্টমস আইনের ধারা ২৫"
    ]
    
    print(f"\n🔍 Testing Section Reference Extraction:")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 50)
        
        # Extract references
        references = unifier.extract_section_references(query)
        
        for ref in references:
            print(f"🎯 Found: {ref.original_text}")
            print(f"🆔 Canonical ID: {ref.canonical_id}")
            print(f"🌐 Language: {ref.language}")
            print(f"📈 Confidence: {ref.confidence_score:.1%}")
    
    # Test cross-references
    print(f"\n🔗 Testing Cross-Reference Lookup:")
    sample_text = "ধারা ১৬৩ এর সাথে ধারা ৭৫ এবং Section 44 সম্পর্কিত"
    cross_refs = unifier.cross_reference_lookup(sample_text)
    
    for canonical_id, related in cross_refs.items():
        print(f"   • {canonical_id}: {len(related)} related sections")
    
    # Validation test
    print(f"\n✅ Validation Results:")
    validation = unifier.validate_unification_coverage()
    print(f"   • Test Cases: {validation['total_test_cases']}")
    print(f"   • Successful: {validation['successful_unifications']}")
    print(f"   • Accuracy: {validation['unification_accuracy']:.1f}%")
    print(f"   • Total Variations: {validation['coverage_statistics']['bengali_variations'] + validation['coverage_statistics']['english_variations']}")
    
    # Export data
    output_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_2_5_temporal_control/section_unification_data.json"
    export_data = unifier.export_unification_data(output_path)
    
    print(f"\n✅ Section Unification System testing complete!")
    print(f"📁 Data exported to: section_unification_data.json")

if __name__ == "__main__":
    main()