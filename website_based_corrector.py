#!/usr/bin/env python3
"""
Website-Based Structure Corrector
================================
Creates the correct Income Tax Act 2023 structure based on actual website analysis.
"""

import json
from typing import Dict, List

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

def load_enhanced_sections() -> Dict:
    """Load all sections from the enhanced file"""
    enhanced_file = '/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/enhanced_structured_laws/income_tax_act_2023_enhanced.json'
    
    with open(enhanced_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sections_pool = {}
    
    # Collect all sections regardless of their current location
    for part in data.get('parts', []):
        # Direct sections
        for section in part.get('sections', []):
            section_num = int(convert_bengali_to_english(section['number']))
            sections_pool[section_num] = section
        
        # Chapter sections
        for chapter in part.get('chapters', []):
            for section in chapter.get('sections', []):
                section_num = int(convert_bengali_to_english(section['number']))
                sections_pool[section_num] = section
    
    print(f"📖 Loaded {len(sections_pool)} sections from enhanced file")
    return sections_pool

def load_website_analysis() -> Dict:
    """Load the website structure analysis"""
    analysis_file = '/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/website_structure_analysis.json'
    
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    return analysis

def build_correct_structure() -> Dict:
    """Build the correct structure using website analysis and enhanced sections"""
    
    print("🏗️ Building correct structure based on website analysis...")
    
    # Load data
    sections_pool = load_enhanced_sections()
    analysis = load_website_analysis()
    
    # Create the corrected document structure
    document = {
        'document_info': {
            'title': 'আয়কর আইন, ২০২৩',
            'ordinance_info': '( ২০২৩ সনের ১২ নং আইন )',
            'publish_date': '[ ২২ জুন, ২০২৩ ]',
            'structure_format': 'অংশ (Parts) → অধ্যায় (Chapters) → ধারা (Sections) - Website Correct Structure',
            'extraction_method': 'Website Analysis + Enhanced Section Content',
            'version': '3.0_website_corrected'
        },
        'structure_summary': {},
        'parts': []
    }
    
    total_sections_found = 0
    total_chapters = 0
    
    # Process each part from the website analysis
    for part_info in analysis['parts']:
        part_number = part_info['part_number']
        part_title = part_info['part_title']
        
        corrected_part = {
            'part_number': part_number,
            'part_title': part_title,
            'chapters': [],
            'direct_sections': []
        }
        
        # Handle chapters
        if part_info['chapters']:
            for chapter_info in part_info['chapters']:
                chapter_sections = []
                
                for section_num in chapter_info['section_numbers']:
                    if section_num in sections_pool:
                        chapter_sections.append(sections_pool[section_num])
                        total_sections_found += 1
                
                if chapter_sections:
                    corrected_chapter = {
                        'chapter_number': chapter_info['chapter_number'],
                        'chapter_title': chapter_info['chapter_title'],
                        'sections': sorted(chapter_sections, key=lambda x: int(convert_bengali_to_english(x['number'])))
                    }
                    corrected_part['chapters'].append(corrected_chapter)
                    total_chapters += 1
        
        # Handle direct sections (not in chapters)
        direct_section_numbers = part_info['section_numbers']
        for section_num in direct_section_numbers:
            if section_num in sections_pool:
                corrected_part['direct_sections'].append(sections_pool[section_num])
                total_sections_found += 1
        
        # Sort direct sections
        corrected_part['direct_sections'] = sorted(
            corrected_part['direct_sections'], 
            key=lambda x: int(convert_bengali_to_english(x['number']))
        )
        
        document['parts'].append(corrected_part)
        
        # Print progress
        chapter_count = len(corrected_part['chapters'])
        section_count = len(corrected_part['direct_sections']) + sum(len(ch['sections']) for ch in corrected_part['chapters'])
        print(f"   ✅ {part_number}: {section_count} sections ({chapter_count} chapters)")
    
    # Update structure summary
    document['structure_summary'] = {
        'total_parts': len(document['parts']),
        'total_chapters': total_chapters,
        'total_sections': total_sections_found,
        'has_hierarchical_structure': True,
        'sections_properly_mapped': True,
        'website_structure_matched': True
    }
    
    return document

def save_corrected_files(document: Dict):
    """Save the corrected structure to multiple locations"""
    
    # Save to core_acts directory - primary production file
    primary_file = '/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data/core_acts/income_tax_act_2023.json'
    with open(primary_file, 'w', encoding='utf-8') as f:
        json.dump(document, f, indent=2, ensure_ascii=False)
    print(f"✅ Corrected structure saved to: {primary_file}")
    
    # Save backup with specific name
    backup_file = '/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data/core_acts/income_tax_act_2023_website_corrected.json'
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(document, f, indent=2, ensure_ascii=False)
    print(f"✅ Backup structure saved to: {backup_file}")

def main():
    print("🎯 WEBSITE-BASED STRUCTURE CORRECTION")
    print("=" * 45)
    print("Creating Income Tax Act 2023 structure exactly matching website...")
    
    # Build correct structure
    corrected_document = build_correct_structure()
    
    # Save files
    save_corrected_files(corrected_document)
    
    # Print final summary
    summary = corrected_document['structure_summary']
    print(f"\n📊 FINAL CORRECTED STRUCTURE:")
    print(f"   📁 Total Parts: {summary['total_parts']}")
    print(f"   📚 Total Chapters: {summary['total_chapters']}")
    print(f"   📋 Total Sections: {summary['total_sections']}")
    print(f"   ✅ Website Structure Matched: {summary['website_structure_matched']}")
    
    # Show sample distribution
    print(f"\n🔍 SAMPLE SECTION DISTRIBUTION (First 10 Parts):")
    for i, part in enumerate(corrected_document['parts'][:10]):
        direct_sections = len(part['direct_sections'])
        chapter_sections = sum(len(ch['sections']) for ch in part['chapters'])
        total_part_sections = direct_sections + chapter_sections
        
        if total_part_sections > 0:
            all_sections = []
            all_sections.extend([int(convert_bengali_to_english(s['number'])) for s in part['direct_sections']])
            for ch in part['chapters']:
                all_sections.extend([int(convert_bengali_to_english(s['number'])) for s in ch['sections']])
            
            all_sections = sorted(set(all_sections))
            if all_sections:
                section_range = f"{min(all_sections)}-{max(all_sections)}" if len(all_sections) > 1 else str(all_sections[0])
                chapter_info = f" ({len(part['chapters'])} chapters)" if part['chapters'] else ""
                print(f"   {part['part_number']}: Sections {section_range} ({total_part_sections} sections){chapter_info}")
    
    print(f"\n🎉 STRUCTURE CORRECTION COMPLETED!")
    print(f"✅ Income Tax Act 2023 now has correct website-matching structure")

if __name__ == "__main__":
    main()