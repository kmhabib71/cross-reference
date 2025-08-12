#!/usr/bin/env python3
"""
Bilingual Content Standardizer - Phase 1 Task 1.3
Create bilingual section mapping and standardized content directory
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BilingualContentStandardizer:
    def __init__(self, data_dir: str, phase_dir: str):
        self.data_dir = Path(data_dir)
        self.phase_dir = Path(phase_dir)
        self.standardized_dir = self.phase_dir / "standardized_content"
        
        # Create standardized content directory
        self.standardized_dir.mkdir(exist_ok=True)
        
        # Bengali to English number mapping
        self.bengali_to_english = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        
        # English to Bengali number mapping
        self.english_to_bengali = {v: k for k, v in self.bengali_to_english.items()}
        
        # Bilingual section mapping template
        self.bilingual_mapping = {
            "section_normalization": {},
            "schedule_normalization": {},
            "rule_normalization": {},
            "legal_term_mapping": {},
            "numerical_standardization": {}
        }
    
    def convert_bengali_to_english_numbers(self, text: str) -> str:
        """Convert Bengali numerals to English"""
        result = text
        for bengali, english in self.bengali_to_english.items():
            result = result.replace(bengali, english)
        return result
    
    def convert_english_to_bengali_numbers(self, text: str) -> str:
        """Convert English numerals to Bengali"""
        result = text
        for english, bengali in self.english_to_bengali.items():
            result = result.replace(english, bengali)
        return result
    
    def extract_section_numbers(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract section numbers in both languages"""
        sections = []
        
        # Bengali section patterns
        bengali_patterns = [
            r'ধারা\s*([০-৯0-9]+)(?:[a-z০-৯]*)?',
            r'([০-৯0-9]+)\s*(?:নং|নম্বর)\s*ধারা',
        ]
        
        # English section patterns
        english_patterns = [
            r'[Ss]ection\s*([0-9]+)(?:[a-z]*)?',
            r'[Ss]ec\.?\s*([0-9]+)(?:[a-z]*)?',
        ]
        
        # Extract Bengali sections
        for pattern in bengali_patterns:
            for match in re.finditer(pattern, text):
                original = match.group(0)
                section_num = self.convert_bengali_to_english_numbers(match.group(1))
                sections.append((original, section_num, "bengali"))
        
        # Extract English sections
        for pattern in english_patterns:
            for match in re.finditer(pattern, text):
                original = match.group(0)
                section_num = match.group(1)
                sections.append((original, section_num, "english"))
        
        return sections
    
    def create_bilingual_section_mapping(self) -> Dict[str, Any]:
        """Create comprehensive bilingual section mapping"""
        logger.info("🔄 Creating bilingual section mapping...")
        
        section_mapping = {}
        schedule_mapping = {}
        rule_mapping = {}
        
        files_processed = 0
        
        for json_file in self.data_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract text content
                text_content = ""
                if isinstance(data, dict):
                    for key in ['main_content', 'content', 'text', 'body', 'sections']:
                        if key in data and data[key]:
                            text_content += str(data[key]) + " "
                else:
                    text_content = str(data)
                
                if len(text_content.strip()) < 50:
                    continue
                
                # Extract and map section numbers
                sections = self.extract_section_numbers(text_content)
                
                for original_text, section_num, language in sections:
                    if section_num not in section_mapping:
                        section_mapping[section_num] = {
                            "canonical_id": f"ITA_2023_S{section_num}",
                            "bengali_variations": set(),
                            "english_variations": set(),
                            "found_in_files": []
                        }
                    
                    if language == "bengali":
                        section_mapping[section_num]["bengali_variations"].add(original_text)
                        # Add standardized variations
                        section_mapping[section_num]["bengali_variations"].add(f"ধারা {self.convert_english_to_bengali_numbers(section_num)}")
                        section_mapping[section_num]["bengali_variations"].add(f"ধারা {section_num}")
                    else:
                        section_mapping[section_num]["english_variations"].add(original_text)
                        # Add standardized variations
                        section_mapping[section_num]["english_variations"].add(f"Section {section_num}")
                        section_mapping[section_num]["english_variations"].add(f"Sec {section_num}")
                    
                    relative_path = str(json_file.relative_to(self.data_dir))
                    if relative_path not in section_mapping[section_num]["found_in_files"]:
                        section_mapping[section_num]["found_in_files"].append(relative_path)
                
                files_processed += 1
                if files_processed % 10 == 0:
                    logger.info(f"Processed {files_processed} files for section mapping...")
                
            except Exception as e:
                logger.warning(f"Error processing {json_file}: {e}")
        
        # Convert sets to lists for JSON serialization
        for section_num in section_mapping:
            section_mapping[section_num]["bengali_variations"] = list(section_mapping[section_num]["bengali_variations"])
            section_mapping[section_num]["english_variations"] = list(section_mapping[section_num]["english_variations"])
        
        # Create legal term mapping
        legal_term_mapping = {
            "tax_terms": {
                "আয়কর": ["income tax", "income-tax"],
                "tax": ["কর"],
                "ধারা": ["section", "sec"],
                "তফসিল": ["schedule"],
                "বিধি": ["rule", "rules"],
                "আইন": ["act", "law"],
                "অধ্যাদেশ": ["ordinance"],
                "অর্থবছর": ["financial year", "FY"],
                "করদাতা": ["taxpayer", "assessee"],
                "নিবন্ধন": ["registration"],
                "রিটার্ন": ["return"],
                "নির্ধারণ": ["assessment"],
                "আপিল": ["appeal"],
                "জরিমানা": ["penalty"],
                "সুদ": ["interest"],
                "ছাড়": ["exemption", "deduction"],
                "হার": ["rate"],
                "সীমা": ["limit", "threshold"]
            },
            "procedural_terms": {
                "দাখিল": ["filing", "submission"],
                "প্রদান": ["payment"],
                "গ্রহণ": ["acceptance"],
                "অনুমোদন": ["approval"],
                "বাতিল": ["cancellation"],
                "সংশোধন": ["amendment", "modification"],
                "প্রত্যাহার": ["withdrawal"],
                "স্থগিত": ["postponement", "deferment"]
            }
        }
        
        return {
            "section_normalization": section_mapping,
            "schedule_normalization": schedule_mapping,  # To be populated similarly
            "rule_normalization": rule_mapping,  # To be populated similarly
            "legal_term_mapping": legal_term_mapping,
            "numerical_standardization": {
                "bengali_to_english": self.bengali_to_english,
                "english_to_bengali": self.english_to_bengali
            },
            "statistics": {
                "files_processed": files_processed,
                "sections_mapped": len(section_mapping),
                "total_bengali_variations": sum(len(s["bengali_variations"]) for s in section_mapping.values()),
                "total_english_variations": sum(len(s["english_variations"]) for s in section_mapping.values())
            }
        }
    
    def clean_and_standardize_content(self, content: str) -> Dict[str, str]:
        """Clean and standardize content format"""
        
        # Remove HTML/XML tags
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # Normalize whitespace
        clean_content = re.sub(r'\s+', ' ', clean_content)
        clean_content = clean_content.strip()
        
        # Standardize quotes
        clean_content = re.sub(r'["""]', '"', clean_content)
        clean_content = re.sub(r"[''']", "'", clean_content)
        
        # Standardize section references
        # Bengali: ধারা ১৬৩ → ধারা 163
        clean_content = re.sub(
            r'ধারা\s*([০-৯]+)',
            lambda m: f"ধারা {self.convert_bengali_to_english_numbers(m.group(1))}",
            clean_content
        )
        
        # Create both versions
        standardized_versions = {
            "original": content,
            "cleaned": clean_content,
            "bengali_normalized": self.convert_english_to_bengali_numbers(clean_content),
            "english_normalized": self.convert_bengali_to_english_numbers(clean_content)
        }
        
        return standardized_versions
    
    def create_standardized_content_directory(self, bilingual_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized content directory structure"""
        logger.info("📁 Creating standardized content directory...")
        
        standardization_results = {
            "directory_structure": {
                "core_acts": [],
                "schedules": [],
                "rules": [],
                "circulars": [],
                "finance_laws": []
            },
            "processing_summary": {
                "total_files_processed": 0,
                "successfully_standardized": 0,
                "files_with_errors": []
            }
        }
        
        # Create subdirectories
        for subdir in ["core_acts", "schedules", "rules", "circulars", "finance_laws"]:
            (self.standardized_dir / subdir).mkdir(exist_ok=True)
        
        for json_file in self.data_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Determine file category
                file_name = json_file.name.lower()
                relative_path = json_file.relative_to(self.data_dir)
                
                if "income-tax-act" in file_name or "income_tax_act" in file_name:
                    category = "core_acts"
                elif "schedule" in file_name:
                    category = "schedules"
                elif "tds" in file_name or "rule" in file_name:
                    category = "rules"
                elif "circular" in file_name:
                    category = "circulars"
                elif "finance" in file_name:
                    category = "finance_laws"
                else:
                    category = "core_acts"  # Default
                
                # Extract and standardize content
                text_content = ""
                if isinstance(data, dict):
                    for key in ['main_content', 'content', 'text', 'body']:
                        if key in data and data[key]:
                            text_content = str(data[key])
                            break
                
                if not text_content:
                    text_content = str(data)
                
                # Standardize content
                standardized_versions = self.clean_and_standardize_content(text_content)
                
                # Create standardized file
                standardized_data = {
                    "metadata": {
                        "original_file": str(relative_path),
                        "category": category,
                        "standardization_date": "2025-01-15",
                        "content_length": len(text_content),
                        "standardization_applied": True
                    },
                    "content_versions": standardized_versions,
                    "section_mappings": {},
                    "extracted_entities": {
                        "sections": [],
                        "schedules": [],
                        "rules": [],
                        "amounts": [],
                        "dates": []
                    }
                }
                
                # Add section mappings for this file
                sections = self.extract_section_numbers(text_content)
                for original_text, section_num, language in sections:
                    if section_num in bilingual_mapping["section_normalization"]:
                        standardized_data["section_mappings"][original_text] = {
                            "canonical_id": bilingual_mapping["section_normalization"][section_num]["canonical_id"],
                            "section_number": section_num,
                            "language": language,
                            "bengali_standard": f"ধারা {self.convert_english_to_bengali_numbers(section_num)}",
                            "english_standard": f"Section {section_num}"
                        }
                
                # Save standardized file
                output_file = self.standardized_dir / category / f"{json_file.stem}_standardized.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(standardized_data, f, ensure_ascii=False, indent=2)
                
                standardization_results["directory_structure"][category].append(str(output_file.name))
                standardization_results["processing_summary"]["successfully_standardized"] += 1
                
                standardization_results["processing_summary"]["total_files_processed"] += 1
                
                if standardization_results["processing_summary"]["total_files_processed"] % 10 == 0:
                    logger.info(f"Standardized {standardization_results['processing_summary']['total_files_processed']} files...")
                
            except Exception as e:
                logger.warning(f"Error standardizing {json_file}: {e}")
                standardization_results["processing_summary"]["files_with_errors"].append(str(json_file))
        
        return standardization_results

def main():
    """Complete Phase 1 Task 1.3: Content Standardization"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    phase_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_document_analysis"
    
    standardizer = BilingualContentStandardizer(data_dir, phase_dir)
    
    # Create bilingual mapping
    bilingual_mapping = standardizer.create_bilingual_section_mapping()
    
    # Save bilingual mapping
    mapping_output = Path(phase_dir) / "bilingual_section_mapping.json"
    with open(mapping_output, 'w', encoding='utf-8') as f:
        json.dump(bilingual_mapping, f, ensure_ascii=False, indent=2)
    
    # Create standardized content directory
    standardization_results = standardizer.create_standardized_content_directory(bilingual_mapping)
    
    # Save standardization results
    results_output = Path(phase_dir) / "content_standardization_results.json"
    with open(results_output, 'w', encoding='utf-8') as f:
        json.dump(standardization_results, f, ensure_ascii=False, indent=2)
    
    print("\n🎯 PHASE 1 TASK 1.3 COMPLETED")
    print(f"Bilingual mapping saved to: {mapping_output}")
    print(f"Standardized content directory created: {standardizer.standardized_dir}")
    print(f"Standardization results: {results_output}")
    print(f"Files processed: {bilingual_mapping['statistics']['files_processed']}")
    print(f"Sections mapped: {bilingual_mapping['statistics']['sections_mapped']}")
    print(f"Files standardized: {standardization_results['processing_summary']['successfully_standardized']}")
    print(f"Bengali variations: {bilingual_mapping['statistics']['total_bengali_variations']}")
    print(f"English variations: {bilingual_mapping['statistics']['total_english_variations']}")

if __name__ == "__main__":
    main()