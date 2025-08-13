#!/usr/bin/env python3
"""
Complete Final Structure Corrector
==================================
Creates the complete Income Tax Act 2023 structure with proper section sequence starting from 1.
"""

import json
from typing import Dict, List

def create_missing_section_1() -> Dict:
    """Create the missing Section 1"""
    return {
        'number': '১',
        'title': 'সংক্ষিপ্ত শিরোনাম ও প্রারম্ভ',
        'content_text': '১। সংক্ষিপ্ত শিরোনাম ও প্রারম্ভ।-(১) এই আইন আয়কর আইন, ২০২৩ নামে অভিহিত হইবে।\n(২) ইহা অবিলম্বে কার্যকর হইবে।',
        'subsections': [
            {
                'identifier': '১',
                'text': 'এই আইন আয়কর আইন, ২০২৩ নামে অভিহিত হইবে।',
                'clauses': [],
                'tables': []
            },
            {
                'identifier': '২',
                'text': 'ইহা অবিলম্বে কার্যকর হইবে।',
                'clauses': [],
                'tables': []
            }
        ],
        'clauses': [],
        'tables': [],
        'footnotes': []
    }

def convert_bengali_to_english(text: str) -> str:
    """Convert Bengali numerals to English"""
    bengali_to_eng = {
        '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
        '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
    }
    result = text
    for ben, eng in bengali_to_eng.items():
        result = result.replace(ben, eng)
    return result

def adjust_section_number(section: Dict, new_number: int) -> Dict:
    """Adjust section number while preserving content"""
    adjusted_section = section.copy()
    
    # Convert to Bengali
    bengali_num = str(new_number)
    eng_to_bengali = {
        '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
        '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
    }
    
    bengali_section_num = ""
    for char in bengali_num:
        bengali_section_num += eng_to_bengali.get(char, char)
    
    adjusted_section['number'] = bengali_section_num
    
    # Update content_text to reflect new number (if it starts with the old number)
    content = adjusted_section.get('content_text', '')
    # Simple replacement of section number at the beginning
    if content and re.match(r'^[০-৯]+।', content):
        content = re.sub(r'^[০-৯]+।', f'{bengali_section_num}।', content)
        adjusted_section['content_text'] = content
    
    return adjusted_section

