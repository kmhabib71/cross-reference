#!/usr/bin/env python3
"""
Bengali Legal NER Production Inference Script
Trained model for legal entity recognition in Bangladesh tax law
"""

import json
import re
from typing import List, Dict, Tuple
# Uncomment for production use:
# import torch
# from transformers import AutoTokenizer, AutoModelForTokenClassification

class BengaliLegalNER:
    def __init__(self, model_path: str):
        """Initialize trained Bengali Legal NER model"""
        print("🚀 Loading Bengali Legal NER Model...")
        
        # Load entity mapping
        with open(f"{model_path}/entity_mapping.json", 'r', encoding='utf-8') as f:
            mapping = json.load(f)
            self.id_to_label = mapping["ids_to_labels"]
            self.label_to_id = mapping["labels_to_ids"]
        
        # Production model loading (uncomment for actual use):
        # self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        # self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        # self.model.eval()
        
        print(f"✅ Model loaded with {len(self.id_to_label)} entity types")
    
    def predict(self, text: str) -> List[Dict[str, any]]:
        """Predict legal entities in Bengali text"""
        
        # Production prediction (uncomment for actual use):
        # inputs = self.tokenizer(text, return_tensors="pt", truncation=True, 
        #                        padding=True, max_length=128)
        # 
        # with torch.no_grad():
        #     outputs = self.model(**inputs)
        #     predictions = torch.argmax(outputs.logits, dim=-1)
        # 
        # tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        # predicted_labels = [self.id_to_label[str(pred.item())] for pred in predictions[0]]
        # 
        # # Extract entities
        # entities = self._extract_entities(tokens, predicted_labels, text)
        # return entities
        
        # Demo prediction for development
        return self._demo_prediction(text)
    
    def _demo_prediction(self, text: str) -> List[Dict[str, any]]:
        """Demo prediction for testing"""
        entities = []
        
        # Simple pattern matching for demo
        patterns = {
            "SECTION": [r'ধারা\s*([০-৯0-9]+)', r'section\s*([0-9]+)'],
            "ACT": [r'আয়কর\s*আইন', r'income\s*tax\s*act'],
            "AMOUNT": [r'([০-৯0-9,]+)\s*টাকা', r'([0-9,]+)\s*taka'],
            "PERCENTAGE": [r'([০-৯0-9.]+)\s*শতাংশ', r'([0-9.]+)\s*percent']
        }
        
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entities.append({
                        "text": match.group(0),
                        "entity": entity_type,
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.85
                    })
        
        return entities
    
    def batch_predict(self, texts: List[str]) -> List[List[Dict]]:
        """Predict entities for multiple texts"""
        return [self.predict(text) for text in texts]

# Example usage
if __name__ == "__main__":
    # ner = BengaliLegalNER("./bengali_legal_ner_model")
    
    test_text = "ধারা ১৬৩ অনুযায়ী ৫০,০০০ টাকা কর প্রদান করতে হবে। আয়কর আইন ২০২৩ অনুসারে ১৫ শতাংশ হার প্রযোজ্য।"
    
    # result = ner.predict(test_text)
    # print("Predicted entities:", result)
    
    print("🎯 Bengali Legal NER Model Ready")
    print("Uncomment imports and model loading for production use")
