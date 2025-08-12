#!/usr/bin/env python3
"""
Honest File Quality Check
Re-check actual file quality to see if claims are accurate or exaggerated
"""

import json
from pathlib import Path
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_file_quality():
    """Do an honest check of actual file quality"""
    data_dir = Path("/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data")
    
    quality_check = {
        "total_files": 0,
        "files_with_content": 0,
        "empty_files": 0,
        "small_files": 0,
        "large_files": 0,
        "files_with_meaningful_content": 0,
        "bilingual_files": 0,
        "files_by_size": {
            "empty": [],
            "tiny": [],  # <1KB
            "small": [],  # 1KB-10KB  
            "medium": [],  # 10KB-100KB
            "large": [],  # 100KB-1MB
            "huge": []  # >1MB
        },
        "content_analysis": {
            "files_with_legal_text": 0,
            "files_with_sections": 0,
            "files_with_bengali": 0,
            "files_with_english": 0
        }
    }
    
    for json_file in data_dir.rglob("*.json"):
        quality_check["total_files"] += 1
        file_size = json_file.stat().st_size
        
        # Size categorization
        if file_size == 0:
            quality_check["files_by_size"]["empty"].append(str(json_file.relative_to(data_dir)))
        elif file_size < 1024:
            quality_check["files_by_size"]["tiny"].append(str(json_file.relative_to(data_dir)))
        elif file_size < 10240:
            quality_check["files_by_size"]["small"].append(str(json_file.relative_to(data_dir)))
        elif file_size < 102400:
            quality_check["files_by_size"]["medium"].append(str(json_file.relative_to(data_dir)))
        elif file_size < 1048576:
            quality_check["files_by_size"]["large"].append(str(json_file.relative_to(data_dir)))
        else:
            quality_check["files_by_size"]["huge"].append(str(json_file.relative_to(data_dir)))
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Content analysis
            text_content = ""
            has_content = False
            
            if isinstance(data, dict):
                # Check main_content field
                if 'main_content' in data:
                    main_content = data['main_content']
                    if main_content and str(main_content).strip():
                        text_content = str(main_content)
                        has_content = True
                        quality_check["files_with_content"] += 1
                    else:
                        quality_check["empty_files"] += 1
                        continue
                elif 'content' in data:
                    content = data['content']
                    if content and str(content).strip():
                        text_content = str(content)
                        has_content = True
                        quality_check["files_with_content"] += 1
                else:
                    # Check if there's any meaningful content in other fields
                    content_fields = ['sections', 'chapters', 'parts', 'rules', 'schedules', 'text', 'data']
                    for field in content_fields:
                        if field in data and data[field]:
                            text_content += str(data[field])
                            has_content = True
                    
                    if has_content:
                        quality_check["files_with_content"] += 1
                    else:
                        quality_check["empty_files"] += 1
                        continue
            else:
                text_content = str(data)
                if text_content.strip():
                    has_content = True
                    quality_check["files_with_content"] += 1
                else:
                    quality_check["empty_files"] += 1
                    continue
            
            # Check if file has meaningful legal content
            if len(text_content) > 100:  # At least 100 characters
                quality_check["files_with_meaningful_content"] += 1
                
                # Check for legal terms
                legal_terms = ['ধারা', 'section', 'আইন', 'act', 'তফসিল', 'schedule', 'বিধি', 'rule']
                if any(term in text_content.lower() for term in legal_terms):
                    quality_check["content_analysis"]["files_with_legal_text"] += 1
                
                # Check for section references
                if 'ধারা' in text_content or 'section' in text_content.lower():
                    quality_check["content_analysis"]["files_with_sections"] += 1
                
                # Check for Bengali content
                bengali_chars = ['আ', 'ই', 'উ', 'ও', 'ক', 'খ', 'গ', 'ঘ', 'চ', 'ছ', 'জ', 'ধ', 'ন', 'প', 'ব', 'ম', 'য়', 'র', 'ল', 'স', 'হ', '০', '১', '২', '৩', '৪', '৫']
                if any(char in text_content for char in bengali_chars):
                    quality_check["content_analysis"]["files_with_bengali"] += 1
                
                # Check for English content  
                if any(char.isalpha() and ord(char) < 128 for char in text_content):
                    quality_check["content_analysis"]["files_with_english"] += 1
                
                # Check if bilingual
                has_bengali = any(char in text_content for char in bengali_chars)
                has_english = any(char.isalpha() and ord(char) < 128 for char in text_content)
                if has_bengali and has_english:
                    quality_check["bilingual_files"] += 1
            
            if file_size < 1024:
                quality_check["small_files"] += 1
            elif file_size > 100000:
                quality_check["large_files"] += 1
                
        except Exception as e:
            logger.warning(f"Error processing {json_file}: {e}")
            quality_check["empty_files"] += 1
    
    # Calculate percentages
    total = quality_check["total_files"]
    quality_check["percentages"] = {
        "files_with_content": round(quality_check["files_with_content"] / total * 100, 1) if total > 0 else 0,
        "empty_files": round(quality_check["empty_files"] / total * 100, 1) if total > 0 else 0,
        "meaningful_content": round(quality_check["files_with_meaningful_content"] / total * 100, 1) if total > 0 else 0,
        "bilingual": round(quality_check["bilingual_files"] / total * 100, 1) if total > 0 else 0,
        "legal_content": round(quality_check["content_analysis"]["files_with_legal_text"] / total * 100, 1) if total > 0 else 0
    }
    
    return quality_check

