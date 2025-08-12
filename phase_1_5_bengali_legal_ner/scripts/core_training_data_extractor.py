#!/usr/bin/env python3
"""
Core Training Data Extractor for Bengali Legal NER
Phase 1.5A: Extract 5K high-value lines from priority documents
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoreTrainingDataExtractor:
    def __init__(self, data_dir: str, phase_1_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.phase_1_dir = Path(phase_1_dir)
        self.output_dir = Path(output_dir)
        
        # Load Phase 1 citation results to identify high-value sections
        self.citation_results = self.load_phase_1_citations()
        
        # Define priority sections based on Bangladesh Tax Law importance
        self.priority_sections = {
            "minimum_tax": [163],  # Section 163 - Minimum Tax
            "exemptions": [44, 45, 46],  # Tax exemption sections
            "rates": [20, 21, 22],  # Tax rate sections  
            "tds_core": [82, 83, 84],  # TDS main sections
            "filing": [75, 76, 77],  # Return filing sections
            "assessment": [120, 121, 122],  # Assessment sections
        }
        
        # Target data distribution for 5K lines
        self.target_distribution = {
            "income_tax_act_core": 2500,  # 50% - Main Act
            "schedules_key": 1000,        # 20% - Key Schedules 
            "tds_rules": 800,             # 16% - TDS Rules
            "finance_ordinance": 500,     # 10% - Finance Ordinance
            "circulars_sample": 200       # 4% - Circular samples
        }
    
    def load_phase_1_citations(self) -> Dict[str, Any]:
        """Load Phase 1 citation results to identify high-frequency sections"""
        try:
            citation_file = self.phase_1_dir / "ACTUAL_citation_extraction_results.json"
            with open(citation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Phase 1 citation results not found, using default priorities")
            return {"extracted_citations": {"sections": []}}
    
    def get_high_frequency_sections(self) -> List[int]:
        """Identify most cited sections from Phase 1 data"""
        section_counts = {}
        
        for citation in self.citation_results.get("extracted_citations", {}).get("sections", []):
            try:
                section_num = int(citation.get("section_number", 0))
                section_counts[section_num] = section_counts.get(section_num, 0) + 1
            except (ValueError, TypeError):
                continue
        
        # Sort by frequency and return top sections
        high_freq_sections = sorted(section_counts.items(), key=lambda x: x[1], reverse=True)
        return [section for section, count in high_freq_sections[:20]]
    
    def extract_section_content(self, text: str, section_number: int, context_lines: int = 10) -> List[str]:
        """Extract content around a specific section with context"""
        lines = text.split('\n')
        section_content = []
        
        # Bengali and English patterns for the section
        patterns = [
            rf'ধারা\s*{section_number}(?:\D|$)',
            rf'ধারা\s*{self.convert_to_bengali_number(section_number)}(?:\D|$)',
            rf'[Ss]ection\s*{section_number}(?:\D|$)',
        ]
        
        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    # Extract section with context
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 10)  # More lines after section
                    section_content.extend(lines[start:end])
                    break
        
        return section_content
    
    def convert_to_bengali_number(self, number: int) -> str:
        """Convert English number to Bengali"""
        bengali_digits = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
                         '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'}
        return ''.join(bengali_digits.get(d, d) for d in str(number))
    
    def extract_income_tax_act_core(self, target_lines: int) -> List[Dict[str, Any]]:
        """Extract core sections from Income Tax Act 2023"""
        logger.info(f"Extracting {target_lines} lines from Income Tax Act core sections...")
        
        act_file = self.data_dir / "core_acts" / "income_tax_act_2023_cleaned.json"
        extracted_content = []
        
        try:
            with open(act_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract main content
            content = data.get('main_content', '') or str(data)
            
            # Get high frequency sections from Phase 1
            high_freq_sections = self.get_high_frequency_sections()
            
            # Combine priority sections with high frequency sections
            all_priority_sections = []
            for category, sections in self.priority_sections.items():
                all_priority_sections.extend(sections)
            
            # Add high frequency sections
            all_priority_sections.extend(high_freq_sections[:10])
            all_priority_sections = list(set(all_priority_sections))  # Remove duplicates
            
            current_lines = 0
            for section_num in all_priority_sections:
                if current_lines >= target_lines:
                    break
                
                section_content = self.extract_section_content(content, section_num)
                if section_content:
                    content_text = '\n'.join(section_content)
                    line_count = len(section_content)
                    
                    extracted_content.append({
                        "source": "income_tax_act_2023",
                        "section_number": section_num,
                        "content": content_text,
                        "line_count": line_count,
                        "priority_category": self.get_section_category(section_num),
                        "extraction_method": "section_targeted"
                    })
                    
                    current_lines += line_count
                    logger.info(f"Extracted Section {section_num}: {line_count} lines")
            
            logger.info(f"Total lines extracted from Income Tax Act: {current_lines}")
            return extracted_content
            
        except Exception as e:
            logger.error(f"Error extracting from Income Tax Act: {e}")
            return []
    
    def get_section_category(self, section_num: int) -> str:
        """Get category for a section number"""
        for category, sections in self.priority_sections.items():
            if section_num in sections:
                return category
        return "high_frequency"
    
    def extract_key_schedules(self, target_lines: int) -> List[Dict[str, Any]]:
        """Extract content from key tax schedules"""
        logger.info(f"Extracting {target_lines} lines from key schedules...")
        
        extracted_content = []
        current_lines = 0
        
        # Priority schedules
        priority_schedules = [
            "income-tax-schedule-bangla-6th-schedule-part-1-exclusions-from-computation-of-total-income.json",
            "income-tax-schedule-bangla-7th-schedule-special-tax-rate.json",
            "income-tax-schedule-bangla-1st-schedule-part-1-disclosure-of-investment-by-paying-special-taxes.json"
        ]
        
        for schedule_file in priority_schedules:
            if current_lines >= target_lines:
                break
                
            schedule_path = self.data_dir / "schedules" / schedule_file
            if schedule_path.exists():
                try:
                    with open(schedule_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    content = data.get('main_content', '') or str(data)
                    lines = content.split('\n')
                    
                    # Take sample lines from schedule
                    sample_size = min(len(lines), target_lines - current_lines)
                    sample_content = lines[:sample_size]
                    
                    extracted_content.append({
                        "source": schedule_file,
                        "content": '\n'.join(sample_content),
                        "line_count": len(sample_content),
                        "priority_category": "key_schedules",
                        "extraction_method": "schedule_sample"
                    })
                    
                    current_lines += len(sample_content)
                    logger.info(f"Extracted from {schedule_file}: {len(sample_content)} lines")
                    
                except Exception as e:
                    logger.warning(f"Error extracting from {schedule_file}: {e}")
        
        return extracted_content
    
    def extract_tds_rules(self, target_lines: int) -> List[Dict[str, Any]]:
        """Extract content from TDS rules"""
        logger.info(f"Extracting {target_lines} lines from TDS rules...")
        
        extracted_content = []
        current_lines = 0
        
        # Process TDS rules files
        tds_files = list((self.data_dir / "tds_rules").glob("*rules*.json"))
        
        for tds_file in tds_files[:5]:  # Limit to first 5 files
            if current_lines >= target_lines:
                break
                
            try:
                with open(tds_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                content = data.get('main_content', '') or str(data)
                if len(content.strip()) < 50:  # Skip very small files
                    continue
                
                lines = content.split('\n')
                sample_size = min(len(lines), (target_lines - current_lines) // 3)
                
                if sample_size > 0:
                    sample_content = lines[:sample_size]
                    
                    extracted_content.append({
                        "source": tds_file.name,
                        "content": '\n'.join(sample_content),
                        "line_count": len(sample_content),
                        "priority_category": "tds_rules",
                        "extraction_method": "rule_sample"
                    })
                    
                    current_lines += len(sample_content)
                    logger.info(f"Extracted from {tds_file.name}: {len(sample_content)} lines")
                
            except Exception as e:
                logger.warning(f"Error extracting from {tds_file}: {e}")
        
        return extracted_content
    
    def extract_finance_ordinance(self, target_lines: int) -> List[Dict[str, Any]]:
        """Extract content from Finance Ordinance"""
        logger.info(f"Extracting {target_lines} lines from Finance Ordinance...")
        
        ordinance_file = self.data_dir / "finance_laws" / "finance_ordinance_2025_cleaned.json"
        
        try:
            with open(ordinance_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            content = data.get('main_content', '') or str(data)
            lines = content.split('\n')
            
            # Extract sample focusing on amendments
            sample_content = lines[:target_lines]
            
            return [{
                "source": "finance_ordinance_2025",
                "content": '\n'.join(sample_content),
                "line_count": len(sample_content),
                "priority_category": "finance_ordinance",
                "extraction_method": "ordinance_sample"
            }]
            
        except Exception as e:
            logger.error(f"Error extracting from Finance Ordinance: {e}")
            return []
    
    def create_training_dataset(self) -> Dict[str, Any]:
        """Create the complete 5K line training dataset"""
        logger.info("🚀 Creating core 5K line training dataset for Bengali Legal NER...")
        
        training_data = []
        
        # Extract according to target distribution
        training_data.extend(self.extract_income_tax_act_core(self.target_distribution["income_tax_act_core"]))
        training_data.extend(self.extract_key_schedules(self.target_distribution["schedules_key"]))
        training_data.extend(self.extract_tds_rules(self.target_distribution["tds_rules"]))
        training_data.extend(self.extract_finance_ordinance(self.target_distribution["finance_ordinance"]))
        
        # Calculate statistics
        total_lines = sum(item["line_count"] for item in training_data)
        source_distribution = {}
        for item in training_data:
            category = item["priority_category"]
            source_distribution[category] = source_distribution.get(category, 0) + item["line_count"]
        
        dataset = {
            "metadata": {
                "dataset_name": "Bengali Legal NER Core Training Data",
                "version": "1.0",
                "creation_date": "2025-08-12",
                "total_lines": total_lines,
                "total_documents": len(training_data),
                "target_lines": 5000,
                "actual_lines": total_lines
            },
            "source_distribution": source_distribution,
            "training_data": training_data,
            "extraction_summary": {
                "method": "priority_section_targeted",
                "phase_1_integration": "Used citation frequency data for section prioritization",
                "quality_focus": "High-value legal sections with Bengali content"
            }
        }
        
        return dataset

def main():
    """Extract core training data for Phase 1.5A"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    phase_1_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_document_analysis"
    output_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_5_bengali_legal_ner/training_data"
    
    extractor = CoreTrainingDataExtractor(data_dir, phase_1_dir, output_dir)
    dataset = extractor.create_training_dataset()
    
    # Save training dataset
    output_file = Path(output_dir) / "core_5k_training_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print("\n🎯 PHASE 1.5A COMPLETED: Core Training Data Extraction")
    print(f"Dataset saved to: {output_file}")
    print(f"Total lines extracted: {dataset['metadata']['total_lines']}")
    print(f"Documents processed: {dataset['metadata']['total_documents']}")
    print("\nSource Distribution:")
    for category, lines in dataset['source_distribution'].items():
        print(f"  {category}: {lines} lines")

if __name__ == "__main__":
    main()