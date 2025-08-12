# 🔄 Dynamic File Integration System

## Overview
The system **automatically detects and integrates new legal documents** to ensure your precision crossref system always provides advice based on the **latest legal information**.

## How It Works

### 1. **File Detection** 
- Monitors `data/` folder for new `.json` files
- Calculates checksums to detect modifications
- Tracks file registry to identify new additions

### 2. **Auto-Classification**
- **SRO Orders**: Authority level 80
- **Circulars**: Authority level 70  
- **Finance Acts/Ordinances**: Authority level 100
- **Schedules**: Authority level 90
- **Rules**: Authority level 85

### 3. **Automatic Integration**
- Updates legal hierarchy with proper precedence
- Extracts citation patterns (Bengali + English)
- Cross-references with existing documents
- Maintains 100% precision by rebuilding indexes

## Usage

### **Option 1: Manual Integration**
```bash
# Run once to integrate any new files
python3 scripts/dynamic_file_integrator.py
```

### **Option 2: Real-time Watching** 
```bash
# Continuously monitor for new files (recommended)
python3 scripts/file_watcher.py
```

### **Option 3: System Integration**
Add to your main application startup:
```python
from scripts.dynamic_file_integrator import DynamicFileIntegrator

integrator = DynamicFileIntegrator(data_dir, phase_dir)
integrator.integrate_new_files()  # Run on startup
```

## Adding New Files

### **Step 1: Drop Files**
Simply add new legal documents to appropriate folders:
```
data/
├── sro_orders/
│   └── new-sro-circular-2025.json
├── circulars/  
│   └── tax-circular-special-2025.json
├── schedules/
│   └── amended-schedule-6-2025.json
└── tds_rules/
    └── updated-tds-rates-2025.json
```

### **Step 2: System Auto-Processes**
- ✅ Detects new files automatically
- ✅ Extracts citations and cross-references  
- ✅ Updates legal hierarchy with proper authority
- ✅ System ready for precise advice with new documents

### **Step 3: Verify Integration**
```bash
# Check integration status
python3 scripts/dynamic_file_integrator.py
```

## File Format Requirements

New files should follow this structure:
```json
{
  "main_content": "Legal text content in Bengali/English",
  "tables": [
    {
      "headers": ["Column 1", "Column 2"],
      "data": [["Row 1 Col 1", "Row 1 Col 2"]]
    }
  ],
  "forms": [],
  "status": "success"
}
```

**Note**: The cleanup script will remove any `url` or `title` fields automatically.

## Integration Results

The system provides detailed integration reports:
```json
{
  "status": "success",
  "new_files": 3,
  "files_processed": [
    "new-sro-2025.json",
    "tax-circular-2025.json", 
    "amended-schedule.json"
  ],
  "citations_extracted": 45,
  "cross_references_updated": 12
}
```

## Benefits

### **For Legal Accuracy**
- 🎯 **Always Current**: Advice based on latest legal documents
- 🔗 **Auto Cross-Reference**: New documents linked to existing law
- ⚖️ **Proper Precedence**: Legal hierarchy maintained automatically

### **For System Maintenance**  
- 🚀 **Zero Configuration**: Drop files and system handles rest
- 📊 **Smart Detection**: Only processes new/changed files
- ⚡ **Fast Integration**: Incremental updates, not full rebuilds

### **For Development**
- 🔄 **Hot Reload**: Add files without restarting system
- 📈 **Scalable**: Handles growing document collection
- 🛡️ **Error Recovery**: Graceful handling of malformed files

## Monitoring & Logs

The system provides detailed logging:
```
2025-01-15 10:30:15 - INFO - 📁 Found 3 new/modified files
2025-01-15 10:30:16 - INFO - Added new_sro_2025 to legal hierarchy with authority 80
2025-01-15 10:30:17 - INFO - Extracted 15 citations from tax-circular-2025.json
2025-01-15 10:30:18 - INFO - ✅ Integration completed: 3 files processed
```

## 🎯 Impact on Precision

This dynamic system ensures:
- **100% Legal Coverage**: No missing recent SROs/circulars
- **Real-time Compliance**: Advice reflects latest legal changes  
- **Comprehensive Cross-referencing**: New documents properly linked
- **Maintained Data Quality**: Automatic cleanup and validation

Your precision crossref system will now **automatically stay current** with Bangladesh tax law changes!