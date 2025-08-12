#!/usr/bin/env python3
"""
Legal Citation Pattern Extraction System
Phase 1: Document Structure Analysis & Mapping

Extracts and analyzes citation patterns from Bangladesh legal documents
for precision cross-reference system.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalCitationExtractor:
    """Extract and analyze legal citation patterns from JSON documents"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.citation_patterns = {
            "act_reference": [
                r'([আয়কর আইন|অর্থ আইন|মূল্য সংযোজন কর ও সম্পূরক শুল্ক আইন]),?\s*([২০][২৩৪][০-৯])\s*(?:এর)?\s*([০-৯]+)(?:য়|ম|ষ্ঠ)?\s*ধারা',
                r'([আয়কর আইন|অর্থ আইন]),?\s*([১২]\d{3})\s*(?:এর)?\s*ধারা\s*([০-৯]+)',
                r'Income Tax Act,?\s*(20[2-4][0-9])\s*(?:Section|section|sec\.?)\s*([0-9]+)',
                r'Section\s*([0-9]+)\s*of\s*(?:the\s*)?Income Tax Act,?\s*(20[2-4][0-9])'
            ],
            "schedule_reference": [
                r'([০-৯]+)(?:ম|য়|ষ্ঠ)\s*তফসিল',
                r'তফসিল\s*([০-৯]+)',
                r'Schedule\s*([0-9]+)',
                r'([0-9]+)(?:st|nd|rd|th)\s*Schedule'
            ],
            "sro_reference": [
                r'এসআরও\s*নং?\s*([০-৯]+)/?([০-৯]+)',
                r'SRO\s*No\.?\s*([0-9]+)/?([0-9]+)',
                r'এস\.আর\.ও\.\s*([০-৯]+)/?([০-৯]+)'
            ],
            "circular_reference": [
                r'পরিপত্র\s*নং?\s*([০-৯]+)/?([০-৯]+)',
                r'[Cc]ircular\s*[Nn]o\.?\s*([0-9]+)/?([0-9]+)',
                r'অধ্যাদেশ\s*নং?\s*([০-৯]+)/?([০-৯]+)'
            ],
            "rules_reference": [
                r'বিধি\s*([০-৯]+)',
                r'[Rr]ule\s*([0-9]+)',
                r'TDS\s*[Rr]ule\s*([0-9]+)'
            ],
            "indirect_reference": [
                r'উক্ত\s*ধারা',
                r'সংশ্লিষ্ট\s*তফসিল',
                r'প্রযোজ্য\s*বিধি',
                r'উপরোক্ত\s*বিধান',
                r'said\s*section',
                r'relevant\s*schedule',
                r'applicable\s*rule'
            ],
            "numerical_amounts": [
                r'([০-৯]+\.?[০-৯]*)\s*লক্ষ\s*টাকা',
                r'([০-৯]+)\s*কোটি\s*টাকা',
                r'([০-৯]+\.?[০-৯]*)\s*হাজার\s*টাকা',
                r'([০-৯]+\.?[০-৯]*)\s*%\s*(?:হার)?',
                r'Tk\.?\s*([0-9,]+)',
                r'([0-9]+\.?[0-9]*)\s*%\s*rate'
            ],
            "financial_year": [
                r'([২০][২৩৪][০-৯])-([২০][২৩৪][০-৯])\s*অর্থবছর',
                r'FY\s*([2][0][2][3-9])-?([2][0][2][4-9])',
                r'([২০][২৩৪][০-৯])\s*সালের?\s*অর্থবছর'
            ]
        }
        
        self.extracted_citations = defaultdict(list)
        self.document_metadata = {}
        
    def load_document(self, file_path: Path) -> Dict:
        """Load JSON document safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return {}
    
    def extract_text_content(self, data: Dict) -> str:
        """Extract all text content from JSON structure"""
        text_content = []
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['main_content', 'content', 'text', 'description', 'title']:
                        if isinstance(value, str):
                            text_content.append(value)
                    extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
            elif isinstance(obj, str):
                # Only add if it's substantial content
                if len(obj) > 50:
                    text_content.append(obj)
        
        extract_recursive(data)
        return ' '.join(text_content)
    
    def extract_citations_from_text(self, text: str, document_name: str) -> Dict[str, List]:
        """Extract all citation patterns from text content"""
        results = defaultdict(list)
        
        for pattern_type, patterns in self.citation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.UNICODE)
                for match in matches:
                    citation_data = {
                        'text': match.group(0),
                        'groups': match.groups(),
                        'start': match.start(),
                        'end': match.end(),
                        'source_document': document_name,
                        'pattern_type': pattern_type,
                        'context': text[max(0, match.start()-100):match.end()+100]
                    }
                    results[pattern_type].append(citation_data)
        
        return dict(results)
    
    def analyze_core_documents(self) -> Dict:
        """Analyze core legal documents for citation patterns"""
        
        # Priority documents based on Phase 0 analysis
        core_documents = {
            "income_tax_act_english": "ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income-tax-act-2023-in-english.json",
            "income_tax_act_bangla": "ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income-tax-act-bangla.json", 
            "section_163_minimum_tax": "ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income-tax-act-bangla-section-163-minimum-tax.json",
            "schedules_english": "ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income-tax-schedule-english.json",
            "schedules_bangla": "ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income-tax-schedule-bangla.json",
            "finance_ordinance_2025": "ai-tax-lawyer-bangladesh/data/legal_documents/circulars/finance_ordinance_2025_cleaned.json",
            "tds_rules_2025": "ai-tax-lawyer-bangladesh/data/income_tax_comprehensive/tds_rules/tds-rules-2024-fy-2025-26-bd.json"
        }
        
        analysis_results = {
            'documents_analyzed': 0,
            'total_citations': 0,
            'citation_by_type': defaultdict(int),
            'citation_by_document': defaultdict(dict),
            'cross_references': defaultdict(set),
            'pattern_statistics': defaultdict(int)
        }
        
        for doc_key, relative_path in core_documents.items():
            full_path = self.base_path / relative_path
            
            if not full_path.exists():
                logger.warning(f"Document not found: {full_path}")
                continue
                
            logger.info(f"Analyzing {doc_key}...")
            
            # Load document
            document_data = self.load_document(full_path)
            if not document_data:
                continue
            
            # Extract text content
            text_content = self.extract_text_content(document_data)
            if not text_content:
                logger.warning(f"No text content extracted from {doc_key}")
                continue
            
            # Extract citations
            citations = self.extract_citations_from_text(text_content, doc_key)
            
            # Store results
            analysis_results['documents_analyzed'] += 1
            analysis_results['citation_by_document'][doc_key] = citations
            
            # Update statistics
            for pattern_type, pattern_citations in citations.items():
                count = len(pattern_citations)
                analysis_results['citation_by_type'][pattern_type] += count
                analysis_results['total_citations'] += count
                analysis_results['pattern_statistics'][pattern_type] += count
                
                # Build cross-reference relationships
                for citation in pattern_citations:
                    ref_key = f"{pattern_type}:{citation['text']}"
                    analysis_results['cross_references'][ref_key].add(doc_key)
        
        return analysis_results
    
    def generate_citation_registry(self, analysis_results: Dict) -> Dict:
        """Generate standardized citation registry"""
        
        registry = {
            'sections': {},
            'schedules': {},
            'rules': {},
            'sros': {},
            'circulars': {},
            'amounts': {},
            'financial_years': {},
            'indirect_references': []
        }
        
        # Process each document's citations
        for doc_name, citations in analysis_results['citation_by_document'].items():
            
            # Process act references (sections)
            for citation in citations.get('act_reference', []):
                groups = citation['groups']
                if len(groups) >= 3:
                    act_name = groups[0]
                    year = groups[1] 
                    section = groups[2]
                    
                    section_key = f"s{section}_{year}"
                    if section_key not in registry['sections']:
                        registry['sections'][section_key] = {
                            'section_number': section,
                            'act_name': act_name,
                            'year': year,
                            'bengali_variations': [],
                            'english_variations': [],
                            'referenced_in': []
                        }
                    
                    registry['sections'][section_key]['referenced_in'].append({
                        'document': doc_name,
                        'text': citation['text'],
                        'context': citation['context']
                    })
            
            # Process schedule references
            for citation in citations.get('schedule_reference', []):
                groups = citation['groups']
                if groups:
                    schedule_num = groups[0]
                    
                    schedule_key = f"sch{schedule_num}"
                    if schedule_key not in registry['schedules']:
                        registry['schedules'][schedule_key] = {
                            'schedule_number': schedule_num,
                            'bengali_variations': [],
                            'english_variations': [],
                            'referenced_in': []
                        }
                    
                    registry['schedules'][schedule_key]['referenced_in'].append({
                        'document': doc_name,
                        'text': citation['text'],
                        'context': citation['context']
                    })
            
            # Process indirect references
            for citation in citations.get('indirect_reference', []):
                registry['indirect_references'].append({
                    'text': citation['text'],
                    'document': doc_name,
                    'context': citation['context'],
                    'requires_resolution': True
                })
        
        return registry
    
    def run_analysis(self) -> Dict:
        """Run complete citation pattern analysis"""
        logger.info("Starting legal citation pattern extraction...")
        
        # Analyze core documents
        analysis_results = self.analyze_core_documents()
        
        # Generate citation registry
        citation_registry = self.generate_citation_registry(analysis_results)
        
        # Compile final results
        final_results = {
            'analysis_summary': {
                'documents_analyzed': analysis_results['documents_analyzed'],
                'total_citations_found': analysis_results['total_citations'],
                'citation_types': dict(analysis_results['citation_by_type']),
                'cross_reference_patterns': len(analysis_results['cross_references'])
            },
            'citation_registry': citation_registry,
            'detailed_analysis': analysis_results,
            'pattern_effectiveness': self._calculate_pattern_effectiveness(analysis_results)
        }
        
        logger.info(f"Analysis complete: {final_results['analysis_summary']}")
        return final_results
    
    def _calculate_pattern_effectiveness(self, analysis_results: Dict) -> Dict:
        """Calculate effectiveness of different citation patterns"""
        effectiveness = {}
        
        for pattern_type, count in analysis_results['pattern_statistics'].items():
            total_patterns = len(self.citation_patterns[pattern_type])
            avg_matches_per_pattern = count / total_patterns if total_patterns > 0 else 0
            
            effectiveness[pattern_type] = {
                'total_matches': count,
                'patterns_used': total_patterns,
                'avg_matches_per_pattern': round(avg_matches_per_pattern, 2),
                'effectiveness_score': min(1.0, avg_matches_per_pattern / 10)  # Normalize to 0-1
            }
        
        return effectiveness

def main():
    """Main execution function"""
    base_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap"
    
    extractor = LegalCitationExtractor(base_path)
    results = extractor.run_analysis()
    
    # Save results
    output_path = Path(base_path) / "precision_crossref_system_2025/phase_1_structures/citation_patterns_analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ Citation pattern analysis complete!")
    print(f"📊 Results saved to: {output_path}")
    print(f"📈 Found {results['analysis_summary']['total_citations_found']} citations across {results['analysis_summary']['documents_analyzed']} documents")

if __name__ == "__main__":
    main()