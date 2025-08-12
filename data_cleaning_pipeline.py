#!/usr/bin/env python3
"""
Data Cleaning Pipeline for Bangladesh Income Tax Act 2023
Production-grade cleaning to achieve 99.5% precision requirements

Author: AI Tax Lawyer System
Purpose: Clean Bengali legal text to production quality (≥95% quality score)
"""

import json
import re
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
from data_quality_assessment import BengaliTextCleaner, DataQualityAssessment, CrossReferenceValidator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CleaningResult:
    """Result of cleaning operation"""
    original_quality: float
    cleaned_quality: float
    fixes_applied: List[str]
    total_fixes: int
    success: bool

class ProductionDataCleaner:
    """Production-grade data cleaning system"""
    
    def __init__(self):
        self.cleaner = BengaliTextCleaner()
        self.assessor = DataQualityAssessment()
        
        # Enhanced legal terminology standardization
        self.legal_term_standardization = {
            # Common misspellings and variations
            'নূন্যতম কর': 'ন্যূনতম কর',
            'মিনিমাম ট্যাক্স': 'ন্যূনতম কর',
            'সর্বনিম্ন কর': 'ন্যূনতম কর',
            'মিনিমাম ট্যাক্স': 'ন্যূনতম কর',
            
            # Income variations
            'ইনকাম ট্যাক্স': 'আয়কর',
            'income tax': 'আয়কর',
            
            # Section variations
            'সেকশন': 'ধারা',
            'section': 'ধারা',
            
            # Schedule variations  
            'স্কিডিউল': 'তফসিল',
            'schedule': 'তফসিল',
            'তপসিল': 'তফসিল',
            
            # Return variations
            'রিটার্ন': 'রিটার্ন',  # Keep consistent
            'return': 'রিটার্ন',
            
            # Financial year variations
            'ফিনান্সিয়াল ইয়ার': 'অর্থবছর',
            'financial year': 'অর্থবছর',
            'FY': 'অর্থবছর',
        }
        
        # Bengali script fixes for footnote positions
        self.footnote_position_fixes = {
            'section_২': 'section_2',
            'section_৩': 'section_3', 
            'section_৪': 'section_4',
            'section_৫': 'section_5',
            'section_৬': 'section_6',
            'section_৭': 'section_7',
            'section_৮': 'section_8',
            'section_৯': 'section_9',
            'section_১০': 'section_10',
            'section_১১': 'section_11',
            'section_১২': 'section_12',
            'section_১৩': 'section_13',
            'section_১৪': 'section_14',
            'section_১৫': 'section_15',
            'section_১৬': 'section_16',
            'section_১৭': 'section_17',
            'section_১৮': 'section_18',
            'section_১৯': 'section_19',
            'section_২০': 'section_20',
            'section_২১': 'section_21',
            'section_২২': 'section_22',
            'section_২৩': 'section_23',
            'section_২৪': 'section_24',
            'section_২৫': 'section_25',
        }
        
        # Add more footnote position fixes for higher numbers
        for i in range(26, 300):
            bengali_num = self.convert_english_to_bengali_number(str(i))
            self.footnote_position_fixes[f'section_{bengali_num}'] = f'section_{i}'
    
    def convert_english_to_bengali_number(self, english_num: str) -> str:
        """Convert English number to Bengali numerals"""
        bengali_digits = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
                         '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'}
        
        result = ""
        for char in english_num:
            if char in bengali_digits:
                result += bengali_digits[char]
            else:
                result += char
        return result
    
    def fix_mixed_english_bengali_text(self, text: str) -> str:
        """Fix mixed English-Bengali text issues"""
        if not isinstance(text, str):
            return text
            
        # Fix common patterns where English words are mixed inappropriately
        fixes = [
            # Fix Partnership Act references
            (r'"অংশীদারিত্ব"\s*অর্থ\s*Partnership Act', '"অংশীদারিত্ব" অর্থ পার্টনারশিপ আইন (Partnership Act'),
            
            # Fix systematic references  
            (r'"গবেষণা ও উন্নয়ন"\s*অর্থ\s*প্রণালিবদ্ধ\s*\(systematic\)', '"গবেষণা ও উন্নয়ন" অর্থ প্রণালিবদ্ধ (systematic)'),
            
            # Fix bank references
            (r'"তফসিলি ব্যাংক"\s*অর্থ\s*Bangladesh Bank Order', '"তফসিলি ব্যাংক" অর্থ বাংলাদেশ ব্যাংক আদেশ (Bangladesh Bank Order'),
            
            # Fix firm references
            (r'"ফার্ম"\s*অর্থ\s*Partnership Act', '"ফার্ম" অর্থ পার্টনারশিপ আইন (Partnership Act'),
            
            # Fix board references  
            (r'"বোর্ড"\s*অর্থ\s*National Board of Revenue', '"বোর্ড" অর্থ জাতীয় রাজস্ব বোর্ড (National Board of Revenue'),
            
            # Fix retained earnings
            (r'সংরক্ষিত আয়\s*\(retained earnings\)', 'সংরক্ষিত আয় (retained earnings)'),
            
            # Fix accounting standards
            (r'International Accounting Standard', 'আন্তর্জাতিক অ্যাকাউন্টিং স্ট্যান্ডার্ড (International Accounting Standard'),
            
            # Fix inland ship
            (r'"নৌ-যান\s*\(Inland Ship\)"\s*এবং\s*"অভ্যন্তরীণ নৌ', '"নৌ-যান (Inland Ship)" এবং "অভ্যন্তরীণ নৌ'),
        ]
        
        for pattern, replacement in fixes:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def clean_footnote_positions(self, obj: Dict) -> Dict:
        """Clean footnote position fields to use English numbers"""
        if isinstance(obj, dict):
            cleaned_obj = {}
            for key, value in obj.items():
                if key == 'position' and isinstance(value, str):
                    # Fix Bengali numerals in footnote positions
                    cleaned_position = value
                    for bengali_pos, english_pos in self.footnote_position_fixes.items():
                        cleaned_position = cleaned_position.replace(bengali_pos, english_pos)
                    cleaned_obj[key] = cleaned_position
                elif isinstance(value, (dict, list)):
                    cleaned_obj[key] = self.clean_footnote_positions(value)
                else:
                    cleaned_obj[key] = value
            return cleaned_obj
        elif isinstance(obj, list):
            return [self.clean_footnote_positions(item) for item in obj]
        else:
            return obj
    
    def enhance_cross_references(self, legal_document: Dict) -> Dict:
        """Enhance cross-reference extraction and validation"""
        validator = CrossReferenceValidator(legal_document)
        
        def enhance_section(obj, path=""):
            if isinstance(obj, dict):
                enhanced_obj = {}
                for key, value in obj.items():
                    if key in ['text', 'content', 'description'] and isinstance(value, str):
                        # Extract and validate references
                        ref_result = validator.validate_and_extract_references(value)
                        
                        # Add cross-reference metadata
                        enhanced_obj[key] = value
                        if ref_result['valid_references']:
                            enhanced_obj[f'{key}_cross_references'] = {
                                'valid_references': ref_result['valid_references'],
                                'reference_count': len(ref_result['valid_references'])
                            }
                    elif isinstance(value, (dict, list)):
                        enhanced_obj[key] = enhance_section(value, f"{path}.{key}")
                    else:
                        enhanced_obj[key] = value
                return enhanced_obj
            elif isinstance(obj, list):
                return [enhance_section(item, f"{path}[{i}]") for i, item in enumerate(obj)]
            else:
                return obj
        
        return enhance_section(legal_document)
    
    def fix_table_cell_numbering(self, obj: Dict) -> Dict:
        """Fix table cell numbering issues"""
        if isinstance(obj, dict):
            cleaned_obj = {}
            for key, value in obj.items():
                if key == 'content' and isinstance(value, str):
                    # Fix table cell numbering like "১।", "২।", etc.
                    if re.match(r'^[০-৯]+।', value.strip()):
                        # Keep Bengali numerals but ensure proper formatting
                        cleaned_content = value.strip()
                        # Ensure space after number-period
                        cleaned_content = re.sub(r'^([০-৯]+।)([^\s])', r'\1 \2', cleaned_content)
                        cleaned_obj[key] = cleaned_content
                    else:
                        cleaned_obj[key] = value
                elif isinstance(value, (dict, list)):
                    cleaned_obj[key] = self.fix_table_cell_numbering(value)
                else:
                    cleaned_obj[key] = value
            return cleaned_obj
        elif isinstance(obj, list):
            return [self.fix_table_cell_numbering(item) for item in obj]
        else:
            return obj
    
    def apply_comprehensive_cleaning(self, legal_document: Dict) -> Tuple[Dict, List[str]]:
        """Apply comprehensive cleaning to the legal document"""
        fixes_applied = []
        
        logger.info("Starting comprehensive cleaning...")
        
        def deep_clean(obj, path=""):
            nonlocal fixes_applied
            
            if isinstance(obj, dict):
                cleaned_obj = {}
                for key, value in obj.items():
                    if isinstance(value, str) and value.strip():
                        # Apply text cleaning
                        original_text = value
                        
                        # 1. Fix mixed English-Bengali issues
                        cleaned_text = self.fix_mixed_english_bengali_text(value)
                        if cleaned_text != original_text:
                            fixes_applied.append(f"Fixed mixed language text at {path}.{key}")
                        
                        # 2. Apply Bengali text cleaning
                        cleaned_text = self.cleaner.clean_bengali_text(cleaned_text)
                        
                        # 3. Standardize legal terminology
                        for wrong_term, correct_term in self.legal_term_standardization.items():
                            if wrong_term in cleaned_text:
                                cleaned_text = cleaned_text.replace(wrong_term, correct_term)
                                fixes_applied.append(f"Standardized '{wrong_term}' → '{correct_term}' at {path}.{key}")
                        
                        cleaned_obj[key] = cleaned_text
                        
                    elif isinstance(value, (dict, list)):
                        cleaned_obj[key] = deep_clean(value, f"{path}.{key}")
                    else:
                        cleaned_obj[key] = value
                
                return cleaned_obj
            
            elif isinstance(obj, list):
                return [deep_clean(item, f"{path}[{i}]") for i, item in enumerate(obj)]
            
            else:
                return obj
        
        # Apply deep cleaning
        cleaned_document = deep_clean(legal_document)
        
        # Apply specialized fixes
        logger.info("Applying specialized fixes...")
        
        # Fix footnote positions
        original_footnotes = str(cleaned_document).count('section_')
        cleaned_document = self.clean_footnote_positions(cleaned_document)
        footnote_fixes = original_footnotes - str(cleaned_document).count('section_')
        if footnote_fixes > 0:
            fixes_applied.append(f"Fixed {footnote_fixes} footnote position encodings")
        
        # Fix table cell numbering
        cleaned_document = self.fix_table_cell_numbering(cleaned_document)
        fixes_applied.append("Applied table cell numbering fixes")
        
        # Enhance cross-references
        cleaned_document = self.enhance_cross_references(cleaned_document)
        fixes_applied.append("Enhanced cross-reference extraction and validation")
        
        logger.info(f"Applied {len(fixes_applied)} fixes")
        return cleaned_document, fixes_applied
    
    def clean_legal_document(self, file_path: Path) -> CleaningResult:
        """Clean legal document to production quality"""
        logger.info(f"Starting production-grade cleaning of: {file_path}")
        
        try:
            # Load original document
            with open(file_path, 'r', encoding='utf-8') as f:
                original_document = json.load(f)
            
            # Assess original quality
            logger.info("Assessing original data quality...")
            original_report = self.assessor.assess_data_quality(original_document)
            original_quality = original_report.overall_quality
            
            logger.info(f"Original quality score: {original_quality:.1%}")
            
            if original_quality >= 0.95:
                logger.info("Document already meets production quality!")
                return CleaningResult(
                    original_quality=original_quality,
                    cleaned_quality=original_quality,
                    fixes_applied=["No fixes needed - already production ready"],
                    total_fixes=0,
                    success=True
                )
            
            # Apply comprehensive cleaning
            cleaned_document, fixes_applied = self.apply_comprehensive_cleaning(original_document)
            
            # Assess cleaned quality
            logger.info("Assessing cleaned data quality...")
            cleaned_report = self.assessor.assess_data_quality(cleaned_document)
            cleaned_quality = cleaned_report.overall_quality
            
            logger.info(f"Cleaned quality score: {cleaned_quality:.1%}")
            
            # Save cleaned document
            cleaned_file_path = file_path.parent / f"{file_path.stem}_production_ready.json"
            with open(cleaned_file_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_document, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved cleaned document to: {cleaned_file_path}")
            
            # Save cleaning report
            cleaning_report = {
                "cleaning_date": "2025-01-15",
                "source_file": str(file_path),
                "cleaned_file": str(cleaned_file_path),
                "quality_improvement": {
                    "original_quality": original_quality,
                    "cleaned_quality": cleaned_quality,
                    "improvement": cleaned_quality - original_quality
                },
                "fixes_applied": fixes_applied,
                "total_fixes": len(fixes_applied),
                "production_ready": cleaned_quality >= 0.95,
                "original_report": {
                    "utf8_integrity": original_report.utf8_score,
                    "bengali_script_purity": original_report.bengali_score,
                    "legal_term_consistency": original_report.terminology_score,
                    "section_number_consistency": original_report.numbering_score,
                    "cross_reference_validity": original_report.reference_score,
                    "content_completeness": original_report.completeness_score
                },
                "cleaned_report": {
                    "utf8_integrity": cleaned_report.utf8_score,
                    "bengali_script_purity": cleaned_report.bengali_score,
                    "legal_term_consistency": cleaned_report.terminology_score,
                    "section_number_consistency": cleaned_report.numbering_score,
                    "cross_reference_validity": cleaned_report.reference_score,
                    "content_completeness": cleaned_report.completeness_score
                }
            }
            
            report_path = file_path.parent.parent / "precision_crossref_system_2025" / "cleaning_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(cleaning_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved cleaning report to: {report_path}")
            
            success = cleaned_quality >= 0.95
            if success:
                logger.info("✅ SUCCESS: Document cleaned to production quality!")
            else:
                logger.warning("⚠️ WARNING: Additional manual cleaning may be required")
            
            return CleaningResult(
                original_quality=original_quality,
                cleaned_quality=cleaned_quality,
                fixes_applied=fixes_applied,
                total_fixes=len(fixes_applied),
                success=success
            )
            
        except Exception as e:
            logger.error(f"Cleaning failed: {e}")
            raise

