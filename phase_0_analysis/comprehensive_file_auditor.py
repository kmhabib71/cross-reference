#!/usr/bin/env python3
"""
Comprehensive File Structure Auditor for Phase 0
Audits all 80+ data files for structure consistency and completeness
Ensures data quality for 100% precision target
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveFileAuditor:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.audit_results = {
            "total_files": 0,
            "successful_audits": 0,
            "failed_audits": 0,
            "structure_analysis": {},
            "content_quality": {},
            "consistency_report": {},
            "recommendations": []
        }
        
    def audit_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Audit a single JSON file for structure and content quality"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            file_audit = {
                "file_path": str(file_path.relative_to(self.data_dir)),
                "file_size": file_path.stat().st_size,
                "structure": self.analyze_structure(data),
                "content_quality": self.analyze_content_quality(data),
                "legal_elements": self.identify_legal_elements(data),
                "bilingual_support": self.check_bilingual_support(data),
                "status": "success"
            }
            
            return file_audit
            
        except json.JSONDecodeError as e:
            return {
                "file_path": str(file_path.relative_to(self.data_dir)),
                "error": f"JSON decode error: {e}",
                "status": "failed"
            }
        except Exception as e:
            return {
                "file_path": str(file_path.relative_to(self.data_dir)),
                "error": f"General error: {e}",
                "status": "failed"
            }
    
    def analyze_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the structure of a JSON file"""
        structure = {
            "top_level_keys": list(data.keys()),
            "has_main_content": "main_content" in data,
            "has_tables": "tables" in data and len(data.get("tables", [])) > 0,
            "has_forms": "forms" in data and len(data.get("forms", [])) > 0,
            "structure_type": self.classify_structure_type(data),
            "nested_levels": self.count_nested_levels(data)
        }
        
        # Content lengths
        if "main_content" in data:
            structure["main_content_length"] = len(str(data["main_content"]))
        if "tables" in data:
            structure["table_count"] = len(data["tables"])
            structure["total_table_rows"] = sum(len(table.get("data", [])) for table in data["tables"])
        
        return structure
    
    def classify_structure_type(self, data: Dict[str, Any]) -> str:
        """Classify the structure type of the document"""
        if "main_content" in data and "tables" in data:
            return "standard_legal_document"
        elif "chapters" in data or "parts" in data:
            return "hierarchical_legal_act"
        elif "structured_content" in data:
            return "enriched_content"
        elif "metadata" in data:
            return "metadata_enriched"
        else:
            return "unknown"
    
    def count_nested_levels(self, obj, level=0) -> int:
        """Count maximum nesting levels in the JSON structure"""
        if isinstance(obj, dict):
            if not obj:
                return level
            return max(self.count_nested_levels(v, level + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return level
            return max(self.count_nested_levels(item, level + 1) for item in obj)
        else:
            return level
    
    def analyze_content_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content quality metrics"""
        quality = {
            "has_meaningful_content": False,
            "content_completeness": 0.0,
            "text_quality": {},
            "data_completeness": {}
        }
        
        # Check for meaningful content
        total_text_length = 0
        if "main_content" in data:
            content = str(data["main_content"])
            total_text_length += len(content)
            quality["text_quality"]["main_content"] = {
                "length": len(content),
                "has_bengali": bool(re.search(r'[\u0980-\u09FF]', content)),
                "has_english": bool(re.search(r'[a-zA-Z]', content)),
                "has_numbers": bool(re.search(r'\d', content))
            }
        
        # Check table quality
        if "tables" in data:
            tables = data["tables"]
            quality["data_completeness"]["tables"] = {
                "count": len(tables),
                "total_rows": sum(len(table.get("data", [])) for table in tables),
                "has_headers": all("headers" in table for table in tables),
                "average_columns": sum(len(table.get("headers", [])) for table in tables) / max(len(tables), 1)
            }
        
        # Overall completeness score
        quality["has_meaningful_content"] = total_text_length > 100
        quality["content_completeness"] = min(1.0, total_text_length / 1000)  # Scale to 0-1
        
        return quality
    
    def identify_legal_elements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify legal elements in the document"""
        legal_elements = {
            "sections_found": [],
            "schedules_found": [],
            "rules_found": [],
            "citations_found": [],
            "legal_references": 0
        }
        
        # Extract text content for analysis
        text_content = ""
        if "main_content" in data:
            text_content += str(data["main_content"])
        
        # Bengali legal patterns
        bengali_patterns = {
            "sections": r'ধারা\s*([০-৯]+)',
            "schedules": r'([০-৯]+)(?:ম|য়|ষ্ঠ)\s*তফসিল',
            "rules": r'বিধি\s*([০-৯]+)',
            "acts": r'আয়কর আইন|অর্থ আইন'
        }
        
        # English legal patterns
        english_patterns = {
            "sections": r'[Ss]ection\s*([0-9]+)',
            "schedules": r'[Ss]chedule\s*([0-9]+)',
            "rules": r'[Rr]ule\s*([0-9]+)',
            "acts": r'Income Tax Act|Finance Act'
        }
        
        # Find matches
        for pattern_type, pattern in {**bengali_patterns, **english_patterns}.items():
            matches = re.findall(pattern, text_content)
            if matches:
                legal_elements[f"{pattern_type}_found"] = matches[:10]  # Limit to first 10
                legal_elements["legal_references"] += len(matches)
        
        return legal_elements
    
    def check_bilingual_support(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check bilingual content support"""
        bilingual = {
            "has_bengali": False,
            "has_english": False,
            "bengali_percentage": 0.0,
            "english_percentage": 0.0,
            "mixed_content": False
        }
        
        all_text = ""
        if "main_content" in data:
            all_text += str(data["main_content"])
        
        if all_text:
            bengali_chars = len(re.findall(r'[\u0980-\u09FF]', all_text))
            english_chars = len(re.findall(r'[a-zA-Z]', all_text))
            total_chars = len(all_text)
            
            if total_chars > 0:
                bilingual["bengali_percentage"] = bengali_chars / total_chars * 100
                bilingual["english_percentage"] = english_chars / total_chars * 100
                bilingual["has_bengali"] = bengali_chars > 0
                bilingual["has_english"] = english_chars > 0
                bilingual["mixed_content"] = bengali_chars > 0 and english_chars > 0
        
        return bilingual
    
    def generate_consistency_report(self, all_audits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate consistency report across all files"""
        successful_audits = [audit for audit in all_audits if audit["status"] == "success"]
        
        # Structure type distribution
        structure_types = defaultdict(int)
        content_patterns = defaultdict(list)
        quality_metrics = defaultdict(list)
        
        for audit in successful_audits:
            structure_type = audit["structure"]["structure_type"]
            structure_types[structure_type] += 1
            
            # Collect quality metrics
            if "content_quality" in audit:
                quality = audit["content_quality"]
                quality_metrics["content_completeness"].append(quality["content_completeness"])
                quality_metrics["has_meaningful_content"].append(quality["has_meaningful_content"])
            
            # Collect bilingual metrics
            if "bilingual_support" in audit:
                bilingual = audit["bilingual_support"]
                quality_metrics["bilingual_files"].append(bilingual["mixed_content"])
        
        consistency = {
            "structure_type_distribution": dict(structure_types),
            "quality_statistics": {
                "average_content_completeness": sum(quality_metrics["content_completeness"]) / max(len(quality_metrics["content_completeness"]), 1),
                "files_with_meaningful_content": sum(quality_metrics["has_meaningful_content"]),
                "bilingual_files_count": sum(quality_metrics["bilingual_files"])
            },
            "recommendations": self.generate_recommendations(successful_audits)
        }
        
        return consistency
    
    def generate_recommendations(self, audits: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on audit results"""
        recommendations = []
        
        # Check for files with low content
        low_content_files = [
            audit for audit in audits 
            if audit.get("content_quality", {}).get("content_completeness", 0) < 0.1
        ]
        
        if low_content_files:
            recommendations.append(f"Review {len(low_content_files)} files with minimal content")
        
        # Check for missing bilingual support
        monolingual_files = [
            audit for audit in audits
            if not audit.get("bilingual_support", {}).get("mixed_content", False)
        ]
        
        if monolingual_files:
            recommendations.append(f"Consider adding bilingual support to {len(monolingual_files)} files")
        
        # Check for structural inconsistencies
        structure_types = set(audit["structure"]["structure_type"] for audit in audits)
        if len(structure_types) > 3:
            recommendations.append("Standardize document structures - too many different types found")
        
        return recommendations
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive audit on all files"""
        logger.info("🔍 Starting comprehensive file structure audit...")
        
        # Find all JSON files
        json_files = list(self.data_dir.rglob("*.json"))
        self.audit_results["total_files"] = len(json_files)
        
        logger.info(f"📁 Found {len(json_files)} files to audit")
        
        # Audit each file
        all_audits = []
        for file_path in json_files:
            logger.info(f"Auditing: {file_path.relative_to(self.data_dir)}")
            audit_result = self.audit_single_file(file_path)
            all_audits.append(audit_result)
            
            if audit_result["status"] == "success":
                self.audit_results["successful_audits"] += 1
            else:
                self.audit_results["failed_audits"] += 1
                logger.warning(f"❌ Failed to audit {file_path.name}: {audit_result.get('error')}")
        
        # Generate comprehensive report
        successful_audits = [audit for audit in all_audits if audit["status"] == "success"]
        
        self.audit_results["file_details"] = all_audits
        self.audit_results["consistency_report"] = self.generate_consistency_report(all_audits)
        self.audit_results["audit_summary"] = {
            "success_rate": (self.audit_results["successful_audits"] / max(self.audit_results["total_files"], 1)) * 100,
            "files_with_meaningful_content": sum(1 for audit in successful_audits if audit.get("content_quality", {}).get("has_meaningful_content", False)),
            "bilingual_files": sum(1 for audit in successful_audits if audit.get("bilingual_support", {}).get("mixed_content", False)),
            "total_legal_references": sum(audit.get("legal_elements", {}).get("legal_references", 0) for audit in successful_audits)
        }
        
        logger.info(f"✅ Audit completed: {self.audit_results['successful_audits']}/{self.audit_results['total_files']} files successful")
        
        return self.audit_results
    
    def save_audit_report(self, output_path: str) -> None:
        """Save comprehensive audit report"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 Audit report saved to: {output_path}")

def main():
    """Run comprehensive file audit"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    output_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_0_analysis/comprehensive_audit_report.json"
    
    auditor = ComprehensiveFileAuditor(data_dir)
    audit_results = auditor.run_comprehensive_audit()
    auditor.save_audit_report(output_path)
    
    # Print summary
    print("\n📊 COMPREHENSIVE AUDIT SUMMARY:")
    print(f"Total files: {audit_results['total_files']}")
    print(f"Successful audits: {audit_results['successful_audits']}")
    print(f"Success rate: {audit_results['audit_summary']['success_rate']:.1f}%")
    print(f"Files with meaningful content: {audit_results['audit_summary']['files_with_meaningful_content']}")
    print(f"Bilingual files: {audit_results['audit_summary']['bilingual_files']}")
    print(f"Total legal references: {audit_results['audit_summary']['total_legal_references']}")

if __name__ == "__main__":
    main()