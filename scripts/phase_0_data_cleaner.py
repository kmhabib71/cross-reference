#!/usr/bin/env python3
"""
Phase 0 Data Cleaner
Removes URLs and titles from all JSON files in data directory
Part of precision crossref system roadmap Phase 0 completion
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.cleaned_count = 0
        self.error_count = 0
        self.total_files = 0
        
    def clean_file(self, file_path: Path) -> bool:
        """Clean a single JSON file by removing url and title keys"""
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Track if we made changes
            changed = False
            
            # Remove url if present
            if 'url' in data:
                del data['url']
                changed = True
                logger.info(f"Removed URL from {file_path.name}")
            
            # Remove title if it contains "Tax VAT Point"
            if 'title' in data:
                title = data['title']
                if 'Tax VAT Point' in title or 'taxvatpoint' in title.lower():
                    del data['title']
                    changed = True
                    logger.info(f"Removed title from {file_path.name}")
            
            # Write back if changes were made
            if changed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"✅ Cleaned: {file_path.name}")
                self.cleaned_count += 1
            else:
                logger.info(f"⚪ No changes needed: {file_path.name}")
            
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error in {file_path.name}: {e}")
            self.error_count += 1
            return False
        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")
            self.error_count += 1
            return False
    
    def validate_content_structure(self, file_path: Path) -> Dict[str, Any]:
        """Validate the content structure of a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            validation_result = {
                'file': file_path.name,
                'has_main_content': 'main_content' in data,
                'has_tables': 'tables' in data,
                'has_forms': 'forms' in data,
                'main_content_length': len(data.get('main_content', '')) if 'main_content' in data else 0,
                'table_count': len(data.get('tables', [])),
                'form_count': len(data.get('forms', [])),
                'other_keys': [k for k in data.keys() if k not in ['main_content', 'tables', 'forms', 'url', 'title']]
            }
            
            return validation_result
            
        except Exception as e:
            return {
                'file': file_path.name,
                'error': str(e)
            }
    
    def clean_all_files(self) -> None:
        """Clean all JSON files in the data directory"""
        logger.info(f"Starting data cleanup in: {self.data_dir}")
        
        # Find all JSON files
        json_files = list(self.data_dir.rglob("*.json"))
        self.total_files = len(json_files)
        
        logger.info(f"Found {self.total_files} JSON files to process")
        
        # Process each file
        for file_path in json_files:
            logger.info(f"Processing: {file_path.relative_to(self.data_dir)}")
            self.clean_file(file_path)
        
        # Summary
        logger.info(f"\n📊 CLEANUP SUMMARY:")
        logger.info(f"Total files: {self.total_files}")
        logger.info(f"Files cleaned: {self.cleaned_count}")
        logger.info(f"Files with errors: {self.error_count}")
        logger.info(f"Success rate: {((self.total_files - self.error_count) / self.total_files * 100):.1f}%")
    
    def validate_all_content(self) -> List[Dict[str, Any]]:
        """Validate content structure of all JSON files"""
        logger.info(f"Validating content structure in: {self.data_dir}")
        
        json_files = list(self.data_dir.rglob("*.json"))
        validation_results = []
        
        for file_path in json_files:
            result = self.validate_content_structure(file_path)
            validation_results.append(result)
        
        # Generate summary report
        files_with_main_content = sum(1 for r in validation_results if r.get('has_main_content', False))
        files_with_tables = sum(1 for r in validation_results if r.get('has_tables', False))
        files_with_forms = sum(1 for r in validation_results if r.get('has_forms', False))
        
        logger.info(f"\n📊 CONTENT VALIDATION SUMMARY:")
        logger.info(f"Files with main_content: {files_with_main_content}/{len(validation_results)}")
        logger.info(f"Files with tables: {files_with_tables}/{len(validation_results)}")
        logger.info(f"Files with forms: {files_with_forms}/{len(validation_results)}")
        
        return validation_results

def main():
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return
    
    cleaner = DataCleaner(data_dir)
    
    # Step 1: Clean files
    logger.info("🧹 PHASE 0 DATA CLEANUP - Removing URLs and titles")
    cleaner.clean_all_files()
    
    # Step 2: Validate content
    logger.info("\n🔍 PHASE 0 CONTENT VALIDATION")
    validation_results = cleaner.validate_all_content()
    
    # Save validation report
    report_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/reports/phase_0_cleanup_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'cleanup_summary': {
                'total_files': cleaner.total_files,
                'files_cleaned': cleaner.cleaned_count,
                'files_with_errors': cleaner.error_count,
                'success_rate': ((cleaner.total_files - cleaner.error_count) / cleaner.total_files * 100) if cleaner.total_files > 0 else 0
            },
            'validation_results': validation_results
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"📄 Report saved to: {report_path}")
    logger.info("✅ Phase 0 data cleanup completed!")

if __name__ == "__main__":
    main()