def main():
    """Check actual file quality"""
    print("🔍 HONEST FILE QUALITY CHECK")
    print("Checking actual file content and quality...")
    
    quality = check_file_quality()
    
    print(f"\n📊 ACTUAL FILE QUALITY RESULTS:")
    print(f"Total files: {quality['total_files']}")
    print(f"Files with ANY content: {quality['files_with_content']} ({quality['percentages']['files_with_content']}%)")
    print(f"Files with meaningful content (>100 chars): {quality['files_with_meaningful_content']} ({quality['percentages']['meaningful_content']}%)")
    print(f"Empty or near-empty files: {quality['empty_files']} ({quality['percentages']['empty_files']}%)")
    print(f"Bilingual files: {quality['bilingual_files']} ({quality['percentages']['bilingual']}%)")
    print(f"Files with legal content: {quality['content_analysis']['files_with_legal_text']} ({quality['percentages']['legal_content']}%)")
    print(f"Files with sections: {quality['content_analysis']['files_with_sections']}")
    print(f"Files with Bengali: {quality['content_analysis']['files_with_bengali']}")
    print(f"Files with English: {quality['content_analysis']['files_with_english']}")
    
    print(f"\n📁 FILE SIZE DISTRIBUTION:")
    print(f"Empty files: {len(quality['files_by_size']['empty'])}")
    print(f"Tiny files (<1KB): {len(quality['files_by_size']['tiny'])}")
    print(f"Small files (1-10KB): {len(quality['files_by_size']['small'])}")
    print(f"Medium files (10-100KB): {len(quality['files_by_size']['medium'])}")
    print(f"Large files (100KB-1MB): {len(quality['files_by_size']['large'])}")
    print(f"Huge files (>1MB): {len(quality['files_by_size']['huge'])}")
    
    # Check against claimed metrics
    print(f"\n⚠️ CHECKING CLAIMED METRICS:")
    print(f"Claimed data quality score: 0.911 (91.1%)")
    print(f"Actual meaningful content: {quality['percentages']['meaningful_content']}%")
    print(f"Match: {'✅' if abs(quality['percentages']['meaningful_content'] - 91.1) < 5 else '❌'}")
    
    print(f"Claimed bilingual completeness: 0.772 (77.2%)")  
    print(f"Actual bilingual files: {quality['percentages']['bilingual']}%")
    print(f"Match: {'✅' if abs(quality['percentages']['bilingual'] - 77.2) < 5 else '❌'}")
    
    if len(quality['files_by_size']['empty']) > 0:
        print(f"\n❌ EMPTY FILES FOUND:")
        for empty_file in quality['files_by_size']['empty'][:5]:
            print(f"  - {empty_file}")
    
    if len(quality['files_by_size']['tiny']) > 5:
        print(f"\n⚠️ SUSPICIOUS TINY FILES:")
        for tiny_file in quality['files_by_size']['tiny'][:5]:
            print(f"  - {tiny_file}")
    
    # Save results
    output_path = Path("/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_0_analysis/honest_file_quality_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(quality, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {output_path}")

if __name__ == "__main__":
    main()