#!/usr/bin/env python3
"""
Data Quality Assessment Pipeline for Bangladesh Income Tax Act 2023
Critical foundation for achieving 99.5% precision in legal cross-referencing

Author: AI Tax Lawyer System
Purpose: Ensure data quality foundation for production-grade legal precision
"""

import json
import re
import unicodedata
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DataQualityReport:
    """Comprehensive data quality assessment report"""
    utf8_score: float = 0.0
    bengali_score: float = 0.0  
    terminology_score: float = 0.0
    numbering_score: float = 0.0
    reference_score: float = 0.0
    completeness_score: float = 0.0
    overall_quality: float = 0.0
    production_ready: bool = False
    required_fixes: List[str] = None
    
    def __post_init__(self):
        if self.required_fixes is None:
            self.required_fixes = []

@dataclass 
class DataQualityException(Exception):
    """Exception raised when data quality is insufficient"""
    pass

class BengaliTextCleaner:
    """Bengali text validation and cleaning system"""
    
    def __init__(self):
        self.bengali_numerals = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4', 
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        
        # Standardize legal terminology
        self.legal_terms_standard = {
            'নূন্যতম কর': 'ন্যূনতম কর',  # Fix common misspelling
            'মিনিমাম ট্যাক্স': 'ন্যূনতম কর',  # Standardize English mixed
            'সর্বনিম্ন কর': 'ন্যূনতম কর',   # Alternative to standard
            'আয়কর': 'আয়কর',  # Ensure consistent spelling
            'অর্থবছর': 'অর্থবছর',  # Financial year consistency
            'রিটার্ন': 'রিটার্ন',  # Return filing
            'তফসিল': 'তফসিল',  # Schedule consistency
            'ধারা': 'ধারা',  # Section consistency
        }
        
        # HTML/XML artifacts to clean
        self.html_artifacts = [
            r'&nbsp;', r'&amp;', r'&lt;', r'&gt;', r'&quot;', r'&apos;',
            r'<br/>', r'<br>', r'</br>', r'<div[^>]*>', r'</div>',
            r'<p[^>]*>', r'</p>', r'<span[^>]*>', r'</span>',
            r'<table[^>]*>', r'</table>', r'<tr[^>]*>', r'</tr>',
            r'<td[^>]*>', r'</td>', r'<th[^>]*>', r'</th>'
        ]
        
    def fix_utf8_corruption(self, text: str) -> str:
        """Fix common UTF-8 corruption in Bengali text"""
        try:
            # Try to decode if it's incorrectly encoded
            if isinstance(text, str):
                # Check for common UTF-8 corruption patterns
                corruption_fixes = {
                    'à¦§à¦¾à¦°à¦¾': 'ধারা',
                    'à§§à§¬à§©': '১৬৩',
                    'à¦¨à§‚à¦¨à§à¦¯à¦¤à¦®': 'ন্যূনতম',
                    'à¦•à¦°': 'কর',
                    'à¦†à¦¯à¦¼à¦•à¦°': 'আয়কর',
                }
                
                for corrupted, fixed in corruption_fixes.items():
                    text = text.replace(corrupted, fixed)
                    
            return text
        except Exception as e:
            logger.warning(f"UTF-8 corruption fix failed: {e}")
            return text
    
    def remove_html_artifacts(self, text: str) -> str:
        """Remove HTML/XML artifacts from text"""
        for artifact in self.html_artifacts:
            text = re.sub(artifact, ' ', text, flags=re.IGNORECASE)
        return text
    
    def is_valid_bengali_text(self, text: str) -> bool:
        """Validate Bengali script integrity"""
        if not text:
            return False
            
        # Count Bengali characters
        bengali_chars = 0
        total_chars = 0
        
        for char in text:
            if char.isspace() or char in ',.!?;:"\'()[]{}+-=0123456789':
                continue  # Skip whitespace and common punctuation
                
            total_chars += 1
            
            # Check if character is in Bengali Unicode range
            if '\u0980' <= char <= '\u09FF':
                bengali_chars += 1
            elif char.isascii() and char.isalpha():
                # English characters are acceptable in legal documents
                continue
            else:
                # Unknown character - might be corruption
                continue
        
        if total_chars == 0:
            return False
            
        # At least 70% should be Bengali characters in Bengali documents
        bengali_percentage = bengali_chars / total_chars
        return bengali_percentage >= 0.7
    
    def convert_to_bengali_numerals(self, number_str: str) -> str:
        """Convert English numerals to Bengali numerals"""
        english_to_bengali = {v: k for k, v in self.bengali_numerals.items()}
        
        result = ""
        for char in str(number_str):
            if char in english_to_bengali:
                result += english_to_bengali[char]
            else:
                result += char
        return result
    
    def clean_bengali_text(self, text: str) -> str:
        """Clean Bengali text for precise parsing"""
        if not isinstance(text, str):
            return str(text)
            
        # 1. Fix UTF-8 corruption
        text = self.fix_utf8_corruption(text)
        
        # 2. Standardize legal terminology
        for wrong, correct in self.legal_terms_standard.items():
            text = text.replace(wrong, correct)
        
        # 3. Clean HTML/XML artifacts
        text = self.remove_html_artifacts(text)
        
        # 4. Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 5. Validate Bengali script integrity
        if text and not self.is_valid_bengali_text(text):
            logger.warning(f"Bengali text validation failed: {text[:50]}...")
        
        return text
    
    def standardize_section_numbers(self, section_data: Dict) -> Dict:
        """Ensure consistent section numbering"""
        if 'number' in section_data:
            # Extract number and standardize
            number_str = str(section_data['number'])
            
            # Remove any non-numeric characters except Bengali numerals
            clean_number = re.sub(r'[^\d০-৯]', '', number_str)
            
            if clean_number:
                # Convert to English numerals for canonical ID
                english_number = clean_number
                for bengali, english in self.bengali_numerals.items():
                    english_number = english_number.replace(bengali, english)
                
                # Add standardized fields
                section_data['canonical_number'] = self.convert_to_bengali_numerals(english_number)
                section_data['english_number'] = english_number
                section_data['canonical_id'] = f"ITA_2023_S{english_number.zfill(3)}"
        
        return section_data

