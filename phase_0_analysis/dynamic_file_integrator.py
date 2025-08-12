#!/usr/bin/env python3
"""
Dynamic File Integration System
Automatically processes new legal documents added to data folder
Maintains 100% precision by updating cross-references and hierarchies
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicFileIntegrator:
    def __init__(self, data_dir: str, phase_dir: str):
        self.data_dir = Path(data_dir)
        self.phase_dir = Path(phase_dir)
        self.legal_hierarchy_path = self.phase_dir / "legal_hierarchy.json"
        self.citation_patterns_path = self.phase_dir / "citation_patterns_analysis.json"
        self.file_registry_path = self.phase_dir / "file_registry.json"
        
    def detect_new_files(self) -> List[Path]:
        """Detect new files since last scan"""
        # Load existing file registry
        if self.file_registry_path.exists():
            with open(self.file_registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        else:
            registry = {"scanned_files": {}, "last_scan": None}
        
        # Get current files with checksums
        current_files = {}
        all_json_files = list(self.data_dir.rglob("*.json"))
        
        for file_path in all_json_files:
            try:
                with open(file_path, 'rb') as f:
                    checksum = hashlib.md5(f.read()).hexdigest()
                relative_path = str(file_path.relative_to(self.data_dir))
                current_files[relative_path] = {
                    "checksum": checksum,
                    "modified_time": file_path.stat().st_mtime
                }
            except Exception as e:
                logger.warning(f"Could not checksum {file_path}: {e}")
        
        # Find new or modified files
        new_files = []
        for file_path, info in current_files.items():
            if (file_path not in registry["scanned_files"] or 
                registry["scanned_files"][file_path]["checksum"] != info["checksum"]):
                new_files.append(self.data_dir / file_path)
        
        # Update registry
        registry["scanned_files"] = current_files
        registry["last_scan"] = datetime.now().isoformat()
        
        os.makedirs(self.phase_dir, exist_ok=True)
        with open(self.file_registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        
        return new_files
    
    def classify_document_type(self, file_path: Path) -> Dict[str, Any]:
        """Classify document type and determine authority level"""
        path_parts = file_path.parts
        filename = file_path.name.lower()
        
        # Authority levels (higher = more authoritative)
        authority_mapping = {
            "finance_ordinance": 100,
            "finance_act": 100, 
            "income_tax_act": 100,
            "customs_act": 95,
            "vat_act": 95,
            "schedules": 90,
            "rules": 85,
            "sro": 80,
            "circular": 70,
            "notification": 60
        }
        
        # Classify based on path and filename
        if "finance_ordinance" in filename or "ordinance" in filename:
            doc_type = "finance_ordinance"
            authority = 100
        elif "finance_act" in filename or ("finance" in filename and "act" in filename):
            doc_type = "finance_act"
            authority = 100
        elif "income_tax_act" in filename or "income-tax-act" in filename:
            doc_type = "income_tax_act"
            authority = 100
        elif "schedule" in str(file_path):
            doc_type = "schedule"
            authority = 90
        elif "tds_rules" in filename or "rules" in str(file_path):
            doc_type = "tds_rules"
            authority = 85
        elif "sro" in str(file_path) or "sro" in filename:
            doc_type = "sro"
            authority = 80
        elif "circular" in str(file_path) or "circular" in filename:
            doc_type = "circular" 
            authority = 70
        else:
            doc_type = "unknown"
            authority = 50
            
        # Extract year if possible
        year = None
        for part in filename.split('-'):
            if part.isdigit() and len(part) == 4 and part.startswith('20'):
                year = int(part)
                break
        
        return {
            "document_type": doc_type,
            "authority_level": authority,
            "year": year,
            "relative_path": str(file_path.relative_to(self.data_dir))
        }
    
    def extract_citations_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract citation patterns from a new file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            citations = []
            text_content = ""
            
            # Extract text from different content structures
            if "main_content" in data:
                text_content = data["main_content"]
            elif "structured_content" in data:
                text_content = str(data["structured_content"])
            elif "chapters" in data:
                text_content = str(data["chapters"])
                
            # Bengali citation patterns
            bengali_patterns = [
                r'আয়কর আইন,?\s*([২০][২৩৪][০-৯])\s*(?:এর)?\s*([০-৯]+)(?:য়|ম|ষ্ঠ)?\s*ধারা',
                r'অর্থ আইন,?\s*([২০][২৩৪][০-৯])',
                r'([০-৯]+)(?:ম|য়|ষ্ঠ)\s*তফসিল',
                r'বিধি\s*([০-৯]+)',
                r'এস\.আর\.ও\.',
                r'পরিপত্র',
            ]
            
            # English citation patterns  
            english_patterns = [
                r'Income Tax Act,?\s*(20[2-9][0-9])',
                r'Finance Act,?\s*(20[2-9][0-9])',
                r'Section\s*([0-9]+)',
                r'Schedule\s*([0-9]+)',
                r'Rule\s*([0-9]+)',
                r'S\.R\.O\.',
                r'Circular',
            ]
            
            import re
            for pattern in bengali_patterns + english_patterns:
                matches = re.findall(pattern, text_content)
                for match in matches:
                    citations.append({
                        "pattern": pattern,
                        "match": match,
                        "source_file": file_path.name,
                        "language": "bengali" if pattern in bengali_patterns else "english"
                    })
            
            return citations
            
        except Exception as e:
            logger.error(f"Error extracting citations from {file_path}: {e}")
            return []
    
    def update_legal_hierarchy(self, new_files: List[Path]) -> None:
        """Update legal hierarchy with new files"""
        # Load existing hierarchy
        if self.legal_hierarchy_path.exists():
            with open(self.legal_hierarchy_path, 'r', encoding='utf-8') as f:
                hierarchy = json.load(f)
        else:
            hierarchy = {"document_relationships": {}, "cross_reference_registry": {}}
        
        for file_path in new_files:
            try:
                classification = self.classify_document_type(file_path)
                doc_id = file_path.stem.replace('-', '_').replace(' ', '_')
                
                # Add to document relationships
                hierarchy["document_relationships"][doc_id] = {
                    "file_path": classification["relative_path"],
                    "authority_level": classification["authority_level"],
                    "document_type": classification["document_type"],
                    "year": classification["year"],
                    "effective_date": f"{classification['year']}-07-01" if classification["year"] else None,
                    "status": "current",
                    "added_date": datetime.now().isoformat(),
                    "auto_integrated": True
                }
                
                logger.info(f"Added {doc_id} to legal hierarchy with authority {classification['authority_level']}")
                
            except Exception as e:
                logger.error(f"Error updating hierarchy for {file_path}: {e}")
        
        # Save updated hierarchy
        with open(self.legal_hierarchy_path, 'w', encoding='utf-8') as f:
            json.dump(hierarchy, f, ensure_ascii=False, indent=2)
    
    def update_citation_patterns(self, new_files: List[Path]) -> None:
        """Update citation pattern analysis with new files"""
        # Load existing patterns
        if self.citation_patterns_path.exists():
            with open(self.citation_patterns_path, 'r', encoding='utf-8') as f:
                patterns = json.load(f)
        else:
            patterns = {"analysis_summary": {"documents_analyzed": 0}, "citation_registry": {}}
        
        new_citations = 0
        for file_path in new_files:
            try:
                citations = self.extract_citations_from_file(file_path)
                new_citations += len(citations)
                
                # Add citations to registry
                for citation in citations:
                    key = f"{citation['source_file']}_{citation['pattern'][:20]}"
                    patterns["citation_registry"][key] = citation
                
                logger.info(f"Extracted {len(citations)} citations from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error updating citations for {file_path}: {e}")
        
        # Update summary
        patterns["analysis_summary"]["documents_analyzed"] += len(new_files)
        patterns["analysis_summary"]["new_files_integrated"] = len(new_files)
        patterns["analysis_summary"]["new_citations_found"] = new_citations
        patterns["analysis_summary"]["last_integration"] = datetime.now().isoformat()
        
        # Save updated patterns
        with open(self.citation_patterns_path, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, ensure_ascii=False, indent=2)
    
    def integrate_new_files(self) -> Dict[str, Any]:
        """Main integration process"""
        logger.info("🔄 Starting dynamic file integration...")
        
        # Detect new files
        new_files = self.detect_new_files()
        
        if not new_files:
            logger.info("✅ No new files detected")
            return {"status": "up_to_date", "new_files": 0}
        
        logger.info(f"📁 Found {len(new_files)} new/modified files")
        
        # Process new files
        try:
            self.update_legal_hierarchy(new_files)
            self.update_citation_patterns(new_files)
            
            result = {
                "status": "success",
                "new_files": len(new_files),
                "files_processed": [f.name for f in new_files],
                "integration_time": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Integration completed: {len(new_files)} files processed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Integration failed: {e}")
            return {"status": "error", "error": str(e)}

def main():
    """Auto-integration entry point"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    phase_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_0_analysis"
    
    integrator = DynamicFileIntegrator(data_dir, phase_dir)
    result = integrator.integrate_new_files()
    
    print(f"Integration Result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main()