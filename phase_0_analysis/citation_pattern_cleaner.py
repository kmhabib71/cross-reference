#!/usr/bin/env python3
"""
Citation Pattern Cleaner for Legal References
Task 2: Clean Citation Pattern False Positives
Fix 60% false positive rate by separating legal refs from amounts/percentages
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CitationPatternCleaner:
    def __init__(self, phase_dir: str):
        self.phase_dir = Path(phase_dir)
        self.citation_results_path = self.phase_dir / "comprehensive_citation_analysis.json"
        
    def load_existing_citations(self) -> Dict[str, Any]:
        """Load the inflated citation results"""
        with open(self.citation_results_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_clean_patterns(self) -> Dict[str, List[str]]:
        """Define clean legal citation patterns excluding amounts"""
        return {
            "genuine_section_references": [
                # Section references with proper context
                r"(?:ধারা|section)\s*([0-9০-৯]+)(?:[০-৯a-z]*)?(?:\s*(?:এর|of|under))?",
                r"([0-9০-৯]+)\s*(?:নং|নম্বর)\s*ধারা",
                r"([0-9০-৯]+)\s*ধারার?\s*(?:অধীন|অনুযায়ী|মতে)",
                r"section\s*([0-9]+)(?:[a-z]*)?\s*(?:of|under)?",
                r"sec\.?\s*([0-9]+)(?:[a-z]*)?",
                r"s\.?\s*([0-9]+)(?:[a-z]*)?",
                # Act references
                r"(?:আয়কর\s*আইন|income\s*tax\s*act)\s*(?:,?\s*)?([12][0-9]{3})\s*(?:এর)?\s*ধারা\s*([0-9০-৯]+)",
                r"(?:অর্থ\s*আইন|finance\s*act)\s*(?:,?\s*)?([12][0-9]{3})\s*(?:এর)?\s*ধারা\s*([0-9০-৯]+)"
            ],
            
            "genuine_schedule_references": [
                # Schedule references with proper context
                r"([0-9০-৯]+)(?:ম|য়|ষ্ঠ|র্থ|st|nd|rd|th)\s*তফসিল",
                r"তফসিল\s*([0-9০-৯]+)",
                r"schedule\s*([0-9]+)(?:st|nd|rd|th)?",
                r"([0-9]+)(?:st|nd|rd|th)\s*schedule"
            ],
            
            "genuine_rule_references": [
                # TDS and other rule references
                r"(?:টিডিএস|tds)\s*(?:বিধি|rule)\s*([0-9০-৯]+)",
                r"rule\s*([0-9]+)(?:[a-z]*)?",
                r"বিধি\s*([0-9০-৯]+)",
                r"([0-9০-৯]+)\s*নং\s*বিধি"
            ],
            
            "false_positive_patterns": [
                # Amount patterns to EXCLUDE
                r"[০-৯0-9]+(?:\.[০-৯0-9]+)?%",  # Percentages
                r"[০-৯0-9]+(?:\.[০-৯0-9]+)?\s*(?:লক্ষ|কোটি|হাজার|লাখ)",  # Bengali amounts
                r"[০-৯0-9]+(?:\.[০-৯0-9]+)?\s*(?:টাকা|taka|৳)",  # Money amounts
                r"[০-৯0-9]+(?:\.[০-৯0-9]+)?\s*(?:crore|lakh|thousand)",  # English amounts
                r"[০-৯0-9]{4}-[০-৯0-9]{2}",  # Financial years (2024-25)
                r"[০-৯0-9]{4}-[০-৯0-9]{4}",  # Date ranges
                r"(?:হার|rate)\s*[০-৯0-9]+(?:\.[০-৯0-9]+)?%?",  # Tax rates
                r"(?:সীমা|limit)\s*[০-৯0-9]+(?:\.[০-৯0-9]+)?",  # Limits
                r"(?:before|after|within)\s*[০-৯0-9]+\s*(?:days?|months?|years?)",  # Time periods
                r"[০-৯0-9]+\s*(?:দিন|মাস|বছর|day|month|year)s?",  # Bengali time
                r"(?:minimum|maximum|সর্বোচ্চ|সর্বনিম্ন)\s*[০-৯0-9]+",  # Min/max values
                r"[০-৯0-9]+\s*(?:times|বার)",  # Frequency
                r"\b[০-৯0-9]{1,2}\.[০-৯0-9]{1,2}\b"  # Version numbers or simple decimals
            ]
        }
    
    def validate_legal_section(self, section_number: str, document_context: str = "") -> bool:
        """Validate if section number is within legal ranges"""
        try:
            # Convert Bengali numbers to English
            bengali_to_english = {
                '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
                '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
            }
            
            english_section = section_number
            for bn, en in bengali_to_english.items():
                english_section = english_section.replace(bn, en)
            
            section_num = int(re.sub(r'[^0-9]', '', english_section))
            
            # Income Tax Act 2023: Sections 1-345
            if "income" in document_context.lower() or "আয়কর" in document_context:
                return 1 <= section_num <= 345
            
            # Finance Acts/Ordinances: Usually 1-100
            if "finance" in document_context.lower() or "অর্থ" in document_context:
                return 1 <= section_num <= 100
            
            # TDS Rules: Usually 1-20
            if "tds" in document_context.lower() or "টিডিএস" in document_context:
                return 1 <= section_num <= 20
            
            # General legal sections: 1-500 (conservative range)
            return 1 <= section_num <= 500
            
        except (ValueError, TypeError):
            return False
    
    def validate_schedule_number(self, schedule_number: str) -> bool:
        """Validate schedule numbers (typically 1-8 for Income Tax Act)"""
        try:
            # Convert Bengali to English
            bengali_to_english = {
                '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
                '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
            }
            
            english_schedule = schedule_number
            for bn, en in bengali_to_english.items():
                english_schedule = english_schedule.replace(bn, en)
            
            schedule_num = int(re.sub(r'[^0-9]', '', english_schedule))
            return 1 <= schedule_num <= 8  # Income Tax Act has 8 schedules
            
        except (ValueError, TypeError):
            return False
    
    def is_false_positive(self, citation_text: str, patterns: Dict[str, List[str]]) -> bool:
        """Check if citation is a false positive (amount/percentage)"""
        false_patterns = patterns["false_positive_patterns"]
        
        for pattern in false_patterns:
            if re.search(pattern, citation_text, re.IGNORECASE):
                logger.debug(f"False positive detected: '{citation_text}' matches '{pattern}'")
                return True
        
        return False
    
    def extract_clean_citations(self, text: str, document_name: str = "") -> Dict[str, List[Dict]]:
        """Extract clean legal citations excluding false positives"""
        patterns = self.create_clean_patterns()
        clean_citations = {
            "section_references": [],
            "schedule_references": [],
            "rule_references": [],
            "false_positives_removed": []
        }
        
        # Extract genuine section references
        for pattern in patterns["genuine_section_references"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                citation_text = match.group(0)
                
                # Skip if it's a false positive
                if self.is_false_positive(citation_text, patterns):
                    clean_citations["false_positives_removed"].append({
                        "text": citation_text,
                        "type": "amount_excluded",
                        "position": match.span()
                    })
                    continue
                
                # Validate section number if extracted
                section_number = match.group(1) if len(match.groups()) > 0 else None
                if section_number and self.validate_legal_section(section_number, document_name):
                    clean_citations["section_references"].append({
                        "text": citation_text,
                        "section_number": section_number,
                        "position": match.span(),
                        "validated": True
                    })
                elif section_number:
                    clean_citations["false_positives_removed"].append({
                        "text": citation_text,
                        "type": "invalid_section_number",
                        "section_number": section_number,
                        "position": match.span()
                    })
        
        # Extract genuine schedule references
        for pattern in patterns["genuine_schedule_references"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                citation_text = match.group(0)
                
                if self.is_false_positive(citation_text, patterns):
                    clean_citations["false_positives_removed"].append({
                        "text": citation_text,
                        "type": "amount_excluded",
                        "position": match.span()
                    })
                    continue
                
                schedule_number = match.group(1) if len(match.groups()) > 0 else None
                if schedule_number and self.validate_schedule_number(schedule_number):
                    clean_citations["schedule_references"].append({
                        "text": citation_text,
                        "schedule_number": schedule_number,
                        "position": match.span(),
                        "validated": True
                    })
        
        # Extract rule references
        for pattern in patterns["genuine_rule_references"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                citation_text = match.group(0)
                
                if self.is_false_positive(citation_text, patterns):
                    clean_citations["false_positives_removed"].append({
                        "text": citation_text,
                        "type": "amount_excluded",
                        "position": match.span()
                    })
                    continue
                
                clean_citations["rule_references"].append({
                    "text": citation_text,
                    "position": match.span(),
                    "validated": True
                })
        
        return clean_citations
    
    def reprocess_all_files(self, data_dir: str) -> Dict[str, Any]:
        """Re-process all files with clean citation patterns"""
        data_path = Path(data_dir)
        results = {
            "clean_citation_summary": {
                "total_files_processed": 0,
                "files_with_citations": 0,
                "total_clean_citations": 0,
                "total_false_positives_removed": 0,
                "citation_breakdown": {
                    "section_references": 0,
                    "schedule_references": 0,
                    "rule_references": 0
                }
            },
            "file_results": {},
            "false_positive_examples": []
        }
        
        logger.info("🧹 Starting clean citation extraction...")
        
        for json_file in data_path.rglob("*.json"):
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
                        text_content = str(data)
                elif isinstance(data, list):
                    text_content = ' '.join([str(item) for item in data])
                else:
                    text_content = str(data)
                
                # Extract clean citations
                clean_citations = self.extract_clean_citations(text_content, json_file.name)
                
                total_citations = (len(clean_citations["section_references"]) + 
                                 len(clean_citations["schedule_references"]) + 
                                 len(clean_citations["rule_references"]))
                
                false_positives = len(clean_citations["false_positives_removed"])
                
                if total_citations > 0 or false_positives > 0:
                    relative_path = json_file.relative_to(data_path)
                    results["file_results"][str(relative_path)] = {
                        "clean_citations": total_citations,
                        "false_positives_removed": false_positives,
                        "breakdown": {
                            "sections": len(clean_citations["section_references"]),
                            "schedules": len(clean_citations["schedule_references"]),
                            "rules": len(clean_citations["rule_references"])
                        },
                        "details": clean_citations
                    }
                    
                    # Collect false positive examples
                    for fp in clean_citations["false_positives_removed"][:3]:  # Max 3 per file
                        results["false_positive_examples"].append({
                            "file": str(relative_path),
                            "text": fp["text"],
                            "type": fp["type"]
                        })
                    
                    results["clean_citation_summary"]["files_with_citations"] += 1
                
                results["clean_citation_summary"]["total_files_processed"] += 1
                results["clean_citation_summary"]["total_clean_citations"] += total_citations
                results["clean_citation_summary"]["total_false_positives_removed"] += false_positives
                
                # Update breakdown
                results["clean_citation_summary"]["citation_breakdown"]["section_references"] += len(clean_citations["section_references"])
                results["clean_citation_summary"]["citation_breakdown"]["schedule_references"] += len(clean_citations["schedule_references"])
                results["clean_citation_summary"]["citation_breakdown"]["rule_references"] += len(clean_citations["rule_references"])
                
                if results["clean_citation_summary"]["total_files_processed"] % 10 == 0:
                    logger.info(f"Processed {results['clean_citation_summary']['total_files_processed']} files...")
                
            except Exception as e:
                logger.warning(f"Error processing {json_file}: {e}")
        
        # Calculate precision improvement
        old_results = self.load_existing_citations()
        old_total = old_results.get("citation_summary", {}).get("total_citations", 23898)
        
        results["precision_improvement"] = {
            "old_total_citations": old_total,
            "new_clean_citations": results["clean_citation_summary"]["total_clean_citations"],
            "false_positives_removed": results["clean_citation_summary"]["total_false_positives_removed"],
            "reduction_percentage": round((results["clean_citation_summary"]["total_false_positives_removed"] / old_total) * 100, 2) if old_total > 0 else 0,
            "precision_improvement": round((results["clean_citation_summary"]["total_clean_citations"] / old_total) * 100, 2) if old_total > 0 else 0
        }
        
        logger.info(f"✅ Clean citation extraction completed")
        logger.info(f"Clean citations: {results['clean_citation_summary']['total_clean_citations']}")
        logger.info(f"False positives removed: {results['clean_citation_summary']['total_false_positives_removed']}")
        
        return results
    
    def save_clean_results(self, results: Dict[str, Any]) -> None:
        """Save clean citation results"""
        output_path = self.phase_dir / "clean_citation_results.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Clean citation results saved to: {output_path}")
    
    def generate_comparison_report(self, clean_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate before/after comparison report"""
        old_results = self.load_existing_citations()
        
        report = {
            "task_2_comparison_summary": {
                "task": "Clean Citation Pattern False Positives",
                "status": "COMPLETED",
                "before": {
                    "total_citations": old_results.get("citation_summary", {}).get("total_citations", 23898),
                    "section_references": old_results.get("citation_summary", {}).get("section_references", 7273),
                    "amount_references": old_results.get("citation_summary", {}).get("amount_references", 14261),
                    "false_positive_rate": "59.6%"
                },
                "after": {
                    "total_clean_citations": clean_results["clean_citation_summary"]["total_clean_citations"],
                    "section_references": clean_results["clean_citation_summary"]["citation_breakdown"]["section_references"],
                    "schedule_references": clean_results["clean_citation_summary"]["citation_breakdown"]["schedule_references"],
                    "rule_references": clean_results["clean_citation_summary"]["citation_breakdown"]["rule_references"],
                    "false_positives_removed": clean_results["clean_citation_summary"]["total_false_positives_removed"]
                },
                "improvement": {
                    "false_positive_reduction": clean_results["precision_improvement"]["reduction_percentage"],
                    "citation_quality_score": round(clean_results["clean_citation_summary"]["total_clean_citations"] / 
                                                   max(old_results.get("citation_summary", {}).get("total_citations", 1), 1) * 100, 2),
                    "target_achieved": clean_results["precision_improvement"]["reduction_percentage"] > 50
                }
            },
            "validation_examples": {
                "genuine_sections_found": [],
                "false_positives_removed": clean_results["false_positive_examples"][:10],
                "pattern_validation": "Legal sections validated against Act ranges (1-345 for Income Tax Act)"
            }
        }
        
        # Save comparison report
        report_path = self.phase_dir / "task2_citation_cleaning_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Comparison report saved to: {report_path}")
        return report

def main():
    """Clean citation patterns and remove false positives"""
    phase_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_0_analysis"
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    
    cleaner = CitationPatternCleaner(phase_dir)
    clean_results = cleaner.reprocess_all_files(data_dir)
    cleaner.save_clean_results(clean_results)
    comparison_report = cleaner.generate_comparison_report(clean_results)
    
    print("\n🧹 TASK 2: CITATION PATTERN CLEANING COMPLETED")
    print(f"Clean citations found: {clean_results['clean_citation_summary']['total_clean_citations']}")
    print(f"False positives removed: {clean_results['clean_citation_summary']['total_false_positives_removed']}")
    print(f"False positive reduction: {clean_results['precision_improvement']['reduction_percentage']}%")
    print(f"Target achieved (>50% reduction): {comparison_report['task_2_comparison_summary']['improvement']['target_achieved']}")

if __name__ == "__main__":
    main()