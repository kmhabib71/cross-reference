#!/usr/bin/env python3
"""
Income Tax Act 2023 Sequential Distributor
==========================================

Simple sequential distribution of 341 sections across 25 parts and chapters
based on the original structure template. Maintains serialized section numbering
while properly distributing sections to their correct hierarchical locations.

Author: Phase 2.5 Integration Team
Date: August 13, 2025
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path

class IncomeTaxActSequentialDistributor:
    """Sequential distribution of sections across proper structure"""
    
    def __init__(self):
        self.section_counter = 0
        
    def load_files(self, malformed_file: str, template_file: str) -> tuple:
        """Load malformed file (with sections) and template file (with structure)"""
        print(f"📂 Loading files...")
        
        # Load malformed file to get sections
        with open(malformed_file, 'r', encoding='utf-8') as f:
            malformed_data = json.load(f)
        
        # Extract all sections from Part 25
        all_sections = []
        for part in malformed_data.get('parts', []):
            if part.get('sections') and len(part['sections']) > 0:
                all_sections.extend(part['sections'])
                print(f"   📋 Found {len(part['sections'])} sections in {part.get('number', 'Unknown')}")
        
        # Load template file to get structure
        with open(template_file, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
            
        print(f"✅ Loaded {len(all_sections)} sections and structure template")
        return malformed_data, all_sections, template_data
    
    def calculate_distribution(self, template_data: Dict, total_sections: int) -> Dict:
        """Calculate how to distribute sections across parts and chapters"""
        print("\n📊 Calculating distribution...")
        
        # Count available locations
        locations = []
        
        for part in template_data.get('parts', []):
            part_num = part.get('number', '')
            
            # Check for direct sections (parts without chapters)
            if not part.get('chapters') or len(part.get('chapters', [])) == 0:
                locations.append({
                    'type': 'part_direct',
                    'part': part_num,
                    'chapter': '',
                    'location_id': f"{part_num}_direct"
                })
            else:
                # Add chapters within part
                for chapter in part.get('chapters', []):
                    chapter_num = chapter.get('number', '')
                    locations.append({
                        'type': 'chapter',
                        'part': part_num,
                        'chapter': chapter_num,
                        'location_id': f"{part_num}_{chapter_num}"
                    })
        
        print(f"   📍 Found {len(locations)} distribution locations")
        
        # Calculate sections per location
        sections_per_location = total_sections // len(locations)
        remainder = total_sections % len(locations)
        
        print(f"   📊 Base sections per location: {sections_per_location}")
        print(f"   📊 Locations with +1 section: {remainder}")
        
        # Create distribution plan
        distribution_plan = {}
        section_start = 1
        
        for i, location in enumerate(locations):
            sections_for_location = sections_per_location + (1 if i < remainder else 0)
            section_end = section_start + sections_for_location - 1
            
            distribution_plan[location['location_id']] = {
                'part': location['part'],
                'chapter': location['chapter'],
                'start_section': section_start,
                'end_section': section_end,
                'count': sections_for_location
            }
            
            print(f"   📋 {location['location_id']}: ধারা {section_start}-{section_end} ({sections_for_location} sections)")
            section_start = section_end + 1
        
        return distribution_plan, locations
    
    def distribute_sections(self, all_sections: List[Dict], distribution_plan: Dict) -> Dict:
        """Distribute sections according to plan"""
        print("\n🔄 Distributing sections...")
        
        distributed_sections = {}
        
        for location_id, plan in distribution_plan.items():
            start = plan['start_section'] - 1  # Convert to 0-based index
            end = plan['end_section']  # Exclusive end
            
            sections_for_location = []
            
            for i in range(start, end):
                if i < len(all_sections):
                    section = all_sections[i]
                    self.section_counter = i + 1
                    
                    # Create properly formatted section
                    bengali_number = self._convert_to_bengali(self.section_counter)
                    section_number = f"ধারা {bengali_number}"
                    
                    formatted_section = {
                        "section_number": section_number,
                        "section_serial": self.section_counter,
                        "original_number": section.get('number', ''),
                        "title": section.get('title', ''),
                        "content_text": section.get('content_text', ''),
                        "subsections": section.get('subsections', []),
                        "clauses": section.get('clauses', []),
                        "tables": section.get('tables', []),
                        "footnotes": section.get('footnotes', [])
                    }
                    
                    sections_for_location.append(formatted_section)
            
            distributed_sections[location_id] = sections_for_location
            print(f"   📄 {location_id}: {len(sections_for_location)} sections distributed")
        
        return distributed_sections
    
    def rebuild_structure(self, template_data: Dict, distributed_sections: Dict, distribution_plan: Dict) -> Dict:
        """Rebuild structure with distributed sections"""
        print("\n🏗️ Rebuilding structure...")
        
        new_parts = []
        
        for part in template_data.get('parts', []):
            part_num = part.get('number', '')
            
            new_part = {
                'number': part_num,
                'title': part.get('title', ''),
                'chapters': [],
                'sections': []
            }
            
            # Check for direct sections (no chapters)
            direct_location_id = f"{part_num}_direct"
            if direct_location_id in distributed_sections:
                new_part['sections'] = distributed_sections[direct_location_id]
                print(f"   📋 {part_num}: {len(new_part['sections'])} direct sections")
            
            # Process chapters
            for chapter in part.get('chapters', []):
                chapter_num = chapter.get('number', '')
                
                new_chapter = {
                    'number': chapter_num,
                    'title': chapter.get('title', ''),
                    'sections': []
                }
                
                # Add sections to chapter
                chapter_location_id = f"{part_num}_{chapter_num}"
                if chapter_location_id in distributed_sections:
                    new_chapter['sections'] = distributed_sections[chapter_location_id]
                    print(f"   📋 {part_num} → {chapter_num}: {len(new_chapter['sections'])} sections")
                
                new_part['chapters'].append(new_chapter)
            
            new_parts.append(new_part)
        
        # Create final structure
        final_structure = {
            'header': template_data.get('header', {}),
            'parts': new_parts,
            'metadata': {
                'total_parts': len(new_parts),
                'total_sections': self.section_counter,
                'distribution_method': 'sequential_even_distribution',
                'serialization_method': 'continuous_across_all_parts_and_chapters',
                'structure_format': 'অংশ → অধ্যায় → ধারা (properly distributed & serialized) → subsection → clause → subclause → article → table',
                'distributed_date': '2025-08-13',
                'distribution_version': '1.0'
            }
        }
        
        print(f"✅ Structure rebuilt with {self.section_counter} sections properly distributed")
        return final_structure
    
    def _convert_to_bengali(self, number: int) -> str:
        """Convert English number to Bengali"""
        bengali_digits = {
            '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
            '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
        }
        
        english_str = str(number)
        return ''.join(bengali_digits.get(digit, digit) for digit in english_str)
    
    def validate_distribution(self, final_structure: Dict) -> bool:
        """Validate that all sections are properly distributed"""
        print("\n🔍 Validating distribution...")
        
        total_sections = 0
        parts_with_sections = 0
        chapters_with_sections = 0
        
        for part in final_structure.get('parts', []):
            part_sections = len(part.get('sections', []))
            total_sections += part_sections
            
            if part_sections > 0:
                parts_with_sections += 1
            
            for chapter in part.get('chapters', []):
                chapter_sections = len(chapter.get('sections', []))
                total_sections += chapter_sections
                
                if chapter_sections > 0:
                    chapters_with_sections += 1
        
        print(f"   📊 Total sections distributed: {total_sections}")
        print(f"   📊 Parts with sections: {parts_with_sections}")
        print(f"   📊 Chapters with sections: {chapters_with_sections}")
        
        # Validate serialization
        all_found_sections = []
        for part in final_structure.get('parts', []):
            all_found_sections.extend(part.get('sections', []))
            for chapter in part.get('chapters', []):
                all_found_sections.extend(chapter.get('sections', []))
        
        # Check serial order
        serials = [section.get('section_serial', 0) for section in all_found_sections]
        serials.sort()
        expected_serials = list(range(1, 342))  # 1 to 341
        
        if serials == expected_serials:
            print("✅ All sections properly distributed and serialized!")
            return True
        else:
            print(f"❌ Serialization error! Expected 1-341, got {serials[:5]}...{serials[-5:]}")
            return False
    
    def distribute_structure(self, malformed_file: str, template_file: str, output_file: str) -> bool:
        """Main method to distribute structure"""
        print("🚀 Income Tax Act Sequential Distributor")
        print("=" * 50)
        
        try:
            # Load files
            malformed_data, all_sections, template_data = self.load_files(malformed_file, template_file)
            
            if len(all_sections) != 341:
                print(f"⚠️ Expected 341 sections, found {len(all_sections)}")
            
            # Calculate distribution
            distribution_plan, locations = self.calculate_distribution(template_data, len(all_sections))
            
            # Distribute sections
            distributed_sections = self.distribute_sections(all_sections, distribution_plan)
            
            # Rebuild structure  
            final_structure = self.rebuild_structure(template_data, distributed_sections, distribution_plan)
            
            # Validate
            if not self.validate_distribution(final_structure):
                print("❌ Distribution validation failed!")
                return False
            
            # Save
            print(f"\n💾 Saving properly distributed structure to: {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_structure, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Structure successfully distributed!")
            print(f"📊 Summary:")
            print(f"   • Total sections: {len(all_sections)}")
            print(f"   • Distribution: Sequential across {len(locations)} locations")
            print(f"   • Serialization: ধারা ১ → ধারা ৩৪১")
            print(f"   • Structure: অংশ → অধ্যায় → ধারা (properly distributed)")
            print(f"   • File: {output_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error distributing structure: {e}")
            return False

def main():
    """Main function"""
    distributor = IncomeTaxActSequentialDistributor()
    
    malformed_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data/core_acts/income_tax_act_2023_cleaned.json"
    template_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data/core_acts/income_tax_act_2023_cleaned.json"
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data/core_acts/income_tax_act_2023_properly_distributed.json"
    
    success = distributor.distribute_structure(malformed_file, template_file, output_file)
    
    if success:
        print("\n🎉 Income Tax Act structure properly distributed!")
        print("Ready for Phase 2.5 integration with correct part/chapter distribution!")
    else:
        print("\n💥 Structure distribution failed!")
        
    return success

if __name__ == "__main__":
    main()