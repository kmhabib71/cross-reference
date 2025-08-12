#!/usr/bin/env python3
"""
Smart Training Data Extractor - Fixed for actual data structure
Phase 1.5A: Extract meaningful content for Bengali Legal NER training
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartTrainingDataExtractor:
    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        
        # Target for realistic 5K lines
        self.target_lines = 5000
        
    def extract_from_structured_json(self, data: Dict, source_name: str) -> List[str]:
        """Extract text content from structured JSON data"""
        content_lines = []
        
        def extract_text_recursive(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['title', 'content', 'text', 'description', 'provision']:
                        if isinstance(value, str) and len(value.strip()) > 10:
                            content_lines.append(f"{prefix}{value.strip()}")
                    elif isinstance(value, (dict, list)):
                        extract_text_recursive(value, prefix)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text_recursive(item, prefix)
            elif isinstance(obj, str) and len(obj.strip()) > 10:
                content_lines.append(f"{prefix}{obj.strip()}")
        
        # Extract from main content field
        if 'main_content' in data and data['main_content']:
            main_content = str(data['main_content'])
            if len(main_content) > 100:
                content_lines.extend(main_content.split('\n'))
        
        # Extract from structured parts (for Income Tax Act)
        if 'parts' in data:
            for part in data['parts']:
                if isinstance(part, dict):
                    extract_text_recursive(part)
        
        # Extract from chapters
        if 'chapters' in data:
            extract_text_recursive(data['chapters'])
        
        # Extract from any other structured content
        for key in ['sections', 'rules', 'schedules', 'provisions']:
            if key in data:
                extract_text_recursive(data[key])
        
        # If no structured content found, extract from entire data
        if not content_lines:
            extract_text_recursive(data)
        
        # Filter and clean lines
        cleaned_lines = []
        for line in content_lines:
            line = line.strip()
            # Skip very short lines, numbers only, or common artifacts
            if len(line) > 15 and not line.isdigit() and 'success' not in line.lower():
                cleaned_lines.append(line)
        
        return cleaned_lines
    
    def extract_from_file(self, file_path: Path, max_lines: int = None) -> Dict[str, Any]:
        """Extract content from a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            content_lines = self.extract_from_structured_json(data, file_path.name)
            
            if max_lines:
                content_lines = content_lines[:max_lines]
            
            return {
                "source": file_path.name,
                "relative_path": str(file_path.relative_to(self.data_dir)),
                "content_lines": content_lines,
                "line_count": len(content_lines),
                "file_size": file_path.stat().st_size
            }
            
        except Exception as e:
            logger.warning(f"Error extracting from {file_path}: {e}")
            return {
                "source": file_path.name,
                "content_lines": [],
                "line_count": 0,
                "error": str(e)
            }
    
    def prioritize_files_by_importance(self) -> List[Tuple[Path, str, int]]:
        """Prioritize files by legal importance and size"""
        file_priorities = []
        
        # Priority 1: Core Acts (highest importance)
        for act_file in (self.data_dir / "core_acts").glob("*.json"):
            file_priorities.append((act_file, "core_act", 1))
        
        # Priority 2: Finance Laws (amending legislation)
        for finance_file in (self.data_dir / "finance_laws").glob("*.json"):
            file_priorities.append((finance_file, "finance_law", 2))
        
        # Priority 3: Key Schedules (important for exemptions/rates)
        schedule_dir = self.data_dir / "schedules"
        if schedule_dir.exists():
            priority_schedules = [
                "6th-schedule",  # Exemptions
                "7th-schedule",  # Special rates
                "1st-schedule"   # Disclosure requirements
            ]
            for schedule_file in schedule_dir.glob("*.json"):
                priority = 3
                for prio_sched in priority_schedules:
                    if prio_sched in schedule_file.name:
                        priority = 2.5  # Higher priority for key schedules
                        break
                file_priorities.append((schedule_file, "schedule", priority))
        
        # Priority 4: TDS Rules (implementation rules)
        tds_dir = self.data_dir / "tds_rules"
        if tds_dir.exists():
            for tds_file in tds_dir.glob("*.json"):
                file_priorities.append((tds_file, "tds_rule", 4))
        
        # Priority 5: Circulars (interpretive guidance) - limited sample
        circular_dir = self.data_dir / "circulars"
        if circular_dir.exists():
            for circular_file in circular_dir.glob("*.json"):
                file_priorities.append((circular_file, "circular", 5))
        
        # Sort by priority, then by file size (larger files likely have more content)
        file_priorities.sort(key=lambda x: (x[2], -x[0].stat().st_size))
        
        return file_priorities
    
    def create_balanced_training_dataset(self) -> Dict[str, Any]:
        """Create a balanced 5K line training dataset"""
        logger.info("🚀 Creating balanced training dataset for Bengali Legal NER...")
        
        prioritized_files = self.prioritize_files_by_importance()
        training_data = []
        total_lines = 0
        category_distribution = {}
        
        # Target distribution
        target_by_category = {
            "core_act": 2000,      # 40% - Main acts
            "finance_law": 800,    # 16% - Finance laws
            "schedule": 1200,      # 24% - Schedules 
            "tds_rule": 700,       # 14% - TDS rules
            "circular": 300        # 6% - Circulars
        }
        
        for file_path, category, priority in prioritized_files:
            if total_lines >= self.target_lines:
                break
                
            # Calculate how many lines to extract from this file
            remaining_for_category = target_by_category.get(category, 0) - category_distribution.get(category, 0)
            if remaining_for_category <= 0:
                continue
            
            # Extract content
            file_data = self.extract_from_file(file_path, max_lines=remaining_for_category)
            
            if file_data["line_count"] > 0:
                training_data.append(file_data)
                category_distribution[category] = category_distribution.get(category, 0) + file_data["line_count"]
                total_lines += file_data["line_count"]
                
                logger.info(f"Extracted {file_data['line_count']} lines from {file_data['source']} ({category})")
        
        # Create dataset structure
        dataset = {
            "metadata": {
                "dataset_name": "Bengali Legal NER Training Dataset",
                "version": "1.0", 
                "creation_date": "2025-08-12",
                "total_lines_extracted": total_lines,
                "total_files_processed": len(training_data),
                "target_lines": self.target_lines,
                "extraction_method": "balanced_priority_sampling"
            },
            "category_distribution": category_distribution,
            "training_files": training_data,
            "statistics": {
                "lines_per_category": category_distribution,
                "files_per_category": {
                    category: len([f for f in training_data if f["source"].startswith(category.split('_')[0])]) 
                    for category in category_distribution
                }
            }
        }
        
        logger.info(f"✅ Training dataset created with {total_lines} lines from {len(training_data)} files")
        
        return dataset
    
    def create_text_samples(self, dataset: Dict[str, Any]) -> List[str]:
        """Create plain text samples for NER annotation"""
        text_samples = []
        
        for file_data in dataset["training_files"]:
            for line in file_data["content_lines"]:
                # Create samples suitable for NER training
                if len(line) > 30 and len(line) < 500:  # Good length for NER
                    text_samples.append(line)
        
        return text_samples[:1000]  # Limit to 1000 samples for initial training

def main():
    """Extract training data with proper file structure handling"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    output_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_5_bengali_legal_ner/training_data"
    
    extractor = SmartTrainingDataExtractor(data_dir, output_dir)
    dataset = extractor.create_balanced_training_dataset()
    
    # Save training dataset
    output_file = Path(output_dir) / "balanced_training_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    # Create text samples for annotation
    text_samples = extractor.create_text_samples(dataset)
    samples_file = Path(output_dir) / "text_samples_for_annotation.txt"
    with open(samples_file, 'w', encoding='utf-8') as f:
        for sample in text_samples:
            f.write(sample + '\n\n')
    
    print("\n🎯 PHASE 1.5A COMPLETED: Smart Training Data Extraction")
    print(f"Dataset saved to: {output_file}")
    print(f"Text samples saved to: {samples_file}")
    print(f"Total lines extracted: {dataset['metadata']['total_lines_extracted']}")
    print(f"Files processed: {dataset['metadata']['total_files_processed']}")
    print(f"Text samples for annotation: {len(text_samples)}")
    print("\nCategory Distribution:")
    for category, lines in dataset['category_distribution'].items():
        print(f"  {category}: {lines} lines")

if __name__ == "__main__":
    main()