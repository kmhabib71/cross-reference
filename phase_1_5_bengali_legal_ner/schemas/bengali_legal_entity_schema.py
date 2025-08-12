#!/usr/bin/env python3
"""
Bengali Legal Entity Annotation Schema
Phase 1.5B: Define comprehensive entity categories and annotation format
"""

import json
from typing import Dict, List, Any
from pathlib import Path

class BengaliLegalEntitySchema:
    def __init__(self):
        self.entity_categories = self._define_entity_categories()
        self.annotation_format = self._define_annotation_format()
        self.pattern_examples = self._define_pattern_examples()
    
    def _define_entity_categories(self) -> Dict[str, Dict[str, Any]]:
        """Define comprehensive Bengali legal entity categories"""
        return {
            "SECTION": {
                "description": "Legal section references in Bengali/English",
                "bengali_indicators": ["ধারা", "উপধারা", "দফা", "উপদফা"],
                "english_indicators": ["section", "sub-section", "clause", "sub-clause"],
                "patterns": [
                    "ধারা ১৬৩",
                    "section 163", 
                    "উপধারা (১)",
                    "sub-section (1)",
                    "১৬৩ নং ধারা"
                ],
                "entity_type": "LEGAL_REFERENCE"
            },
            
            "SCHEDULE": {
                "description": "Tax schedules and appendices",
                "bengali_indicators": ["তফসিল", "তালিকা", "পরিশিষ্ট"],
                "english_indicators": ["schedule", "table", "appendix"],
                "patterns": [
                    "৬ষ্ঠ তফসিল",
                    "6th schedule",
                    "তৃতীয় তফসিল",
                    "third schedule"
                ],
                "entity_type": "LEGAL_REFERENCE"
            },
            
            "RULE": {
                "description": "Rules and regulations",
                "bengali_indicators": ["বিধি", "বিধিমালা", "নিয়ম"],
                "english_indicators": ["rule", "rules", "regulation"],
                "patterns": [
                    "আয়কর বিধিমালা",
                    "income tax rules",
                    "বিধি ২৫",
                    "rule 25"
                ],
                "entity_type": "LEGAL_REFERENCE"
            },
            
            "ACT": {
                "description": "Acts and ordinances",
                "bengali_indicators": ["আইন", "অধ্যাদেশ", "আইনি"],
                "english_indicators": ["act", "ordinance", "law"],
                "patterns": [
                    "আয়কর আইন",
                    "income tax act",
                    "মূল্য সংযোজন কর আইন",
                    "value added tax act"
                ],
                "entity_type": "LEGAL_REFERENCE"
            },
            
            "AMOUNT": {
                "description": "Monetary amounts in Bengali/English",
                "bengali_indicators": ["টাকা", "পয়সা", "লক্ষ", "কোটি"],
                "english_indicators": ["taka", "paisa", "lakh", "crore"],
                "patterns": [
                    "৫০,০০০ টাকা",
                    "50,000 taka",
                    "১ লক্ষ টাকা",
                    "1 lakh taka"
                ],
                "entity_type": "MONETARY"
            },
            
            "PERCENTAGE": {
                "description": "Tax rates and percentages",
                "bengali_indicators": ["শতাংশ", "হার", "দর"],
                "english_indicators": ["percent", "percentage", "rate"],
                "patterns": [
                    "১৫ শতাংশ",
                    "15 percent",
                    "১৫%",
                    "15%"
                ],
                "entity_type": "RATE"
            },
            
            "DATE": {
                "description": "Dates in Bengali/English format",
                "bengali_indicators": ["তারিখ", "দিন", "মাস", "বছর"],
                "english_indicators": ["date", "day", "month", "year"],
                "patterns": [
                    "১ জুলাই, ২০২৩",
                    "1st July, 2023",
                    "৩০শে জুন",
                    "30th June"
                ],
                "entity_type": "TEMPORAL"
            },
            
            "AUTHORITY": {
                "description": "Government authorities and departments",
                "bengali_indicators": ["বোর্ড", "কমিশনার", "মন্ত্রণালয়"],
                "english_indicators": ["board", "commissioner", "ministry"],
                "patterns": [
                    "জাতীয় রাজস্ব বোর্ড",
                    "national board of revenue",
                    "কর কমিশনার",
                    "tax commissioner"
                ],
                "entity_type": "ORGANIZATION"
            },
            
            "TAXPAYER": {
                "description": "Taxpayer categories and classifications",
                "bengali_indicators": ["করদাতা", "ব্যক্তি", "কোম্পানি"],
                "english_indicators": ["taxpayer", "person", "company"],
                "patterns": [
                    "ব্যক্তি করদাতা",
                    "individual taxpayer",
                    "কোম্পানি করদাতা",
                    "company taxpayer"
                ],
                "entity_type": "PERSON_ORG"
            },
            
            "FORM": {
                "description": "Tax forms and returns",
                "bengali_indicators": ["ফরম", "রিটার্ন", "বিবরণী"],
                "english_indicators": ["form", "return", "statement"],
                "patterns": [
                    "ফরম-১১৬৩",
                    "form-1163",
                    "কর রিটার্ন",
                    "tax return"
                ],
                "entity_type": "DOCUMENT"
            }
        }
    
    def _define_annotation_format(self) -> Dict[str, Any]:
        """Define annotation format compatible with spaCy and NER tools"""
        return {
            "format_type": "BIO_tagging",
            "description": "Beginning-Inside-Outside tagging for token-level annotation",
            "tag_structure": {
                "B-{ENTITY}": "Beginning of entity",
                "I-{ENTITY}": "Inside/continuation of entity", 
                "O": "Outside any entity"
            },
            "example_tags": [
                "B-SECTION", "I-SECTION",
                "B-AMOUNT", "I-AMOUNT", 
                "B-ACT", "I-ACT",
                "O"
            ],
            "alternative_formats": {
                "spacy_format": {
                    "description": "spaCy training format with character offsets",
                    "structure": {
                        "text": "sample text",
                        "entities": "[(start, end, 'ENTITY_LABEL')]"
                    }
                },
                "conll_format": {
                    "description": "CoNLL-2003 format for sequence labeling",
                    "structure": "TOKEN\tPOS\tCHUNK\tNER_TAG"
                }
            }
        }
    
    def _define_pattern_examples(self) -> Dict[str, List[Dict[str, Any]]]:
        """Define contextual pattern examples for training"""
        return {
            "cross_references": [
                {
                    "text": "উক্ত ধারার বিধান অনুযায়ী",
                    "entities": [(5, 8, "SECTION")],
                    "context": "Reference to previous section"
                },
                {
                    "text": "সংশ্লিষ্ট তফসিলে বর্ণিত",
                    "entities": [(9, 15, "SCHEDULE")],
                    "context": "Reference to related schedule"
                }
            ],
            "complex_entities": [
                {
                    "text": "আয়কর আইন, ২০২৩ এর ধারা ১৬৩ এর উপধারা (১) অনুযায়ী",
                    "entities": [
                        (0, 16, "ACT"),
                        (20, 28, "SECTION"),
                        (32, 41, "SECTION")
                    ],
                    "context": "Nested legal references"
                }
            ],
            "bilingual_contexts": [
                {
                    "text": "According to section ১৬৩ of আয়কর আইন",
                    "entities": [
                        (18, 21, "SECTION"),
                        (25, 34, "ACT")
                    ],
                    "context": "Mixed Bengali-English legal text"
                }
            ]
        }
    
    def generate_annotation_guidelines(self) -> Dict[str, Any]:
        """Generate comprehensive annotation guidelines"""
        return {
            "annotation_principles": {
                "consistency": "Use consistent entity boundaries and labels",
                "context_aware": "Consider legal context when annotating",
                "bilingual_support": "Handle Bengali-English mixed text",
                "precision": "Prefer precise boundaries over broad spans"
            },
            "entity_priority": [
                "SECTION", "SCHEDULE", "RULE", "ACT",  # Legal references (highest)
                "AMOUNT", "PERCENTAGE", "DATE",        # Quantitative entities
                "AUTHORITY", "TAXPAYER", "FORM"        # Organizational entities
            ],
            "annotation_rules": {
                "overlapping_entities": "Use longest matching entity span",
                "ambiguous_cases": "Prefer legal reference interpretation",
                "number_handling": "Include currency/percentage indicators in entity span",
                "abbreviation_handling": "Include full forms when present"
            },
            "quality_checks": {
                "entity_completeness": "Ensure all legal entities are tagged",
                "boundary_accuracy": "Verify entity boundaries are precise",
                "label_consistency": "Check consistent labeling across similar contexts",
                "coverage_validation": "Validate coverage of all entity types"
            }
        }
    
    def create_training_templates(self) -> List[Dict[str, Any]]:
        """Create templates for consistent annotation"""
        templates = []
        
        for entity_type, entity_info in self.entity_categories.items():
            for pattern in entity_info["patterns"]:
                template = {
                    "entity_type": entity_type,
                    "pattern": pattern,
                    "template_text": f"এই {pattern} অনুযায়ী কর নির্ধারণ করা হবে।",
                    "expected_annotation": {
                        "text": f"এই {pattern} অনুযায়ী কর নির্ধারণ করা হবে।",
                        "entities": [(4, 4+len(pattern), entity_type)]
                    }
                }
                templates.append(template)
        
        return templates
    
    def export_schema(self, output_dir: str):
        """Export complete schema to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Main schema file
        schema_data = {
            "schema_version": "1.0",
            "creation_date": "2025-08-12",
            "entity_categories": self.entity_categories,
            "annotation_format": self.annotation_format,
            "pattern_examples": self.pattern_examples,
            "annotation_guidelines": self.generate_annotation_guidelines(),
            "training_templates": self.create_training_templates()
        }
        
        with open(output_path / "bengali_legal_entity_schema.json", 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, ensure_ascii=False, indent=2)
        
        # Quick reference for annotators
        quick_ref = {
            "entity_types": list(self.entity_categories.keys()),
            "tag_format": "BIO tagging (B-ENTITY, I-ENTITY, O)",
            "priority_entities": ["SECTION", "SCHEDULE", "RULE", "ACT"],
            "common_patterns": {
                entity: info["patterns"][:2] 
                for entity, info in self.entity_categories.items()
            }
        }
        
        with open(output_path / "annotation_quick_reference.json", 'w', encoding='utf-8') as f:
            json.dump(quick_ref, f, ensure_ascii=False, indent=2)
        
        # Validation patterns for quality control
        validation_patterns = {
            "mandatory_entities": ["SECTION", "ACT"],
            "validation_rules": [
                "Each sentence should have at least one legal entity",
                "Section references must include numbers",
                "Amounts must include currency indicators"
            ],
            "quality_metrics": [
                "Entity coverage percentage",
                "Boundary accuracy score",
                "Inter-annotator agreement"
            ]
        }
        
        with open(output_path / "validation_patterns.json", 'w', encoding='utf-8') as f:
            json.dump(validation_patterns, f, ensure_ascii=False, indent=2)
        
        return output_path

def main():
    """Create comprehensive Bengali legal entity annotation schema"""
    schema = BengaliLegalEntitySchema()
    
    # Export schema files
    output_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_5_bengali_legal_ner/schemas"
    schema_path = schema.export_schema(output_dir)
    
    print("🎯 PHASE 1.5B COMPLETED: Bengali Legal Entity Annotation Schema")
    print(f"Schema exported to: {schema_path}")
    print(f"Entity categories defined: {len(schema.entity_categories)}")
    print(f"Training templates created: {len(schema.create_training_templates())}")
    
    print("\n📋 Entity Categories:")
    for entity_type in schema.entity_categories.keys():
        print(f"  • {entity_type}")
    
    print(f"\n✅ Files created:")
    print(f"  • bengali_legal_entity_schema.json (Complete schema)")
    print(f"  • annotation_quick_reference.json (Annotator guide)")
    print(f"  • validation_patterns.json (Quality control)")

if __name__ == "__main__":
    main()