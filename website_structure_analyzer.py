#!/usr/bin/env python3
"""
Website Structure Analyzer for Income Tax Act 2023
==================================================
Analyzes the actual website structure to determine correct section-to-part mapping.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Tuple

class WebsiteStructureAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def bengali_to_english(self, text: str) -> str:
        """Convert Bengali numerals to English numerals"""
        bengali_to_eng = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        result = text
        for ben, eng in bengali_to_eng.items():
            result = result.replace(ben, eng)
        return result

    def analyze_structure(self, url: str) -> Dict:
        """Analyze the website structure to get correct section mappings"""
        
        print(f"🔍 Fetching content from: {url}")
        response = self.session.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        structure = {
            'parts': [],
            'section_mapping': {},  # section_number -> part_number
            'total_sections': 0
        }
        
        current_part = None
        current_chapter = None
        
        # Find all elements in document order
        all_elements = soup.find_all(['div'])
        
        print("📊 Processing elements in document order...")
        
        for elem in all_elements:
            classes = elem.get('class', [])
            
            # Check for part
            if 'act-part-group' in classes:
                part_no_elem = elem.find('p', class_='act-part-no')
                part_name_elem = elem.find('p', class_='act-part-name')
                
                if part_no_elem and part_name_elem:
                    part_number = part_no_elem.get_text().strip()
                    part_title = part_name_elem.get_text().strip()
                    
                    current_part = {
                        'part_number': part_number,
                        'part_title': part_title,
                        'chapters': [],
                        'sections': [],
                        'section_numbers': []
                    }
                    structure['parts'].append(current_part)
                    print(f"📁 {part_number}: {part_title}")
                    current_chapter = None
            
            # Check for chapter
            elif 'act-chapter-group' in classes and current_part:
                chapter_no_elem = elem.find('p', class_='act-chapter-no')
                chapter_name_elem = elem.find('p', class_='act-chapter-name')
                
                if chapter_no_elem and chapter_name_elem:
                    chapter_number = chapter_no_elem.get_text().strip()
                    chapter_title = chapter_name_elem.get_text().strip()
                    
                    current_chapter = {
                        'chapter_number': chapter_number,
                        'chapter_title': chapter_title,
                        'sections': [],
                        'section_numbers': []
                    }
                    current_part['chapters'].append(current_chapter)
                    print(f"  📚 {chapter_number}: {chapter_title}")
            
            # Check for section
            elif 'row' in classes and current_part:
                txt_head = elem.find('div', class_='txt-head')
                txt_details = elem.find('div', class_='txt-details')
                
                if txt_head or txt_details:
                    content = elem.get_text()
                    
                    # Extract section number more precisely
                    section_pattern = r'([০-৯]+)।'
                    matches = re.findall(section_pattern, content)
                    
                    if matches:
                        for match in matches:
                            eng_num = self.bengali_to_english(match)
                            try:
                                section_num = int(eng_num)
                                if 1 <= section_num <= 400:  # Valid range
                                    # Store the mapping
                                    structure['section_mapping'][section_num] = current_part['part_number']
                                    
                                    # Add to appropriate container
                                    if current_chapter:
                                        current_chapter['section_numbers'].append(section_num)
                                    else:
                                        current_part['section_numbers'].append(section_num)
                                    
                                    structure['total_sections'] += 1
                            except ValueError:
                                continue
        
        # Clean up and sort section numbers
        for part in structure['parts']:
            part['section_numbers'] = sorted(set(part['section_numbers']))
            for chapter in part['chapters']:
                chapter['section_numbers'] = sorted(set(chapter['section_numbers']))
        
        return structure

    def print_structure_summary(self, structure: Dict):
        """Print a summary of the structure"""
        print("\n📋 WEBSITE STRUCTURE SUMMARY")
        print("=" * 40)
        
        total_parts = len(structure['parts'])
        total_sections = len(structure['section_mapping'])
        
        print(f"📁 Total Parts: {total_parts}")
        print(f"📋 Total Sections: {total_sections}")
        
        print("\n🔍 PART-SECTION MAPPING (First 15 parts):")
        
        for i, part in enumerate(structure['parts'][:15]):
            part_sections = part['section_numbers']
            chapter_sections = []
            for chapter in part['chapters']:
                chapter_sections.extend(chapter['section_numbers'])
            
            all_sections = sorted(set(part_sections + chapter_sections))
            
            if all_sections:
                section_range = f"{min(all_sections)}-{max(all_sections)}" if len(all_sections) > 1 else str(all_sections[0])
                chapter_info = f" ({len(part['chapters'])} chapters)" if part['chapters'] else ""
                print(f"   {part['part_number']}: Sections {section_range} ({len(all_sections)} sections){chapter_info}")
            else:
                print(f"   {part['part_number']}: No sections")

    def save_structure(self, structure: Dict, filename: str):
        """Save the structure analysis to a file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Structure saved to: {filename}")

def main():
    analyzer = WebsiteStructureAnalyzer()
    url = "http://bdlaws.minlaw.gov.bd/act-details-1429.html"
    
    # Analyze structure
    structure = analyzer.analyze_structure(url)
    
    # Print summary
    analyzer.print_structure_summary(structure)
    
    # Save analysis
    analyzer.save_structure(structure, 'website_structure_analysis.json')
    
    # Create section mapping for reference
    print("\n🎯 SECTION MAPPING REFERENCE:")
    print("Section → Part")
    section_mapping = structure['section_mapping']
    for section_num in sorted(section_mapping.keys())[:20]:  # First 20 for reference
        part_num = section_mapping[section_num]
        print(f"   ধারা {section_num} → {part_num}")

if __name__ == "__main__":
    main()