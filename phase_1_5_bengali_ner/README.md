# Phase 1.5: Advanced Bengali Legal NER System
## Bangladesh Tax Law - Ultra-Precise Entity Recognition

**Objective**: Create ultra-precise Bengali legal entity recognition system for 98%+ accuracy on legal entities

**Implementation**: Week 2-3 of Precision Cross-Reference Roadmap

---

## System Architecture

### Core Components
1. **Bengali Legal NER Model**: Fine-tuned Bengali-BERT for legal domain
2. **Contextual Disambiguator**: Resolves ambiguous income types and legal contexts
3. **False Positive Controller**: Prevents wrong section linking through contrastive learning
4. **Training Data Generator**: Creates 10,000+ annotated Bengali tax queries
5. **Validation System**: Expert validation with >95% inter-annotator agreement

### Entity Types Supported
- `SECTION_DIRECT`: ধারা ১৬৩, Section 163
- `SECTION_INDIRECT`: উক্ত ধারা, সংশ্লিষ্ট তফসিল
- `SCHEDULE_REF`: তফসিল ৪, Schedule 4
- `AMOUNT_BENGALI`: ৩.৫ লক্ষ টাকা, পাঁচ লক্ষ
- `TAX_RATE`: ১৫% হার, 15% rate
- `FINANCIAL_YEAR`: ২০২৫ অর্থবছর, FY 2025-26
- `TAXPAYER_TYPE`: Individual, Company, Association
- `INCOME_SOURCE`: ইউটিউব আয়, Business income

---

## Implementation Plan

### Task 1.5.1: Bengali Legal Domain NER Training
- Fine-tune Bengali-BERT base model
- Create 10,000+ annotated training dataset
- Implement entity recognition for indirect references
- Achieve >98% accuracy on legal entities

### Task 1.5.2: Contextual Disambiguation System  
- Resolve ambiguous income types (YouTube income classification)
- Interactive clarification dialogue system
- Intent refinement for complex scenarios

### Task 1.5.3: False Positive Control System
- Prevent wrong section linking
- Contrastive learning for negative examples
- Domain separation (VAT vs Income Tax)

---

## Quality Targets
- **Entity Recognition Accuracy**: >98% on legal entities
- **Disambiguation Success**: >95% correct classification
- **False Positive Rate**: <2% wrong section citations
- **Training Data Quality**: >95% inter-annotator agreement
- **Bengali Language Coverage**: All legal pattern variations