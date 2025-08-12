#!/usr/bin/env python3
"""
Real Training Data Extractor for Bengali Legal NER
Phase 1.5G: Extract ACTUAL substantial Bengali legal content (5K+ meaningful lines)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTrainingDataExtractor:
    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track extraction statistics
        self.extraction_stats = {
            "files_processed": 0,
            "files_with_content": 0,
            "total_lines_extracted": 0,
            "meaningful_lines": 0,
            "category_distribution": {}
        }
    
    def extract_substantial_content_from_file(self, file_path: Path) -> List[str]:
        """Extract substantial content from a single JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            content_lines = []
            
            # Extract from main_content field (primary source)
            if 'main_content' in data and data['main_content']:
                main_content = str(data['main_content']).strip()
                if len(main_content) > 100:  # Substantial content only
                    # Split by sentences and legal sections
                    sentences = self._split_into_meaningful_sentences(main_content)
                    content_lines.extend(sentences)
            
            # Extract from structured content (backup)
            if not content_lines:
                content_lines.extend(self._extract_from_structured_data(data))
            
            # Filter and clean content
            meaningful_lines = []
            for line in content_lines:
                line = line.strip()
                if self._is_meaningful_content(line):
                    meaningful_lines.append(line)
            
            return meaningful_lines
            
        except Exception as e:
            logger.warning(f"Error extracting from {file_path}: {e}")
            return []
    
    def _split_into_meaningful_sentences(self, text: str) -> List[str]:
        """Split text into meaningful sentences for NER training"""
        # Clean up the text first
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n+', ' ', text)  # Multiple newlines to space
        
        # Split by Bengali and English sentence terminators
        sentence_pattern = r'[।৷.!?](?=\s|$)'
        sentences = re.split(sentence_pattern, text)
        
        meaningful_sentences = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short fragments
                continue
            
            # Combine short related sentences
            if len(current_chunk) + len(sentence) < 300:  # Optimal for NER
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    meaningful_sentences.append(current_chunk.strip())
                current_chunk = sentence
        
        # Add remaining content
        if current_chunk.strip():
            meaningful_sentences.append(current_chunk.strip())
        
        return meaningful_sentences
    
    def _extract_from_structured_data(self, data: Dict) -> List[str]:
        """Extract from structured fields as backup"""
        content_lines = []
        
        # Extract from various structured fields
        content_fields = ['content', 'text', 'description', 'provision', 'title']
        
        def extract_recursive(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in content_fields and isinstance(value, str):
                        if len(value.strip()) > 20:  # Meaningful content threshold
                            content_lines.append(value.strip())
                    elif isinstance(value, (dict, list)):
                        extract_recursive(value, prefix)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item, prefix)
        
        extract_recursive(data)
        return content_lines
    
    def _is_meaningful_content(self, line: str) -> bool:
        """Check if content line is meaningful for NER training"""
        if len(line) < 15:  # Too short
            return False
        
        if line.isdigit():  # Just numbers
            return False
        
        # Must contain some Bengali or substantial English
        has_bengali = bool(re.search(r'[\u0980-\u09FF]', line))
        has_substantial_english = len(re.findall(r'[a-zA-Z]+', line)) > 2
        
        if not (has_bengali or has_substantial_english):
            return False
        
        # Skip common artifacts
        skip_patterns = [
            r'^[\d\s\-\(\)\.]+$',  # Only numbers, spaces, punctuation
            r'^[০-৯\s\-\(\)\.]+$',  # Only Bengali numbers and punctuation
            r'^\*+$',  # Only asterisks
            r'^[\[\]]+$'  # Only brackets
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, line):
                return False
        
        return True
    
    def _categorize_file(self, file_path: Path) -> str:
        """Categorize file based on path and name"""
        path_str = str(file_path).lower()
        
        if 'core_acts' in path_str:
            return 'core_act'
        elif 'finance_laws' in path_str:
            return 'finance_law'
        elif 'schedules' in path_str:
            return 'schedule'
        elif 'tds_rules' in path_str:
            return 'tds_rule'
        elif 'circulars' in path_str:
            return 'circular'
        elif 'sro_orders' in path_str:
            return 'sro_order'
        else:
            return 'general'
    
    def extract_from_all_files(self) -> Dict[str, Any]:
        """Extract substantial content from all data files"""
        logger.info("🚀 Starting REAL substantial content extraction...")
        
        all_extracted_lines = []
        category_data = {}
        
        # Process all JSON files in data directory
        for json_file in self.data_dir.rglob("*.json"):
            logger.info(f"Processing: {json_file.name}")
            
            self.extraction_stats["files_processed"] += 1
            
            # Extract content from this file
            file_content = self.extract_substantial_content_from_file(json_file)
            
            if file_content:
                self.extraction_stats["files_with_content"] += 1
                self.extraction_stats["total_lines_extracted"] += len(file_content)
                
                # Categorize content
                category = self._categorize_file(json_file)
                if category not in category_data:
                    category_data[category] = []
                
                # Add file info to content
                for line in file_content:
                    content_entry = {
                        "text": line,
                        "source": json_file.name,
                        "category": category,
                        "relative_path": str(json_file.relative_to(self.data_dir)),
                        "length": len(line),
                        "has_bengali": bool(re.search(r'[\u0980-\u09FF]', line)),
                        "has_english": bool(re.search(r'[a-zA-Z]', line))
                    }
                    
                    all_extracted_lines.append(content_entry)
                    category_data[category].append(content_entry)
                
                logger.info(f"  ✅ Extracted {len(file_content)} meaningful lines")
            else:
                logger.info(f"  ⚠️ No substantial content found")
        
        # Update category distribution
        for category, lines in category_data.items():
            self.extraction_stats["category_distribution"][category] = len(lines)
        
        self.extraction_stats["meaningful_lines"] = len(all_extracted_lines)
        
        logger.info(f"🎯 Extraction Complete!")
        logger.info(f"Files processed: {self.extraction_stats['files_processed']}")
        logger.info(f"Files with content: {self.extraction_stats['files_with_content']}")
        logger.info(f"Total meaningful lines: {self.extraction_stats['meaningful_lines']}")
        
        return {
            "extraction_metadata": {
                "extraction_date": "2025-08-12",
                "method": "substantial_content_extraction",
                "target_achieved": self.extraction_stats['meaningful_lines'] >= 5000,
                "quality_threshold": "15+ characters, meaningful content only"
            },
            "statistics": self.extraction_stats,
            "extracted_content": all_extracted_lines,
            "category_breakdown": category_data
        }
    
    def create_balanced_training_dataset(self, extraction_results: Dict[str, Any], target_lines: int = 5000) -> Dict[str, Any]:
        """Create balanced training dataset from extracted content"""
        logger.info(f"📊 Creating balanced dataset (target: {target_lines} lines)...")
        
        all_content = extraction_results["extracted_content"]
        category_breakdown = extraction_results["category_breakdown"]
        
        # Calculate target distribution based on available content
        total_available = len(all_content)
        actual_target = min(target_lines, total_available)
        
        # Priority distribution (adjust based on what's available)
        priority_distribution = {
            "core_act": 0.35,      # 35% - Main acts
            "schedule": 0.25,      # 25% - Schedules
            "tds_rule": 0.20,      # 20% - TDS rules
            "finance_law": 0.10,   # 10% - Finance laws
            "circular": 0.05,      # 5% - Circulars
            "sro_order": 0.03,     # 3% - SRO orders
            "general": 0.02        # 2% - General
        }
        
        balanced_dataset = []
        category_counts = {}
        
        # Select content based on priority
        for category, target_ratio in priority_distribution.items():
            if category not in category_breakdown:
                continue
            
            available_content = category_breakdown[category]
            target_count = int(actual_target * target_ratio)
            
            # Take up to target_count items from this category
            selected_count = min(target_count, len(available_content))
            
            # Sort by length (longer content often more useful for NER)
            sorted_content = sorted(available_content, key=lambda x: x['length'], reverse=True)
            selected_content = sorted_content[:selected_count]
            
            balanced_dataset.extend(selected_content)
            category_counts[category] = selected_count
            
            logger.info(f"  {category}: {selected_content} lines (target: {target_count})")
        
        # If we haven't reached the target, add more from largest categories
        remaining_needed = actual_target - len(balanced_dataset)
        if remaining_needed > 0:
            # Get remaining content not yet selected
            selected_texts = {item['text'] for item in balanced_dataset}
            remaining_content = [item for item in all_content if item['text'] not in selected_texts]
            
            # Sort by length and quality (Bengali + English content preferred)
            remaining_content.sort(key=lambda x: (
                x['has_bengali'] and x['has_english'],  # Bilingual preferred
                x['length']  # Longer preferred
            ), reverse=True)
            
            additional_content = remaining_content[:remaining_needed]
            balanced_dataset.extend(additional_content)
        
        # Final dataset
        final_dataset = {
            "metadata": {
                "dataset_name": "Real Bengali Legal NER Training Dataset",
                "version": "2.0",
                "creation_date": "2025-08-12",
                "extraction_method": "substantial_content_extraction",
                "total_lines_extracted": len(balanced_dataset),
                "target_lines": target_lines,
                "target_achieved": len(balanced_dataset) >= 5000
            },
            "extraction_statistics": extraction_results["statistics"],
            "category_distribution": category_counts,
            "training_data": balanced_dataset,
            "quality_metrics": {
                "avg_line_length": sum(item['length'] for item in balanced_dataset) / len(balanced_dataset),
                "bilingual_content": len([item for item in balanced_dataset if item['has_bengali'] and item['has_english']]),
                "bengali_only": len([item for item in balanced_dataset if item['has_bengali'] and not item['has_english']]),
                "english_only": len([item for item in balanced_dataset if not item['has_bengali'] and item['has_english']])
            }
        }
        
        logger.info(f"✅ Balanced dataset created with {len(balanced_dataset)} lines")
        return final_dataset
    
    def export_training_dataset(self, dataset: Dict[str, Any]):
        """Export the training dataset in multiple formats"""
        
        # Export complete dataset
        dataset_file = self.output_dir / "real_training_dataset.json"
        with open(dataset_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        # Export text-only format for quick review
        text_file = self.output_dir / "extracted_text_samples.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("REAL Bengali Legal Training Data - Text Samples\n")
            f.write("=" * 60 + "\n\n")
            
            for i, item in enumerate(dataset["training_data"][:500]):  # First 500 for review
                f.write(f"SAMPLE {i+1:03d} | {item['category'].upper()} | {item['source']}\n")
                f.write(f"Length: {item['length']} | Bengali: {item['has_bengali']} | English: {item['has_english']}\n")
                f.write("-" * 60 + "\n")
                f.write(item['text'])
                f.write("\n" + "=" * 60 + "\n\n")
        
        # Export statistics summary
        stats_file = self.output_dir / "extraction_statistics.json"
        stats_summary = {
            "extraction_summary": dataset["metadata"],
            "content_statistics": dataset["extraction_statistics"],
            "quality_metrics": dataset["quality_metrics"],
            "category_distribution": dataset["category_distribution"]
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_summary, f, ensure_ascii=False, indent=2)
        
        return dataset_file, text_file, stats_file

def main():
    """Extract real substantial Bengali legal training data"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    output_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_5_bengali_legal_ner/real_training_data"
    
    extractor = RealTrainingDataExtractor(data_dir, output_dir)
    
    # Extract substantial content from all files
    extraction_results = extractor.extract_from_all_files()
    
    # Create balanced training dataset
    training_dataset = extractor.create_balanced_training_dataset(extraction_results, target_lines=5000)
    
    # Export training dataset
    dataset_file, text_file, stats_file = extractor.export_training_dataset(training_dataset)
    
    print("🎯 PHASE 1.5G COMPLETED: Real Training Data Extraction")
    print(f"Dataset file: {dataset_file}")
    print(f"Text samples: {text_file}")
    print(f"Statistics: {stats_file}")
    
    # Print results
    metadata = training_dataset["metadata"]
    stats = training_dataset["extraction_statistics"]
    quality = training_dataset["quality_metrics"]
    
    print(f"\n📊 Extraction Results:")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Files with content: {stats['files_with_content']}")
    print(f"  Total lines extracted: {metadata['total_lines_extracted']}")
    print(f"  Target achieved: {'✅ YES' if metadata['target_achieved'] else '❌ NO'}")
    
    print(f"\n📋 Content Quality:")
    print(f"  Average line length: {quality['avg_line_length']:.1f} characters")
    print(f"  Bilingual content: {quality['bilingual_content']} lines")
    print(f"  Bengali-only content: {quality['bengali_only']} lines")
    print(f"  English-only content: {quality['english_only']} lines")
    
    print(f"\n🗂️  Category Distribution:")
    for category, count in training_dataset['category_distribution'].items():
        print(f"  {category}: {count} lines")

if __name__ == "__main__":
    main()