def main():
    """Run production-grade data cleaning pipeline"""
    
    # Path to the Income Tax Act file
    act_file_path = Path("/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ai-tax-lawyer-bangladesh/data/legal_documents/income_tax/income_tax_act_2023_cleaned.json")
    
    if not act_file_path.exists():
        logger.error(f"Income Tax Act file not found: {act_file_path}")
        return
    
    # Initialize cleaner
    cleaner = ProductionDataCleaner()
    
    # Clean document
    result = cleaner.clean_legal_document(act_file_path)
    
    # Print results
    print("\n" + "="*70)
    print("PRODUCTION DATA CLEANING RESULTS")
    print("="*70)
    print(f"Original Quality: {result.original_quality:.1%}")
    print(f"Cleaned Quality:  {result.cleaned_quality:.1%}")
    print(f"Improvement:     +{(result.cleaned_quality - result.original_quality):.1%}")
    print(f"Total Fixes:      {result.total_fixes}")
    print(f"Production Ready: {'✅ YES' if result.success else '❌ NO'}")
    
    print(f"\nKey Fixes Applied:")
    for i, fix in enumerate(result.fixes_applied[:10], 1):  # Show first 10 fixes
        print(f"  {i}. {fix}")
    
    if len(result.fixes_applied) > 10:
        print(f"  ... and {len(result.fixes_applied) - 10} more fixes")
    
    if result.success:
        print(f"\n🎯 RESULT: Data successfully cleaned to production quality!")
        print(f"   Ready to proceed with Phase 1 development.")
    else:
        print(f"\n⚠️ RESULT: Additional cleaning may be required.")
        print(f"   Consider manual expert review for complex issues.")
    
    print("="*70)

if __name__ == "__main__":
    main()