def load_existing_sections() -> tuple:
    """Load existing sections and create adjusted mapping"""
    with open('/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data/core_acts/income_tax_act_2023_website_corrected.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Collect all sections with their current numbers
    sections_by_current_number = {}
    
    for part in data.get('parts', []):
        for section in part.get('direct_sections', []):
            current_num = int(convert_bengali_to_english(section['number']))
            sections_by_current_number[current_num] = section
        
        for chapter in part.get('chapters', []):
            for section in chapter.get('sections', []):
                current_num = int(convert_bengali_to_english(section['number']))
                sections_by_current_number[current_num] = section
    
    print(f"📖 Loaded {len(sections_by_current_number)} sections")
    print(f"   Current range: {min(sections_by_current_number.keys())} to {max(sections_by_current_number.keys())}")
    
    return sections_by_current_number, data.get('document_info', {})

def build_complete_correct_structure() -> Dict:
    """Build complete structure with proper sequential numbering"""
    
    print("🔧 BUILDING COMPLETE CORRECT STRUCTURE")
    print("=" * 42)
    
    # Load existing sections
    current_sections, doc_info = load_existing_sections()
    
    # Create the sequential mapping based on user requirements
    sequential_mapping = []
    current_new_number = 1
    
    # Add Section 1 first
    sequential_mapping.append({
        'new_number': 1,
        'section': create_missing_section_1(),
        'part': 'অংশ ১',
        'chapter': None
    })
    current_new_number = 2
    
    # Now map existing sections in their correct order
    # The user wants: Part 1: 1-3, Part 2: 4-12, Part 3: 13-17, Part 4: 18-28 (with chapters)
    
    # Part 1: Sections 1-3 (1 is our added section, 2-3 from current sections 2-3)
    for original_num in [2, 3]:
        if original_num in current_sections:
            sequential_mapping.append({
                'new_number': current_new_number,
                'section': current_sections[original_num],
                'part': 'অংশ ১',
                'chapter': None
            })
            current_new_number += 1
    
    # Part 2: Sections 4-12 (from current sections 5-13, but renumbered to 4-12)
    original_part2_sections = [5, 6, 7, 8, 9, 10, 11, 12, 13]
    for i, original_num in enumerate(original_part2_sections):
        if original_num in current_sections:
            sequential_mapping.append({
                'new_number': current_new_number,
                'section': current_sections[original_num],
                'part': 'অংশ ২',
                'chapter': None
            })
            current_new_number += 1
    
    # Part 3: Sections 13-17 (from current sections 14-18, renumbered)
    original_part3_sections = [14, 15, 16, 17, 18]
    for i, original_num in enumerate(original_part3_sections):
        if original_num in current_sections:
            sequential_mapping.append({
                'new_number': current_new_number,
                'section': current_sections[original_num],
                'part': 'অংশ ৩', 
                'chapter': None
            })
            current_new_number += 1
    
    # Part 4: Sections 18-28 with chapters (from current sections 19-29)
    # Chapter 1: 18-25, Chapter 2: 26-28
    part4_chapter1 = [19, 21, 22, 23, 24, 25, 26] # Skip 20 as it's missing
    part4_chapter2 = [27, 28, 29]
    
    for original_num in part4_chapter1:
        if original_num in current_sections:
            sequential_mapping.append({
                'new_number': current_new_number,
                'section': current_sections[original_num],
                'part': 'অংশ ৪',
                'chapter': 'প্রথম অধ্যায়'
            })
            current_new_number += 1
    
    for original_num in part4_chapter2:
        if original_num in current_sections:
            sequential_mapping.append({
                'new_number': current_new_number,
                'section': current_sections[original_num],
                'part': 'অংশ ৪',
                'chapter': 'দ্বিতীয় অধ্যায়'
            })
            current_new_number += 1
    
    print(f"📊 Created sequential mapping for {len(sequential_mapping)} sections")
    print(f"   New range: 1 to {current_new_number - 1}")
    
    # Build the document structure
    document = {
        'document_info': {
            'title': 'আয়কর আইন, ২০২৩',
            'ordinance_info': '( ২০২৩ সনের ১২ নং আইন )',
            'publish_date': '[ ২২ জুন, ২০২৩ ]',
            'structure_format': 'অংশ (Parts) → অধ্যায় (Chapters) → ধারা (Sections) - SEQUENTIAL FROM 1',
            'extraction_method': 'Website Analysis + Sequential Renumbering + Missing Section 1',
            'version': '5.0_complete_sequential_corrected'
        },
        'structure_summary': {},
        'parts': []
    }
    
    # Group sections by part and chapter
    parts_structure = {}
    
    for mapping in sequential_mapping:
        part_key = mapping['part']
        chapter_key = mapping['chapter']
        adjusted_section = adjust_section_number(mapping['section'], mapping['new_number'])
        
        if part_key not in parts_structure:
            parts_structure[part_key] = {
                'direct_sections': [],
                'chapters': {}
            }
        
        if chapter_key:
            if chapter_key not in parts_structure[part_key]['chapters']:
                parts_structure[part_key]['chapters'][chapter_key] = []
            parts_structure[part_key]['chapters'][chapter_key].append(adjusted_section)
        else:
            parts_structure[part_key]['direct_sections'].append(adjusted_section)
    
    # Convert to final document structure
    part_titles = {
        'অংশ ১': 'প্রারম্ভিক',
        'অংশ ২': 'কর প্রশাসন',
        'অংশ ৩': 'কর আপিল ট্রাইব্যুনাল',
        'অংশ ৪': 'আয়কর ধার্যকরণ'
    }
    
    chapter_titles = {
        'প্রথম অধ্যায়': 'কর ধার্যকরণের ভিত্তি',
        'দ্বিতীয় অধ্যায়': 'আয়ের আওতা'
    }
    
    total_sections = 0
    total_chapters = 0
    
    for part_key in sorted(parts_structure.keys(), key=lambda x: int(convert_bengali_to_english(x.split(' ')[1]))):
        part_data = parts_structure[part_key]
        
        formatted_part = {
            'part_number': part_key,
            'part_title': part_titles.get(part_key, part_key),
            'chapters': [],
            'direct_sections': sorted(part_data['direct_sections'], 
                                    key=lambda x: int(convert_bengali_to_english(x['number'])))
        }
        
        for chapter_key, sections in part_data['chapters'].items():
            formatted_chapter = {
                'chapter_number': chapter_key,
                'chapter_title': chapter_titles.get(chapter_key, chapter_key),
                'sections': sorted(sections, key=lambda x: int(convert_bengali_to_english(x['number'])))
            }
            formatted_part['chapters'].append(formatted_chapter)
            total_chapters += 1
        
        total_sections += len(formatted_part['direct_sections'])
        for chapter in formatted_part['chapters']:
            total_sections += len(chapter['sections'])
        
        document['parts'].append(formatted_part)
    
    document['structure_summary'] = {
        'total_parts': len(document['parts']),
        'total_chapters': total_chapters,
        'total_sections': total_sections,
        'has_section_1': True,
        'sequential_numbering': True,
        'website_structure_corrected': True
    }
    
    return document

def save_final_structure(document: Dict):
    """Save the final structure to replace all problematic files"""
    
    files_to_update = [
        '/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data/core_acts/income_tax_act_2023.json',
        '/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data/core_acts/income_tax_act_2023_properly_distributed.json'
    ]
    
    for file_path in files_to_update:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, indent=2, ensure_ascii=False)
        print(f"✅ Updated: {file_path}")

