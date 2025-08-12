#!/usr/bin/env python3
"""
Legal Domain Embeddings - Phase 3.1 Implementation
=================================================

Fine-tuned embedding system for Bangladesh tax law semantic understanding.
Creates specialized embeddings for legal concepts, procedures, and numerical contexts
optimized for 8GB RAM inference with Qwen3-Embedding-0.6B.

Integrates with Phase 2 Knowledge Graph and Phase 2.5 Temporal Control.

Author: Phase 3 Implementation  
Date: August 10, 2025
"""

import json
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, date
from pathlib import Path
import sys
import re
import pickle
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib

# Import Phase 2 and Phase 2.5 components for integration
sys.path.append(str(Path(__file__).parent.parent / "phase_2_knowledge_graph"))
sys.path.append(str(Path(__file__).parent.parent / "phase_2_5_temporal_control"))

from phase_2_integration import Phase2IntegratedSystem
from phase_2_5_integration import Phase25IntegratedSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LegalConcept:
    """Structured legal concept for embedding training"""
    concept_id: str
    bengali_terms: List[str]
    english_terms: List[str]
    concept_type: str  # legal, procedural, numerical
    legal_domain: str  # income_tax, vat_customs, general
    definition_bengali: str
    definition_english: str
    related_sections: List[str]
    example_contexts: List[str]
    embedding_vector: Optional[np.ndarray] = None
    confidence_score: float = 0.0

@dataclass
class EmbeddingCorpus:
    """Training corpus for legal domain embeddings"""
    legal_concepts: List[LegalConcept]
    procedural_terms: List[LegalConcept] 
    numerical_contexts: List[LegalConcept]
    document_texts: Dict[str, str]
    query_examples: List[str]
    metadata: Dict[str, Any]

class MockEmbeddingModel:
    """Mock embedding model for development (replace with actual Qwen3-Embedding-0.6B)"""
    
    def __init__(self, model_dimension: int = 768):
        self.model_dimension = model_dimension
        self.is_trained = False
        
    def encode(self, texts: List[str]) -> np.ndarray:
        """Generate mock embeddings based on text hash for consistency"""
        embeddings = []
        for text in texts:
            # Create deterministic "embedding" based on text hash
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            # Convert hash to vector
            hash_int = int(text_hash, 16)
            np.random.seed(hash_int % (2**32))  # Ensure reproducibility
            embedding = np.random.normal(0, 1, self.model_dimension)
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
        return np.array(embeddings)
    
    def fine_tune(self, training_data: List[Tuple[str, str]], epochs: int = 3):
        """Mock fine-tuning process"""
        logger.info(f"Mock fine-tuning on {len(training_data)} pairs for {epochs} epochs")
        self.is_trained = True
        return {"loss": 0.15, "validation_accuracy": 0.92}