class CrossReferenceValidator:
    """Validate and extract cross-references from legal text"""
    
    def __init__(self, legal_act_data: Dict):
        self.act_data = legal_act_data
        self.known_sections = self.extract_all_section_numbers()
        self.known_schedules = self.extract_all_schedule_numbers()
        
        # Bengali reference patterns
        self.reference_patterns = {
            'section_direct': r'ধারা\s*([০-৯\d]+)',
            'section_english': r'Section\s*(\d+)',
            'schedule_direct': r'তফসিল\s*([০-৯\d]+)',
            'schedule_english': r'Schedule\s*(\d+)',
            'indirect_section': r'উক্ত\s+ধারা|সংশ্লিষ্ট\s+ধারা|পূর্বোক্ত\s+ধারা',
            'indirect_schedule': r'উক্ত\s+তফসিল|সংশ্লিষ্ট\s+তফসিল|পূর্বোক্ত\s+তফসিল'
        }
    
    def extract_all_section_numbers(self) -> set:
        """Extract all section numbers from the act"""
        sections = set()
        
        def extract_from_sections(section_list):
            for section in section_list:
                if 'number' in section:
                    # Normalize section number
                    number_str = str(section['number'])
                    clean_number = re.sub(r'[^\d০-৯]', '', number_str)
                    if clean_number:
                        sections.add(clean_number)
                
                # Recursively check subsections
                if 'sections' in section:
                    extract_from_sections(section['sections'])
        
        # Extract from all parts and chapters
        if 'parts' in self.act_data:
            for part in self.act_data['parts']:
                if 'sections' in part:
                    extract_from_sections(part['sections'])
                if 'chapters' in part:
                    for chapter in part['chapters']:
                        if 'sections' in chapter:
                            extract_from_sections(chapter['sections'])
        
        return sections
    
    def extract_all_schedule_numbers(self) -> set:
        """Extract all schedule numbers from the act"""
        schedules = set()
        
        # Look for schedules in various places
        def find_schedules(data, path=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    if 'schedule' in key.lower() or 'তফসিল' in str(value):
                        # Extract schedule numbers
                        schedule_matches = re.findall(r'(\d+)', str(value))
                        schedules.update(schedule_matches)
                    
                    if isinstance(value, (dict, list)):
                        find_schedules(value, f"{path}.{key}")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    find_schedules(item, f"{path}[{i}]")
        
        find_schedules(self.act_data)
        return schedules
    
    def extract_reference_patterns(self, text: str) -> List[Dict]:
        """Extract potential references from text"""
        references = []
        
        for pattern_name, pattern in self.reference_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                ref_info = {
                    'type': pattern_name,
                    'text': match.group(0),
                    'position': (match.start(), match.end()),
                    'number': match.group(1) if match.groups() else None
                }
                references.append(ref_info)
        
        return references
    
    def is_valid_reference(self, reference: Dict) -> bool:
        """Validate that reference exists in the legal document"""
        if reference['type'] in ['section_direct', 'section_english']:
            number = reference.get('number', '')
            # Normalize Bengali numerals to English
            english_number = number
            bengali_to_english = {'০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4', 
                                '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'}
            for bengali, english in bengali_to_english.items():
                english_number = english_number.replace(bengali, english)
            
            return english_number in self.known_sections
        
        elif reference['type'] in ['schedule_direct', 'schedule_english']:
            number = reference.get('number', '')
            # Convert Bengali numerals
            english_number = number
            bengali_to_english = {'০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4', 
                                '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'}
            for bengali, english in bengali_to_english.items():
                english_number = english_number.replace(bengali, english)
            
            return english_number in self.known_schedules
        
        # Indirect references need context to validate
        return True  # Assume valid for now
    
    def validate_and_extract_references(self, section_content: str) -> List[Dict]:
        """Extract and validate all cross-references in section"""
        potential_refs = self.extract_reference_patterns(section_content)
        validated_refs = []
        invalid_refs = []
        
        for ref in potential_refs:
            if self.is_valid_reference(ref):
                validated_refs.append(ref)
            else:
                invalid_refs.append(ref)
                logger.warning(f"Invalid reference found: {ref}")
        
        return {
            'valid_references': validated_refs,
            'invalid_references': invalid_refs,
            'validation_rate': len(validated_refs) / len(potential_refs) if potential_refs else 1.0
        }

class DataQualityAssessment:
    """Comprehensive data quality assessment system"""
    
    def __init__(self):
        self.quality_thresholds = {
            'utf8_integrity': 0.999,        # 99.9% valid UTF-8
            'bengali_script_purity': 0.995, # 99.5% proper Bengali
            'legal_term_consistency': 0.98, # 98% standardized terms
            'section_number_consistency': 0.99, # 99% consistent numbering
            'cross_reference_validity': 0.95,  # 95% valid references
            'content_completeness': 0.98    # 98% non-empty content
        }
        
        self.cleaner = BengaliTextCleaner()
    
    def test_utf8_integrity(self, legal_document: Dict) -> float:
        """Test UTF-8 encoding integrity"""
        total_texts = 0
        valid_utf8_texts = 0
        
        def check_utf8(obj, path=""):
            nonlocal total_texts, valid_utf8_texts
            
            if isinstance(obj, str):
                total_texts += 1
                try:
                    # Try encoding/decoding to test integrity
                    obj.encode('utf-8').decode('utf-8')
                    # Check for common corruption patterns
                    if not any(corrupt in obj for corrupt in ['à¦§à¦¾à¦°à¦¾', 'à§§à§¬à§©']):
                        valid_utf8_texts += 1
                except (UnicodeEncodeError, UnicodeDecodeError):
                    logger.warning(f"UTF-8 integrity issue at {path}")
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    check_utf8(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_utf8(item, f"{path}[{i}]")
        
        check_utf8(legal_document)
        
        if total_texts == 0:
            return 1.0
        
        score = valid_utf8_texts / total_texts
        logger.info(f"UTF-8 integrity: {score:.3f} ({valid_utf8_texts}/{total_texts})")
        return score
    
    def test_bengali_script_purity(self, legal_document: Dict) -> float:
        """Test Bengali script purity and validity"""
        bengali_texts = 0
        valid_bengali_texts = 0
        
        def check_bengali(obj, path=""):
            nonlocal bengali_texts, valid_bengali_texts
            
            if isinstance(obj, str) and obj.strip():
                # Check if text contains Bengali characters
                if any('\u0980' <= char <= '\u09FF' for char in obj):
                    bengali_texts += 1
                    if self.cleaner.is_valid_bengali_text(obj):
                        valid_bengali_texts += 1
                    else:
                        logger.warning(f"Bengali script issue at {path}: {obj[:50]}...")
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    check_bengali(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_bengali(item, f"{path}[{i}]")
        
        check_bengali(legal_document)
        
        if bengali_texts == 0:
            return 1.0
        
        score = valid_bengali_texts / bengali_texts
        logger.info(f"Bengali script purity: {score:.3f} ({valid_bengali_texts}/{bengali_texts})")
        return score
    
    def test_legal_term_consistency(self, legal_document: Dict) -> float:
        """Test standardization of legal terminology"""
        term_variations = {
            'ন্যূনতম কর': ['নূন্যতম কর', 'মিনিমাম ট্যাক্স', 'সর্বনিম্ন কর'],
            'আয়কর': ['income tax', 'ইনকাম ট্যাক্স'],
            'ধারা': ['section', 'সেকশন'],
            'তফসিল': ['schedule', 'স্কিডিউল'],
        }
        
        total_terms = 0
        consistent_terms = 0
        
        def check_consistency(obj):
            nonlocal total_terms, consistent_terms
            
            if isinstance(obj, str):
                for standard_term, variations in term_variations.items():
                    # Count standard term usage
                    standard_count = obj.count(standard_term)
                    total_terms += standard_count
                    consistent_terms += standard_count
                    
                    # Count variation usage (inconsistent)
                    for variation in variations:
                        variation_count = obj.count(variation)
                        total_terms += variation_count
                        # Don't add to consistent_terms - these are inconsistent
                        
            elif isinstance(obj, dict):
                for value in obj.values():
                    check_consistency(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_consistency(item)
        
        check_consistency(legal_document)
        
        if total_terms == 0:
            return 1.0
        
        score = consistent_terms / total_terms
        logger.info(f"Legal term consistency: {score:.3f} ({consistent_terms}/{total_terms})")
        return score
    
    def test_section_numbering(self, legal_document: Dict) -> float:
        """Test section numbering consistency"""
        section_numbers = []
        
        def extract_section_numbers(obj, path=""):
            if isinstance(obj, dict):
                if 'number' in obj and 'sections' in path.lower():
                    number_str = str(obj['number'])
                    section_numbers.append(number_str)
                
                for key, value in obj.items():
                    extract_section_numbers(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_section_numbers(item, f"{path}[{i}]")
        
        extract_section_numbers(legal_document)
        
        if not section_numbers:
            return 1.0
        
        # Check consistency (all Bengali numerals or all English numerals)
        bengali_pattern = re.compile(r'^[০-৯\s]+$')
        english_pattern = re.compile(r'^[\d\s]+$')
        
        bengali_count = sum(1 for num in section_numbers if bengali_pattern.match(num))
        english_count = sum(1 for num in section_numbers if english_pattern.match(num))
        
        # Consistency is higher format usage percentage
        consistency_score = max(bengali_count, english_count) / len(section_numbers)
        
        logger.info(f"Section numbering consistency: {consistency_score:.3f} "
                   f"(Bengali: {bengali_count}, English: {english_count})")
        return consistency_score
    
    def test_cross_references(self, legal_document: Dict) -> float:
        """Test cross-reference validity"""
        validator = CrossReferenceValidator(legal_document)
        
        total_refs = 0
        valid_refs = 0
        
        def check_references(obj):
            nonlocal total_refs, valid_refs
            
            if isinstance(obj, str) and obj.strip():
                ref_result = validator.validate_and_extract_references(obj)
                total_refs += len(ref_result['valid_references']) + len(ref_result['invalid_references'])
                valid_refs += len(ref_result['valid_references'])
                
            elif isinstance(obj, dict):
                for value in obj.values():
                    check_references(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_references(item)
        
        check_references(legal_document)
        
        if total_refs == 0:
            return 1.0
        
        score = valid_refs / total_refs
        logger.info(f"Cross-reference validity: {score:.3f} ({valid_refs}/{total_refs})")
        return score
    
    def test_content_completeness(self, legal_document: Dict) -> float:
        """Test content completeness (non-empty fields)"""
        total_content_fields = 0
        complete_fields = 0
        
        content_field_names = ['content', 'text', 'description', 'title', 'definition']
        
        def check_completeness(obj, path=""):
            nonlocal total_content_fields, complete_fields
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if any(field in key.lower() for field in content_field_names):
                        total_content_fields += 1
                        if isinstance(value, str) and value.strip():
                            complete_fields += 1
                        else:
                            logger.warning(f"Empty content field at {path}.{key}")
                    
                    if isinstance(value, (dict, list)):
                        check_completeness(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_completeness(item, f"{path}[{i}]")
        
        check_completeness(legal_document)
        
        if total_content_fields == 0:
            return 1.0
        
        score = complete_fields / total_content_fields
        logger.info(f"Content completeness: {score:.3f} ({complete_fields}/{total_content_fields})")
        return score
    
    def calculate_weighted_quality_score(self, report: DataQualityReport) -> float:
        """Calculate overall weighted quality score"""
        weights = {
            'utf8_score': 0.20,
            'bengali_score': 0.20,
            'terminology_score': 0.15,
            'numbering_score': 0.15,
            'reference_score': 0.15,
            'completeness_score': 0.15
        }
        
        weighted_sum = (
            report.utf8_score * weights['utf8_score'] +
            report.bengali_score * weights['bengali_score'] +
            report.terminology_score * weights['terminology_score'] +
            report.numbering_score * weights['numbering_score'] +
            report.reference_score * weights['reference_score'] +
            report.completeness_score * weights['completeness_score']
        )
        
        return weighted_sum
    
    def identify_required_fixes(self, report: DataQualityReport) -> List[str]:
        """Identify specific fixes needed for production readiness"""
        fixes = []
        
        if report.utf8_score < self.quality_thresholds['utf8_integrity']:
            fixes.append(f"Fix UTF-8 encoding issues (current: {report.utf8_score:.1%}, required: {self.quality_thresholds['utf8_integrity']:.1%})")
        
        if report.bengali_score < self.quality_thresholds['bengali_script_purity']:
            fixes.append(f"Fix Bengali script corruption (current: {report.bengali_score:.1%}, required: {self.quality_thresholds['bengali_script_purity']:.1%})")
        
        if report.terminology_score < self.quality_thresholds['legal_term_consistency']:
            fixes.append(f"Standardize legal terminology (current: {report.terminology_score:.1%}, required: {self.quality_thresholds['legal_term_consistency']:.1%})")
        
        if report.numbering_score < self.quality_thresholds['section_number_consistency']:
            fixes.append(f"Standardize section numbering (current: {report.numbering_score:.1%}, required: {self.quality_thresholds['section_number_consistency']:.1%})")
        
        if report.reference_score < self.quality_thresholds['cross_reference_validity']:
            fixes.append(f"Fix cross-reference validity (current: {report.reference_score:.1%}, required: {self.quality_thresholds['cross_reference_validity']:.1%})")
        
        if report.completeness_score < self.quality_thresholds['content_completeness']:
            fixes.append(f"Complete missing content fields (current: {report.completeness_score:.1%}, required: {self.quality_thresholds['content_completeness']:.1%})")
        
        return fixes
    
    def assess_data_quality(self, legal_document: Dict) -> DataQualityReport:
        """Comprehensive data quality assessment"""
        logger.info("Starting comprehensive data quality assessment...")
        
        report = DataQualityReport()
        
        # Test each quality dimension
        report.utf8_score = self.test_utf8_integrity(legal_document)
        report.bengali_score = self.test_bengali_script_purity(legal_document)
        report.terminology_score = self.test_legal_term_consistency(legal_document)
        report.numbering_score = self.test_section_numbering(legal_document)
        report.reference_score = self.test_cross_references(legal_document)
        report.completeness_score = self.test_content_completeness(legal_document)
        
        # Calculate overall quality score
        report.overall_quality = self.calculate_weighted_quality_score(report)
        
        # Determine if ready for production pipeline
        report.production_ready = report.overall_quality >= 0.95
        
        if not report.production_ready:
            report.required_fixes = self.identify_required_fixes(report)
        
        logger.info(f"Overall data quality score: {report.overall_quality:.1%}")
        logger.info(f"Production ready: {report.production_ready}")
        
        return report

def main():
    """Run data quality assessment on Income Tax Act 2023 Bengali JSON"""
    
    # Path to the main Income Tax Act file
    act_file_path = Path("/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income_tax_act_2023_cleaned.json")
    
    if not act_file_path.exists():
        logger.error(f"Income Tax Act file not found: {act_file_path}")
        return
    
    logger.info(f"Loading Income Tax Act 2023 from: {act_file_path}")
    
    try:
        with open(act_file_path, 'r', encoding='utf-8') as f:
            legal_document = json.load(f)
        
        logger.info(f"Loaded document with {len(str(legal_document))} characters")
        
        # Run comprehensive assessment
        assessor = DataQualityAssessment()
        report = assessor.assess_data_quality(legal_document)
        
        # Save detailed report
        report_path = Path("/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precision_crossref_system_2025/data_quality_report.json")
        
        report_data = {
            "assessment_date": "2025-01-15",
            "source_file": str(act_file_path),
            "quality_scores": {
                "utf8_integrity": report.utf8_score,
                "bengali_script_purity": report.bengali_score,
                "legal_term_consistency": report.terminology_score,
                "section_number_consistency": report.numbering_score,
                "cross_reference_validity": report.reference_score,
                "content_completeness": report.completeness_score,
                "overall_quality": report.overall_quality
            },
            "production_readiness": {
                "ready": report.production_ready,
                "required_fixes": report.required_fixes
            },
            "quality_thresholds": assessor.quality_thresholds,
            "recommendation": "PROCEED" if report.production_ready else "CLEAN_REQUIRED"
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Detailed report saved to: {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("DATA QUALITY ASSESSMENT SUMMARY")
        print("="*60)
        print(f"Overall Quality Score: {report.overall_quality:.1%}")
        print(f"Production Ready: {'✅ YES' if report.production_ready else '❌ NO'}")
        
        if report.required_fixes:
            print(f"\nRequired Fixes ({len(report.required_fixes)}):")
            for i, fix in enumerate(report.required_fixes, 1):
                print(f"  {i}. {fix}")
        
        print("\nDetailed Scores:")
        print(f"  UTF-8 Integrity: {report.utf8_score:.1%}")
        print(f"  Bengali Script Purity: {report.bengali_score:.1%}")
        print(f"  Legal Term Consistency: {report.terminology_score:.1%}")
        print(f"  Section Numbering: {report.numbering_score:.1%}")
        print(f"  Cross-Reference Validity: {report.reference_score:.1%}")
        print(f"  Content Completeness: {report.completeness_score:.1%}")
        
        if report.production_ready:
            print(f"\n🎯 RESULT: Data quality meets production requirements!")
            print(f"   Ready to proceed with Phase 1 development.")
        else:
            print(f"\n⚠️ RESULT: Data cleaning required before development!")
            print(f"   Must achieve ≥95% quality score for production deployment.")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        raise

if __name__ == "__main__":
    main()