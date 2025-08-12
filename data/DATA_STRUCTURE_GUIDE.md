# Data Structure Guide
## Precision Cross-Reference System Legal Documents

**Date**: January 15, 2025  
**Organization**: File type-based structure for easy navigation and management

---

## 📁 Data Folder Structure

```
data/
├── core_acts/                    [Primary Laws - Authority Level: 100%]
├── schedules/                    [Tax Schedules - Authority Level: 95%]
├── finance_laws/                 [Annual Finance Laws - Authority Level: 100%]
├── tds_rules/                    [TDS Implementation Rules - Authority Level: 85%]
├── circulars/                    [Interpretive Circulars - Authority Level: 70%]
└── sro_orders/                   [Specific Exemption Orders - Authority Level: 80%]
```

---

## 🏛️ Core Acts (Authority: 100%)

### Primary Income Tax Legislation
```
core_acts/
├── income-tax-act-2023-in-english.json           [Main Act - English]
├── income-tax-act-bangla.json                    [Main Act - Bengali]
└── income-tax-act-bangla-section-163-minimum-tax.json  [Section 163 Details]
```

**Description**: 
- Core Income Tax Act 2023 with 345 sections
- Section 163 specifically deals with minimum tax structure
- Bilingual versions for cross-language precision matching

**Key Sections for Precision System**:
- **Section 163**: Minimum tax (ন্যূনতম কর)
- **Section 75**: Return filing obligations
- **Sections 88-139**: TDS and collection provisions

---

## 📊 Schedules (Authority: 95%)

### Tax Rate Tables and Exemptions
```
schedules/
├── income-tax-schedule-english.json              [All Schedules - English]
├── income-tax-schedule-bangla.json               [All Schedules - Bengali]
├── income-tax-act-2023-1st-schedule-part-1.json [Tax Rates]
└── income-tax-act-2023-6th-schedule-part-4.json [Tax Holidays]
```

**Description**:
- **1st Schedule**: Tax rates and tax-free income limits
- **3rd Schedule**: Depreciation allowance calculations  
- **4th Schedule**: Tax exemptions and reductions (critical for Section 163)
- **6th Schedule**: Tax holidays for specific industries

**Cross-References**:
- Schedule 4 ↔ Section 163 (minimum tax exemptions)
- Schedule 1 ↔ Section 44 (tax-free limits)

---

## 💰 Finance Laws (Authority: 100% - Overrides Acts)

### Annual Budget Laws
```
finance_laws/
└── finance_ordinance_2025_cleaned.json          [Current FY 2025-26]
```

**Description**:
- **Finance Ordinance 2025**: Overrides Income Tax Act provisions
- **Effective Period**: 2025-07-01 to 2026-06-30
- **Key Changes**: Tax-free limit increased to 4 lakh, revised Section 163 rates

**Temporal Authority**:
- Finance Ordinance 2025 > Income Tax Act 2023
- Updates minimum tax rates and exemption criteria

---

## 📋 TDS Rules (Authority: 85%)

### Tax Deduction at Source Implementation
```
tds_rules/
├── tds-rules-2024-fy-2025-26-bd.json            [Current FY 2025-26]
└── tds-rules-2024-fy-2024-2025-bangladesh.json  [Previous FY 2024-25]
```

**Description**:
- **Current Rules**: TDS Rules for FY 2025-26 (effective 2025-07-01)
- **Previous Rules**: TDS Rules for FY 2024-25 (for temporal comparison)
- **Implementation**: Rules 3-9 covering contractors, services, non-residents

**Key Rule Categories**:
- **Rule 3**: Deduction from contractors
- **Rule 4**: Deduction from services  
- **Rule 5**: Non-resident income
- **Rule 6**: Property transfer tax collection

---

## 🔄 Circulars (Authority: 70%)

### Administrative Interpretations
```
circulars/
[Empty - To be populated with interpretive circulars]
```

**Purpose**: 
- Administrative guidance on law interpretation
- NBR (National Board of Revenue) clarifications
- Case-specific guidance for complex scenarios

