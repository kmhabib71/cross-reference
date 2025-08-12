#!/usr/bin/env python3
"""
Actual Citation Extractor - Apply regex patterns to get real results
Fix the false "30,762 citations" claim with actual extraction
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActualCitationExtractor:
    def __init__(self, data_dir: str, phase_dir: str):
        self.data_dir = Path(data_dir)
        self.phase_dir = Path(phase_dir)
        
        # Load the regex patterns we created
        patterns_file = self.phase_dir / "citation_patterns.json"
        with open(patterns_file, 'r', encoding='utf-8') as f:
            self.patterns_data = json.load(f)
            self.patterns = self.patterns_data["citation_patterns"]
    
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
    
    def extract_with_patterns(self, content: str, file_path: str) -> Dict[str, List[Dict]]:
        """Actually apply the regex patterns to extract citations"""
        results = {
            "sections": [],
            "schedules": [],
            "rules": [],
            "contextual": [],
            "numerical": [],
            "legal_entities": []
        }
        
        # Apply section patterns
        for pattern in self.patterns["direct_section_references"]["bengali_section"]:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                if len(match.groups()) > 0:
                    section_num = self.convert_bengali_to_english_numbers(match.group(1))
                    try:
                        # Validate section number is reasonable
                        if 1 <= int(section_num) <= 400:  # Legal range
                            results["sections"].append({
                                "text": match.group(0),
                                "section_number": section_num,
                                "type": "bengali_section",
                                "file": file_path,
                                "position": match.span()
                            })
                    except ValueError:
                        continue
        
        for pattern in self.patterns["direct_section_references"]["english_section"]:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                if len(match.groups()) > 0:
                    section_num = match.group(1)
                    try:
                        if 1 <= int(section_num) <= 400:
                            results["sections"].append({
                                "text": match.group(0),
                                "section_number": section_num,
                                "type": "english_section",
                                "file": file_path,
                                "position": match.span()
                            })
                    except ValueError:
                        continue
        
        # Apply schedule patterns
        for pattern in self.patterns["direct_section_references"]["schedule_references"]:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                if len(match.groups()) > 0:
                    schedule_num = self.convert_bengali_to_english_numbers(match.group(1))
                    try:
                        if 1 <= int(schedule_num) <= 8:  # Income Tax Act has 8 schedules
                            results["schedules"].append({
                                "text": match.group(0),
                                "schedule_number": schedule_num,
                                "file": file_path,
                                "position": match.span()
                            })
                    except ValueError:
                        continue
        
        # Apply contextual patterns
        for context_type, patterns in self.patterns["contextual_references"].items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    results["contextual"].append({
                        "text": match.group(0),
                        "context_type": context_type,
                        "file": file_path,
                        "position": match.span()
                    })
        
        # Apply numerical patterns (sample)
        if "numerical_references" in self.patterns:
            for num_type, patterns in self.patterns["numerical_references"].items():
                for pattern in patterns[:2]:  # Limit to avoid false positives
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        results["numerical"].append({
                            "text": match.group(0),
                            "number_type": num_type,
                            "file": file_path,
                            "position": match.span()
                        })
        
        return results
    
    def process_all_files(self) -> Dict[str, Any]:
        """Actually extract citations from all files"""
        logger.info("📊 Starting ACTUAL citation extraction (not fake numbers)...")
        
        extraction_results = {
            "sections": [],
            "schedules": [],
            "rules": [],
            "contextual": [],
            "numerical": [],
            "legal_entities": []
        }
        
        file_stats = {
            "files_processed": 0,
            "files_with_citations": 0,
            "files_skipped": 0
        }
        
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
                        # Try other fields
                        for key in ['text', 'body', 'sections', 'parts']:
                            if key in data and data[key]:
                                text_content += str(data[key]) + " "
                else:
                    text_content = str(data)
                
                # Skip very small files
                if len(text_content.strip()) < 50:
                    file_stats["files_skipped"] += 1
                    continue
                
                relative_path = str(json_file.relative_to(self.data_dir))
                file_citations = self.extract_with_patterns(text_content, relative_path)
                
                # Aggregate results
                file_total = 0
                for category in extraction_results:
                    extraction_results[category].extend(file_citations[category])
                    file_total += len(file_citations[category])
                
                file_stats["files_processed"] += 1
                if file_total > 0:
                    file_stats["files_with_citations"] += 1
                
                if file_stats["files_processed"] % 10 == 0:
                    logger.info(f"Processed {file_stats['files_processed']} files...")
                
            except Exception as e:
                logger.warning(f"Error processing {json_file}: {e}")
                file_stats["files_skipped"] += 1
        
        # Calculate real statistics
        total_citations = sum(len(extraction_results[category]) for category in extraction_results)
        
        final_results = {
            "extraction_summary": {
                "total_citations_found": total_citations,
                "extraction_date": "2025-08-12",
                "files_processed": file_stats["files_processed"],
                "files_with_citations": file_stats["files_with_citations"],
                "files_skipped": file_stats["files_skipped"]
            },
            "citation_breakdown": {
                "sections_found": len(extraction_results["sections"]),
                "schedules_found": len(extraction_results["schedules"]),
                "rules_found": len(extraction_results["rules"]),
                "contextual_found": len(extraction_results["contextual"]),
                "numerical_found": len(extraction_results["numerical"]),
                "legal_entities_found": len(extraction_results["legal_entities"])
            },
            "extracted_citations": extraction_results,
            "sample_citations": {
                "sections": extraction_results["sections"][:10],
                "schedules": extraction_results["schedules"][:5],
                "contextual": extraction_results["contextual"][:5]
            }
        }
        
        logger.info(f"✅ REAL citation extraction completed")
        logger.info(f"Actual citations found: {total_citations}")
        
        return final_results

def main():
    """Actually extract citations and get real numbers"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    phase_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_document_analysis"
    
    extractor = ActualCitationExtractor(data_dir, phase_dir)
    actual_results = extractor.process_all_files()
    
    # Save REAL extraction results
    output_path = Path(phase_dir) / "ACTUAL_citation_extraction_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(actual_results, f, ensure_ascii=False, indent=2)
    
    print("\n🎯 ACTUAL CITATION EXTRACTION COMPLETED")
    print(f"REAL citations found: {actual_results['extraction_summary']['total_citations_found']}")
    print(f"Files processed: {actual_results['extraction_summary']['files_processed']}")
    print(f"Sections found: {actual_results['citation_breakdown']['sections_found']}")
    print(f"Schedules found: {actual_results['citation_breakdown']['schedules_found']}")
    print(f"Contextual refs found: {actual_results['citation_breakdown']['contextual_found']}")
    print(f"Results saved to: {output_path}")
    print("\nThis replaces the fake '30,762 citations' claim with actual data.")

if __name__ == "__main__":
    main()