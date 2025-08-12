#!/usr/bin/env python3
"""
Comprehensive Citation Pattern Extractor - Phase 1 Task 1.1
Create regex patterns for all citation types as required by roadmap
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveCitationPatternExtractor:
    def __init__(self, data_dir: str, phase_dir: str):
        self.data_dir = Path(data_dir)
        self.phase_dir = Path(phase_dir)
        
        # Define comprehensive regex patterns as required by roadmap
        self.citation_patterns = {
            "direct_section_references": {
                "bengali_section": [
                    r'ধারা\s*([০-৯0-9]+)(?:[a-z০-৯]*)?(?:\s*(?:এর|অনুযায়ী|মতে|অধীন))?',
                    r'([০-৯0-9]+)\s*(?:নং|নম্বর)\s*ধারা',
                    r'([০-৯0-9]+)\s*ধারার?\s*(?:অধীন|অনুযায়ী|মতে)',
                    r'আয়কর\s*আইন.*?ধারা\s*([০-৯0-9]+)',
                ],
                "english_section": [
                    r'[Ss]ection\s*([0-9]+)(?:[a-z]*)?(?:\s*(?:of|under|in))?',
                    r'[Ss]ec\.?\s*([0-9]+)(?:[a-z]*)?',
                    r's\.?\s*([0-9]+)(?:[a-z]*)?',
                    r'Income\s*Tax\s*Act.*?[Ss]ection\s*([0-9]+)',
                ],
                "schedule_references": [
                    r'([০-৯0-9]+)(?:ম|য়|ষ্ঠ|র্থ|st|nd|rd|th)?\s*তফসিল',
                    r'তফসিল\s*([০-৯0-9]+)',
                    r'[Ss]chedule\s*([0-9]+)(?:st|nd|rd|th)?',
                    r'([0-9]+)(?:st|nd|rd|th)\s*[Ss]chedule',
                ],
                "rule_references": [
                    r'(?:বিধি|Rule)\s*([০-৯0-9]+)(?:[a-z০-৯]*)?',
                    r'([০-৯0-9]+)\s*নং\s*বিধি',
                    r'(?:TDS|টিডিএস).*?(?:Rule|বিধি)\s*([০-৯0-9]+)',
                ]
            },
            "contextual_references": {
                "indirect_section": [
                    r'উক্ত\s*ধারা(?:র)?',
                    r'পূর্বোক্ত\s*ধারা(?:র)?',
                    r'সংশ্লিষ্ট\s*ধারা(?:র)?',
                    r'এই\s*ধারা(?:র)?',
                    r'(?:the|said|aforesaid)\s*section',
                    r'above\s*mentioned\s*section',
                ],
                "indirect_schedule": [
                    r'সংশ্লিষ্ট\s*তফসিল',
                    r'উক্ত\s*তফসিল',
                    r'প্রযোজ্য\s*তফসিল',
                    r'(?:the|said|applicable)\s*schedule',
                    r'relevant\s*schedule',
                ],
                "indirect_rule": [
                    r'প্রযোজ্য\s*বিধি',
                    r'সংশ্লিষ্ট\s*বিধি',
                    r'উক্ত\s*বিধি',
                    r'(?:applicable|relevant|said)\s*rule[s]?',
                ]
            },
            "numerical_references": {
                "percentages": [
                    r'([০-৯0-9]+(?:\.[০-৯0-9]+)?)\s*%',
                    r'([০-৯0-9]+(?:\.[০-৯0-9]+)?)\s*শতাংশ',
                    r'percent\s*([০-৯0-9]+(?:\.[০-৯0-9]+)?)',
                ],
                "monetary_amounts": [
                    r'([০-৯0-9]+(?:\.[০-৯0-9]+)?)\s*(?:লক্ষ|লাখ)\s*টাকা',
                    r'([০-৯0-9]+(?:\.[০-৯0-9]+)?)\s*কোটি\s*টাকা',
                    r'([০-৯0-9]+(?:\.[০-৯0-9]+)?)\s*হাজার\s*টাকা',
                    r'([০-৯0-9]+(?:\.[০-৯0-9]+)?)\s*(?:crore|lakh|thousand)',
                    r'৳\s*([০-৯0-9]+(?:,[০-৯0-9]+)*)',
                    r'BDT\s*([0-9]+(?:,[0-9]+)*)',
                ],
                "financial_years": [
                    r'([০-৯0-9]{4})-([০-৯0-9]{2,4})\s*(?:অর্থবছর|financial\s*year)',
                    r'(?:অর্থবছর|FY|financial\s*year)\s*([০-৯0-9]{4})-([০-৯0-9]{2,4})',
                    r'([০-৯0-9]{4})-([০-৯0-9]{2})',
                ],
                "dates": [
                    r'([০-৯0-9]{1,2})[\/\-]([০-৯0-9]{1,2})[\/\-]([০-৯0-9]{4})',
                    r'([০-৯0-9]{1,2})\s*(?:জানুয়ারি|ফেব্রুয়ারি|মার্চ|এপ্রিল|মে|জুন|জুলাই|আগস্ট|সেপ্টেম্বর|অক্টোবর|নভেম্বর|ডিসেম্বর)',
                    r'([0-9]{1,2})\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)',
                ]
            },
            "legal_entity_references": {
                "acts_and_laws": [
                    r'আয়কর\s*আইন\s*(?:,?\s*)?([০-৯0-9]{4})',
                    r'Income\s*Tax\s*Act\s*(?:,?\s*)?([0-9]{4})',
                    r'অর্থ\s*আইন\s*(?:,?\s*)?([০-৯0-9]{4})',
                    r'Finance\s*Act\s*(?:,?\s*)?([0-9]{4})',
                    r'অর্থ\s*অধ্যাদেশ\s*(?:,?\s*)?([০-৯0-9]{4})',
                    r'Finance\s*Ordinance\s*(?:,?\s*)?([0-9]{4})',
                ],
                "authorities": [
                    r'জাতীয়\s*রাজস্ব\s*বোর্ড',
                    r'National\s*Board\s*of\s*Revenue',
                    r'NBR',
                    r'কর\s*কমিশনার',
                    r'Tax\s*Commissioner',
                    r'আপিল\s*ট্রাইব্যুনাল',
                    r'Appeal\s*Tribunal',
                ],
                "taxpayer_categories": [
                    r'ব্যক্তি\s*করদাতা',
                    r'Individual\s*taxpayer',
                    r'কোম্পানি',
                    r'Company',
                    r'অংশীদারি\s*ব্যবসা',
                    r'Partnership',
                    r'এনজিও',
                    r'NGO',
                ]
            }
        }
    
    def convert_bengali_to_english_numbers(self, text: str) -> str:
        """Convert Bengali numerals to English"""
        bengali_to_english = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        
        result = text
        for bengali, english in bengali_to_english.items():
            result = result.replace(bengali, english)
        
        return result
    
    def extract_citations_with_patterns(self, content: str, file_path: str) -> Dict[str, List[Dict]]:
        """Extract citations using comprehensive pattern matching"""
        extracted_citations = {
            "direct_sections": [],
            "direct_schedules": [],
            "direct_rules": [],
            "contextual_references": [],
            "numerical_values": [],
            "legal_entities": []
        }
        
        # Extract direct section references
        for pattern_type, patterns in self.citation_patterns["direct_section_references"].items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    citation_text = match.group(0)
                    
                    # Extract section number if available
                    section_number = None
                    if len(match.groups()) > 0:
                        section_number = self.convert_bengali_to_english_numbers(match.group(1))
                    
                    # Get context
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end].strip()
                    
                    if pattern_type in ["bengali_section", "english_section"]:
                        extracted_citations["direct_sections"].append({
                            "text": citation_text,
                            "section_number": section_number,
                            "pattern_type": pattern_type,
                            "pattern": pattern,
                            "position": match.span(),
                            "context": context,
                            "file": file_path
                        })
                    elif "schedule" in pattern_type:
                        extracted_citations["direct_schedules"].append({
                            "text": citation_text,
                            "schedule_number": section_number,
                            "pattern_type": pattern_type,
                            "pattern": pattern,
                            "position": match.span(),
                            "context": context,
                            "file": file_path
                        })
                    elif "rule" in pattern_type:
                        extracted_citations["direct_rules"].append({
                            "text": citation_text,
                            "rule_number": section_number,
                            "pattern_type": pattern_type,
                            "pattern": pattern,
                            "position": match.span(),
                            "context": context,
                            "file": file_path
                        })
        
        # Extract contextual references
        for context_type, patterns in self.citation_patterns["contextual_references"].items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    citation_text = match.group(0)
                    start = max(0, match.start() - 150)
                    end = min(len(content), match.end() + 150)
                    context = content[start:end].strip()
                    
                    extracted_citations["contextual_references"].append({
                        "text": citation_text,
                        "context_type": context_type,
                        "pattern": pattern,
                        "position": match.span(),
                        "context": context,
                        "file": file_path
                    })
        
        # Extract numerical references
        for num_type, patterns in self.citation_patterns["numerical_references"].items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    citation_text = match.group(0)
                    
                    # Extract numerical value
                    numerical_value = None
                    if len(match.groups()) > 0:
                        numerical_value = self.convert_bengali_to_english_numbers(match.group(1))
                    
                    start = max(0, match.start() - 75)
                    end = min(len(content), match.end() + 75)
                    context = content[start:end].strip()
                    
                    extracted_citations["numerical_values"].append({
                        "text": citation_text,
                        "value": numerical_value,
                        "number_type": num_type,
                        "pattern": pattern,
                        "position": match.span(),
                        "context": context,
                        "file": file_path
                    })
        
        # Extract legal entity references
        for entity_type, patterns in self.citation_patterns["legal_entity_references"].items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    citation_text = match.group(0)
                    
                    # Extract year if available
                    year = None
                    if len(match.groups()) > 0:
                        year = self.convert_bengali_to_english_numbers(match.group(1))
                    
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end].strip()
                    
                    extracted_citations["legal_entities"].append({
                        "text": citation_text,
                        "entity_type": entity_type,
                        "year": year,
                        "pattern": pattern,
                        "position": match.span(),
                        "context": context,
                        "file": file_path
                    })
        
        return extracted_citations
    
    def process_all_documents(self) -> Dict[str, Any]:
        """Process all documents with comprehensive pattern extraction"""
        logger.info("🔍 Starting comprehensive citation pattern extraction...")
        
        all_citations = {
            "direct_sections": [],
            "direct_schedules": [],
            "direct_rules": [],
            "contextual_references": [],
            "numerical_values": [],
            "legal_entities": []
        }
        
        file_statistics = {
            "total_files_processed": 0,
            "files_with_citations": 0,
            "total_citations_found": 0
        }
        
        # Process all JSON files
        for json_file in self.data_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract text content
                text_content = ""
                if isinstance(data, dict):
                    if 'main_content' in data:
                        text_content = str(data['main_content'])
                    elif 'content' in data:
                        text_content = str(data['content'])
                    else:
                        # Try to extract from various possible fields
                        for key in ['text', 'body', 'data', 'sections', 'parts']:
                            if key in data:
                                text_content += str(data[key]) + " "
                        if not text_content:
                            text_content = str(data)
                else:
                    text_content = str(data)
                
                if len(text_content.strip()) < 50:  # Skip very small files
                    continue
                
                file_statistics["total_files_processed"] += 1
                relative_path = str(json_file.relative_to(self.data_dir))
                
                # Extract citations with patterns
                file_citations = self.extract_citations_with_patterns(text_content, relative_path)
                
                # Aggregate citations
                file_total = 0
                for category, citations in file_citations.items():
                    all_citations[category].extend(citations)
                    file_total += len(citations)
                
                if file_total > 0:
                    file_statistics["files_with_citations"] += 1
                    file_statistics["total_citations_found"] += file_total
                
                if file_statistics["total_files_processed"] % 10 == 0:
                    logger.info(f"Processed {file_statistics['total_files_processed']} files...")
                
            except Exception as e:
                logger.warning(f"Error processing {json_file}: {e}")
        
        # Create comprehensive results
        results = {
            "citation_patterns": self.citation_patterns,
            "extracted_citations": all_citations,
            "file_statistics": file_statistics,
            "pattern_statistics": {
                "direct_sections_found": len(all_citations["direct_sections"]),
                "direct_schedules_found": len(all_citations["direct_schedules"]),
                "direct_rules_found": len(all_citations["direct_rules"]),
                "contextual_references_found": len(all_citations["contextual_references"]),
                "numerical_values_found": len(all_citations["numerical_values"]),
                "legal_entities_found": len(all_citations["legal_entities"])
            }
        }
        
        logger.info(f"✅ Comprehensive citation extraction completed")
        logger.info(f"Files processed: {file_statistics['total_files_processed']}")
        logger.info(f"Total citations found: {file_statistics['total_citations_found']}")
        
        return results

def main():
    """Create comprehensive citation patterns as required by Phase 1 Task 1.1"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    phase_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_document_analysis"
    
    extractor = ComprehensiveCitationPatternExtractor(data_dir, phase_dir)
    results = extractor.process_all_documents()
    
    # Save comprehensive citation patterns
    output_path = Path(phase_dir) / "citation_patterns.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n🎯 PHASE 1 TASK 1.1 COMPLETED")
    print(f"Comprehensive citation patterns saved to: {output_path}")
    print(f"Files processed: {results['file_statistics']['total_files_processed']}")
    print(f"Total citations found: {results['file_statistics']['total_citations_found']}")
    print(f"Direct sections: {results['pattern_statistics']['direct_sections_found']}")
    print(f"Contextual references: {results['pattern_statistics']['contextual_references_found']}")
    print(f"Numerical values: {results['pattern_statistics']['numerical_values_found']}")
    print(f"Legal entities: {results['pattern_statistics']['legal_entities_found']}")

if __name__ == "__main__":
    main()