---

## 📜 SRO Orders (Authority: 80%)

### Specific Exemption Orders
```
sro_orders/
└── income-tax-sro.json                          [Tax Exemption Orders]
```

**Description**:
- **SRO Orders**: Statutory Regulatory Orders for specific exemptions
- **Authority**: High authority for granted exemptions
- **Scope**: Industry-specific, event-specific, or category-specific exemptions

---

## 🔗 Cross-Reference Network

### Document Relationships
```yaml
Authority Hierarchy:
  1. Finance Ordinance 2025    → Overrides all
  2. Income Tax Act 2023       → Primary law
  3. Schedules                 → Part of Act
  4. SRO Orders               → Specific exemptions
  5. TDS Rules                → Implementation rules
  6. Circulars                → Interpretive guidance

Cross-Reference Patterns:
  Section 163 ↔ Schedule 4     → Minimum tax exemptions
  TDS Rules ↔ Sections 88-139  → Implementation details
  Finance Laws → Act Sections  → Annual modifications
```

---

## 📊 Document Statistics

| Category | Files | Authority Level | Primary Language | Coverage |
|----------|-------|----------------|------------------|----------|
| Core Acts | 3 | 100% | Bilingual | Complete |
| Schedules | 4 | 95% | Bilingual | Tax rates & exemptions |
| Finance Laws | 1 | 100% (Override) | Bengali | Current FY |
| TDS Rules | 2 | 85% | Bengali | Current + Previous |
| SRO Orders | 1 | 80% | Bengali | Exemptions |
| Circulars | 0 | 70% | - | To be added |

---

## 🎯 Usage Guidelines

### For Phase 1.5 (Bengali Legal NER)
- **Training Data**: Use Section 163 variations from core_acts/
- **Pattern Recognition**: Extract citation patterns from all categories
- **Cross-Language Mapping**: Use bilingual schedules/ files

### For Cross-Reference Resolution
- **Primary Source**: core_acts/ for authoritative definitions
- **Rate Lookups**: schedules/ for tax calculations
- **Current Law**: finance_laws/ for latest provisions
- **Implementation**: tds_rules/ for practical application

### For Temporal Analysis
- **Current**: finance_laws/ + tds_rules/ (2025-26 files)
- **Historical**: tds_rules/ (2024-25 files) for comparison
- **Changes**: Compare finance_laws/ vs core_acts/ for modifications

---

## 🔍 File Selection Priority

### High Priority (Phase 1.5 Training)
1. **core_acts/income-tax-act-bangla-section-163-minimum-tax.json** - Primary training data
2. **schedules/income-tax-schedule-bangla.json** - Cross-reference patterns
3. **finance_laws/finance_ordinance_2025_cleaned.json** - Current law modifications

### Medium Priority (Validation & Testing)  
4. **core_acts/income-tax-act-2023-in-english.json** - Cross-language validation
5. **tds_rules/tds-rules-2024-fy-2025-26-bd.json** - Implementation context

### Low Priority (Future Phases)
6. **sro_orders/income-tax-sro.json** - Exemption edge cases
7. **tds_rules/tds-rules-2024-fy-2024-2025-bangladesh.json** - Historical comparison

---

## 📋 Data Integrity Checklist

### File Organization ✅
- [x] Files categorized by legal document type
- [x] Consistent naming convention maintained
- [x] Bilingual versions properly paired
- [x] Temporal versions clearly identified

### Content Validation ✅  
- [x] All core legal documents secured
- [x] Cross-reference networks preserved
- [x] Authority hierarchy maintained
- [x] Bengali-English mappings available

### Access Optimization ✅
- [x] Logical folder structure for easy navigation
- [x] Priority-based organization for development phases
- [x] Clear documentation for usage guidelines
- [x] Ready for Phase 1.5 NER training data extraction

---

**Status**: ✅ **Data Structure Organized** | Ready for Phase 1.5 Advanced Bengali Legal NER implementation with properly categorized legal documents.