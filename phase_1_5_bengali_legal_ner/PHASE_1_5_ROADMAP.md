# Phase 1.5: Advanced Bengali Legal NER Development

## 🎯 Objective
Create a Bengali Legal Named Entity Recognition system to bridge Phase 1 (document analysis) and semantic understanding.

## 📋 Implementation Plan

### Phase 1.5A: Core Training Data Extraction
**Target**: Extract 5K high-value lines from priority documents
- Income Tax Act 2023 core sections (Section 163, exemptions)
- 6th & 7th Schedules (exemptions, special rates)  
- Key TDS rules for common scenarios
- High-citation density sections from Phase 1 data

### Phase 1.5B: Entity Annotation Schema
**Target**: Define Bengali legal entity categories and annotation format
- Legal entities: SECTION, SCHEDULE, RULE, ACT, AMOUNT, DATE
- Contextual patterns: "উক্ত ধারা", "সংশ্লিষ্ট তফসিল"
- Cross-language mapping: ধারা ১৬৩ ↔ Section 163

### Phase 1.5C: Smart Document Processing  
**Target**: Implement intelligent chunking for large documents
- Section-based processing instead of full file processing
- Priority-based sampling from 200K+ line files
- Context-aware text segmentation

### Phase 1.5D: Transfer Learning Pipeline
**Target**: Setup ML pipeline using existing Bengali NER models
- Base model: ai4bharat/indic-bert or similar
- Fine-tuning architecture for legal domain
- Integration with Phase 1 regex patterns

### Phase 1.5E: Model Training
**Target**: Train Bengali Legal NER on core dataset
- Initial training on 5K curated lines
- Validation on test set
- Performance optimization

### Phase 1.5F: Model Validation
**Target**: Evaluate accuracy and create metrics
- Test on real Bengali legal queries
- Precision/recall metrics for each entity type
- Cross-language validation (Bengali ↔ English)

## 🎯 Success Criteria
- NER model achieves >85% accuracy on legal entities
- Successfully identifies Bengali sections, amounts, dates
- Cross-language entity linking functional
- Ready for Phase 2 knowledge graph integration

## 📁 Directory Structure
```
phase_1_5_bengali_legal_ner/
├── training_data/          # Curated training datasets
├── models/                 # Trained NER models
├── scripts/               # Processing and training scripts
├── evaluation/            # Test results and metrics
└── PHASE_1_5_ROADMAP.md   # This roadmap
```