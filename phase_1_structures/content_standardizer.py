#!/usr/bin/env python3
"""
Content Standardization System
Phase 1: Document Structure Analysis & Mapping

Normalizes content format for precise cross-language matching
and creates bilingual mapping for section references.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentStandardizer:
    """Standardize legal content format for precise matching"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        
        # Bengali-English number mappings
        self.bengali_to_english_numbers = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        
        # Bengali-English word mappings for legal terms
        self.bengali_english_mappings = {
            'legal_terms': {
                'ধারা': 'Section',
                'অনুচ্ছেদ': 'Section', 
                'তফসিল': 'Schedule',
                'বিধি': 'Rule',
                'আইন': 'Act',
                'অর্থ আইন': 'Finance Act',
                'আয়কর আইন': 'Income Tax Act',
                'অধ্যাদেশ': 'Ordinance',
                'পরিপত্র': 'Circular',
                'এসআরও': 'SRO',
                'ন্যূনতম কর': 'Minimum tax',
                'কর অব্যাহতি': 'Tax exemption',
                'উৎসে কর কর্তন': 'Tax deduction at source',
                'গ্রস প্রাপ্তি': 'Gross receipt',
                'অর্থবছর': 'Financial year',
                'করদাতা': 'Taxpayer'
            },
            'numerical_terms': {
                'একশত': '100',
                'তেষট্টি': '63',
                'চতুর্থ': '4th',
                'প্রথম': '1st', 
                'দ্বিতীয়': '2nd',
                'তৃতীয়': '3rd',
                'পঞ্চম': '5th',
                'ষষ্ঠ': '6th',
                'সপ্তম': '7th',
                'অষ্টম': '8th'
            },
            'amount_terms': {
                'লক্ষ': 'lakh',
                'কোটি': 'crore', 
                'হাজার': 'thousand',
                'টাকা': 'taka'
            }
        }
        
        # Section reference patterns for standardization
        self.section_patterns = {
            'bengali': [
                r'ধারা\s*([০-৯]+)',
                r'([০-৯]+)\s*নং\s*ধারা',
                r'([০-৯]+)\s*ধারা'
            ],
            'english': [
                r'[Ss]ection\s*([0-9]+)',
                r'[Ss]ec\.?\s*([0-9]+)',
                r's\.\s*([0-9]+)'
            ]
        }
        
        self.standardized_content = {}
        self.bilingual_mappings = {}
        
    def normalize_bengali_numbers(self, text: str) -> str:
        """Convert Bengali numerals to English numerals"""
        for bengali, english in self.bengali_to_english_numbers.items():
            text = text.replace(bengali, english)
        return text
    
    def normalize_english_numbers(self, text: str) -> str:
        """Ensure consistent English numeral format"""
        # Remove extra spaces around numbers
        text = re.sub(r'\s+(\d+)\s+', r' \1 ', text)
        return text
    
    def extract_section_references(self, text: str, language: str = 'auto') -> List[Dict]:
        """Extract and standardize section references"""
        references = []
        
        if language == 'auto':
            # Try both languages
            patterns_to_try = [
                ('bengali', self.section_patterns['bengali']),
                ('english', self.section_patterns['english'])
            ]
        else:
            patterns_to_try = [(language, self.section_patterns.get(language, []))]
        
        for lang, patterns in patterns_to_try:
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    section_num = match.group(1)
                    
                    # Normalize Bengali numbers to English
                    if lang == 'bengali':
                        section_num = self.normalize_bengali_numbers(section_num)
                    
                    references.append({
                        'original_text': match.group(0),
                        'section_number': section_num,
                        'language': lang,
                        'position': match.span(),
                        'canonical_form': f"Section {section_num}"
                    })
        
        return references
    
    def create_bilingual_section_mapping(self, documents: Dict) -> Dict:
        """Create comprehensive bilingual section mappings"""
        
        mappings = {
            'section_mappings': {},
            'schedule_mappings': {},
            'act_mappings': {},
            'cross_language_references': {}
        }
        
        # Process each document for section references
        for doc_name, doc_data in documents.items():
            
            # Extract text content
            text_content = self._extract_text_content(doc_data)
            if not text_content:
                continue
            
            # Extract section references
            section_refs = self.extract_section_references(text_content, 'auto')
            
            # Build section mappings
            for ref in section_refs:
                section_num = ref['section_number']
                
                if section_num not in mappings['section_mappings']:
                    mappings['section_mappings'][section_num] = {
                        'canonical_id': f"ITA_2023_S{section_num}",
                        'bengali_variations': [],
                        'english_variations': [],
                        'found_in_documents': []
                    }
                
                # Add variations
                if ref['language'] == 'bengali':
                    if ref['original_text'] not in mappings['section_mappings'][section_num]['bengali_variations']:
                        mappings['section_mappings'][section_num]['bengali_variations'].append(ref['original_text'])
                else:
                    if ref['original_text'] not in mappings['section_mappings'][section_num]['english_variations']:
                        mappings['section_mappings'][section_num]['english_variations'].append(ref['original_text'])
                
                # Track document occurrences
                if doc_name not in mappings['section_mappings'][section_num]['found_in_documents']:
                    mappings['section_mappings'][section_num]['found_in_documents'].append(doc_name)
        
        # Add specific important sections with manual mappings
        important_sections = {
            '163': {
                'title_bengali': 'ন্যূনতম কর',
                'title_english': 'Minimum tax',
                'bengali_variations': ['ধারা ১৬৩', 'ধারা একশত তেষট্টি', '১৬৩ নং ধারা'],
                'english_variations': ['Section 163', 'Sec 163', 's. 163'],
                'importance': 'high',
                'related_schedules': ['4'],
                'related_sections': ['88', '89', '90', '91', '92', '94', '95']
            },
            '75': {
                'title_bengali': 'রিটার্ন দাখিল',
                'title_english': 'Filing of return',
                'bengali_variations': ['ধারা ৭৫', '৭৫ নং ধারা'],
                'english_variations': ['Section 75', 'Sec 75'],
                'importance': 'high'
            },
            '25': {
                'title_bengali': 'আয় নির্ধারণের বিশেষ বিধান',
                'title_english': 'Special provisions for computation of income',
                'bengali_variations': ['ধারা ২৫', '২৫ নং ধারা'],
                'english_variations': ['Section 25', 'Sec 25'],
                'importance': 'medium'
            }
        }
        
        # Merge important sections
        for section_num, section_info in important_sections.items():
            if section_num not in mappings['section_mappings']:
                mappings['section_mappings'][section_num] = {
                    'canonical_id': f"ITA_2023_S{section_num}",
                    'bengali_variations': [],
                    'english_variations': [],
                    'found_in_documents': []
                }
            
            mappings['section_mappings'][section_num].update(section_info)
        
        return mappings
    
    def standardize_content_format(self, documents: Dict) -> Dict:
        """Standardize content format across all documents"""
        
        standardized = {
            'documents': {},
            'standardization_stats': {
                'total_documents': 0,
                'successfully_standardized': 0,
                'normalization_applied': {
                    'bengali_numbers': 0,
                    'english_numbers': 0,
                    'section_references': 0,
                    'legal_terms': 0
                }
            }
        }
        
        for doc_name, doc_data in documents.items():
            logger.info(f"Standardizing content for {doc_name}...")
            
            try:
                # Extract text content
                original_content = self._extract_text_content(doc_data)
                if not original_content:
                    continue
                
                # Apply normalizations
                normalized_content = original_content
                
                # Normalize Bengali numbers
                if re.search(r'[০-৯]', normalized_content):
                    normalized_content = self.normalize_bengali_numbers(normalized_content)
                    standardized['standardization_stats']['normalization_applied']['bengali_numbers'] += 1
                
                # Normalize English numbers
                normalized_content = self.normalize_english_numbers(normalized_content)
                standardized['standardization_stats']['normalization_applied']['english_numbers'] += 1
                
                # Extract and standardize section references
                section_refs = self.extract_section_references(normalized_content, 'auto')
                standardized['standardization_stats']['normalization_applied']['section_references'] += len(section_refs)
                
                # Apply legal term mappings
                term_mappings = 0
                for bengali_term, english_term in self.bengali_english_mappings['legal_terms'].items():
                    if bengali_term in normalized_content:
                        term_mappings += 1
                
                standardized['standardization_stats']['normalization_applied']['legal_terms'] += term_mappings
                
                # Store standardized content
                standardized['documents'][doc_name] = {
                    'original_length': len(original_content),
                    'normalized_length': len(normalized_content),
                    'section_references_found': len(section_refs),
                    'section_references': section_refs,
                    'standardized_content': normalized_content[:1000] + '...' if len(normalized_content) > 1000 else normalized_content,  # Store sample
                    'normalization_summary': {
                        'bengali_numbers_converted': bool(re.search(r'[০-৯]', original_content)),
                        'section_references_extracted': len(section_refs),
                        'legal_terms_mapped': term_mappings
                    }
                }
                
                standardized['standardization_stats']['successfully_standardized'] += 1
                
            except Exception as e:
                logger.error(f"Failed to standardize {doc_name}: {e}")
            
            standardized['standardization_stats']['total_documents'] += 1
        
        return standardized
    
    def _extract_text_content(self, data: Dict) -> str:
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
            elif isinstance(obj, str) and len(obj) > 20:
                text_content.append(obj)
        
        extract_recursive(data)
        return ' '.join(text_content)
    
    def load_core_documents(self) -> Dict:
        """Load core documents for standardization"""
        
        core_documents = {
            "income_tax_act_english": "ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income-tax-act-2023-in-english.json",
            "income_tax_act_bangla": "ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income-tax-act-bangla.json", 
            "section_163_minimum_tax": "ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income-tax-act-bangla-section-163-minimum-tax.json",
            "schedules_english": "ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income-tax-schedule-english.json",
            "schedules_bangla": "ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income-tax-schedule-bangla.json"
        }
        
        loaded_documents = {}
        
        for doc_key, relative_path in core_documents.items():
            full_path = self.base_path / relative_path
            
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        loaded_documents[doc_key] = json.load(f)
                    logger.info(f"Loaded {doc_key}")
                except Exception as e:
                    logger.error(f"Failed to load {doc_key}: {e}")
            else:
                logger.warning(f"Document not found: {full_path}")
        
        return loaded_documents
    
    def run_standardization(self) -> Dict:
        """Run complete content standardization"""
        logger.info("Starting content standardization...")
        
        # Load documents
        documents = self.load_core_documents()
        
        # Create bilingual mappings
        logger.info("Creating bilingual section mappings...")
        bilingual_mappings = self.create_bilingual_section_mapping(documents)
        
        # Standardize content format
        logger.info("Standardizing content format...")
        standardized_content = self.standardize_content_format(documents)
        
        # Compile results
        results = {
            'metadata': {
                'created_date': '2025-01-15',
                'phase': 'Phase_1_Content_Standardization',
                'version': '1.0',
                'documents_processed': len(documents)
            },
            'bilingual_mappings': bilingual_mappings,
            'standardized_content': standardized_content,
            'normalization_rules': {
                'bengali_to_english_numbers': self.bengali_to_english_numbers,
                'legal_term_mappings': self.bengali_english_mappings,
                'section_patterns': self.section_patterns
            },
            'quality_metrics': {
                'section_mappings_created': len(bilingual_mappings['section_mappings']),
                'documents_standardized': standardized_content['standardization_stats']['successfully_standardized'],
                'total_section_references': sum([
                    doc['section_references_found'] 
                    for doc in standardized_content['documents'].values()
                ])
            }
        }
        
        logger.info("Content standardization complete!")
        return results

def main():
    """Main execution function"""
    base_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap"
    
    standardizer = ContentStandardizer(base_path)
    results = standardizer.run_standardization()
    
    # Save results
    output_path = Path(base_path) / "precision_crossref_system_2025/phase_1_structures/standardized_content.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ Content standardization complete!")
    print(f"📊 Results saved to: {output_path}")
    print(f"🔗 Created {results['quality_metrics']['section_mappings_created']} section mappings")
    print(f"📈 Standardized {results['quality_metrics']['documents_standardized']} documents")
    print(f"🎯 Found {results['quality_metrics']['total_section_references']} section references")

if __name__ == "__main__":
    main()