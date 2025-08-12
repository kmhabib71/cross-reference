#!/usr/bin/env python3
"""
Quick JSON Key Extractor
Simple script to quickly extract any key values from JSON

Usage Examples:
  python3 quick_extract.py --key "title"
  python3 quick_extract.py --key "number" --limit 10
  python3 quick_extract.py --path "header.title"
  python3 quick_extract.py --keys  (show all keys)
"""

import json
import argparse
from pathlib import Path
from typing import Any, List

def load_json(file_path: str):
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_all_keys(obj, keys=None):
    """Get all unique keys from JSON"""
    if keys is None:
        keys = set()
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            keys.add(key)
            get_all_keys(value, keys)
    elif isinstance(obj, list):
        for item in obj:
            get_all_keys(item, keys)
    
    return keys

def extract_key_values(obj, target_key: str, values=None):
    """Extract all values for a specific key"""
    if values is None:
        values = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == target_key:
                values.append(value)
            extract_key_values(value, target_key, values)
    elif isinstance(obj, list):
        for item in obj:
            extract_key_values(item, target_key, values)
    
    return values

def extract_path_value(obj, path: str):
    """Extract value from JSON path like 'header.title' or 'parts[0].number'"""
    try:
        current = obj
        
        # Handle array indices and dot notation
        import re
        parts = re.split(r'[\.\[\]]', path)
        parts = [p for p in parts if p]  # Remove empty parts
        
        for part in parts:
            if part.isdigit():
                current = current[int(part)]
            else:
                current = current[part]
        
        return current
    except Exception as e:
        print(f"Error extracting path '{path}': {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Extract keys and values from JSON file")
    parser.add_argument("--file", default="/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precision_crossref_system_2025/data/core_acts/income_tax_act_2023_cleaned.json", help="JSON file path")
    parser.add_argument("--keys", action="store_true", help="Show all available keys")
    parser.add_argument("--key", help="Extract all values for this key")
    parser.add_argument("--path", help="Extract value from specific path (e.g., 'header.title')")
    parser.add_argument("--limit", type=int, default=20, help="Limit number of results")
    parser.add_argument("--save", help="Save results to file")
    
    args = parser.parse_args()
    
    # Load JSON
    if not Path(args.file).exists():
        print(f"❌ File not found: {args.file}")
        return
    
    print(f"📂 Loading: {args.file}")
    data = load_json(args.file)
    print(f"✅ Loaded {len(str(data))} characters")
    
    if args.keys:
        # Show all keys
        all_keys = get_all_keys(data)
        print(f"\n🗝️  ALL KEYS ({len(all_keys)} found):")
        print("=" * 40)
        for i, key in enumerate(sorted(all_keys), 1):
            print(f"{i:3d}. {key}")
    
    elif args.key:
        # Extract specific key values
        values = extract_key_values(data, args.key)
        print(f"\n📦 KEY '{args.key}' VALUES ({len(values)} found):")
        print("=" * 40)
        
        display_values = values[:args.limit] if args.limit else values
        
        for i, value in enumerate(display_values, 1):
            if isinstance(value, str):
                if len(value) > 100:
                    print(f"{i:3d}. {value[:100]}...")
                else:
                    print(f"{i:3d}. {value}")
            else:
                print(f"{i:3d}. {value}")
        
        if len(values) > args.limit:
            print(f"... and {len(values) - args.limit} more values")
        
        # Save to file if requested
        if args.save:
            with open(args.save, 'w', encoding='utf-8') as f:
                json.dump(values, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to: {args.save}")
    
    elif args.path:
        # Extract specific path
        value = extract_path_value(data, args.path)
        print(f"\n📍 PATH '{args.path}':")
        print("=" * 40)
        
        if isinstance(value, str) and len(value) > 500:
            print(f"{value[:500]}...")
        else:
            print(f"{value}")
        
        # Save to file if requested
        if args.save:
            with open(args.save, 'w', encoding='utf-8') as f:
                if isinstance(value, str):
                    f.write(value)
                else:
                    json.dump(value, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to: {args.save}")
    
    else:
        print("❌ Please specify --keys, --key <keyname>, or --path <path>")
        print("Examples:")
        print("  python3 quick_extract.py --keys")
        print("  python3 quick_extract.py --key 'title'")
        print("  python3 quick_extract.py --path 'header.title'")

if __name__ == "__main__":
    main()