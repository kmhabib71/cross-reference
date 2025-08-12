#!/usr/bin/env python3
"""
JSON Structure Explorer and Key Extractor
Interactive tool to explore JSON structure and extract any key values

Usage: python3 json_explorer.py
"""

import json
import sys
from typing import Any, Dict, List, Set, Union
from pathlib import Path
from collections import defaultdict

class JSONExplorer:
    """Interactive JSON structure explorer and key extractor"""
    
    def __init__(self, json_file_path: str):
        self.file_path = Path(json_file_path)
        self.data = None
        self.all_keys = set()
        self.key_paths = defaultdict(list)
        self.structure = {}
        
        self.load_json()
        self.analyze_structure()
    
    def load_json(self):
        """Load JSON file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✅ Loaded JSON file: {self.file_path}")
            print(f"📊 File size: {len(str(self.data))} characters")
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            sys.exit(1)
    
    def analyze_structure(self):
        """Analyze complete JSON structure"""
        print("🔍 Analyzing JSON structure...")
        self._extract_all_keys(self.data, "")
        print(f"📋 Found {len(self.all_keys)} distinct keys")
    
    def _extract_all_keys(self, obj: Any, path: str = ""):
        """Recursively extract all keys and their paths"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                self.all_keys.add(key)
                self.key_paths[key].append(current_path)
                
                # Store structure info
                if key not in self.structure:
                    self.structure[key] = {
                        'type': type(value).__name__,
                        'paths': [],
                        'sample_values': []
                    }
                
                self.structure[key]['paths'].append(current_path)
                
                # Store sample values
                if isinstance(value, (str, int, float, bool)) and len(self.structure[key]['sample_values']) < 3:
                    self.structure[key]['sample_values'].append(value)
                
                self._extract_all_keys(value, current_path)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                list_path = f"{path}[{i}]"
                self._extract_all_keys(item, list_path)
    
    def show_all_keys(self):
        """Display all unique keys found"""
        print("\n" + "="*60)
        print("🗝️  ALL DISTINCT KEYS FOUND")
        print("="*60)
        
        sorted_keys = sorted(self.all_keys)
        for i, key in enumerate(sorted_keys, 1):
            key_info = self.structure[key]
            print(f"{i:3d}. {key:<30} ({key_info['type']:<10}) - {len(key_info['paths'])} locations")
    
    def show_key_structure(self, key_name: str):
        """Show detailed structure for a specific key"""
        if key_name not in self.all_keys:
            print(f"❌ Key '{key_name}' not found!")
            return
        
        key_info = self.structure[key_name]
        print(f"\n🔍 KEY ANALYSIS: '{key_name}'")
        print("="*50)
        print(f"Type: {key_info['type']}")
        print(f"Occurrences: {len(key_info['paths'])}")
        
        print(f"\n📍 All Paths:")
        for path in key_info['paths'][:10]:  # Show first 10 paths
            print(f"   {path}")
        
        if len(key_info['paths']) > 10:
            print(f"   ... and {len(key_info['paths']) - 10} more locations")
        
        if key_info['sample_values']:
            print(f"\n📝 Sample Values:")
            for value in key_info['sample_values']:
                print(f"   {repr(value)}")
    
    def extract_key_values(self, key_name: str, limit: int = None) -> List[Any]:
        """Extract all values for a specific key"""
        if key_name not in self.all_keys:
            print(f"❌ Key '{key_name}' not found!")
            return []
        
        values = []
        self._collect_key_values(self.data, key_name, values)
        
        if limit:
            values = values[:limit]
        
        print(f"\n📦 EXTRACTED VALUES for '{key_name}' ({len(values)} found)")
        print("="*50)
        
        for i, value in enumerate(values, 1):
            if isinstance(value, str) and len(value) > 100:
                print(f"{i:3d}. {repr(value[:100])}...")
            else:
                print(f"{i:3d}. {repr(value)}")
        
        return values
    
    def _collect_key_values(self, obj: Any, target_key: str, values: List):
        """Recursively collect all values for target key"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == target_key:
                    values.append(value)
                self._collect_key_values(value, target_key, values)
        elif isinstance(obj, list):
            for item in obj:
                self._collect_key_values(item, target_key, values)
    
    def search_keys(self, pattern: str):
        """Search for keys containing pattern"""
        matching_keys = [key for key in self.all_keys if pattern.lower() in key.lower()]
        
        print(f"\n🔎 KEYS CONTAINING '{pattern}' ({len(matching_keys)} found)")
        print("="*50)
        
        for key in sorted(matching_keys):
            key_info = self.structure[key]
            print(f"• {key:<30} ({key_info['type']:<10}) - {len(key_info['paths'])} locations")
        
        return matching_keys
    
    def show_json_tree(self, max_depth: int = 3):
        """Show JSON structure as a tree"""
        print(f"\n🌳 JSON STRUCTURE TREE (depth: {max_depth})")
        print("="*50)
        self._print_tree(self.data, "", 0, max_depth)
    
    def _print_tree(self, obj: Any, indent: str, depth: int, max_depth: int):
        """Recursively print JSON tree structure"""
        if depth >= max_depth:
            return
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                value_type = type(value).__name__
                if isinstance(value, list):
                    count = len(value)
                    print(f"{indent}├─ {key}: [{value_type}] ({count} items)")
                elif isinstance(value, dict):
                    count = len(value)
                    print(f"{indent}├─ {key}: {{{value_type}}} ({count} keys)")
                else:
                    if isinstance(value, str) and len(value) > 50:
                        preview = value[:50] + "..."
                    else:
                        preview = str(value)
                    print(f"{indent}├─ {key}: {value_type} = {repr(preview)}")
                
                if isinstance(value, (dict, list)) and depth < max_depth - 1:
                    self._print_tree(value, indent + "│  ", depth + 1, max_depth)
        
        elif isinstance(obj, list) and obj:
            # Show structure of first item in list
            first_item = obj[0]
            print(f"{indent}└─ [0]: {type(first_item).__name__}")
            if isinstance(first_item, (dict, list)):
                self._print_tree(first_item, indent + "   ", depth + 1, max_depth)
    
    def extract_specific_path(self, path: str):
        """Extract value from specific JSON path (e.g., 'header.title' or 'parts[0].sections[0].number')"""
        try:
            result = self.data
            
            # Parse path components
            components = []
            current = ""
            i = 0
            while i < len(path):
                char = path[i]
                if char == '.':
                    if current:
                        components.append(current)
                        current = ""
                elif char == '[':
                    if current:
                        components.append(current)
                        current = ""
                    # Find closing bracket
                    j = path.find(']', i)
                    if j == -1:
                        raise ValueError("Invalid path: missing closing bracket")
                    index = path[i+1:j]
                    try:
                        components.append(int(index))
                    except ValueError:
                        components.append(index)  # String index
                    i = j
                else:
                    current += char
                i += 1
            
            if current:
                components.append(current)
            
            # Navigate to the target
            for component in components:
                if isinstance(component, int):
                    result = result[component]
                else:
                    result = result[component]
            
            print(f"\n📍 PATH: {path}")
            print("="*50)
            if isinstance(result, str) and len(result) > 200:
                print(f"Value: {repr(result[:200])}...")
            else:
                print(f"Value: {repr(result)}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error extracting path '{path}': {e}")
            return None
    
    def interactive_mode(self):
        """Interactive exploration mode"""
        print("\n🚀 INTERACTIVE JSON EXPLORER")
        print("="*50)
        print("Available commands:")
        print("  'keys' - Show all distinct keys")
        print("  'search <pattern>' - Search for keys containing pattern")  
        print("  'info <key>' - Show detailed info about a key")
        print("  'extract <key>' - Extract all values for a key")
        print("  'path <path>' - Extract value from specific path")
        print("  'tree [depth]' - Show JSON structure tree")
        print("  'quit' - Exit")
        print()
        
        while True:
            try:
                command = input("json_explorer> ").strip()
                
                if command == 'quit':
                    break
                elif command == 'keys':
                    self.show_all_keys()
                elif command.startswith('search '):
                    pattern = command[7:]
                    self.search_keys(pattern)
                elif command.startswith('info '):
                    key = command[5:]
                    self.show_key_structure(key)
                elif command.startswith('extract '):
                    key = command[8:]
                    self.extract_key_values(key, limit=20)
                elif command.startswith('path '):
                    path = command[5:]
                    self.extract_specific_path(path)
                elif command.startswith('tree'):
                    parts = command.split()
                    depth = int(parts[1]) if len(parts) > 1 else 3
                    self.show_json_tree(depth)
                else:
                    print("❌ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("👋 Goodbye!")

def main():
    """Main function"""
    # Default file path
    json_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precision_crossref_system_2025/data/core_acts/income_tax_act_2023_cleaned.json"
    
    # Check if file exists
    if not Path(json_file).exists():
        print(f"❌ JSON file not found: {json_file}")
        print("Please provide the correct path to your JSON file.")
        return
    
    # Initialize explorer
    explorer = JSONExplorer(json_file)
    
    # Show quick overview
    print("\n🎯 QUICK OVERVIEW")
    print("="*50)
    explorer.show_json_tree(depth=2)
    
    print("\n🔧 COMMON EXTRACTIONS")
    print("="*50)
    
    # Show some common key extractions
    common_keys = ['title', 'number', 'sections', 'text', 'content']
    for key in common_keys:
        if key in explorer.all_keys:
            print(f"\n• Key '{key}' found - use 'extract {key}' to get all values")
    
    # Start interactive mode
    explorer.interactive_mode()

if __name__ == "__main__":
    main()