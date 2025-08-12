#!/usr/bin/env python3
"""
Smart Document Chunker for Bengali Legal NER
Phase 1.5C: Intelligent chunking of legal documents for optimal NER training
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartDocumentChunker:
    def __init__(self, training_data_file: str, output_dir: str):
        self.training_data_file = Path(training_data_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Chunking parameters optimized for NER training
        self.optimal_chunk_size = 128  # tokens for BERT-based models
        self.min_chunk_size = 32       # minimum viable chunk
        self.max_chunk_size = 256      # maximum for memory efficiency
        self.overlap_size = 16         # overlap between chunks to preserve context
        
        # Priority section indicators
        self.priority_indicators = {
            "high_priority": [
                "ধারা", "section", "উপধারা", "sub-section",
                "তফসিল", "schedule", "বিধি", "rule"
            ],
            "medium_priority": [
                "অধ্যায়", "chapter", "পরিচ্ছেদ", "part",
                "ব্যাখ্যা", "explanation", "সংজ্ঞা", "definition"
            ],
            "special_entities": [
                "টাকা", "taka", "শতাংশ", "percent",
                "তারিখ", "date", "ফরম", "form"
            ]
        }
    
    def load_training_data(self) -> Dict[str, Any]:
        """Load the training dataset"""
        with open(self.training_data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_priority_score(self, text: str) -> float:
        """Calculate priority score based on legal entity density"""
        score = 0.0
        text_lower = text.lower()
        
        # High priority indicators (legal references)
        for indicator in self.priority_indicators["high_priority"]:
            count = text_lower.count(indicator.lower())
            score += count * 3.0
        
        # Medium priority indicators (structural elements)
        for indicator in self.priority_indicators["medium_priority"]:
            count = text_lower.count(indicator.lower())
            score += count * 2.0
        
        # Special entities (quantitative data)
        for indicator in self.priority_indicators["special_entities"]:
            count = text_lower.count(indicator.lower())
            score += count * 1.5
        
        # Bonus for mixed Bengali-English content
        has_bengali = bool(re.search(r'[\u0980-\u09FF]', text))
        has_english = bool(re.search(r'[a-zA-Z]', text))
        if has_bengali and has_english:
            score += 2.0
        
        # Normalize by text length
        return score / max(len(text.split()), 1)
    
    def detect_sentence_boundaries(self, text: str) -> List[int]:
        """Detect sentence boundaries in Bengali-English mixed text"""
        # Bengali sentence endings
        bengali_endings = r'[।৷]'
        # English sentence endings
        english_endings = r'[.!?]'
        # Combined pattern
        sentence_pattern = f'({bengali_endings}|{english_endings})'
        
        boundaries = [0]
        for match in re.finditer(sentence_pattern, text):
            end_pos = match.end()
            # Skip if it's likely an abbreviation or number
            if not self._is_abbreviation(text, match.start()):
                boundaries.append(end_pos)
        
        if boundaries[-1] != len(text):
            boundaries.append(len(text))
        
        return boundaries
    
    def _is_abbreviation(self, text: str, pos: int) -> bool:
        """Check if the period is part of an abbreviation"""
        # Look for common patterns that indicate abbreviations
        context_before = text[max(0, pos-10):pos]
        context_after = text[pos:min(len(text), pos+10)]
        
        # Check for number patterns
        if re.search(r'\d', context_before) and re.search(r'\d', context_after):
            return True
        
        # Check for common legal abbreviations
        abbrev_patterns = [
            r'[A-Za-z]{1,3}$',  # Short abbreviations
            r'No$', r'সং$',     # Number indicators
        ]
        
        for pattern in abbrev_patterns:
            if re.search(pattern, context_before):
                return True
        
        return False
    
    def create_smart_chunks(self, text: str, source_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create smart chunks optimized for NER training"""
        sentences = self.extract_sentences(text)
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence_info in sentences:
            sentence = sentence_info["text"]
            tokens = sentence.split()
            token_count = len(tokens)
            
            # If adding this sentence exceeds optimal size, finalize current chunk
            if current_tokens + token_count > self.optimal_chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append(self._create_chunk_metadata(chunk_text, source_info))
                
                # Start new chunk with overlap
                if len(current_chunk) > self.overlap_size:
                    current_chunk = current_chunk[-self.overlap_size:]
                    current_tokens = len(" ".join(current_chunk).split())
                else:
                    current_chunk = []
                    current_tokens = 0
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_tokens += token_count
            
            # If chunk becomes too large, force finalization
            if current_tokens > self.max_chunk_size:
                chunk_text = " ".join(current_chunk)
                chunks.append(self._create_chunk_metadata(chunk_text, source_info))
                current_chunk = []
                current_tokens = 0
        
        # Add remaining content as final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text.split()) >= self.min_chunk_size:
                chunks.append(self._create_chunk_metadata(chunk_text, source_info))
        
        return chunks
    
    def extract_sentences(self, text: str) -> List[Dict[str, Any]]:
        """Extract sentences with metadata"""
        boundaries = self.detect_sentence_boundaries(text)
        sentences = []
        
        for i in range(len(boundaries) - 1):
            start = boundaries[i]
            end = boundaries[i + 1]
            sentence_text = text[start:end].strip()
            
            if len(sentence_text) > 10:  # Skip very short sentences
                sentences.append({
                    "text": sentence_text,
                    "start_pos": start,
                    "end_pos": end,
                    "priority_score": self.calculate_priority_score(sentence_text),
                    "token_count": len(sentence_text.split())
                })
        
        return sentences
    
    def _create_chunk_metadata(self, chunk_text: str, source_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for a chunk"""
        return {
            "text": chunk_text,
            "source": source_info.get("source", "unknown"),
            "source_category": self._infer_category_from_source(source_info.get("source", "")),
            "token_count": len(chunk_text.split()),
            "character_count": len(chunk_text),
            "priority_score": self.calculate_priority_score(chunk_text),
            "has_bengali": bool(re.search(r'[\u0980-\u09FF]', chunk_text)),
            "has_english": bool(re.search(r'[a-zA-Z]', chunk_text)),
            "entity_density": self._estimate_entity_density(chunk_text)
        }
    
    def _infer_category_from_source(self, source_name: str) -> str:
        """Infer document category from source filename"""
        source_lower = source_name.lower()
        
        if any(keyword in source_lower for keyword in ["income", "আয়কর"]):
            return "income_tax"
        elif any(keyword in source_lower for keyword in ["vat", "মূল্য"]):
            return "vat"
        elif "schedule" in source_lower or "তফসিল" in source_lower:
            return "schedule"
        elif "rule" in source_lower or "বিধি" in source_lower:
            return "rule"
        elif "circular" in source_lower or "পরিপত্র" in source_lower:
            return "circular"
        else:
            return "general"
    
    def _estimate_entity_density(self, text: str) -> float:
        """Estimate density of legal entities in text"""
        entity_indicators = [
            "ধারা", "section", "তফসিল", "schedule",
            "টাকা", "taka", "শতাংশ", "percent",
            "আইন", "act", "বিধি", "rule"
        ]
        
        entity_count = 0
        for indicator in entity_indicators:
            entity_count += text.lower().count(indicator.lower())
        
        return entity_count / max(len(text.split()), 1)
    
    def create_prioritized_chunks(self, dataset: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Create prioritized chunks from the training dataset"""
        logger.info("🔄 Creating smart chunks for NER training...")
        
        all_chunks = []
        category_chunks = {}
        
        for file_data in dataset["training_files"]:
            file_chunks = []
            
            # Process each line as potential chunk content
            full_text = "\n".join(file_data.get("content_lines", []))
            
            if len(full_text.strip()) > 0:
                chunks = self.create_smart_chunks(full_text, file_data)
                file_chunks.extend(chunks)
                all_chunks.extend(chunks)
                
                # Categorize chunks
                category = self._infer_category_from_source(file_data.get("source", ""))
                if category not in category_chunks:
                    category_chunks[category] = []
                category_chunks[category].extend(chunks)
        
        # Sort chunks by priority score
        all_chunks.sort(key=lambda x: x["priority_score"], reverse=True)
        
        logger.info(f"✅ Created {len(all_chunks)} smart chunks")
        
        return {
            "all_chunks": all_chunks,
            "by_category": category_chunks,
            "statistics": self._calculate_chunk_statistics(all_chunks)
        }
    
    def _calculate_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for the chunks"""
        if not chunks:
            return {}
        
        token_counts = [chunk["token_count"] for chunk in chunks]
        priority_scores = [chunk["priority_score"] for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_tokens_per_chunk": sum(token_counts) / len(token_counts),
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts),
            "avg_priority_score": sum(priority_scores) / len(priority_scores),
            "high_priority_chunks": len([c for c in chunks if c["priority_score"] > 2.0]),
            "bilingual_chunks": len([c for c in chunks if c["has_bengali"] and c["has_english"]]),
            "bengali_only_chunks": len([c for c in chunks if c["has_bengali"] and not c["has_english"]]),
            "english_only_chunks": len([c for c in chunks if c["has_english"] and not c["has_bengali"]])
        }
    
    def create_training_ready_chunks(self, prioritized_chunks: Dict[str, Any], max_chunks: int = 1000) -> List[Dict[str, Any]]:
        """Select top chunks ready for NER annotation"""
        all_chunks = prioritized_chunks["all_chunks"]
        
        # Select top chunks based on priority and diversity
        selected_chunks = []
        category_counts = {}
        
        for chunk in all_chunks:
            if len(selected_chunks) >= max_chunks:
                break
            
            category = chunk["source_category"]
            category_count = category_counts.get(category, 0)
            
            # Ensure diversity across categories (max 40% from any single category)
            max_per_category = max_chunks * 0.4
            
            if category_count < max_per_category and chunk["token_count"] >= self.min_chunk_size:
                selected_chunks.append(chunk)
                category_counts[category] = category_count + 1
        
        return selected_chunks
    
    def export_chunks(self, prioritized_chunks: Dict[str, Any]):
        """Export chunks in multiple formats for NER training"""
        
        # Export complete chunk dataset
        chunks_file = self.output_dir / "smart_chunks_dataset.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(prioritized_chunks, f, ensure_ascii=False, indent=2)
        
        # Export training-ready chunks
        training_chunks = self.create_training_ready_chunks(prioritized_chunks)
        training_file = self.output_dir / "training_ready_chunks.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_chunks, f, ensure_ascii=False, indent=2)
        
        # Export text files for annotation tools
        annotation_file = self.output_dir / "chunks_for_annotation.txt"
        with open(annotation_file, 'w', encoding='utf-8') as f:
            for i, chunk in enumerate(training_chunks[:500]):  # Limit for manual annotation
                f.write(f"CHUNK_{i+1:03d}\n")
                f.write(f"Source: {chunk['source']}\n")
                f.write(f"Priority: {chunk['priority_score']:.2f}\n")
                f.write(f"Tokens: {chunk['token_count']}\n")
                f.write("-" * 50 + "\n")
                f.write(chunk['text'])
                f.write("\n" + "=" * 80 + "\n\n")
        
        return chunks_file, training_file, annotation_file

def main():
    """Create smart chunks for Bengali Legal NER training"""
    training_data_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_5_bengali_legal_ner/training_data/balanced_training_dataset.json"
    output_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_1_5_bengali_legal_ner/chunks"
    
    chunker = SmartDocumentChunker(training_data_file, output_dir)
    
    # Load training data
    dataset = chunker.load_training_data()
    
    # Create prioritized chunks
    prioritized_chunks = chunker.create_prioritized_chunks(dataset)
    
    # Export chunks
    chunks_file, training_file, annotation_file = chunker.export_chunks(prioritized_chunks)
    
    # Print results
    print("🎯 PHASE 1.5C COMPLETED: Smart Document Chunking")
    print(f"Chunks dataset: {chunks_file}")
    print(f"Training ready: {training_file}")
    print(f"Annotation file: {annotation_file}")
    
    stats = prioritized_chunks["statistics"]
    print(f"\n📊 Chunk Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Avg tokens per chunk: {stats['avg_tokens_per_chunk']:.1f}")
    print(f"  High priority chunks: {stats['high_priority_chunks']}")
    print(f"  Bilingual chunks: {stats['bilingual_chunks']}")
    print(f"  Bengali-only chunks: {stats['bengali_only_chunks']}")
    print(f"  English-only chunks: {stats['english_only_chunks']}")

if __name__ == "__main__":
    main()