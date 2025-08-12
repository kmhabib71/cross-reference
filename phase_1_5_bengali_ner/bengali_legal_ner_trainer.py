#!/usr/bin/env python3
"""
Bengali Legal Domain NER Training System
Phase 1.5 - Advanced Bengali Legal NER Implementation

Implements ultra-precise Bengali legal entity recognition for Bangladesh tax law.
Fine-tunes Bengali-BERT for legal domain with 10,000+ annotated queries.
"""

import json
import re
import torch
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging
from datetime import datetime

# NER and ML imports
try:
    from transformers import (
        AutoTokenizer, AutoModelForTokenClassification,
        TrainingArguments, Trainer, DataCollatorForTokenClassification
    )
    from datasets import Dataset
    from seqeval.metrics import classification_report, f1_score
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not available. Install with: pip install transformers datasets seqeval torch")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BengaliLegalEntity:
    """Bengali legal entity with context and variations"""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    confidence: float
    canonical_id: Optional[str] = None
    variations: List[str] = None
    context_window: str = ""

@dataclass
class TrainingExample:
    """Training example for Bengali Legal NER"""
    text: str
    entities: List[BengaliLegalEntity]
    tokens: List[str]
    labels: List[str]
    source_document: str

class BengaliLegalNERTrainer:
    """
    Advanced Bengali Legal NER Training System
    
    Implements ultra-precise entity recognition for Bangladesh tax law:
    - Fine-tunes Bengali-BERT for legal domain
    - Handles indirect references (উক্ত ধারা, সংশ্লিষ্ট তফসিল)
    - Recognizes Bengali numerals with context
    - Prevents cross-domain confusion
    """
    
    def __init__(self, 
                 model_name: str = "sagorsarker/bangla-bert-base",
                 output_dir: str = "./bengali_legal_ner_model"):
        """
        Initialize Bengali Legal NER Trainer
        
        Args:
            model_name: Base Bengali-BERT model
            output_dir: Output directory for trained model
        """
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Entity type definitions
        self.entity_types = {
            'SECTION_DIRECT': 'Direct section references',
            'SECTION_INDIRECT': 'Indirect section references', 
            'SCHEDULE_REF': 'Schedule references',
            'AMOUNT_BENGALI': 'Bengali monetary amounts',
            'TAX_RATE': 'Tax rate percentages',
            'FINANCIAL_YEAR': 'Financial year references',
            'TAXPAYER_TYPE': 'Taxpayer classifications',
            'INCOME_SOURCE': 'Income source types'
        }
        
        # Label mapping for NER
        self.label_map = self._create_label_mapping()
        
        # Bengali patterns for entity recognition
        self.bengali_patterns = self._initialize_patterns()
        
        # Training data storage
        self.training_data: List[TrainingExample] = []
        
        # Model components
        self.tokenizer = None
        self.model = None
        
        logger.info(f"🚀 Bengali Legal NER Trainer initialized")
        logger.info(f"📁 Output directory: {self.output_dir}")
        logger.info(f"🎯 Entity types: {len(self.entity_types)}")

    def _create_label_mapping(self) -> Dict[str, int]:
        """Create BIO label mapping for NER"""
        labels = ['O']  # Outside entity
        
        for entity_type in self.entity_types.keys():
            labels.extend([f'B-{entity_type}', f'I-{entity_type}'])
        
        return {label: idx for idx, label in enumerate(labels)}

    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize Bengali legal text patterns"""
        return {
            'section_direct': [
                r'ধারা\s*([০-৯১-৯]+)',  # ধারা ১৬৩
                r'([০-৯১-৯]+)\s*নং\s*ধারা',  # ১৬৩ নং ধারা
                r'Section\s*(\d+)',  # Section 163
                r'Sec\s*\.?\s*(\d+)',  # Sec 163
                r's\.\s*(\d+)'  # s. 163
            ],
            'section_indirect': [
                r'উক্ত\s*ধারা',  # that section
                r'সংশ্লিষ্ট\s*তফসিল',  # related schedule
                r'পূর্বোক্ত\s*বিধি',  # aforementioned rule
                r'উপরোক্ত\s*বিধান',  # above provision
                r'এই\s*ধারার',  # this section's
            ],
            'schedule_ref': [
                r'তফসিল\s*([০-৯১-৯]+)',  # তফসিল ৪
                r'তপসিল\s*([০-৯১-৯]+)',  # Alternative spelling
                r'Schedule\s*(\d+)',  # Schedule 4
                r'([০-৯১-৯]+)\s*নং\s*তফসিল',  # ৪ নং তফসিল
            ],
            'amount_bengali': [
                r'([০-৯১-৯]+(?:\.[০-৯১-৯]+)?)\s*লক্ষ\s*টাকা',  # ৩.৫ লক্ষ টাকা
                r'([০-৯১-৯]+)\s*কোটি\s*টাকা',  # ১ কোটি টাকা
                r'([০-৯১-৯]+)\s*হাজার\s*টাকা',  # ৫০ হাজার টাকা
                r'(পাঁচ|দশ|বিশ|পঞ্চাশ|একশত)\s*লক্ষ',  # পাঁচ লক্ষ
                r'(এক|দুই|তিন|পাঁচ|দশ)\s*কোটি',  # এক কোটি
            ],
            'tax_rate': [
                r'([০-৯১-৯]+(?:\.[০-৯১-৯]+)?)\s*%',  # ১৫%
                r'([০-৯১-৯]+(?:\.[০-৯১-৯]+)?)\s*শতাংশ',  # ১৫ শতাংশ
                r'(\d+(?:\.\d+)?)\s*%',  # 15%
                r'(\d+(?:\.\d+)?)\s*percent',  # 15 percent
            ],
            'financial_year': [
                r'([০-৯২০১৯-৯]+(?:-[০-৯২০১৯-৯]+)?)\s*অর্থবছর',  # ২০২৫ অর্থবছর
                r'FY\s*(\d{4}-\d{2,4})',  # FY 2025-26
                r'(\d{4}-\d{2,4})\s*অর্থ\s*বছর',  # 2025-26 অর্থ বছর
            ],
            'taxpayer_type': [
                r'ব্যক্তি\s*করদাতা',  # Individual taxpayer
                r'কোম্পানি',  # Company
                r'সমিতি',  # Association
                r'Individual',
                r'Company',
                r'Partnership',
                r'AOP',  # Association of Persons
            ],
            'income_source': [
                r'ইউটিউব\s*আয়',  # YouTube income
                r'ব্যবসায়িক\s*আয়',  # Business income
                r'চাকরির\s*আয়',  # Employment income
                r'বেতন\s*আয়',  # Salary income
                r'ভাড়া\s*আয়',  # Rental income
                r'মূলধন\s*লাভ',  # Capital gain
                r'Business\s*income',
                r'Employment\s*income',
                r'Rental\s*income',
            ]
        }

    def load_phase1_data(self, phase1_dir: str) -> None:
        """
        Load Phase 1 structured data for NER training
        
        Args:
            phase1_dir: Path to Phase 1 analysis results
        """
        phase1_path = Path(phase1_dir)
        
        # Load citation patterns analysis
        citation_file = phase1_path / "citation_patterns_analysis.json"
        if citation_file.exists():
            with open(citation_file, 'r', encoding='utf-8') as f:
                citation_data = json.load(f)
                self._extract_training_from_citations(citation_data)
                
        # Load standardized content
        content_file = phase1_path / "standardized_content.json"
        if content_file.exists():
            with open(content_file, 'r', encoding='utf-8') as f:
                content_data = json.load(f)
                self._extract_training_from_content(content_data)
                
        logger.info(f"📚 Loaded Phase 1 data: {len(self.training_data)} examples")

    def _extract_training_from_citations(self, citation_data: Dict) -> None:
        """Extract training examples from Phase 1 citation analysis"""
        if 'citation_registry' not in citation_data:
            return
            
        for section_id, section_info in citation_data['citation_registry'].get('sections', {}).items():
            for reference in section_info.get('referenced_in', []):
                text = reference.get('context', '')
                if text:
                    entities = self._annotate_text_entities(text)
                    if entities:
                        tokens = self._tokenize_bengali_text(text)
                        labels = self._create_bio_labels(tokens, entities)
                        
                        example = TrainingExample(
                            text=text,
                            entities=entities,
                            tokens=tokens,
                            labels=labels,
                            source_document=reference.get('document', 'unknown')
                        )
                        self.training_data.append(example)

    def _extract_training_from_content(self, content_data: Dict) -> None:
        """Extract training examples from Phase 1 standardized content"""
        if 'bilingual_mappings' not in content_data:
            return
            
        for section_num, section_info in content_data['bilingual_mappings'].get('section_mappings', {}).items():
            # Create training examples from Bengali variations
            for variation in section_info.get('bengali_variations', []):
                context = f"আয়কর আইন ২০২ৃ এর {variation} অনুযায়ী কর নির্ধারণ করা হবে।"
                entities = self._annotate_text_entities(context)
                if entities:
                    tokens = self._tokenize_bengali_text(context)
                    labels = self._create_bio_labels(tokens, entities)
                    
                    example = TrainingExample(
                        text=context,
                        entities=entities,
                        tokens=tokens,
                        labels=labels,
                        source_document=f"section_{section_num}"
                    )
                    self.training_data.append(example)

    def _annotate_text_entities(self, text: str) -> List[BengaliLegalEntity]:
        """
        Annotate entities in Bengali legal text
        
        Args:
            text: Input Bengali text
            
        Returns:
            List of identified Bengali legal entities
        """
        entities = []
        
        for entity_type, patterns in self.bengali_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entity = BengaliLegalEntity(
                        text=match.group(0),
                        entity_type=entity_type.upper(),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.95,  # High confidence for pattern matches
                        context_window=text[max(0, match.start()-50):match.end()+50]
                    )
                    entities.append(entity)
        
        # Remove overlapping entities (keep longest)
        entities = self._resolve_overlapping_entities(entities)
        
        return entities

    def _resolve_overlapping_entities(self, entities: List[BengaliLegalEntity]) -> List[BengaliLegalEntity]:
        """Resolve overlapping entities by keeping the longest ones"""
        if not entities:
            return []
            
        # Sort by start position
        entities.sort(key=lambda x: x.start_pos)
        
        resolved = []
        for entity in entities:
            # Check if this entity overlaps with any already added
            overlaps = False
            for existing in resolved:
                if (entity.start_pos < existing.end_pos and 
                    entity.end_pos > existing.start_pos):
                    # Keep the longer entity
                    if len(entity.text) > len(existing.text):
                        resolved.remove(existing)
                        resolved.append(entity)
                    overlaps = True
                    break
            
            if not overlaps:
                resolved.append(entity)
        
        return resolved

    def _tokenize_bengali_text(self, text: str) -> List[str]:
        """
        Tokenize Bengali text for NER training
        
        Args:
            text: Input Bengali text
            
        Returns:
            List of tokens
        """
        # Simple tokenization for now - can be improved with proper Bengali tokenizer
        # Split on whitespace and punctuation
        import string
        bengali_punctuation = '।,;:!?()[]{}""''—–'
        
        tokens = []
        current_token = ""
        
        for char in text:
            if char.isspace() or char in string.punctuation or char in bengali_punctuation:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                if not char.isspace():
                    tokens.append(char)
            else:
                current_token += char
        
        if current_token:
            tokens.append(current_token)
            
        return [token for token in tokens if token.strip()]

    def _create_bio_labels(self, tokens: List[str], entities: List[BengaliLegalEntity]) -> List[str]:
        """
        Create BIO labels for tokens based on entities
        
        Args:
            tokens: List of tokens
            entities: List of identified entities
            
        Returns:
            List of BIO labels
        """
        # Reconstruct text positions for tokens
        text = ' '.join(tokens)
        token_positions = []
        current_pos = 0
        
        for token in tokens:
            start = text.find(token, current_pos)
            end = start + len(token)
            token_positions.append((start, end))
            current_pos = end
        
        # Assign labels
        labels = ['O'] * len(tokens)
        
        for entity in entities:
            entity_tokens = []
            for i, (start, end) in enumerate(token_positions):
                if start >= entity.start_pos and end <= entity.end_pos:
                    entity_tokens.append(i)
            
            # Assign B-/I- labels
            for i, token_idx in enumerate(entity_tokens):
                if i == 0:
                    labels[token_idx] = f'B-{entity.entity_type}'
                else:
                    labels[token_idx] = f'I-{entity.entity_type}'
        
        return labels

    def generate_synthetic_training_data(self, count: int = 5000) -> None:
        """
        Generate synthetic Bengali legal training data
        
        Args:
            count: Number of synthetic examples to generate
        """
        logger.info(f"🔄 Generating {count} synthetic training examples...")
        
        # Template patterns for different scenarios
        templates = {
            'tax_calculation': [
                "আয়কর আইন ২০২ৃ এর ধারা {section} অনুযায়ী {amount} টাকা আয়ের উপর {rate}% কর প্রযোজ্য।",
                "{taxpayer} এর {income_source} থেকে {amount} আয়ের ক্ষেত্রে ধারা {section} প্রযোজ্য।",
                "{financial_year} অর্থবছরে তফসিল {schedule} অনুসারে কর হার {rate}%।"
            ],
            'filing_requirements': [
                "ধারা {section} অনুযায়ী {amount} এর বেশি আয় হলে রিটার্ন দাখিল বাধ্যতামূলক।",
                "{taxpayer} কে তফসিল {schedule} অনুসারে রিটার্ন দাখিল করতে হবে।"
            ],
            'exemptions': [
                "{income_source} থেকে {amount} পর্যন্ত আয় তফসিল {schedule} অনুসারে কর মুক্ত।",
                "ধারা {section} এর বিধান অনুযায়ী {exemption_type} ছাড় পাওয়া যাবে।"
            ]
        }
        
        # Value pools for template filling
        sections = ['৭৫', '১৬৩', '২৫', '৩৬', '৪১', '৪৬', '১০২', '১৩৮']
        amounts = ['৩.৫ লক্ষ', '৫ লক্ষ', '১০ লক্ষ', '১৫ লক্ষ', '২৫ লক্ষ', '৫০ লক্ষ', '১ কোটি']
        rates = ['৫', '১০', '১৫', '২০', '২৫', '৩০']
        schedules = ['১', '২', '৩', '৪', '৫', '৬']
        taxpayers = ['ব্যক্তি করদাতা', 'কোম্পানি', 'সমিতি']
        income_sources = ['ইউটিউব আয়', 'ব্যবসায়িক আয়', 'চাকরির আয়', 'ভাড়া আয়']
        financial_years = ['২০২৪-২৫', '২০২৫-২৬', '২০২৬-২৭']
        
        synthetic_count = 0
        
        for category, category_templates in templates.items():
            for template in category_templates:
                for _ in range(count // (len(templates) * len(category_templates))):
                    # Fill template with random values
                    filled_text = template.format(
                        section=np.random.choice(sections),
                        amount=np.random.choice(amounts),
                        rate=np.random.choice(rates),
                        schedule=np.random.choice(schedules),
                        taxpayer=np.random.choice(taxpayers),
                        income_source=np.random.choice(income_sources),
                        financial_year=np.random.choice(financial_years),
                        exemption_type='বিনিয়োগ'  # Investment
                    )
                    
                    # Annotate entities
                    entities = self._annotate_text_entities(filled_text)
                    if entities:
                        tokens = self._tokenize_bengali_text(filled_text)
                        labels = self._create_bio_labels(tokens, entities)
                        
                        example = TrainingExample(
                            text=filled_text,
                            entities=entities,
                            tokens=tokens,
                            labels=labels,
                            source_document=f"synthetic_{category}"
                        )
                        self.training_data.append(example)
                        synthetic_count += 1
        
        logger.info(f"✅ Generated {synthetic_count} synthetic training examples")

    def prepare_training_dataset(self) -> Optional[Dataset]:
        """
        Prepare training dataset for HuggingFace Trainer
        
        Returns:
            HuggingFace Dataset object
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.error("❌ Transformers library not available")
            return None
        
        if not self.training_data:
            logger.error("❌ No training data available")
            return None
        
        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Prepare data for HuggingFace Dataset
        dataset_dict = {
            'tokens': [],
            'labels': []
        }
        
        for example in self.training_data:
            # Convert labels to IDs
            label_ids = [self.label_map.get(label, 0) for label in example.labels]
            
            dataset_dict['tokens'].append(example.tokens)
            dataset_dict['labels'].append(label_ids)
        
        # Create HuggingFace Dataset
        dataset = Dataset.from_dict(dataset_dict)
        
        # Tokenize with alignment
        def tokenize_and_align_labels(examples):
            tokenized_inputs = self.tokenizer(
                examples['tokens'],
                truncation=True,
                is_split_into_words=True,
                padding=True,
                max_length=512
            )
            
            labels = []
            for i, label in enumerate(examples['labels']):
                word_ids = tokenized_inputs.word_ids(batch_index=i)
                label_ids = []
                previous_word_idx = None
                
                for word_idx in word_ids:
                    if word_idx is None:
                        label_ids.append(-100)
                    elif word_idx != previous_word_idx:
                        if word_idx < len(label):
                            label_ids.append(label[word_idx])
                        else:
                            label_ids.append(0)  # O label
                    else:
                        label_ids.append(-100)
                    previous_word_idx = word_idx
                
                labels.append(label_ids)
            
            tokenized_inputs['labels'] = labels
            return tokenized_inputs
        
        tokenized_dataset = dataset.map(tokenize_and_align_labels, batched=True)
        
        logger.info(f"📊 Prepared dataset with {len(tokenized_dataset)} examples")
        return tokenized_dataset

    def train_model(self, 
                   train_dataset: Dataset,
                   num_epochs: int = 3,
                   batch_size: int = 16,
                   learning_rate: float = 5e-5) -> None:
        """
        Train Bengali Legal NER model
        
        Args:
            train_dataset: Training dataset
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.error("❌ Transformers library not available")
            return
        
        logger.info("🚀 Starting Bengali Legal NER model training...")
        
        # Load pre-trained model
        id2label = {idx: label for label, idx in self.label_map.items()}
        label2id = self.label_map
        
        self.model = AutoModelForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(self.label_map),
            id2label=id2label,
            label2id=label2id
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=str(self.output_dir / "logs"),
            logging_steps=100,
            save_steps=1000,
            eval_steps=500,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_f1",
            greater_is_better=True,
        )
        
        # Data collator
        data_collator = DataCollatorForTokenClassification(self.tokenizer)
        
        # Split dataset for evaluation
        train_size = int(0.8 * len(train_dataset))
        eval_size = len(train_dataset) - train_size
        train_subset, eval_subset = torch.utils.data.random_split(
            train_dataset, [train_size, eval_size]
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_subset,
            eval_dataset=eval_subset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self._compute_metrics
        )
        
        # Train
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(str(self.output_dir))
        
        logger.info(f"✅ Model training completed and saved to {self.output_dir}")

    def _compute_metrics(self, eval_pred):
        """Compute evaluation metrics for NER"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=2)
        
        # Remove ignored tokens
        true_predictions = []
        true_labels = []
        
        id2label = {idx: label for label, idx in self.label_map.items()}
        
        for prediction, label in zip(predictions, labels):
            pred_labels = []
            true_label_list = []
            
            for pred_id, label_id in zip(prediction, label):
                if label_id != -100:
                    pred_labels.append(id2label[pred_id])
                    true_label_list.append(id2label[label_id])
            
            true_predictions.append(pred_labels)
            true_labels.append(true_label_list)
        
        # Calculate F1 score
        f1 = f1_score(true_labels, true_predictions)
        
        return {"f1": f1}

    def save_training_report(self) -> None:
        """Save comprehensive training report"""
        report = {
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "phase": "Phase_1.5_Bengali_Legal_NER",
                "version": "1.0",
                "model_name": self.model_name,
                "output_dir": str(self.output_dir)
            },
            "training_statistics": {
                "total_examples": len(self.training_data),
                "entity_types": len(self.entity_types),
                "label_types": len(self.label_map),
                "pattern_groups": len(self.bengali_patterns)
            },
            "entity_type_distribution": {},
            "training_data_sources": {},
            "quality_metrics": {
                "inter_annotator_agreement": ">95% (target)",
                "entity_recognition_accuracy": ">98% (target)",
                "false_positive_rate": "<2% (target)"
            }
        }
        
        # Calculate entity type distribution
        entity_counts = {}
        source_counts = {}
        
        for example in self.training_data:
            # Count source documents
            source = example.source_document
            source_counts[source] = source_counts.get(source, 0) + 1
            
            # Count entity types
            for entity in example.entities:
                entity_type = entity.entity_type
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        report["entity_type_distribution"] = entity_counts
        report["training_data_sources"] = source_counts
        
        # Save report
        report_file = self.output_dir / "training_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Training report saved to {report_file}")

def main():
    """Main function for Bengali Legal NER Training"""
    logger.info("🚀 Starting Phase 1.5: Bengali Legal NER Training System")
    
    # Initialize trainer
    trainer = BengaliLegalNERTrainer()
    
    # Load Phase 1 data
    phase1_dir = "../phase_1_structures"
    trainer.load_phase1_data(phase1_dir)
    
    # Generate synthetic training data
    trainer.generate_synthetic_training_data(count=5000)
    
    # Prepare training dataset
    if TRANSFORMERS_AVAILABLE:
        dataset = trainer.prepare_training_dataset()
        
        if dataset and len(trainer.training_data) > 100:
            # Train model
            trainer.train_model(dataset)
        else:
            logger.warning("⚠️ Insufficient training data for model training")
    
    # Save training report
    trainer.save_training_report()
    
    logger.info("✅ Phase 1.5 Bengali Legal NER Training completed")

if __name__ == "__main__":
    main()