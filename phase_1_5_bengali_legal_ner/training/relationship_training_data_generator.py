#!/usr/bin/env python3
"""
Relationship Training Data Generator for Phase 2.1
Generates Bengali legal relationship training data for knowledge graph construction
"""

import json
import random
from typing import List, Dict, Tuple, Any
from datetime import datetime
import re

class RelationshipTrainingDataGenerator:
    def __init__(self):
        self.relationship_patterns = self._load_relationship_patterns()
        self.base_entities = self._load_base_entities()
        self.relationship_vocabulary = self._load_relationship_vocabulary()
        
    def _load_relationship_patterns(self) -> Dict[str, Any]:
        """Load relationship patterns from expanded schema"""
        return {
            "REFERENCE": {
                "bengali_patterns": [
                    "উক্ত {entity} অনুসারে",
                    "সংশ্লিষ্ট {entity} মতে", 
                    "উল্লেখিত {entity} ভিত্তিতে",
                    "বর্ণিত {entity} অনুযায়ী",
                    "নির্দেশিত {entity} অনুসরণে"
                ],
                "english_patterns": [
                    "according to the said {entity}",
                    "as per the mentioned {entity}",
                    "in accordance with the {entity}",
                    "pursuant to the {entity}",
                    "as specified in the {entity}"
                ]
            },
            "OVERRIDE": {
                "bengali_patterns": [
                    "এই {entity} পূর্বের বিধান রহিত করে",
                    "{entity} বাতিল করা হয়েছে",
                    "নতুন {entity} পুরাতন {entity} প্রতিস্থাপন করে",
                    "{entity} সংশোধন করে প্রতিস্থাপন",
                    "পরিবর্তিত {entity} পূর্বের স্থলে"
                ],
                "english_patterns": [
                    "this {entity} overrides the previous provision",
                    "the {entity} supersedes earlier rules", 
                    "new {entity} replaces the old {entity}",
                    "amended {entity} substitutes the former",
                    "revised {entity} cancels previous version"
                ]
            },
            "IMPLEMENT": {
                "bengali_patterns": [
                    "{entity} বাস্তবায়নের জন্য",
                    "এই {entity} কার্যকর করার উদ্দেশ্যে",
                    "{entity} প্রয়োগের নির্দেশনা",
                    "{entity} পালনের বিধি",
                    "{entity} অনুসরণের পদ্ধতি"
                ],
                "english_patterns": [
                    "for implementing the {entity}",
                    "to enforce the {entity}",
                    "guidelines for applying the {entity}",
                    "procedure for executing the {entity}",
                    "mechanism to carry out the {entity}"
                ]
            },
            "MODIFY": {
                "bengali_patterns": [
                    "{entity} সংশোধন করা হয়েছে",
                    "পরিবর্তিত {entity} প্রকাশ",
                    "{entity} হালনাগাদকরণ",
                    "সংস্কৃত {entity} অনুমোদন",
                    "{entity} পরিমার্জন বিজ্ঞপ্তি"
                ],
                "english_patterns": [
                    "the {entity} has been amended",
                    "modified {entity} notification", 
                    "updated {entity} published",
                    "revised {entity} approved",
                    "altered {entity} in effect"
                ]
            },
            "CONDITION": {
                "bengali_patterns": [
                    "যদি {condition} তাহলে {entity} প্রযোজ্য",
                    "{entity} শর্তসাপেক্ষে কার্যকর",
                    "তবে {condition} ছাড়া {entity} প্রযোজ্য নয়",
                    "{condition} ক্ষেত্রে {entity} বলবৎ",
                    "শর্ত পূরণে {entity} কার্যকরী"
                ],
                "english_patterns": [
                    "if {condition} then {entity} applies",
                    "{entity} is subject to {condition}",
                    "provided that {condition}, {entity} shall apply",
                    "in case of {condition}, {entity} is effective",
                    "unless {condition}, {entity} does not apply"
                ]
            },
            "HIERARCHY": {
                "bengali_patterns": [
                    "{parent} এর অধীনে প্রণীত {child}",
                    "প্রধান {parent} ও গৌণ {child}",
                    "{parent} কর্তৃক প্রণীত {child}",
                    "উপ-{child} ও মূল {parent}",
                    "{parent} আইনের অধীন {child} বিধিমালা"
                ],
                "english_patterns": [
                    "{child} made under the {parent}",
                    "primary {parent} and secondary {child}",
                    "{child} framed by {parent}",
                    "sub-{child} under main {parent}",
                    "{child} rules under {parent} act"
                ]
            }
        }
    
    def _load_base_entities(self) -> Dict[str, List[str]]:
        """Load base entity examples from Phase 1.5"""
        return {
            "SECTION": ["ধারা ১৬৩", "section 163", "উপধারা (১)", "sub-section (1)"],
            "ACT": ["আয়কর আইন", "income tax act", "মূল্য সংযোজন কর আইন", "value added tax act"],
            "RULE": ["আয়কর বিধিমালা", "income tax rules", "বিধি ২৫", "rule 25"],
            "SCHEDULE": ["৬ষ্ঠ তফসিল", "6th schedule", "তৃতীয় তফসিল", "third schedule"],
            "AMOUNT": ["৫০,০০০ টাকা", "50,000 taka", "১ লক্ষ টাকা", "1 lakh taka"],
            "PERCENTAGE": ["১৫ শতাংশ", "15 percent", "১৫%", "15%"],
            "DATE": ["১ জুলাই, ২০২৩", "1st July, 2023", "৩০শে জুন", "30th June"],
            "AUTHORITY": ["জাতীয় রাজস্ব বোর্ড", "national board of revenue", "কর কমিশনার", "tax commissioner"],
            "TAXPAYER": ["ব্যক্তি করদাতা", "individual taxpayer", "কোম্পানি করদাতা", "company taxpayer"],
            "FORM": ["ফরম-১১৬৩", "form-1163", "কর রিটার্ন", "tax return"]
        }
    
    def _load_relationship_vocabulary(self) -> Dict[str, List[str]]:
        """Load relationship-specific vocabulary"""
        return {
            "reference_words": ["উক্ত", "সংশ্লিষ্ট", "উল্লেখিত", "বর্ণিত", "অনুসারে", "মতে", "ভিত্তিতে"],
            "override_words": ["রহিত", "বাতিল", "প্রতিস্থাপন", "পরিবর্তন", "সংশোধন", "নতুন", "পরিবর্তে"],
            "implement_words": ["বাস্তবায়ন", "কার্যকর", "প্রয়োগ", "পালন", "অনুসরণ", "কার্যকরী"],
            "modify_words": ["সংশোধন", "পরিবর্তন", "সংযোজন", "হালনাগাদ", "সংস্কার", "পরিমার্জন"],
            "condition_words": ["শর্ত", "যদি", "তাহলে", "তবে", "শর্তসাপেক্ষে", "ব্যতিক্রম", "ক্ষেত্রে"],
            "hierarchy_words": ["অধীন", "প্রধান", "গৌণ", "উপ", "কর্তৃক", "প্রণীত"]
        }
    
    def generate_relationship_sample(self, relationship_type: str, language: str = "mixed") -> Dict[str, Any]:
        """Generate a single relationship training sample"""
        patterns = self.relationship_patterns[relationship_type]
        
        if language == "bengali":
            pattern = random.choice(patterns["bengali_patterns"])
        elif language == "english": 
            pattern = random.choice(patterns["english_patterns"])
        else:  # mixed
            pattern = random.choice(patterns["bengali_patterns"] + patterns["english_patterns"])
        
        # Select appropriate entities
        entity_type = random.choice(list(self.base_entities.keys()))
        entity = random.choice(self.base_entities[entity_type])
        
        # Generate text based on relationship type
        if relationship_type == "HIERARCHY":
            parent_entity = random.choice(self.base_entities["ACT"])
            child_entity = random.choice(self.base_entities["RULE"])
            text = pattern.format(parent=parent_entity, child=child_entity)
        elif relationship_type == "CONDITION":
            condition = "করদাতার আয় ৫০ হাজার টাকার বেশি হয়"
            text = pattern.format(condition=condition, entity=entity)
        else:
            text = pattern.format(entity=entity)
        
        # Generate BIO tags
        entities, bio_tags = self._generate_bio_tags(text, relationship_type)
        
        return {
            "text": text,
            "entities": entities,
            "bio_tags": bio_tags,
            "relationship_type": relationship_type,
            "language": language,
            "generated": True
        }
    
    def _generate_bio_tags(self, text: str, relationship_type: str) -> Tuple[List[Tuple[int, int, str]], List[str]]:
        """Generate BIO tags for the text"""
        tokens = text.split()
        entities = []
        bio_tags = ["O"] * len(tokens)
        
        # Simple pattern matching for demonstration
        # In practice, this would use more sophisticated NLP
        
        relationship_indicators = self.relationship_vocabulary
        
        for i, token in enumerate(tokens):
            # Check for base entities
            for entity_type, examples in self.base_entities.items():
                for example in examples:
                    if token in example or example in token:
                        start_pos = text.find(token)
                        end_pos = start_pos + len(token)
                        entities.append((start_pos, end_pos, entity_type))
                        bio_tags[i] = f"B-{entity_type}"
                        break
            
            # Check for relationship indicators
            for word_type, words in relationship_indicators.items():
                if token in words:
                    start_pos = text.find(token)
                    end_pos = start_pos + len(token)
                    entities.append((start_pos, end_pos, relationship_type))
                    bio_tags[i] = f"B-{relationship_type}" if bio_tags[i] == "O" else bio_tags[i]
                    break
        
        return entities, bio_tags
    
    def generate_training_dataset(self, 
                                samples_per_relationship: int = 400, 
                                output_file: str = "relationship_training_data.json") -> Dict[str, Any]:
        """Generate complete relationship training dataset"""
        
        dataset = {
            "metadata": {
                "generation_date": datetime.now().isoformat(),
                "phase": "Phase 2.1 - Relationship Entity Expansion",
                "total_samples": samples_per_relationship * 6,
                "relationship_types": 6,
                "samples_per_type": samples_per_relationship
            },
            "training_samples": []
        }
        
        relationship_types = ["REFERENCE", "OVERRIDE", "IMPLEMENT", "MODIFY", "CONDITION", "HIERARCHY"]
        
        print(f"🔄 Generating relationship training data...")
        
        for relationship_type in relationship_types:
            print(f"  ⚡ Generating {samples_per_relationship} samples for {relationship_type}...")
            
            for i in range(samples_per_relationship):
                # Mix of languages: 50% Bengali, 30% English, 20% mixed
                lang_choice = random.choices(
                    ["bengali", "english", "mixed"], 
                    weights=[0.5, 0.3, 0.2]
                )[0]
                
                sample = self.generate_relationship_sample(relationship_type, lang_choice)
                sample["sample_id"] = f"{relationship_type}_{i+1:04d}"
                dataset["training_samples"].append(sample)
        
        # Shuffle the dataset
        random.shuffle(dataset["training_samples"])
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Generated {len(dataset['training_samples'])} relationship training samples")
        print(f"📁 Saved to: {output_file}")
        
        return dataset
    
    def create_mixed_training_dataset(self, 
                                    base_data_file: str = "real_training_dataset.json",
                                    relationship_samples: int = 400) -> Dict[str, Any]:
        """Create mixed dataset combining Phase 1.5 base data with relationship data"""
        
        print("🔄 Creating mixed training dataset...")
        
        # Load base data from Phase 1.5
        try:
            with open(base_data_file, 'r', encoding='utf-8') as f:
                base_data = json.load(f)
            print(f"✅ Loaded {len(base_data.get('training_data', []))} base samples")
        except FileNotFoundError:
            print(f"⚠️ Base data file {base_data_file} not found, creating relationship data only")
            base_data = {"training_data": []}
        
        # Generate relationship data
        relationship_data = self.generate_training_dataset(relationship_samples, "temp_relationship_data.json")
        
        # Combine datasets
        mixed_dataset = {
            "metadata": {
                "creation_date": datetime.now().isoformat(),
                "phase": "Phase 2.1 - Mixed Training Dataset",
                "base_samples": len(base_data.get("training_data", [])),
                "relationship_samples": len(relationship_data["training_samples"]),
                "total_samples": len(base_data.get("training_data", [])) + len(relationship_data["training_samples"]),
                "entity_types": 16,
                "bio_labels": 33
            },
            "training_data": []
        }
        
        # Add base data (convert to new format if needed)
        for sample in base_data.get("training_data", []):
            mixed_dataset["training_data"].append({
                "sample_id": sample.get("id", f"base_{len(mixed_dataset['training_data'])}"),
                "text": sample.get("text", ""),
                "entities": sample.get("entities", []),
                "bio_tags": sample.get("labels", []),
                "source": "phase_1_5_base",
                "relationship_type": None
            })
        
        # Add relationship data
        mixed_dataset["training_data"].extend(relationship_data["training_samples"])
        
        # Shuffle combined dataset
        random.shuffle(mixed_dataset["training_data"])
        
        # Save mixed dataset
        output_file = "mixed_training_dataset.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mixed_dataset, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Created mixed training dataset with {mixed_dataset['metadata']['total_samples']} samples")
        print(f"📁 Saved to: {output_file}")
        
        # Clean up temporary file
        import os
        if os.path.exists("temp_relationship_data.json"):
            os.remove("temp_relationship_data.json")
        
        return mixed_dataset
    
    def validate_dataset_quality(self, dataset_file: str = "mixed_training_dataset.json") -> Dict[str, Any]:
        """Validate the quality of generated training dataset"""
        
        print("🔍 Validating dataset quality...")
        
        with open(dataset_file, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        validation_report = {
            "total_samples": len(dataset["training_data"]),
            "entity_type_distribution": {},
            "relationship_type_distribution": {},
            "language_distribution": {},
            "quality_metrics": {}
        }
        
        # Analyze entity types
        for sample in dataset["training_data"]:
            entities = sample.get("entities", [])
            for entity in entities:
                entity_type = entity[2] if len(entity) > 2 else "UNKNOWN"
                validation_report["entity_type_distribution"][entity_type] = \
                    validation_report["entity_type_distribution"].get(entity_type, 0) + 1
            
            # Analyze relationship types
            rel_type = sample.get("relationship_type")
            if rel_type:
                validation_report["relationship_type_distribution"][rel_type] = \
                    validation_report["relationship_type_distribution"].get(rel_type, 0) + 1
            
            # Analyze language distribution
            lang = sample.get("language", "unknown")
            validation_report["language_distribution"][lang] = \
                validation_report["language_distribution"].get(lang, 0) + 1
        
        # Calculate quality metrics
        validation_report["quality_metrics"] = {
            "avg_entities_per_sample": sum(len(s.get("entities", [])) for s in dataset["training_data"]) / len(dataset["training_data"]),
            "samples_with_relationships": sum(1 for s in dataset["training_data"] if s.get("relationship_type")),
            "base_entity_coverage": len(validation_report["entity_type_distribution"]),
            "relationship_coverage": len(validation_report["relationship_type_distribution"])
        }
        
        print(f"✅ Dataset validation complete:")
        print(f"   📊 Total samples: {validation_report['total_samples']}")
        print(f"   📈 Avg entities per sample: {validation_report['quality_metrics']['avg_entities_per_sample']:.2f}")
        print(f"   🔗 Relationship samples: {validation_report['quality_metrics']['samples_with_relationships']}")
        print(f"   🏷️ Entity types: {validation_report['quality_metrics']['base_entity_coverage']}")
        print(f"   ⚡ Relationship types: {validation_report['quality_metrics']['relationship_coverage']}")
        
        # Save validation report
        with open("dataset_validation_report.json", 'w', encoding='utf-8') as f:
            json.dump(validation_report, f, ensure_ascii=False, indent=2)
        
        return validation_report

def main():
    """Main execution function"""
    generator = RelationshipTrainingDataGenerator()
    
    print("🚀 Phase 2.1: Relationship Training Data Generation")
    print("=" * 60)
    
    # Generate relationship training data
    relationship_dataset = generator.generate_training_dataset(
        samples_per_relationship=400,
        output_file="relationship_training_data.json"
    )
    
    print("\n" + "=" * 60)
    
    # Create mixed training dataset
    mixed_dataset = generator.create_mixed_training_dataset(
        base_data_file="../real_training_data/real_training_dataset.json",
        relationship_samples=400
    )
    
    print("\n" + "=" * 60)
    
    # Validate dataset quality
    validation_report = generator.validate_dataset_quality("mixed_training_dataset.json")
    
    print("\n✅ Phase 2.1 Relationship Training Data Generation COMPLETE")
    print(f"📁 Files created:")
    print(f"   - relationship_training_data.json")
    print(f"   - mixed_training_dataset.json")  
    print(f"   - dataset_validation_report.json")

if __name__ == "__main__":
    main()