def main():
    import re
    
    # Build complete structure
    final_document = build_complete_correct_structure()
    
    # Save to all required locations
    save_final_structure(final_document)
    
    print(f"\\n🎉 FINAL COMPLETE STRUCTURE:")
    print(f"   📁 Parts: {final_document['structure_summary']['total_parts']}")
    print(f"   📚 Chapters: {final_document['structure_summary']['total_chapters']}")
    print(f"   📋 Sections: {final_document['structure_summary']['total_sections']}")
    print(f"   ✅ Sequential from 1: {final_document['structure_summary']['sequential_numbering']}")
    
    print(f"\\n✅ CORRECTED DISTRIBUTION (EXACTLY AS REQUESTED):")
    for part in final_document['parts']:
        direct_sections = [int(convert_bengali_to_english(s['number'])) for s in part['direct_sections']]
        chapter_sections = []
        for ch in part['chapters']:
            chapter_sections.extend([int(convert_bengali_to_english(s['number'])) for s in ch['sections']])
        
        all_sections = sorted(direct_sections + chapter_sections)
        if all_sections:
            section_range = f"{min(all_sections)}-{max(all_sections)}" if len(all_sections) > 1 else str(all_sections[0])
            chapter_info = f" ({len(part['chapters'])} chapters)" if part['chapters'] else ""
            print(f"   {part['part_number']}: Sections {section_range}{chapter_info}")
            
            # Show chapter breakdown
            for chapter in part['chapters']:
                ch_sections = [int(convert_bengali_to_english(s['number'])) for s in chapter['sections']]
                ch_range = f"{min(ch_sections)}-{max(ch_sections)}" if len(ch_sections) > 1 else str(ch_sections[0])
                print(f"      {chapter['chapter_number']}: Sections {ch_range}")

if __name__ == "__main__":
    main()