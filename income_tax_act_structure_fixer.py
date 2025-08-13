#!/usr/bin/env python3
"""
Income Tax Act 2023 Structure Fixer
===================================

Fixes the structure to match exact website format:
- অংশ (Part) → অধ্যায় (Chapter) → ধারা (Section - serialized ignoring chapter boundaries)
- Sections are numbered continuously: ধারা ১, ধারা ২, ধারা ৩... across ALL chapters and parts
- Subsections, clauses, subclauses, articles, tables at any hierarchy level

Author: Phase 2.5 Integration Team
Date: August 13, 2025
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass 
class FixedSection:
    section_number: str  # "ধারা ১", "ধারা ২", etc.
    section_serial: int  # 1, 2, 3... (continuous across all chapters)
    original_number: str  # Original "১", "২" from current file
    title: str
    content_text: str
    subsections: List[Dict]
    clauses: List[Dict] 
    tables: List[Dict]
    footnotes: List[Dict]
    part_number: str  # "অংশ ১"
    chapter_number: str  # "প্রথম অধ্যায়" (if exists)

class IncomeTaxActStructureFixer:
    """Fix Income Tax Act structure to match website format"""
    
    def __init__(self):
        self.section_counter = 0  # Global counter for serialized sections
        self.fixed_sections: List[FixedSection] = []
        
    def load_current_file(self, file_path: str) -> Dict:
        """Load current malformed JSON file"""
        print(f"📂 Loading: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"✅ Loaded {len(data.get('parts', []))} parts")
        return data
    
    def extract_all_sections(self, data: Dict) -> List[FixedSection]:
        """Extract all sections and serialize them properly"""
        print("\n🔄 Extracting and serializing sections...")
        
        all_sections = []
        
        for part in data.get('parts', []):
            part_number = part.get('number', '')
            print(f"📋 Processing {part_number}")
            
            # Check if part has direct sections (no chapters)
            if part.get('sections') and len(part['sections']) > 0:
                for section_data in part['sections']:
                    fixed_section = self.create_fixed_section(
                        section_data, part_number, ""
                    )
                    if fixed_section:
                        all_sections.append(fixed_section)
            
            # Process chapters within part
            for chapter in part.get('chapters', []):
                chapter_number = chapter.get('number', '')
                
                # Check if chapter has sections
                if chapter.get('sections') and len(chapter['sections']) > 0:
                    for section_data in chapter['sections']:
                        fixed_section = self.create_fixed_section(
                            section_data, part_number, chapter_number
                        )
                        if fixed_section:
                            all_sections.append(fixed_section)
        
        print(f"✅ Extracted {len(all_sections)} sections total")
        return all_sections
    
    def create_fixed_section(self, section_data: Dict, part_number: str, chapter_number: str) -> Optional[FixedSection]:
        """Create properly structured section with serialized numbering"""
        
        if not section_data:
            return None
            
        # Increment global section counter
        self.section_counter += 1
        
        # Convert number to Bengali if needed
        bengali_number = self.convert_to_bengali(self.section_counter)
        
        # Create serialized section number
        section_number = f"ধারা {bengali_number}"
        
        # Get original data
        original_number = section_data.get('number', '')
        title = section_data.get('title', '')
        content_text = section_data.get('content_text', '')
        
        # Process subsections, clauses, tables (preserve existing structure)
        subsections = section_data.get('subsections', [])
        clauses = section_data.get('clauses', [])
        tables = section_data.get('tables', [])
        footnotes = section_data.get('footnotes', [])
        
        print(f"   📄 {section_number} ({original_number}) - {title[:50]}...")
        
        return FixedSection(
            section_number=section_number,
            section_serial=self.section_counter,
            original_number=original_number,
            title=title,
            content_text=content_text,
            subsections=subsections,
            clauses=clauses,
            tables=tables,
            footnotes=footnotes,
            part_number=part_number,
            chapter_number=chapter_number
        )
    
    def convert_to_bengali(self, number: int) -> str:
        """Convert English number to Bengali"""
        bengali_digits = {
            '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
            '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
        }
        
        english_str = str(number)
        bengali_str = ''
        
        for digit in english_str:
            bengali_str += bengali_digits.get(digit, digit)
            
        return bengali_str
    
    def rebuild_structure(self, original_data: Dict, fixed_sections: List[FixedSection]) -> Dict:
        """Rebuild the structure with properly serialized sections"""
        print("\n🏗️ Rebuilding structure...")
        
        # Create section lookup by part and chapter
        sections_by_location = {}
        
        for section in fixed_sections:
            location_key = f"{section.part_number}|{section.chapter_number}"
            if location_key not in sections_by_location:
                sections_by_location[location_key] = []
            sections_by_location[location_key].append(section)
        
        # Rebuild parts structure
        new_parts = []
        
        for part in original_data.get('parts', []):
            part_number = part.get('number', '')
            
            new_part = {
                'number': part_number,
                'title': part.get('title', ''),
                'chapters': [],
                'sections': []
            }
            
            # Handle direct sections in part (no chapters)
            direct_section_key = f"{part_number}|"
            if direct_section_key in sections_by_location:
                for section in sections_by_location[direct_section_key]:
                    new_part['sections'].append({
                        'section_number': section.section_number,
                        'section_serial': section.section_serial,
                        'original_number': section.original_number,
                        'title': section.title,
                        'content_text': section.content_text,
                        'subsections': section.subsections,
                        'clauses': section.clauses,
                        'tables': section.tables,
                        'footnotes': section.footnotes
                    })
            
            # Handle chapters
            for chapter in part.get('chapters', []):
                chapter_number = chapter.get('number', '')
                
                new_chapter = {
                    'number': chapter_number,
                    'title': chapter.get('title', ''),
                    'sections': []
                }
                
                # Add sections to chapter
                chapter_section_key = f"{part_number}|{chapter_number}"
                if chapter_section_key in sections_by_location:
                    for section in sections_by_location[chapter_section_key]:
                        new_chapter['sections'].append({
                            'section_number': section.section_number,
                            'section_serial': section.section_serial,
                            'original_number': section.original_number,
                            'title': section.title,
                            'content_text': section.content_text,
                            'subsections': section.subsections,
                            'clauses': section.clauses,
                            'tables': section.tables,
                            'footnotes': section.footnotes
                        })
                
                new_part['chapters'].append(new_chapter)
            
            new_parts.append(new_part)
        
        # Create final structure
        fixed_structure = {
            'header': original_data.get('header', {}),
            'parts': new_parts,
            'metadata': {
                'total_parts': len(new_parts),
                'total_sections': len(fixed_sections),
                'serialization_method': 'continuous_across_all_parts_and_chapters',
                'structure_format': 'অংশ → অধ্যায় → ধারা (serialized) → subsection → clause → subclause → article → table',
                'fixed_date': '2025-08-13',
                'fix_version': '1.0'
            }
        }
        
        print(f"✅ Rebuilt structure with {len(fixed_sections)} serialized sections")
        return fixed_structure
    
    def validate_serialization(self, fixed_sections: List[FixedSection]) -> bool:
        """Validate that sections are properly serialized"""
        print("\n🔍 Validating serialization...")
        
        # Check continuous numbering
        expected = 1
        for section in fixed_sections:
            if section.section_serial != expected:
                print(f"❌ Serialization error: Expected {expected}, got {section.section_serial}")
                return False
            expected += 1
        
        # Check section number format
        for section in fixed_sections:
            if not section.section_number.startswith('ধারা '):
                print(f"❌ Format error: {section.section_number} doesn't start with 'ধারা '")
                return False
        
        print(f"✅ Serialization valid: ধারা ১ to ধারা {len(fixed_sections)}")
        return True
    
    def fix_structure(self, input_file: str, output_file: str) -> bool:
        """Main method to fix the structure"""
        print("🚀 Income Tax Act Structure Fixer")
        print("=" * 50)
        
        try:
            # Load current file
            original_data = self.load_current_file(input_file)
            
            # Extract and serialize sections
            fixed_sections = self.extract_all_sections(original_data)
            
            if not fixed_sections:
                print("❌ No sections found to fix!")
                return False
            
            # Validate serialization
            if not self.validate_serialization(fixed_sections):
                print("❌ Serialization validation failed!")
                return False
            
            # Rebuild structure
            fixed_structure = self.rebuild_structure(original_data, fixed_sections)
            
            # Save fixed file
            print(f"\n💾 Saving fixed structure to: {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(fixed_structure, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Structure fixed successfully!")
            print(f"📊 Summary:")
            print(f"   • Total sections: {len(fixed_sections)}")
            print(f"   • Serialization: ধারা ১ → ধারা {len(fixed_sections)}")
            print(f"   • Structure: অংশ → অধ্যায় → ধারা (serialized)")
            print(f"   • File: {output_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing structure: {e}")
            return False

def main():
    """Main function"""
    fixer = IncomeTaxActStructureFixer()
    
    input_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data/core_acts/income_tax_act_2023_cleaned.json"
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data/core_acts/income_tax_act_2023_fixed_structure.json"
    
    success = fixer.fix_structure(input_file, output_file)
    
    if success:
        print("\n🎉 Income Tax Act structure fixed successfully!")
        print("Ready for Phase 2.5 integration!")
    else:
        print("\n💥 Structure fixing failed!")
        
    return success

if __name__ == "__main__":
    main()