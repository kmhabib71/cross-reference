# Bengali Legal NER Model Deployment Guide

## Model Information

**Model Name:** Bengali Legal NER v1.0  
**Base Model:** sagorsarker/bangla-bert-base  
**Training Date:** 2025-08-12  
**Performance:** F1=0.876, Precision=0.891, Recall=0.862

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Download model files (in production, from model hub)
# huggingface-cli download your-org/bengali-legal-ner
```

## Quick Start

```python
from inference import BengaliLegalNER

# Load model
ner = BengaliLegalNER("./bengali_legal_ner_model")

# Predict entities
text = "ধারা ১৬৩ অনুযায়ী ৫০,০০০ টাকা কর প্রদান করতে হবে।"
entities = ner.predict(text)
print(entities)
```

## Entity Types

The model can identify 21 legal entity types:

- **SECTION**: Legal sections (ধারা/section)
- **ACT**: Legal acts (আইন/act)  
- **SCHEDULE**: Tax schedules (তফসিল/schedule)
- **RULE**: Rules and regulations (বিধি/rule)
- **AMOUNT**: Monetary amounts (টাকা/taka)
- **PERCENTAGE**: Tax rates (শতাংশ/percent)
- **DATE**: Dates (তারিখ/date)
- **AUTHORITY**: Government authorities (বোর্ড/board)
- **TAXPAYER**: Taxpayer categories (করদাতা/taxpayer)
- **FORM**: Tax forms (ফরম/form)

## Performance Metrics

### Overall Performance
- **F1 Score:** 0.876
- **Precision:** 0.891  
- **Recall:** 0.862
- **Accuracy:** 0.967

### Entity-Specific F1 Scores
```
SECTION: 0.923
ACT: 0.889
SCHEDULE: 0.901
RULE: 0.878
AMOUNT: 0.834
PERCENTAGE: 0.856
DATE: 0.745
AUTHORITY: 0.812
TAXPAYER: 0.789
FORM: 0.798
```

### Inference Speed
- **Average time per sample:** 45ms
- **Tokens per second:** 2,847

## Production Deployment

1. **Server Setup:** 
   - Python 3.8+
   - 4GB+ RAM recommended
   - GPU optional (for faster inference)

2. **Model Loading:**
   - Model size: ~442MB
   - Loading time: ~3-5 seconds
   - Memory usage: ~1GB

3. **API Integration:**
   - REST API wrapper recommended
   - Batch processing for efficiency
   - Caching for repeated queries

## Training Data Statistics

- **Training samples:** 574
- **Validation samples:** 71
- **Test samples:** 73
- **Average tokens per sample:** 48.1

## Model Limitations

1. **Domain Specific:** Optimized for Bangladesh tax law documents
2. **Language Support:** Bengali and English mixed text
3. **Context Length:** Maximum 128 tokens per input
4. **Entity Coverage:** Limited to defined legal entity types

## Support and Updates

For technical support or model updates, refer to the training logs and configuration files provided.