class LegalDomainEmbeddings:
    """
    Legal Domain Embeddings System for Bangladesh Tax Law
    
    Features:
    - Fine-tuned Qwen3-Embedding-0.6B for legal domain
    - Specialized embeddings for legal concepts, procedures, numerical contexts
    - Bengali-English bilingual support
    - Integration with Phase 2 Knowledge Graph
    - Integration with Phase 2.5 Temporal Control
    - 8GB RAM optimized inference
    """
    
    def __init__(self, phase2_system: Optional[Phase2IntegratedSystem] = None,
                 phase25_system: Optional[Phase25IntegratedSystem] = None):
        """Initialize legal domain embeddings system"""
        
        # Initialize embedding model (mock for development)
        self.embedding_model = MockEmbeddingModel(model_dimension=768)
        
        # Integration with previous phases
        self.phase2_system = phase2_system
        self.phase25_system = phase25_system
        
        # Embedding corpus and training data
        self.legal_corpus = None
        self.concept_embeddings = {}
        self.document_embeddings = {}
        
        # Model metadata
        self.model_metadata = {
            'version': '3.1.0',
            'model_type': 'qwen3_embedding_0.6b_legal_finetuned',
            'dimension': 768,
            'languages': ['bengali', 'english'],
            'domains': ['income_tax', 'vat_customs', 'legal_procedures'],
            'optimization': '8gb_ram_inference'
        }
        
        # Initialize legal concept taxonomy
        self._initialize_legal_taxonomy()
        
        logger.info("Legal Domain Embeddings system initialized")
    
    def _initialize_legal_taxonomy(self):
        """Initialize comprehensive legal concept taxonomy"""
        
        self.legal_taxonomy = {
            'legal_concepts': {
                'tax_types': {
                    'bengali': ['আয়কর', 'মূল্য সংযোজন কর', 'সম্পূরক শুল্ক', 'উৎসে কর কর্তন'],
                    'english': ['income_tax', 'value_added_tax', 'supplementary_duty', 'tax_deduction_at_source'],
                    'domain': 'tax_classification'
                },
                'income_sources': {
                    'bengali': ['বেতন', 'ব্যবসায়িক আয়', 'পেশাগত আয়', 'সম্পত্তি আয়', 'পুঁজি লাভ'],
                    'english': ['salary', 'business_income', 'professional_income', 'property_income', 'capital_gains'],
                    'domain': 'income_classification'
                },
                'exemptions': {
                    'bengali': ['করমুক্ত', 'ছাড়', 'অব্যাহতি', 'বিশেষ সুবিধা'],
                    'english': ['tax_free', 'exemption', 'relief', 'special_benefit'],
                    'domain': 'tax_benefits'
                }
            },
            'procedural_terms': {
                'filing_procedures': {
                    'bengali': ['রিটার্ন দাখিল', 'নিবন্ধন', 'আবেদন', 'প্রত্যয়ন'],
                    'english': ['return_filing', 'registration', 'application', 'certification'],
                    'domain': 'compliance_procedures'
                },
                'assessment_procedures': {
                    'bengali': ['মূল্যায়ন', 'পরিদর্শন', 'তদন্ত', 'নিরীক্ষা'],
                    'english': ['assessment', 'inspection', 'investigation', 'audit'],
                    'domain': 'enforcement_procedures'
                },
                'appeal_procedures': {
                    'bengali': ['আপিল', 'পুনর্বিবেচনা', 'অভিযোগ', 'সংশোধন'],
                    'english': ['appeal', 'revision', 'complaint', 'rectification'],
                    'domain': 'dispute_resolution'
                }
            },
            'numerical_contexts': {
                'tax_rates': {
                    'patterns': [r'(\d+(?:\.\d+)?)\s*%', r'(\d+(?:\.\d+)?)\s*শতাংশ'],
                    'contexts': ['কর হার', 'tax rate', 'percentage', 'শতাংশ'],
                    'domain': 'rate_calculations'
                },
                'amounts': {
                    'patterns': [r'(\d+(?:,\d+)*)\s*টাকা', r'(\d+(?:,\d+)*)\s*taka', r'(\d+(?:\.\d+)?)\s*লক্ষ', r'(\d+(?:\.\d+)?)\s*কোটি'],
                    'contexts': ['পরিমাণ', 'amount', 'limit', 'সীমা'],
                    'domain': 'monetary_values'
                },
                'dates': {
                    'patterns': [r'(\d{4})-(\d{2})', r'(\d{1,2})/(\d{1,2})/(\d{4})', r'(\d{4})\s*সাল'],
                    'contexts': ['তারিখ', 'date', 'deadline', 'সময়সীমা'],
                    'domain': 'temporal_references'
                }
            }
        }
    
    def build_training_corpus(self, legal_documents_path: str = None) -> EmbeddingCorpus:
        """
        Build comprehensive training corpus from legal documents
        
        Args:
            legal_documents_path: Path to legal documents directory
            
        Returns:
            Structured embedding corpus for training
        """
        logger.info("Building legal domain training corpus")
        
        # Initialize corpus components
        legal_concepts = []
        procedural_terms = []
        numerical_contexts = []
        document_texts = {}
        query_examples = []
        
        # Build legal concepts from taxonomy
        concept_id = 0
        for category, subcategories in self.legal_taxonomy.items():
            for subcategory, terms_data in subcategories.items():
                if isinstance(terms_data, dict) and 'bengali' in terms_data:
                    concept = LegalConcept(
                        concept_id=f"{category}_{subcategory}_{concept_id:04d}",
                        bengali_terms=terms_data['bengali'],
                        english_terms=terms_data.get('english', []),
                        concept_type=category,
                        legal_domain=terms_data.get('domain', 'general'),
                        definition_bengali=f"{subcategory} সংক্রান্ত আইনি ধারণা",
                        definition_english=f"Legal concept related to {subcategory}",
                        related_sections=[],
                        example_contexts=[]
                    )
                    
                    if category == 'legal_concepts':
                        legal_concepts.append(concept)
                    elif category == 'procedural_terms':
                        procedural_terms.append(concept)
                    elif category == 'numerical_contexts':
                        numerical_contexts.append(concept)
                    
                    concept_id += 1
        
        # Build document texts from Phase 2/2.5 integration
        if self.phase2_system:
            logger.info("Integrating Phase 2 knowledge graph data")
            # Extract key document content
            document_texts['phase2_entities'] = "Legal entities and relationships from Phase 2"
            
        if self.phase25_system:
            logger.info("Integrating Phase 2.5 temporal data")
            # Extract temporal law versions
            temporal_data = self.phase25_system.temporal_manager.law_versions
            for version_key, version_data in temporal_data.items():
                document_texts[f"temporal_{version_key}"] = f"Law version: {version_data.version_id}"
        
        # Generate example queries for training
        query_examples = [
            "২০২৫ অর্থবছরে ইউটিউব আয়ের কর হার কত?",
            "ধারা ৭৫ অনুযায়ী রিটার্ন দাখিলের সময়সীমা কী?",
            "What is the tax-free income limit for individual taxpayers?",
            "Section 163 এ minimum tax সম্পর্কে কী বলা আছে?",
            "TDS rules 2024 according to which provision?",
            "করমুক্ত সীমা ৪ লক্ষ টাকা কোন আইনে আছে?",
            "Business income and professional income difference",
            "চতুর্থ তফসিলে কোন কোন ছাড় দেওয়া আছে?"
        ]
        
        # Create corpus metadata
        corpus_metadata = {
            'created_date': datetime.now().isoformat(),
            'total_concepts': len(legal_concepts) + len(procedural_terms) + len(numerical_contexts),
            'total_documents': len(document_texts),
            'total_queries': len(query_examples),
            'phase2_integration': bool(self.phase2_system),
            'phase25_integration': bool(self.phase25_system),
            'language_coverage': ['bengali', 'english'],
            'domain_coverage': list(set(concept.legal_domain for concept in legal_concepts))
        }
        
        # Build final corpus
        legal_corpus = EmbeddingCorpus(
            legal_concepts=legal_concepts,
            procedural_terms=procedural_terms,
            numerical_contexts=numerical_contexts,
            document_texts=document_texts,
            query_examples=query_examples,
            metadata=corpus_metadata
        )
        
        self.legal_corpus = legal_corpus
        
        logger.info(f"Training corpus built: {len(legal_concepts)} legal concepts, " +
                   f"{len(procedural_terms)} procedural terms, {len(numerical_contexts)} numerical contexts")
        
        return legal_corpus
    
    def fine_tune_embeddings(self, corpus: EmbeddingCorpus = None, epochs: int = 3) -> Dict[str, Any]:
        """
        Fine-tune embedding model on Bangladesh legal corpus
        
        Args:
            corpus: Training corpus (uses self.legal_corpus if None)
            epochs: Number of training epochs
            
        Returns:
            Training results and metrics
        """
        if corpus is None:
            corpus = self.legal_corpus
        
        if corpus is None:
            raise ValueError("No training corpus available. Call build_training_corpus() first.")
        
        logger.info(f"Fine-tuning embedding model on legal corpus (epochs: {epochs})")
        
        # Prepare training data
        training_pairs = []
        
        # Create positive pairs from legal concepts
        all_concepts = corpus.legal_concepts + corpus.procedural_terms + corpus.numerical_contexts
        
        for concept in all_concepts:
            # Bengali-English term pairs (positive similarity)
            for bengali_term in concept.bengali_terms:
                for english_term in concept.english_terms:
                    training_pairs.append((bengali_term, english_term))
            
            # Same-concept term pairs (high similarity)
            for i, term1 in enumerate(concept.bengali_terms + concept.english_terms):
                for term2 in (concept.bengali_terms + concept.english_terms)[i+1:]:
                    training_pairs.append((term1, term2))
        
        # Add query-concept pairs
        for query in corpus.query_examples:
            # Match query with relevant concepts (simplified matching for mock)
            for concept in all_concepts[:10]:  # Limit for mock
                if any(term in query.lower() for term in concept.bengali_terms + concept.english_terms):
                    training_pairs.append((query, concept.definition_bengali))
                    training_pairs.append((query, concept.definition_english))
        
        # Fine-tune model (mock process)
        training_results = self.embedding_model.fine_tune(training_pairs, epochs)
        
        # Generate embeddings for all concepts after training
        self._generate_concept_embeddings(all_concepts)
        
        # Training metrics
        training_metrics = {
            'model_version': self.model_metadata['version'],
            'training_pairs': len(training_pairs),
            'epochs': epochs,
            'concepts_processed': len(all_concepts),
            'fine_tuning_results': training_results,
            'embedding_dimension': self.model_metadata['dimension'],
            'optimization_target': '8gb_ram_inference',
            'training_date': datetime.now().isoformat()
        }
        
        logger.info(f"Fine-tuning complete: {len(training_pairs)} training pairs, " +
                   f"{len(all_concepts)} concept embeddings generated")
        
        return training_metrics
    
    def _generate_concept_embeddings(self, concepts: List[LegalConcept]):
        """Generate embeddings for all legal concepts"""
        
        # Prepare texts for embedding
        concept_texts = []
        concept_ids = []
        
        for concept in concepts:
            # Create comprehensive text representation
            full_text = " ".join([
                " ".join(concept.bengali_terms),
                " ".join(concept.english_terms), 
                concept.definition_bengali,
                concept.definition_english
            ])
            concept_texts.append(full_text)
            concept_ids.append(concept.concept_id)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(concept_texts)
        
        # Store embeddings
        for i, concept in enumerate(concepts):
            concept.embedding_vector = embeddings[i]
            concept.confidence_score = 0.85  # Mock confidence
            self.concept_embeddings[concept.concept_id] = concept
    
    def semantic_search(self, query: str, top_k: int = 10, similarity_threshold: float = 0.7) -> List[Tuple[LegalConcept, float]]:
        """
        Perform semantic search for legal concepts
        
        Args:
            query: Search query in Bengali/English
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of (concept, similarity_score) tuples
        """
        if not self.concept_embeddings:
            logger.warning("No concept embeddings available. Run fine_tune_embeddings() first.")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Calculate similarities
        similarities = []
        for concept_id, concept in self.concept_embeddings.items():
            if concept.embedding_vector is not None:
                similarity = np.dot(query_embedding, concept.embedding_vector)
                if similarity >= similarity_threshold:
                    similarities.append((concept, float(similarity)))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Semantic search for '{query[:30]}...': {len(similarities)} matches found")
        
        return similarities[:top_k]
    
    def get_concept_by_terms(self, terms: List[str]) -> List[LegalConcept]:
        """Find legal concepts matching specific terms"""
        
        matching_concepts = []
        for concept in self.concept_embeddings.values():
            all_terms = concept.bengali_terms + concept.english_terms
            if any(term.lower() in [t.lower() for t in all_terms] for term in terms):
                matching_concepts.append(concept)
        
        return matching_concepts
    
    def enhance_with_temporal_context(self, query: str, financial_year: str = None) -> Dict[str, Any]:
        """
        Enhance semantic search with temporal context from Phase 2.5
        
        Args:
            query: Legal query
            financial_year: Target financial year (e.g., "2025-26")
            
        Returns:
            Enhanced search results with temporal context
        """
        if not self.phase25_system:
            logger.warning("Phase 2.5 system not available for temporal enhancement")
            return {"semantic_results": self.semantic_search(query)}
        
        logger.info(f"Enhancing semantic search with temporal context: FY {financial_year}")
        
        # Get temporal analysis from Phase 2.5
        temporal_result = self.phase25_system.process_temporal_query(query)
        
        # Get semantic search results
        semantic_results = self.semantic_search(query)
        
        # Combine temporal and semantic intelligence
        enhanced_results = {
            "query": query,
            "temporal_context": {
                "financial_year": temporal_result["applicable_law"]["financial_year"],
                "law_version": temporal_result["applicable_law"]["version_id"],
                "temporal_confidence": temporal_result["temporal_analysis"]["temporal_confidence"]
            },
            "semantic_results": [
                {
                    "concept": asdict(concept),
                    "similarity_score": score,
                    "temporal_relevance": self._assess_temporal_relevance(concept, temporal_result)
                }
                for concept, score in semantic_results
            ],
            "section_unification": temporal_result["section_unification"],
            "integration_confidence": min(
                temporal_result["temporal_analysis"]["temporal_confidence"],
                max([score for _, score in semantic_results]) if semantic_results else 0.0
            )
        }
        
        return enhanced_results
    
    def _assess_temporal_relevance(self, concept: LegalConcept, temporal_result: Dict) -> float:
        """Assess temporal relevance of concept to query result"""
        
        # Mock temporal relevance assessment
        financial_year = temporal_result["applicable_law"]["financial_year"]
        
        # Higher relevance for concepts related to current financial year
        if financial_year in ["2025-26"]:
            if concept.legal_domain in ["income_tax", "tax_classification"]:
                return 0.9
        
        return 0.7  # Default relevance
    
    def export_embeddings(self, output_path: str):
        """Export trained embeddings and model data"""
        
        export_data = {
            "model_metadata": self.model_metadata,
            "legal_taxonomy": self.legal_taxonomy,
            "concept_embeddings": {
                concept_id: {
                    "concept_data": asdict(concept),
                    "embedding_vector": concept.embedding_vector.tolist() if concept.embedding_vector is not None else None
                }
                for concept_id, concept in self.concept_embeddings.items()
            },
            "corpus_metadata": asdict(self.legal_corpus.metadata) if self.legal_corpus else {},
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Save as JSON (for readability) and pickle (for embeddings)
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # JSON export
        with open(output_path / "legal_embeddings.json", 'w', encoding='utf-8') as f:
            # Convert numpy arrays to lists for JSON serialization
            json_data = json.loads(json.dumps(export_data, default=str, ensure_ascii=False))
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # Pickle export for embeddings
        embeddings_only = {
            concept_id: concept.embedding_vector 
            for concept_id, concept in self.concept_embeddings.items()
            if concept.embedding_vector is not None
        }
        
        with open(output_path / "embeddings_vectors.pkl", 'wb') as f:
            pickle.dump(embeddings_only, f)
        
        logger.info(f"Legal embeddings exported to {output_path}")
    
    def generate_embedding_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive statistics about the embedding system"""
        
        stats = {
            "system_overview": {
                "model_version": self.model_metadata['version'],
                "total_concepts": len(self.concept_embeddings),
                "embedding_dimension": self.model_metadata['dimension'],
                "supported_languages": self.model_metadata['languages'],
                "legal_domains": self.model_metadata['domains']
            },
            "concept_distribution": {
                "by_type": defaultdict(int),
                "by_domain": defaultdict(int),
                "by_language": {"bengali": 0, "english": 0, "bilingual": 0}
            },
            "embedding_quality": {
                "concepts_with_embeddings": 0,
                "average_confidence": 0.0,
                "embedding_coverage": 0.0
            },
            "integration_status": {
                "phase2_connected": bool(self.phase2_system),
                "phase25_connected": bool(self.phase25_system),
                "corpus_available": bool(self.legal_corpus)
            }
        }
        
        # Calculate distributions
        for concept in self.concept_embeddings.values():
            stats["concept_distribution"]["by_type"][concept.concept_type] += 1
            stats["concept_distribution"]["by_domain"][concept.legal_domain] += 1
            
            if concept.embedding_vector is not None:
                stats["embedding_quality"]["concepts_with_embeddings"] += 1
            
            # Language analysis
            has_bengali = bool(concept.bengali_terms)
            has_english = bool(concept.english_terms)
            if has_bengali and has_english:
                stats["concept_distribution"]["by_language"]["bilingual"] += 1
            elif has_bengali:
                stats["concept_distribution"]["by_language"]["bengali"] += 1
            elif has_english:
                stats["concept_distribution"]["by_language"]["english"] += 1
        
        # Calculate quality metrics
        if self.concept_embeddings:
            confidence_scores = [c.confidence_score for c in self.concept_embeddings.values()]
            stats["embedding_quality"]["average_confidence"] = sum(confidence_scores) / len(confidence_scores)
            stats["embedding_quality"]["embedding_coverage"] = (
                stats["embedding_quality"]["concepts_with_embeddings"] / len(self.concept_embeddings)
            )
        
        return dict(stats)

def main():
    """Test the Legal Domain Embeddings system"""
    
    # Initialize Phase 2.5 system for integration
    from temporal_law_manager import TemporalLawManager
    from legal_change_tracker import LegalChangeTracker
    from section_unification_system import SectionUnificationSystem
    
    phase25_system = Phase25IntegratedSystem()
    
    # Initialize embeddings system
    embeddings_system = LegalDomainEmbeddings(phase25_system=phase25_system)
    
    print("🧠 Legal Domain Embeddings System Test")
    print("=" * 50)
    
    # Build training corpus
    print("\n📚 Building Training Corpus:")
    print("-" * 30)
    
    corpus = embeddings_system.build_training_corpus()
    
    print(f"Legal Concepts: {len(corpus.legal_concepts)}")
    print(f"Procedural Terms: {len(corpus.procedural_terms)}")
    print(f"Numerical Contexts: {len(corpus.numerical_contexts)}")
    print(f"Example Queries: {len(corpus.query_examples)}")
    
    # Fine-tune embeddings
    print("\n🎯 Fine-tuning Embeddings:")
    print("-" * 28)
    
    training_results = embeddings_system.fine_tune_embeddings(epochs=3)
    
    print(f"Training Pairs: {training_results['training_pairs']}")
    print(f"Concepts Processed: {training_results['concepts_processed']}")
    print(f"Model Dimension: {training_results['embedding_dimension']}")
    
    # Test semantic search
    print("\n🔍 Testing Semantic Search:")
    print("-" * 29)
    
    test_queries = [
        "ইউটিউব আয়",
        "রিটার্ন দাখিল",
        "tax exemption",
        "minimum tax",
        "আয়কর"
    ]
    
    for query in test_queries:
        results = embeddings_system.semantic_search(query, top_k=3)
        print(f"\nQuery: '{query}'")
        for i, (concept, score) in enumerate(results, 1):
            print(f"  {i}. {concept.concept_id} (similarity: {score:.3f})")
            print(f"     Bengali: {', '.join(concept.bengali_terms[:2])}")
            print(f"     English: {', '.join(concept.english_terms[:2])}")
    
    # Test temporal enhancement
    print("\n⏰ Testing Temporal Enhancement:")
    print("-" * 32)
    
    enhanced_result = embeddings_system.enhance_with_temporal_context(
        "২০২৫ অর্থবছরে ইউটিউব আয়ের কর হার", 
        financial_year="2025-26"
    )
    
    print(f"Query: {enhanced_result['query']}")
    print(f"Financial Year: {enhanced_result['temporal_context']['financial_year']}")
    print(f"Law Version: {enhanced_result['temporal_context']['law_version']}")
    print(f"Integration Confidence: {enhanced_result['integration_confidence']:.3f}")
    print(f"Semantic Results: {len(enhanced_result['semantic_results'])}")
    
    # Generate statistics
    print("\n📊 System Statistics:")
    print("-" * 20)
    
    stats = embeddings_system.generate_embedding_statistics()
    
    print(f"Total Concepts: {stats['system_overview']['total_concepts']}")
    print(f"Embedding Coverage: {stats['embedding_quality']['embedding_coverage']:.1%}")
    print(f"Average Confidence: {stats['embedding_quality']['average_confidence']:.3f}")
    print(f"Phase 2.5 Integration: {stats['integration_status']['phase25_connected']}")
    print(f"Concept Types: {dict(stats['concept_distribution']['by_type'])}")
    
    # Export embeddings
    output_path = Path(__file__).parent / "embeddings_export"
    embeddings_system.export_embeddings(str(output_path))
    print(f"\n✅ Embeddings exported to: {output_path}")

if __name__ == "__main__":
    main()