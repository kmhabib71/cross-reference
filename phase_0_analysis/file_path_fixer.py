#!/usr/bin/env python3
"""
File Path Fixer for Legal Hierarchy
Task 1: Fix all file paths to match actual data folder structure
Critical fix to ensure legal hierarchy references real files
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FilePathFixer:
    def __init__(self, data_dir: str, phase_dir: str):
        self.data_dir = Path(data_dir)
        self.phase_dir = Path(phase_dir)
        self.hierarchy_path = self.phase_dir / "legal_hierarchy.json"
        
    def discover_actual_files(self) -> Dict[str, str]:
        """Discover all actual JSON files in data directory"""
        actual_files = {}
        
        for json_file in self.data_dir.rglob("*.json"):
            relative_path = json_file.relative_to(self.data_dir)
            filename = json_file.name
            actual_files[filename] = str(relative_path)
        
        logger.info(f"Found {len(actual_files)} actual JSON files in data directory")
        return actual_files
    
    def map_logical_to_actual_files(self, actual_files: Dict[str, str]) -> Dict[str, Any]:
        """Map logical document names to actual files"""
        mappings = {
            "finance_ordinance_2025": {
                "actual_file": "finance_ordinance_2025_cleaned.json",
                "logical_name": "Finance Ordinance 2025"
            },
            "income_tax_act_2023": {
                "actual_file": "income_tax_act_2023_cleaned.json", 
                "logical_name": "Income Tax Act 2023"
            },
            "income_tax_circular_2025": {
                "actual_file": "income_tax_circular_2024_25_ultra_enriched.json",
                "logical_name": "Income Tax Circular 2024-25"
            },
            "schedules_english": {
                "actual_file": "income-tax-schedule-english.json",
                "logical_name": "Income Tax Schedules (English)"
            },
            "schedules_bangla": {
                "actual_file": "income-tax-schedule-bangla.json", 
                "logical_name": "Income Tax Schedules (Bengali)"
            },
            "tds_rules_2025": {
                "actual_file": "tds-rules-2024-fy-2025-26-bd.json",
                "logical_name": "TDS Rules FY 2025-26"
            },
            "tds_rules_2024": {
                "actual_file": "tds-rules-2024-fy-2024-2025-bangladesh.json",
                "logical_name": "TDS Rules FY 2024-25"
            }
        }
        
        # Validate mappings against actual files
        validated_mappings = {}
        for logical_name, mapping in mappings.items():
            actual_file = mapping["actual_file"]
            if actual_file in actual_files:
                validated_mappings[logical_name] = {
                    **mapping,
                    "actual_path": actual_files[actual_file],
                    "exists": True,
                    "file_size": (self.data_dir / actual_files[actual_file]).stat().st_size
                }
                logger.info(f"✅ Mapped {logical_name} → {actual_files[actual_file]}")
            else:
                validated_mappings[logical_name] = {
                    **mapping,
                    "actual_path": None,
                    "exists": False,
                    "file_size": 0
                }
                logger.warning(f"❌ Missing file for {logical_name}: {actual_file}")
        
        return validated_mappings
    
    def find_schedule_files(self, actual_files: Dict[str, str]) -> Dict[str, str]:
        """Find actual schedule files"""
        schedule_files = {}
        
        schedule_patterns = [
            "1st-schedule", "2nd-schedule", "3rd-schedule", 
            "4th-schedule", "5th-schedule", "6th-schedule",
            "7th-schedule", "8th-schedule"
        ]
        
        for filename, path in actual_files.items():
            for pattern in schedule_patterns:
                if pattern in filename.lower():
                    schedule_num = pattern.split('-')[0]
                    if schedule_num not in schedule_files:
                        schedule_files[schedule_num] = []
                    schedule_files[schedule_num].append(path)
        
        return schedule_files
    
    def find_tds_rule_files(self, actual_files: Dict[str, str]) -> Dict[str, List[str]]:
        """Find actual TDS rule files"""
        tds_files = {"2024": [], "2025": []}
        
        for filename, path in actual_files.items():
            if "tds-rules" in filename:
                if "2025-26" in filename:
                    tds_files["2025"].append(path)
                elif "2024-2025" in filename or "2024-25" in filename:
                    tds_files["2024"].append(path)
        
        return tds_files
    
    def fix_legal_hierarchy(self) -> Dict[str, Any]:
        """Fix all file paths in legal hierarchy"""
        logger.info("🔧 Starting file path corrections...")
        
        # Load existing hierarchy
        with open(self.hierarchy_path, 'r', encoding='utf-8') as f:
            hierarchy = json.load(f)
        
        # Discover actual files
        actual_files = self.discover_actual_files()
        
        # Create file mappings
        file_mappings = self.map_logical_to_actual_files(actual_files)
        schedule_files = self.find_schedule_files(actual_files)
        tds_files = self.find_tds_rule_files(actual_files)
        
        # Fix document relationships
        fixed_relationships = {}
        
        for doc_id, doc_data in hierarchy["document_relationships"].items():
            fixed_doc = doc_data.copy()
            
            if doc_id == "finance_ordinance_2025":
                mapping = file_mappings.get("finance_ordinance_2025")
                if mapping and mapping["exists"]:
                    fixed_doc["file_path"] = mapping["actual_path"]
                    fixed_doc["file_size"] = mapping["file_size"]
                    fixed_doc["validation_status"] = "verified"
                else:
                    fixed_doc["validation_status"] = "file_missing"
            
            elif doc_id == "income_tax_act_2023":
                mapping = file_mappings.get("income_tax_act_2023")
                if mapping and mapping["exists"]:
                    fixed_doc["file_path"] = mapping["actual_path"]
                    fixed_doc["file_size"] = mapping["file_size"]
                    fixed_doc["validation_status"] = "verified"
                else:
                    fixed_doc["validation_status"] = "file_missing"
                
                # Remove non-existent bangla path reference
                if "file_path_bangla" in fixed_doc:
                    del fixed_doc["file_path_bangla"]
            
            elif doc_id == "schedules_1st_8th":
                english_mapping = file_mappings.get("schedules_english")
                bangla_mapping = file_mappings.get("schedules_bangla")
                
                if english_mapping and english_mapping["exists"]:
                    fixed_doc["file_path"] = english_mapping["actual_path"]
                    fixed_doc["file_size"] = english_mapping["file_size"]
                
                if bangla_mapping and bangla_mapping["exists"]:
                    fixed_doc["file_path_bangla"] = bangla_mapping["actual_path"]
                    fixed_doc["file_size_bangla"] = bangla_mapping["file_size"]
                
                # Update schedule file mappings
                for schedule_id, schedule_data in fixed_doc.get("schedules", {}).items():
                    if schedule_id in schedule_files:
                        available_files = schedule_files[schedule_id]
                        if available_files:
                            schedule_data["available_files"] = available_files
                            schedule_data["file_specific"] = available_files[0]  # Use first available
                
                fixed_doc["validation_status"] = "partially_verified"
            
            elif doc_id in ["tds_rules_2025", "tds_rules_2024"]:
                year = "2025" if doc_id == "tds_rules_2025" else "2024"
                year_files = tds_files.get(year, [])
                
                if year_files:
                    fixed_doc["file_path"] = year_files[0]  # Main summary file
                    fixed_doc["available_files"] = year_files
                    fixed_doc["file_count"] = len(year_files)
                    fixed_doc["validation_status"] = "verified"
                
                # Fix rule file mappings
                if "rule_files" in fixed_doc:
                    updated_rule_files = {}
                    for rule_num, rule_file in fixed_doc["rule_files"].items():
                        # Find actual file for this rule
                        matching_files = [f for f in year_files if f"rule-{rule_num}-" in f]
                        if matching_files:
                            updated_rule_files[rule_num] = matching_files[0]
                    
                    fixed_doc["rule_files"] = updated_rule_files
            
            elif doc_id == "income_tax_circulars_2025":
                mapping = file_mappings.get("income_tax_circular_2025")
                if mapping and mapping["exists"]:
                    fixed_doc["file_path"] = mapping["actual_path"]
                    fixed_doc["file_size"] = mapping["file_size"]
                    fixed_doc["validation_status"] = "verified"
            
            elif doc_id == "sro_orders":
                # Look for SRO files
                sro_files = [path for filename, path in actual_files.items() if "sro" in filename.lower()]
                if sro_files:
                    fixed_doc["file_path"] = sro_files[0]
                    fixed_doc["available_files"] = sro_files
                    fixed_doc["validation_status"] = "verified"
                else:
                    fixed_doc["validation_status"] = "no_sro_files_found"
            
            fixed_relationships[doc_id] = fixed_doc
        
        # Update hierarchy
        hierarchy["document_relationships"] = fixed_relationships
        
        # Add file validation metadata
        hierarchy["file_validation"] = {
            "total_files_mapped": len(file_mappings),
            "files_verified": sum(1 for m in file_mappings.values() if m["exists"]),
            "files_missing": sum(1 for m in file_mappings.values() if not m["exists"]),
            "schedule_files_found": sum(len(files) for files in schedule_files.values()),
            "tds_files_found": sum(len(files) for files in tds_files.values()),
            "validation_date": "2025-08-11",
            "data_directory": str(self.data_dir)
        }
        
        logger.info("✅ File path corrections completed")
        return hierarchy
    
    def save_fixed_hierarchy(self, fixed_hierarchy: Dict[str, Any]) -> None:
        """Save the corrected hierarchy"""
        # Backup original
        backup_path = self.phase_dir / "legal_hierarchy_original_backup.json"
        if not backup_path.exists():
            with open(self.hierarchy_path, 'r', encoding='utf-8') as f:
                original = json.load(f)
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(original, f, ensure_ascii=False, indent=2)
            logger.info(f"📄 Original hierarchy backed up to: {backup_path}")
        
        # Save fixed version
        with open(self.hierarchy_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_hierarchy, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Fixed hierarchy saved to: {self.hierarchy_path}")
    
    def generate_validation_report(self, fixed_hierarchy: Dict[str, Any]) -> None:
        """Generate validation report"""
        report = {
            "file_path_corrections_summary": {
                "task": "Fix Legal Hierarchy File Paths",
                "status": "COMPLETED",
                "corrections_made": [],
                "files_verified": [],
                "files_missing": [],
                "warnings": []
            }
        }
        
        # Analyze corrections
        for doc_id, doc_data in fixed_hierarchy["document_relationships"].items():
            status = doc_data.get("validation_status", "unknown")
            
            if status == "verified":
                report["file_path_corrections_summary"]["files_verified"].append({
                    "document": doc_id,
                    "file_path": doc_data.get("file_path", "unknown"),
                    "file_size": doc_data.get("file_size", 0)
                })
            elif status == "file_missing":
                report["file_path_corrections_summary"]["files_missing"].append({
                    "document": doc_id,
                    "issue": "Referenced file not found in data directory"
                })
            elif status == "partially_verified":
                report["file_path_corrections_summary"]["warnings"].append({
                    "document": doc_id,
                    "issue": "Some referenced files found, others missing"
                })
        
        # Save report
        report_path = self.phase_dir / "task1_file_path_corrections_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Validation report saved to: {report_path}")
        
        return report

def main():
    """Fix file paths in legal hierarchy"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    phase_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_0_analysis"
    
    fixer = FilePathFixer(data_dir, phase_dir)
    fixed_hierarchy = fixer.fix_legal_hierarchy()
    fixer.save_fixed_hierarchy(fixed_hierarchy)
    report = fixer.generate_validation_report(fixed_hierarchy)
    
    print("\n🔧 TASK 1: FILE PATH CORRECTIONS COMPLETED")
    print(f"Files verified: {len(report['file_path_corrections_summary']['files_verified'])}")
    print(f"Files missing: {len(report['file_path_corrections_summary']['files_missing'])}")
    print(f"Warnings: {len(report['file_path_corrections_summary']['warnings'])}")

if __name__ == "__main__":
    main()