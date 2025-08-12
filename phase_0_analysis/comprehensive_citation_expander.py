#!/usr/bin/env python3
"""
Comprehensive Citation Pattern Expander for Phase 0
Expands citation pattern analysis to cover all 79 data files
Builds comprehensive cross-reference network for 100% precision
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveCitationExpander:
    def __init__(self, data_dir: str, phase_dir: str):
        self.data_dir = Path(data_dir)
        self.phase_dir = Path(phase_dir)
        
        # Enhanced Bengali patterns for comprehensive extraction
        self.bengali_patterns = {
            "act_references": [
                r'আয়কর আইন,?\s*([২০][২৩৪][০-৯])',
                r'অর্থ আইন,?\s*([২০][২৩৪][০-৯])',
                r'কাস্টমস আইন,?\s*([২০][২৩৪][০-৯])',
                r'মূল্য সংযোজন কর আইন,?\s*([২০][২৩৪][০-৯])',
            ],
            "section_references": [
                r'ধারা\s*([০-৯০১২৩৪৫৬৭৮৯]+)',
                r'([০-৯০১২৩৪৫৬৭৮৯]+)\s*(?:নং)?\s*ধারা',
                r'উক্ত\s+ধারা',
                r'সংশ্লিষ্ট\s+ধারা',
            ],
            "schedule_references": [
                r'([০-৯০১২৩৪৫৶৭৮৯]+)(?:ম|য়|ষ্ঠ|র্থ|ঞ্চ)\s*তফসিল',
                r'তফসিল\s*([০-৯০১২৩৪৫৬৭৮৯]+)',
                r'উক্ত\s+তফসিল',
                r'সংশ্লিষ্ট\s+তফসিল',
            ],
            "rule_references": [
                r'বিধি\s*([০-৯০১২৩৪৫৬৭৮৯]+)',
                r'([০-৯০১২৩৪৫৶৭৮৯]+)\s*(?:নং)?\s*বিধি',
                r'উৎসে\s*কর\s*বিধিমালা',
            ],
            "amount_references": [
                r'([০-৯০১২৩৪৫৶৭৮৯]+(?:\.[০-৯০১২৩৪৫৶৭৮৯]+)?)\s*(?:লক্ষ|লাখ)\s*টাকা',
                r'([০-৯০১২৩৪৫৶৭৮৯]+(?:\.[০-৯০১২৩৪৫৶৭৮৯]+)?)\s*(?:কোটি)\s*টাকা',
                r'([০-৯০১২৩৪৫৶৭৮৯]+(?:\.[০-৯০১২৩৪৫৶৭৮৯]+)?)\s*(?:%|শতাংশ)',
            ],
            "date_references": [
                r'([০-৯০১২৩৪৫৶৭৮৯]+)\s*(?:জুলাই|জানুয়ারি|ফেব্রুয়ারি|মার্চ|এপ্রিল|মে|জুন|আগস্ট|সেপ্টেম্বর|অক্টোবর|নভেম্বর|ডিসেম্বর),?\s*([২০][২৩৪][০-৯])',
                r'অর্থবছর\s*([২০][২৩৪][০-৯])-([২৩৪][০-৯])',
            ],
            "special_terms": [
                r'ন্যূনতম\s*কর',
                r'উৎসে\s*কর\s*কর্তন',
                r'করমুক্ত\s*আয়',
                r'কর\s*অব্যাহতি',
                r'কর\s*অবকাশ',
            ]
        }
        
        # Enhanced English patterns
        self.english_patterns = {
            "act_references": [
                r'Income Tax Act,?\s*(20[2-9][0-9])',
                r'Finance Act,?\s*(20[2-9][0-9])',
                r'Customs Act,?\s*(20[2-9][0-9])',
                r'Value Added Tax Act,?\s*(20[2-9][0-9])',
            ],
            "section_references": [
                r'[Ss]ection\s*([0-9]+)',
                r'[Ss]ec\.?\s*([0-9]+)',
                r'[Ss]\.\s*([0-9]+)',
                r'under section ([0-9]+)',
                r'pursuant to section ([0-9]+)',
            ],
            "schedule_references": [
                r'([0-9]+)(?:st|nd|rd|th)\s*[Ss]chedule',
                r'[Ss]chedule\s*([0-9]+)',
                r'under schedule ([0-9]+)',
            ],
            "rule_references": [
                r'[Rr]ule\s*([0-9]+)',
                r'under rule ([0-9]+)',
                r'TDS Rules',
                r'Withholding Tax Rules',
            ],
            "amount_references": [
                r'([0-9,]+(?:\.[0-9]+)?)\s*(?:lakh|lac)\s*(?:taka|BDT)',
                r'([0-9,]+(?:\.[0-9]+)?)\s*(?:crore)\s*(?:taka|BDT)',
                r'([0-9]+(?:\.[0-9]+)?)\s*(?:%|percent)',
            ],
            "date_references": [
                r'([0-9]{1,2})\s*(January|February|March|April|May|June|July|August|September|October|November|December),?\s*(20[2-9][0-9])',
                r'Financial Year\s*(20[2-9][0-9])-([2-9][0-9])',
                r'FY\s*(20[2-9][0-9])-([2-9][0-9])',
            ],
            "special_terms": [
                r'minimum tax',
                r'tax deduction at source',
                r'TDS',
                r'tax-free income',
                r'tax exemption',
                r'tax holiday',
            ]
        }
    
    def extract_citations_from_text(self, text: str, source_file: str) -> List[Dict[str, Any]]:
        """Extract comprehensive citations from text content"""
        citations = []
        
        # Process Bengali patterns
        for category, patterns in self.bengali_patterns.items():
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        citations.append({
                            "type": category,
                            "language": "bengali",
                            "pattern": pattern,
                            "match_text": match.group(0),
                            "match_groups": match.groups(),
                            "start_pos": match.start(),
                            "end_pos": match.end(),
                            "source_file": source_file,
                            "context": text[max(0, match.start()-50):match.end()+50]
                        })
                except Exception as e:
                    logger.warning(f"Error processing Bengali pattern {pattern}: {e}")
        
        # Process English patterns
        for category, patterns in self.english_patterns.items():
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        citations.append({
                            "type": category,
                            "language": "english",
                            "pattern": pattern,
                            "match_text": match.group(0),
                            "match_groups": match.groups(),
                            "start_pos": match.start(),
                            "end_pos": match.end(),
                            "source_file": source_file,
                            "context": text[max(0, match.start()-50):match.end()+50]
                        })
                except Exception as e:
                    logger.warning(f"Error processing English pattern {pattern}: {e}")
        
        return citations
    
    def process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file for comprehensive citation extraction"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract text content from various structures
            text_content = ""
            
            if "main_content" in data:
                text_content += str(data["main_content"]) + " "
            
            if "structured_content" in data:
                text_content += str(data["structured_content"]) + " "
            
            if "chapters" in data:
                for chapter in data.get("chapters", []):
                    if isinstance(chapter, dict):
                        text_content += str(chapter.get("content", "")) + " "
                    else:
                        text_content += str(chapter) + " "
            
            if "tables" in data:
                for table in data.get("tables", []):
                    if isinstance(table, dict) and "data" in table:
                        for row in table["data"]:
                            text_content += " ".join(str(cell) for cell in row) + " "
            
            # Extract citations
            citations = self.extract_citations_from_text(text_content, file_path.name)
            
            return {
                "file_path": str(file_path.relative_to(self.data_dir)),
                "citations_found": len(citations),
                "citations": citations,
                "text_length": len(text_content),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return {
                "file_path": str(file_path.relative_to(self.data_dir)),
                "error": str(e),
                "status": "failed"
            }
    
    def build_cross_reference_network(self, all_citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build comprehensive cross-reference network"""
        
        # Group citations by type and reference
        reference_network = defaultdict(lambda: {
            "referenced_in": [],
            "citation_count": 0,
            "languages": set(),
            "contexts": []
        })
        
        canonical_mappings = {}
        
        for citation in all_citations:
            # Create canonical reference ID
            ref_key = self.create_canonical_reference(citation)
            
            if ref_key:
                reference_network[ref_key]["referenced_in"].append({
                    "file": citation["source_file"],
                    "match_text": citation["match_text"],
                    "context": citation["context"],
                    "position": f"{citation['start_pos']}-{citation['end_pos']}"
                })
                reference_network[ref_key]["citation_count"] += 1
                reference_network[ref_key]["languages"].add(citation["language"])
                
                if citation["context"] not in reference_network[ref_key]["contexts"]:
                    reference_network[ref_key]["contexts"].append(citation["context"])
        
        # Convert sets to lists for JSON serialization
        for ref_key in reference_network:
            reference_network[ref_key]["languages"] = list(reference_network[ref_key]["languages"])
            reference_network[ref_key]["contexts"] = reference_network[ref_key]["contexts"][:3]  # Limit contexts
        
        return dict(reference_network)
    
    def create_canonical_reference(self, citation: Dict[str, Any]) -> str:
        """Create canonical reference ID for grouping"""
        try:
            citation_type = citation["type"]
            match_groups = citation.get("match_groups", [])
            
            if citation_type == "act_references" and match_groups:
                year = match_groups[0] if match_groups else "unknown"
                return f"ACT_{year}"
            
            elif citation_type == "section_references" and match_groups:
                section_num = match_groups[0] if match_groups else "unknown"
                # Normalize Bengali numbers
                section_num = self.normalize_bengali_number(section_num)
                return f"SECTION_{section_num}"
            
            elif citation_type == "schedule_references" and match_groups:
                schedule_num = match_groups[0] if match_groups else "unknown"
                schedule_num = self.normalize_bengali_number(schedule_num)
                return f"SCHEDULE_{schedule_num}"
            
            elif citation_type == "rule_references" and match_groups:
                rule_num = match_groups[0] if match_groups else "unknown"
                rule_num = self.normalize_bengali_number(rule_num)
                return f"RULE_{rule_num}"
            
            elif citation_type == "special_terms":
                term = citation["match_text"].lower().strip()
                if "minimum tax" in term or "ন্যূনতম কর" in term:
                    return "CONCEPT_MINIMUM_TAX"
                elif "tds" in term or "উৎসে কর" in term:
                    return "CONCEPT_TDS"
                elif "tax exemption" in term or "কর অব্যাহতি" in term:
                    return "CONCEPT_TAX_EXEMPTION"
        
        except Exception as e:
            logger.warning(f"Error creating canonical reference: {e}")
        
        return None
    
    def normalize_bengali_number(self, number_str: str) -> str:
        """Normalize Bengali numbers to English"""
        bengali_to_english = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        
        result = number_str
        for bengali, english in bengali_to_english.items():
            result = result.replace(bengali, english)
        
        return result
    
    def expand_citation_analysis(self) -> Dict[str, Any]:
        """Run comprehensive citation expansion on all files"""
        logger.info("🔍 Starting comprehensive citation pattern expansion...")
        
        # Find all JSON files
        json_files = list(self.data_dir.rglob("*.json"))
        logger.info(f"📁 Processing {len(json_files)} files for citation extraction")
        
        # Process each file
        all_file_results = []
        all_citations = []
        
        for file_path in json_files:
            logger.info(f"Processing: {file_path.relative_to(self.data_dir)}")
            file_result = self.process_single_file(file_path)
            all_file_results.append(file_result)
            
            if file_result["status"] == "success":
                all_citations.extend(file_result["citations"])
        
        # Build cross-reference network
        logger.info("🔗 Building cross-reference network...")
        cross_reference_network = self.build_cross_reference_network(all_citations)
        
        # Generate comprehensive analysis
        analysis_summary = {
            "total_files_processed": len(json_files),
            "successful_extractions": sum(1 for r in all_file_results if r["status"] == "success"),
            "total_citations_found": len(all_citations),
            "unique_references": len(cross_reference_network),
            "citation_types": self.analyze_citation_types(all_citations),
            "language_distribution": self.analyze_language_distribution(all_citations),
            "most_referenced": self.find_most_referenced(cross_reference_network)
        }
        
        # Compile final result
        comprehensive_result = {
            "analysis_summary": analysis_summary,
            "file_results": all_file_results,
            "cross_reference_network": cross_reference_network,
            "citation_patterns_used": {
                "bengali_patterns": self.bengali_patterns,
                "english_patterns": self.english_patterns
            },
            "generation_timestamp": self.get_timestamp()
        }
        
        logger.info(f"✅ Citation expansion completed:")
        logger.info(f"   Total citations: {len(all_citations)}")
        logger.info(f"   Unique references: {len(cross_reference_network)}")
        
        return comprehensive_result
    
    def analyze_citation_types(self, citations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze distribution of citation types"""
        type_counts = defaultdict(int)
        for citation in citations:
            type_counts[citation["type"]] += 1
        return dict(type_counts)
    
    def analyze_language_distribution(self, citations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze language distribution of citations"""
        lang_counts = defaultdict(int)
        for citation in citations:
            lang_counts[citation["language"]] += 1
        return dict(lang_counts)
    
    def find_most_referenced(self, network: Dict[str, Any], top_n: int = 10) -> List[Dict[str, Any]]:
        """Find most frequently referenced items"""
        references = []
        for ref_id, ref_data in network.items():
            references.append({
                "reference_id": ref_id,
                "citation_count": ref_data["citation_count"],
                "file_count": len(ref_data["referenced_in"]),
                "languages": ref_data["languages"]
            })
        
        return sorted(references, key=lambda x: x["citation_count"], reverse=True)[:top_n]
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def save_expanded_analysis(self, results: Dict[str, Any]) -> None:
        """Save comprehensive citation analysis"""
        output_path = self.phase_dir / "comprehensive_citation_analysis.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 Comprehensive citation analysis saved to: {output_path}")

def main():
    """Run comprehensive citation expansion"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    phase_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_0_analysis"
    
    expander = ComprehensiveCitationExpander(data_dir, phase_dir)
    results = expander.expand_citation_analysis()
    expander.save_expanded_analysis(results)
    
    # Print summary
    print("\n📊 COMPREHENSIVE CITATION ANALYSIS SUMMARY:")
    print(f"Files processed: {results['analysis_summary']['total_files_processed']}")
    print(f"Total citations found: {results['analysis_summary']['total_citations_found']}")
    print(f"Unique references: {results['analysis_summary']['unique_references']}")
    print(f"Citation types: {results['analysis_summary']['citation_types']}")
    print(f"Language distribution: {results['analysis_summary']['language_distribution']}")

if __name__ == "__main__":
    main()