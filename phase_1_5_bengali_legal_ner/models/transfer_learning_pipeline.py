#!/usr/bin/env python3
"""
Transfer Learning Pipeline for Bengali Legal NER
Phase 1.5D: Setup transfer learning with existing Bengali NER models
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import logging
from dataclasses import dataclass
import re

# For production use, these would be actual imports:
# import torch
# from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
# import datasets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for Bengali NER models"""
    model_name: str
    tokenizer_name: str
    num_labels: int
    max_length: int = 128
    learning_rate: float = 2e-5
    batch_size: int = 16
    num_epochs: int = 3
    warmup_steps: int = 500

class BengaliLegalNERPipeline:
    def __init__(self, config_file: str, output_dir: str):
        self.config_file = Path(config_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Bengali NER model options (production would use actual models)
        self.available_models = {
            "bert_base_bengali": {
                "model_name": "sagorsarker/bangla-bert-base",
                "description": "Bengali BERT base model",
                "size": "110M parameters",
                "performance": "Good general purpose Bengali understanding"
            },
            "roberta_bengali": {
                "model_name": "flax-community/bangla-roberta-base", 
                "description": "Bengali RoBERTa model",
                "size": "125M parameters",
                "performance": "Enhanced contextual understanding"
            },
            "distilbert_bengali": {
                "model_name": "neuropark/sahaj-bangla-distilbert",
                "description": "Distilled Bengali BERT",
                "size": "66M parameters", 
                "performance": "Faster inference, good accuracy"
            }
        }
        
        # Legal entity mappings from schema
        self.entity_mapping = self._load_entity_mapping()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        return {
            "model_selection": {
                "primary_model": "bert_base_bengali",
                "fallback_model": "distilbert_bengali",
                "ensemble_models": ["bert_base_bengali", "roberta_bengali"]
            },
            "training_params": {
                "max_length": 128,
                "learning_rate": 2e-5,
                "batch_size": 16,
                "num_epochs": 3,
                "warmup_ratio": 0.1,
                "weight_decay": 0.01
            },
            "data_params": {
                "train_split": 0.8,
                "val_split": 0.1,
                "test_split": 0.1,
                "min_entity_frequency": 5
            }
        }
    
    def _load_entity_mapping(self) -> Dict[str, int]:
        """Load entity mapping from schema"""
        schema_file = self.output_dir.parent / "schemas" / "bengali_legal_entity_schema.json"
        
        if schema_file.exists():
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            entities = list(schema["entity_categories"].keys())
            
            # Create BIO tagging scheme
            entity_mapping = {"O": 0}  # Outside
            label_id = 1
            
            for entity in entities:
                entity_mapping[f"B-{entity}"] = label_id
                entity_mapping[f"I-{entity}"] = label_id + 1
                label_id += 2
            
            return entity_mapping
        else:
            # Default entity mapping
            return {
                "O": 0,
                "B-SECTION": 1, "I-SECTION": 2,
                "B-ACT": 3, "I-ACT": 4,
                "B-SCHEDULE": 5, "I-SCHEDULE": 6,
                "B-AMOUNT": 7, "I-AMOUNT": 8,
                "B-PERCENTAGE": 9, "I-PERCENTAGE": 10
            }
    
    def prepare_training_data(self, chunks_file: str) -> Dict[str, Any]:
        """Prepare training data from smart chunks"""
        logger.info("📊 Preparing training data for Bengali Legal NER...")
        
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        # Get training ready chunks
        if isinstance(chunks_data, dict) and "all_chunks" in chunks_data:
            chunks = chunks_data["all_chunks"]
        else:
            chunks = chunks_data
        
        # Convert chunks to NER training format
        training_examples = []
        
        for chunk in chunks[:1000]:  # Limit for initial training
            text = chunk.get("text", "")
            if len(text.strip()) > 0:
                # Tokenize and create mock annotations for demo
                tokens = self._tokenize_bengali_text(text)
                labels = self._create_mock_labels(tokens)
                
                training_examples.append({
                    "tokens": tokens,
                    "labels": labels,
                    "source": chunk.get("source", "unknown"),
                    "priority_score": chunk.get("priority_score", 0.0)
                })
        
        # Split data
        train_size = int(len(training_examples) * self.config["data_params"]["train_split"])
        val_size = int(len(training_examples) * self.config["data_params"]["val_split"])
        
        train_data = training_examples[:train_size]
        val_data = training_examples[train_size:train_size + val_size]
        test_data = training_examples[train_size + val_size:]
        
        logger.info(f"✅ Prepared {len(train_data)} training, {len(val_data)} validation, {len(test_data)} test examples")
        
        return {
            "train": train_data,
            "validation": val_data,
            "test": test_data,
            "entity_mapping": self.entity_mapping,
            "num_labels": len(self.entity_mapping)
        }
    
    def _tokenize_bengali_text(self, text: str) -> List[str]:
        """Tokenize Bengali text handling mixed script"""
        # Basic tokenization - in production would use proper tokenizer
        
        # Handle mixed Bengali-English
        text = re.sub(r'([।৷])', r' \1 ', text)  # Bengali punctuation
        text = re.sub(r'([.!?])', r' \1 ', text)  # English punctuation
        text = re.sub(r'(\d+)', r' \1 ', text)    # Numbers
        text = re.sub(r'\s+', ' ', text)          # Multiple spaces
        
        tokens = text.strip().split()
        
        # Filter out empty tokens
        return [token for token in tokens if len(token.strip()) > 0]
    
    def _create_mock_labels(self, tokens: List[str]) -> List[str]:
        """Create mock labels for demonstration (in production, use real annotations)"""
        labels = []
        
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            
            # Section references
            if token_lower in ["ধারা", "section"]:
                labels.append("B-SECTION")
            elif i > 0 and labels[-1] in ["B-SECTION", "I-SECTION"] and re.match(r'\d+', token):
                labels.append("I-SECTION")
            
            # Acts
            elif token_lower in ["আইন", "act"]:
                labels.append("B-ACT")
            elif i > 0 and labels[-1] in ["B-ACT", "I-ACT"] and token_lower in ["আয়কর", "income", "tax"]:
                labels.append("I-ACT")
            
            # Schedules
            elif token_lower in ["তফসিল", "schedule"]:
                labels.append("B-SCHEDULE")
            elif i > 0 and labels[-1] in ["B-SCHEDULE", "I-SCHEDULE"] and re.match(r'\d+', token):
                labels.append("I-SCHEDULE")
            
            # Amounts
            elif token_lower in ["টাকা", "taka"]:
                labels.append("B-AMOUNT")
            elif i > 0 and labels[-1] in ["B-AMOUNT", "I-AMOUNT"] and re.match(r'[\d,]+', token):
                labels.append("I-AMOUNT")
            
            # Percentages
            elif token_lower in ["শতাংশ", "percent"] or "%" in token:
                labels.append("B-PERCENTAGE")
            elif i > 0 and labels[-1] in ["B-PERCENTAGE", "I-PERCENTAGE"] and re.match(r'\d+', token):
                labels.append("I-PERCENTAGE")
            
            else:
                labels.append("O")
        
        return labels
    
    def create_model_configs(self) -> List[ModelConfig]:
        """Create model configurations for different Bengali models"""
        configs = []
        
        for model_key, model_info in self.available_models.items():
            config = ModelConfig(
                model_name=model_info["model_name"],
                tokenizer_name=model_info["model_name"],
                num_labels=len(self.entity_mapping),
                max_length=self.config["training_params"]["max_length"],
                learning_rate=self.config["training_params"]["learning_rate"],
                batch_size=self.config["training_params"]["batch_size"],
                num_epochs=self.config["training_params"]["num_epochs"]
            )
            configs.append(config)
        
        return configs
    
    def setup_transfer_learning_framework(self) -> Dict[str, Any]:
        """Setup complete transfer learning framework"""
        logger.info("🚀 Setting up Bengali Legal NER transfer learning framework...")
        
        framework = {
            "model_configs": [
                {
                    "model_key": key,
                    "model_name": info["model_name"],
                    "description": info["description"],
                    "size": info["size"],
                    "performance": info["performance"]
                }
                for key, info in self.available_models.items()
            ],
            "entity_mapping": self.entity_mapping,
            "training_config": self.config,
            "pipeline_steps": [
                "Load pre-trained Bengali model",
                "Adapt tokenizer for legal terminology",
                "Add classification head for legal entities",
                "Fine-tune on legal training data",
                "Validate on held-out legal text",
                "Optimize for inference speed"
            ],
            "optimization_strategies": [
                "Gradual unfreezing of model layers",
                "Learning rate scheduling",
                "Class weight balancing for rare entities",
                "Data augmentation with legal synonyms",
                "Ensemble predictions from multiple models"
            ]
        }
        
        # Save framework configuration
        framework_file = self.output_dir / "transfer_learning_framework.json"
        with open(framework_file, 'w', encoding='utf-8') as f:
            json.dump(framework, f, ensure_ascii=False, indent=2)
        
        # Create training script template
        self._create_training_script_template()
        
        # Create evaluation framework
        self._create_evaluation_framework()
        
        return framework
    
    def _create_training_script_template(self):
        """Create training script template for production use"""
        template = '''#!/usr/bin/env python3
"""
Bengali Legal NER Training Script
Generated template for production training
"""

# Production imports (uncomment for actual use):
# from transformers import AutoTokenizer, AutoModelForTokenClassification
# from transformers import TrainingArguments, Trainer, DataCollatorForTokenClassification
# import torch
# from datasets import Dataset

def load_model_and_tokenizer(model_name: str):
    """Load pre-trained Bengali model and tokenizer"""
    # tokenizer = AutoTokenizer.from_pretrained(model_name)
    # model = AutoModelForTokenClassification.from_pretrained(
    #     model_name, 
    #     num_labels=len(entity_mapping)
    # )
    # return model, tokenizer
    pass

def prepare_dataset(training_data, tokenizer):
    """Prepare dataset for training"""
    # Convert training data to HuggingFace dataset format
    # Apply tokenization and label alignment
    # Handle subword tokenization for Bengali text
    pass

def train_model(model, train_dataset, val_dataset):
    """Train the Bengali Legal NER model"""
    # training_args = TrainingArguments(
    #     output_dir="./results",
    #     num_train_epochs=3,
    #     per_device_train_batch_size=16,
    #     per_device_eval_batch_size=64,
    #     warmup_steps=500,
    #     weight_decay=0.01,
    #     logging_dir="./logs",
    # )
    # 
    # trainer = Trainer(
    #     model=model,
    #     args=training_args,
    #     train_dataset=train_dataset,
    #     eval_dataset=val_dataset,
    #     data_collator=DataCollatorForTokenClassification(tokenizer),
    # )
    # 
    # trainer.train()
    pass

if __name__ == "__main__":
    print("🎯 Bengali Legal NER Training Script")
    print("Uncomment imports and implementation for production use")
'''
        
        script_file = self.output_dir / "training_script_template.py"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(template)
    
    def _create_evaluation_framework(self):
        """Create evaluation framework for model performance"""
        evaluation_config = {
            "metrics": [
                "Entity-level F1 score",
                "Token-level accuracy", 
                "Precision and recall per entity type",
                "Confusion matrix analysis",
                "Cross-validation performance"
            ],
            "evaluation_datasets": [
                "Hold-out test set (10%)",
                "External legal documents",
                "Manually annotated samples",
                "Cross-domain legal texts"
            ],
            "performance_targets": {
                "overall_f1": 0.85,
                "section_entity_f1": 0.90,
                "amount_entity_f1": 0.80,
                "inference_time_ms": 100
            },
            "error_analysis": [
                "Entity boundary errors",
                "Cross-lingual confusion",
                "Rare entity detection",
                "Context-dependent disambiguation"
            ]
        }
        
        eval_file = self.output_dir / "evaluation_framework.json"
        with open(eval_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_config, f, ensure_ascii=False, indent=2)
    
    def export_pipeline_summary(self, framework: Dict[str, Any], training_data: Dict[str, Any]):
        """Export comprehensive pipeline summary"""
        summary = {
            "pipeline_overview": {
                "name": "Bengali Legal NER Transfer Learning Pipeline",
                "version": "1.0",
                "creation_date": "2025-08-12",
                "purpose": "Fine-tune Bengali NER models for legal document processing"
            },
            "data_summary": {
                "training_examples": len(training_data["train"]),
                "validation_examples": len(training_data["validation"]),
                "test_examples": len(training_data["test"]),
                "entity_types": len(training_data["entity_mapping"]),
                "entity_mapping": training_data["entity_mapping"]
            },
            "model_options": framework["model_configs"],
            "training_pipeline": framework["pipeline_steps"],
            "optimization_strategies": framework["optimization_strategies"],
            "performance_targets": {
                "target_f1_score": 0.85,
                "target_inference_time": "< 100ms",
                "target_accuracy": 0.90
            },
            "next_steps": [
                "Install required dependencies (transformers, torch)",
                "Download pre-trained Bengali models",
                "Prepare annotated training data", 
                "Run transfer learning training",
                "Evaluate model performance",
                "Deploy for legal document processing"
            ]
        }
        
        summary_file = self.output_dir / "pipeline_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return summary_file

def main():
    """Setup Bengali Legal NER transfer learning pipeline"""
    config_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_5_bengali_legal_ner/models/config.json"
    output_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_5_bengali_legal_ner/models"
    chunks_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_5_bengali_legal_ner/chunks/training_ready_chunks.json"
    
    pipeline = BengaliLegalNERPipeline(config_file, output_dir)
    
    # Setup framework
    framework = pipeline.setup_transfer_learning_framework()
    
    # Prepare training data
    training_data = pipeline.prepare_training_data(chunks_file)
    
    # Export summary
    summary_file = pipeline.export_pipeline_summary(framework, training_data)
    
    print("🎯 PHASE 1.5D COMPLETED: Transfer Learning Pipeline Setup")
    print(f"Framework config: {output_dir}/transfer_learning_framework.json")
    print(f"Training template: {output_dir}/training_script_template.py")
    print(f"Evaluation config: {output_dir}/evaluation_framework.json")
    print(f"Pipeline summary: {summary_file}")
    
    print(f"\n📊 Data Summary:")
    print(f"  Training examples: {len(training_data['train'])}")
    print(f"  Validation examples: {len(training_data['validation'])}")
    print(f"  Test examples: {len(training_data['test'])}")
    print(f"  Entity types: {len(training_data['entity_mapping'])}")
    
    print(f"\n🤖 Available Models:")
    for model_config in framework["model_configs"]:
        print(f"  • {model_config['model_key']}: {model_config['description']}")

if __name__ == "__main__":
    main()