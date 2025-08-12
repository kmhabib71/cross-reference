#!/usr/bin/env python3
"""
Context-Aware Search System - Phase 3.2 Implementation
=====================================================

Intelligent search combining semantic embeddings, temporal context, and legal hierarchy.
Multi-vector search with context expansion and integration with Phase 2 Knowledge Graph
and Phase 2.5 Temporal Control.

Author: Phase 3 Implementation
Date: August 10, 2025
"""

import json
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union, Set
from datetime import datetime, date
from pathlib import Path
import sys
import re
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from enum import Enum
import itertools

# Import previous phase components
sys.path.append(str(Path(__file__).parent.parent / "phase_2_knowledge_graph"))
sys.path.append(str(Path(__file__).parent.parent / "phase_2_5_temporal_control"))

from phase_2_integration import Phase2IntegratedSystem
from phase_2_5_integration import Phase25IntegratedSystem
from legal_domain_embeddings import LegalDomainEmbeddings, LegalConcept

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchType(Enum):
    """Types of context-aware search"""
    CONCEPT_SEARCH = "concept"          # Search for legal concepts
    PROCEDURAL_SEARCH = "procedural"    # Search for procedures/processes
    NUMERICAL_SEARCH = "numerical"      # Search for rates, amounts, dates
    HYBRID_SEARCH = "hybrid"           # Multi-vector search
    TEMPORAL_SEARCH = "temporal"       # Time-sensitive search

class ContextScope(Enum):
    """Scope of context expansion"""
    NARROW = "narrow"          # Current section only
    RELATED = "related"        # Related sections
    DOCUMENT = "document"      # Entire document
    CROSS_DOCUMENT = "cross"   # Multiple documents

@dataclass 
class SearchQuery:
    """Structured search query with context"""
    original_query: str
    processed_query: str
    query_type: SearchType
    context_scope: ContextScope
    temporal_context: Optional[str] = None
    section_hints: List[str] = None
    domain_filter: Optional[str] = None
    confidence_threshold: float = 0.7
    max_results: int = 10

@dataclass
class SearchResult:
    """Structured search result with context"""
    result_id: str
    content: str
    document_source: str
    section_reference: str
    concept_matches: List[LegalConcept]
    similarity_score: float
    context_relevance: float
    temporal_relevance: float
    legal_precedence: int
    explanation: str
    related_provisions: List[str]
    confidence_score: float

@dataclass
class ContextExpansion:
    """Context expansion data"""
    original_sections: List[str]
    expanded_sections: List[str]
    related_concepts: List[str]
    temporal_versions: List[str]
    cross_references: Dict[str, List[str]]
    expansion_rationale: str

class ContextAwareSearch:
    """
    Context-Aware Search System for Bangladesh Legal Documents
    
    Features:
    - Multi-vector semantic search (concept + procedural + numerical)
    - Context expansion using Phase 2 knowledge graph
    - Temporal context integration from Phase 2.5
    - Legal hierarchy-aware ranking
    - Cross-document search capabilities
    - Bengali-English bilingual search
    """
    
    def __init__(self, 
                 embeddings_system: LegalDomainEmbeddings,
                 phase2_system: Optional[Phase2IntegratedSystem] = None,
                 phase25_system: Optional[Phase25IntegratedSystem] = None):
        """Initialize context-aware search system"""
        
        self.embeddings_system = embeddings_system
        self.phase2_system = phase2_system
        self.phase25_system = phase25_system
        
        # Search configuration
        self.search_config = {
            'default_similarity_threshold': 0.7,
            'context_expansion_limit': 20,
            'cross_document_limit': 5,
            'temporal_preference_weight': 0.3,
            'legal_precedence_weight': 0.2,
            'semantic_similarity_weight': 0.5,
            'max_search_results': 50
        }
        
        # Initialize search indices
        self.search_indices = {
            'concept_index': {},
            'procedural_index': {},
            'numerical_index': {},
            'document_index': {},
            'section_index': {}
        }
        
        # Mock legal document repository (would be real documents in production)
        self.legal_documents = self._initialize_mock_documents()
        
        # Build search indices
        self._build_search_indices()
        
        logger.info("Context-Aware Search system initialized")
    
    def _initialize_mock_documents(self) -> Dict[str, Dict]:
        """Initialize mock legal document repository"""
        
        return {
            "income_tax_act_2023_s44": {
                "document_id": "income_tax_act_2023_s44",
                "title": "Section 44 - Tax-free income limit",
                "title_bengali": "ধারা ৪৪ - করমুক্ত আয়ের সীমা",
                "content": "Any individual whose total income does not exceed Tk. 4,00,000 shall be exempt from income tax.",
                "content_bengali": "যে কোনো ব্যক্তির মোট আয় ৪,০০,০০০ টাকা অতিক্রম না করলে তিনি আয়কর থেকে অব্যাহতিপ্রাপ্ত হবেন।",
                "document_type": "income_tax_act",
                "section_number": "44",
                "effective_date": "2025-07-01",
                "authority_level": 95,
                "related_sections": ["Section 43", "Section 45"],
                "keywords": ["tax-free", "exemption", "income limit", "করমুক্ত", "অব্যাহতি"]
            },
            "income_tax_act_2023_s75": {
                "document_id": "income_tax_act_2023_s75",
                "title": "Section 75 - Obligation to furnish return",
                "title_bengali": "ধারা ৭৫ - রিটার্ন দাখিল বাধ্যবাধকতা",
                "content": "Every person whose total income exceeds the maximum amount not chargeable to tax shall furnish return.",
                "content_bengali": "যে কোনো ব্যক্তির মোট আয় সর্বোচ্চ করমুক্ত সীমা অতিক্রম করলে তাকে রিটার্ন দাখিল করতে হবে।",
                "document_type": "income_tax_act",
                "section_number": "75", 
                "effective_date": "2023-07-01",
                "authority_level": 95,
                "related_sections": ["Section 76", "Section 77"],
                "keywords": ["return filing", "obligation", "রিটার্ন", "দাখিল", "বাধ্যবাধকতা"]
            },
            "income_tax_act_2023_s163": {
                "document_id": "income_tax_act_2023_s163",
                "title": "Section 163 - Minimum tax",
                "title_bengali": "ধারা ১৬৩ - ন্যূনতম কর",
                "content": "Notwithstanding anything contained in this Act, minimum tax shall be payable by certain categories of taxpayers.",
                "content_bengali": "এই আইনে যাহা কিছুই থাকুক না কেন, নির্দিষ্ট শ্রেণীর করদাতাদের ন্যূনতম কর প্রদান করতে হবে।",
                "document_type": "income_tax_act",
                "section_number": "163",
                "effective_date": "2023-07-01", 
                "authority_level": 95,
                "related_sections": ["Section 162", "Section 164"],
                "keywords": ["minimum tax", "ন্যূনতম কর", "payable", "প্রদান"]
            },
            "finance_ordinance_2025_digital": {
                "document_id": "finance_ordinance_2025_digital",
                "title": "Digital Platform Income Taxation",
                "title_bengali": "ডিজিটাল প্ল্যাটফর্ম আয়ের কর",
                "content": "Income from YouTube, Facebook monetization shall be treated as business income under Section 25.",
                "content_bengali": "ইউটিউব, ফেসবুক মনিটাইজেশন থেকে প্রাপ্ত আয় ধারা ২৫ অনুযায়ী ব্যবসায়িক আয় হিসেবে গণ্য হবে।",
                "document_type": "finance_ordinance",
                "section_number": "digital_income",
                "effective_date": "2025-07-01",
                "authority_level": 100,
                "related_sections": ["Section 25", "Section 44"],
                "keywords": ["youtube", "digital income", "business income", "ইউটিউব", "ডিজিটাল আয়"]
            },
            "tds_rules_2024_rule3": {
                "document_id": "tds_rules_2024_rule3",
                "title": "Rule 3 - TDS on Professional Services",
                "title_bengali": "বিধি ৩ - পেশাগত সেবার উপর উৎসে কর কর্তন",
                "content": "Tax shall be deducted at source at the rate of 3% on payments for professional services.",
                "content_bengali": "পেশাগত সেবার জন্য প্রদানের উপর ৩% হারে উৎসে কর কর্তন করতে হবে।",
                "document_type": "tds_rules",
                "section_number": "rule_3",
                "effective_date": "2024-07-01",
                "authority_level": 85,
                "related_sections": ["Rule 4", "Rule 5"],
                "keywords": ["tds", "professional services", "3%", "উৎসে কর কর্তন", "পেশাগত সেবা"]
            }
        }
    
    def _build_search_indices(self):
        """Build comprehensive search indices"""
        
        logger.info("Building context-aware search indices")
        
        # Build indices from embeddings system
        if self.embeddings_system.concept_embeddings:
            for concept_id, concept in self.embeddings_system.concept_embeddings.items():
                # Concept index
                self.search_indices['concept_index'][concept_id] = {
                    'concept': concept,
                    'searchable_terms': concept.bengali_terms + concept.english_terms,
                    'embedding': concept.embedding_vector
                }
        
        # Build indices from legal documents  
        for doc_id, doc_data in self.legal_documents.items():
            # Document index
            self.search_indices['document_index'][doc_id] = doc_data
            
            # Section index
            section_key = f"{doc_data['document_type']}_{doc_data['section_number']}"
            self.search_indices['section_index'][section_key] = doc_data
        
        logger.info(f"Search indices built: {len(self.search_indices['concept_index'])} concepts, " +
                   f"{len(self.search_indices['document_index'])} documents")
    
    def parse_search_query(self, query: str) -> SearchQuery:
        """
        Parse and classify search query with context analysis
        
        Args:
            query: User search query in Bengali/English
            
        Returns:
            Structured search query with context
        """
        logger.info(f"Parsing search query: {query[:50]}...")
        
        # Clean and normalize query
        processed_query = query.strip()
        
        # Determine search type based on query content
        search_type = self._classify_query_type(processed_query)
        
        # Determine context scope
        context_scope = self._determine_context_scope(processed_query)
        
        # Extract temporal context
        temporal_context = self._extract_temporal_context(processed_query)
        
        # Extract section hints
        section_hints = self._extract_section_hints(processed_query)
        
        # Determine domain filter
        domain_filter = self._determine_domain_filter(processed_query)
        
        search_query = SearchQuery(
            original_query=query,
            processed_query=processed_query,
            query_type=search_type,
            context_scope=context_scope,
            temporal_context=temporal_context,
            section_hints=section_hints,
            domain_filter=domain_filter
        )
        
        logger.info(f"Query parsed: type={search_type.value}, scope={context_scope.value}, " +
                   f"temporal={temporal_context}")
        
        return search_query
    
    def _classify_query_type(self, query: str) -> SearchType:
        """Classify query type for appropriate search strategy"""
        
        # Check for numerical patterns
        numerical_patterns = [
            r'\d+%', r'\d+\s*শতাংশ', r'\d+\s*লক্ষ', r'\d+\s*টাকা',
            r'\d{4}-\d{2}', r'\d+\s*হার'
        ]
        
        if any(re.search(pattern, query, re.IGNORECASE) for pattern in numerical_patterns):
            return SearchType.NUMERICAL_SEARCH
        
        # Check for procedural terms
        procedural_terms = [
            'দাখিল', 'filing', 'নিবন্ধন', 'registration', 'আবেদন', 'application',
            'মূল্যায়ন', 'assessment', 'আপিল', 'appeal'
        ]
        
        if any(term in query.lower() for term in procedural_terms):
            return SearchType.PROCEDURAL_SEARCH
        
        # Check for concept terms
        concept_terms = [
            'আয়কর', 'income tax', 'কর', 'tax', 'অব্যাহতি', 'exemption',
            'ছাড়', 'relief', 'আয়', 'income'
        ]
        
        if any(term in query.lower() for term in concept_terms):
            return SearchType.CONCEPT_SEARCH
        
        # Default to hybrid search for complex queries
        return SearchType.HYBRID_SEARCH
    
    def _determine_context_scope(self, query: str) -> ContextScope:
        """Determine appropriate context expansion scope"""
        
        # Keywords indicating different scopes
        narrow_indicators = ['specific', 'exact', 'শুধু', 'only']
        related_indicators = ['related', 'সংশ্লিষ্ট', 'connected', 'সম্পর্কিত']
        document_indicators = ['all', 'সব', 'complete', 'সম্পূর্ণ']
        cross_indicators = ['across', 'multiple', 'বিভিন্ন', 'সকল']
        
        query_lower = query.lower()
        
        if any(indicator in query_lower for indicator in cross_indicators):
            return ContextScope.CROSS_DOCUMENT
        elif any(indicator in query_lower for indicator in document_indicators):
            return ContextScope.DOCUMENT
        elif any(indicator in query_lower for indicator in related_indicators):
            return ContextScope.RELATED
        elif any(indicator in query_lower for indicator in narrow_indicators):
            return ContextScope.NARROW
        
        # Default based on query complexity
        word_count = len(query.split())
        if word_count > 10:
            return ContextScope.CROSS_DOCUMENT
        elif word_count > 5:
            return ContextScope.RELATED
        else:
            return ContextScope.NARROW
    
    def _extract_temporal_context(self, query: str) -> Optional[str]:
        """Extract temporal context from query"""
        
        temporal_patterns = [
            r'(\d{4})-(\d{2})\s*অর্থবছর',
            r'FY\s*(\d{4})-(\d{2})',
            r'(\d{4})\s*সাল',
            r'চলতি\s*অর্থবছর',
            r'current\s*financial\s*year',
            r'২০২৫', r'২০২৪', r'2025', r'2024'
        ]
        
        for pattern in temporal_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_section_hints(self, query: str) -> List[str]:
        """Extract section references from query"""
        
        section_patterns = [
            r'ধারা\s*([০-৯\d]+)',
            r'Section\s*(\d+)',
            r'তফসিল\s*([০-৯\d]+)',
            r'Schedule\s*(\d+)',
            r'বিধি\s*([০-৯\d]+)',
            r'Rule\s*(\d+)'
        ]
        
        section_hints = []
        for pattern in section_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            section_hints.extend(matches)
        
        return section_hints
    
    def _determine_domain_filter(self, query: str) -> Optional[str]:
        """Determine legal domain filter"""
        
        domain_keywords = {
            'income_tax': ['আয়কর', 'income tax', 'তফসিল', 'schedule'],
            'vat_customs': ['ভ্যাট', 'vat', 'শুল্ক', 'customs'],
            'tds': ['উৎসে কর কর্তন', 'tds', 'withholding'],
            'digital': ['ইউটিউব', 'youtube', 'digital', 'ডিজিটাল']
        }
        
        query_lower = query.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain
        
        return None
    
    def execute_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """
        Execute context-aware search with multi-vector approach
        
        Args:
            search_query: Structured search query
            
        Returns:
            List of ranked search results
        """
        logger.info(f"Executing {search_query.query_type.value} search with {search_query.context_scope.value} scope")
        
        # Execute appropriate search strategy
        if search_query.query_type == SearchType.CONCEPT_SEARCH:
            results = self._concept_search(search_query)
        elif search_query.query_type == SearchType.PROCEDURAL_SEARCH:
            results = self._procedural_search(search_query)
        elif search_query.query_type == SearchType.NUMERICAL_SEARCH:
            results = self._numerical_search(search_query)
        elif search_query.query_type == SearchType.TEMPORAL_SEARCH:
            results = self._temporal_search(search_query)
        else:  # HYBRID_SEARCH
            results = self._hybrid_search(search_query)
        
        # Apply context expansion
        expanded_results = self._apply_context_expansion(results, search_query)
        
        # Apply temporal context if available
        if search_query.temporal_context:
            expanded_results = self._apply_temporal_context(expanded_results, search_query)
        
        # Rank and score results
        final_results = self._rank_and_score_results(expanded_results, search_query)
        
        logger.info(f"Search complete: {len(final_results)} results")
        
        return final_results[:search_query.max_results]
    
    def _concept_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """Execute concept-based semantic search"""
        
        results = []
        
        # Use embedding system for semantic search
        semantic_matches = self.embeddings_system.semantic_search(
            search_query.processed_query, 
            top_k=20,
            similarity_threshold=search_query.confidence_threshold
        )
        
        # Convert semantic matches to search results
        for concept, similarity in semantic_matches:
            # Find documents containing this concept
            matching_docs = self._find_documents_by_concept(concept)
            
            for doc_id, doc_data in matching_docs.items():
                result = SearchResult(
                    result_id=f"concept_{doc_id}_{concept.concept_id}",
                    content=doc_data['content'],
                    document_source=doc_data['document_type'],
                    section_reference=doc_data['section_number'],
                    concept_matches=[concept],
                    similarity_score=similarity,
                    context_relevance=0.8,  # Base relevance for concept match
                    temporal_relevance=1.0,  # Will be adjusted later
                    legal_precedence=doc_data['authority_level'],
                    explanation=f"Matched legal concept: {concept.concept_id}",
                    related_provisions=doc_data.get('related_sections', []),
                    confidence_score=similarity * 0.8
                )
                results.append(result)
        
        return results
    
    def _procedural_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """Execute procedure-focused search"""
        
        results = []
        
        # Search in documents for procedural content
        procedural_keywords = [
            'দাখিল', 'filing', 'নিবন্ধন', 'registration', 'আবেদন', 'application',
            'প্রক্রিয়া', 'procedure', 'নিয়ম', 'rules', 'বিধি', 'regulations'
        ]
        
        for doc_id, doc_data in self.legal_documents.items():
            content_match = any(keyword in doc_data['content'].lower() or 
                              keyword in doc_data['content_bengali'].lower() 
                              for keyword in procedural_keywords)
            
            keyword_match = any(keyword in doc_data.get('keywords', []) 
                               for keyword in procedural_keywords)
            
            if content_match or keyword_match:
                # Calculate procedural relevance
                procedural_score = self._calculate_procedural_relevance(doc_data, search_query.processed_query)
                
                if procedural_score > 0.5:
                    result = SearchResult(
                        result_id=f"procedural_{doc_id}",
                        content=doc_data['content'],
                        document_source=doc_data['document_type'], 
                        section_reference=doc_data['section_number'],
                        concept_matches=[],
                        similarity_score=procedural_score,
                        context_relevance=0.9,
                        temporal_relevance=1.0,
                        legal_precedence=doc_data['authority_level'],
                        explanation=f"Procedural match in {doc_data['document_type']}",
                        related_provisions=doc_data.get('related_sections', []),
                        confidence_score=procedural_score * 0.9
                    )
                    results.append(result)
        
        return results
    
    def _numerical_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """Execute numerical/quantitative search"""
        
        results = []
        
        # Extract numerical values from query
        numerical_patterns = [
            r'(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:,\d+)*)\s*টাকা',
            r'(\d+(?:\.\d+)?)\s*লক্ষ',
            r'(\d{4})-(\d{2})'
        ]
        
        query_numbers = []
        for pattern in numerical_patterns:
            matches = re.findall(pattern, search_query.processed_query)
            query_numbers.extend([match if isinstance(match, str) else match[0] for match in matches])
        
        # Search documents for matching numerical content
        for doc_id, doc_data in self.legal_documents.items():
            doc_content = f"{doc_data['content']} {doc_data['content_bengali']}"
            
            # Find numerical matches in document
            doc_numbers = []
            for pattern in numerical_patterns:
                matches = re.findall(pattern, doc_content)
                doc_numbers.extend([match if isinstance(match, str) else match[0] for match in matches])
            
            # Calculate numerical similarity
            numerical_score = self._calculate_numerical_similarity(query_numbers, doc_numbers)
            
            if numerical_score > 0.3:
                result = SearchResult(
                    result_id=f"numerical_{doc_id}",
                    content=doc_data['content'],
                    document_source=doc_data['document_type'],
                    section_reference=doc_data['section_number'],
                    concept_matches=[],
                    similarity_score=numerical_score,
                    context_relevance=0.7,
                    temporal_relevance=1.0,
                    legal_precedence=doc_data['authority_level'],
                    explanation=f"Numerical match: {', '.join(query_numbers[:3])}",
                    related_provisions=doc_data.get('related_sections', []),
                    confidence_score=numerical_score * 0.8
                )
                results.append(result)
        
        return results
    
    def _temporal_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """Execute temporal-aware search using Phase 2.5"""
        
        if not self.phase25_system:
            logger.warning("Phase 2.5 system not available for temporal search")
            return self._concept_search(search_query)  # Fallback
        
        # Use Phase 2.5 temporal query processing
        temporal_result = self.phase25_system.process_temporal_query(search_query.original_query)
        
        results = []
        
        # Create result based on temporal analysis
        result = SearchResult(
            result_id=f"temporal_{temporal_result['applicable_law']['version_id']}",
            content=f"Law Version: {temporal_result['applicable_law']['version_id']}, " +
                   f"Financial Year: {temporal_result['applicable_law']['financial_year']}",
            document_source=temporal_result['applicable_law']['version_id'],
            section_reference=temporal_result['section_unification']['matched_section'] or "general",
            concept_matches=[],
            similarity_score=temporal_result['temporal_analysis']['temporal_confidence'],
            context_relevance=0.9,
            temporal_relevance=temporal_result['temporal_analysis']['temporal_confidence'],
            legal_precedence=temporal_result['applicable_law']['authority_level'],
            explanation=f"Temporal match for {temporal_result['temporal_analysis']['inferred_financial_year']}",
            related_provisions=temporal_result['applicable_law'].get('relevant_provisions', []),
            confidence_score=temporal_result['temporal_analysis']['temporal_confidence']
        )
        results.append(result)
        
        return results
    
    def _hybrid_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """Execute multi-vector hybrid search"""
        
        # Combine results from multiple search types
        concept_results = self._concept_search(search_query)
        procedural_results = self._procedural_search(search_query)
        numerical_results = self._numerical_search(search_query)
        
        # Merge and deduplicate results
        all_results = concept_results + procedural_results + numerical_results
        
        # Deduplicate by result_id
        unique_results = {}
        for result in all_results:
            if result.result_id not in unique_results:
                unique_results[result.result_id] = result
            else:
                # Merge scores for duplicate results
                existing = unique_results[result.result_id]
                existing.similarity_score = max(existing.similarity_score, result.similarity_score)
                existing.confidence_score = max(existing.confidence_score, result.confidence_score)
        
        return list(unique_results.values())
    
    def _find_documents_by_concept(self, concept: LegalConcept) -> Dict[str, Dict]:
        """Find documents containing specific legal concept"""
        
        matching_docs = {}
        
        # Search in document keywords and content
        all_concept_terms = concept.bengali_terms + concept.english_terms
        
        for doc_id, doc_data in self.legal_documents.items():
            doc_content = f"{doc_data['content']} {doc_data['content_bengali']} {' '.join(doc_data.get('keywords', []))}"
            doc_content_lower = doc_content.lower()
            
            # Check for term matches
            if any(term.lower() in doc_content_lower for term in all_concept_terms):
                matching_docs[doc_id] = doc_data
        
        return matching_docs
    
    def _calculate_procedural_relevance(self, doc_data: Dict, query: str) -> float:
        """Calculate procedural relevance score"""
        
        procedural_keywords = ['filing', 'দাখিল', 'procedure', 'process', 'rules', 'বিধি']
        
        content = f"{doc_data['content']} {doc_data['content_bengali']} {' '.join(doc_data.get('keywords', []))}"
        query_lower = query.lower()
        content_lower = content.lower()
        
        matches = sum(1 for keyword in procedural_keywords if keyword in content_lower and keyword in query_lower)
        total_keywords = len(procedural_keywords)
        
        return min(matches / total_keywords * 2, 1.0)  # Scale and cap at 1.0
    
    def _calculate_numerical_similarity(self, query_numbers: List[str], doc_numbers: List[str]) -> float:
        """Calculate numerical similarity between query and document"""
        
        if not query_numbers or not doc_numbers:
            return 0.0
        
        # Simple exact match scoring
        matches = len(set(query_numbers) & set(doc_numbers))
        total_query_numbers = len(query_numbers)
        
        return matches / total_query_numbers if total_query_numbers > 0 else 0.0
    
    def _apply_context_expansion(self, results: List[SearchResult], search_query: SearchQuery) -> List[SearchResult]:
        """Apply context expansion based on search scope"""
        
        if search_query.context_scope == ContextScope.NARROW:
            return results  # No expansion needed
        
        expanded_results = results.copy()
        
        # Expand based on related provisions
        for result in results:
            if search_query.context_scope in [ContextScope.RELATED, ContextScope.DOCUMENT, ContextScope.CROSS_DOCUMENT]:
                # Find related documents
                related_docs = self._find_related_documents(result.section_reference, result.document_source)
                
                for doc_id, doc_data in related_docs.items():
                    # Create expanded result
                    expanded_result = SearchResult(
                        result_id=f"expanded_{doc_id}",
                        content=doc_data['content'],
                        document_source=doc_data['document_type'],
                        section_reference=doc_data['section_number'],
                        concept_matches=[],
                        similarity_score=result.similarity_score * 0.8,  # Reduced for expansion
                        context_relevance=0.6,  # Lower relevance for expanded content
                        temporal_relevance=result.temporal_relevance,
                        legal_precedence=doc_data['authority_level'],
                        explanation=f"Context expansion from {result.section_reference}",
                        related_provisions=doc_data.get('related_sections', []),
                        confidence_score=result.confidence_score * 0.7
                    )
                    expanded_results.append(expanded_result)
        
        return expanded_results
    
    def _find_related_documents(self, section_ref: str, document_type: str) -> Dict[str, Dict]:
        """Find documents related to given section"""
        
        related_docs = {}
        
        for doc_id, doc_data in self.legal_documents.items():
            # Check if document references the target section
            if section_ref in doc_data.get('related_sections', []):
                related_docs[doc_id] = doc_data
            
            # Check for same document type (for document scope)
            elif document_type == doc_data['document_type'] and doc_id not in related_docs:
                related_docs[doc_id] = doc_data
        
        return related_docs
    
    def _apply_temporal_context(self, results: List[SearchResult], search_query: SearchQuery) -> List[SearchResult]:
        """Apply temporal context weighting to results"""
        
        if not search_query.temporal_context or not self.phase25_system:
            return results
        
        # Get temporal information
        temporal_result = self.phase25_system.process_temporal_query(search_query.original_query)
        target_financial_year = temporal_result['applicable_law']['financial_year']
        
        # Adjust temporal relevance for each result
        for result in results:
            # Check if document is from target financial year
            doc_date = self.legal_documents.get(result.result_id.split('_', 1)[1], {}).get('effective_date', '2023-07-01')
            doc_year = doc_date[:4]
            
            if target_financial_year.startswith(doc_year):
                result.temporal_relevance = 1.0  # Perfect match
            elif abs(int(target_financial_year[:4]) - int(doc_year)) == 1:
                result.temporal_relevance = 0.8  # Adjacent year
            else:
                result.temporal_relevance = 0.5  # Older version
        
        return results
    
    def _rank_and_score_results(self, results: List[SearchResult], search_query: SearchQuery) -> List[SearchResult]:
        """Rank and score search results using multi-factor scoring"""
        
        for result in results:
            # Calculate composite score
            composite_score = (
                result.similarity_score * self.search_config['semantic_similarity_weight'] +
                result.temporal_relevance * self.search_config['temporal_preference_weight'] +
                (result.legal_precedence / 100.0) * self.search_config['legal_precedence_weight'] +
                result.context_relevance * 0.2  # Remaining weight
            )
            
            result.confidence_score = composite_score
        
        # Sort by composite score
        results.sort(key=lambda r: r.confidence_score, reverse=True)
        
        return results
    
    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Main search interface with comprehensive result formatting
        
        Args:
            query: Search query string
            **kwargs: Additional search parameters
            
        Returns:
            Comprehensive search results with context
        """
        logger.info(f"Executing context-aware search: {query[:50]}...")
        
        # Parse query
        search_query = self.parse_search_query(query)
        
        # Override default parameters with kwargs
        for key, value in kwargs.items():
            if hasattr(search_query, key):
                setattr(search_query, key, value)
        
        # Execute search
        search_results = self.execute_search(search_query)
        
        # Format comprehensive response
        search_response = {
            "query_analysis": {
                "original_query": search_query.original_query,
                "processed_query": search_query.processed_query,
                "query_type": search_query.query_type.value,
                "context_scope": search_query.context_scope.value,
                "temporal_context": search_query.temporal_context,
                "section_hints": search_query.section_hints,
                "domain_filter": search_query.domain_filter
            },
            "search_results": [
                {
                    "result_id": result.result_id,
                    "content": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                    "document_source": result.document_source,
                    "section_reference": result.section_reference,
                    "similarity_score": round(result.similarity_score, 3),
                    "confidence_score": round(result.confidence_score, 3),
                    "temporal_relevance": round(result.temporal_relevance, 3),
                    "legal_precedence": result.legal_precedence,
                    "explanation": result.explanation,
                    "related_provisions": result.related_provisions
                }
                for result in search_results
            ],
            "search_metadata": {
                "total_results": len(search_results),
                "search_strategy": search_query.query_type.value,
                "context_expansion": search_query.context_scope.value != ContextScope.NARROW.value,
                "temporal_analysis": bool(search_query.temporal_context),
                "phase2_integration": bool(self.phase2_system),
                "phase25_integration": bool(self.phase25_system),
                "search_timestamp": datetime.now().isoformat()
            }
        }
        
        logger.info(f"Search complete: {len(search_results)} results returned")
        
        return search_response

def main():
    """Test the Context-Aware Search system"""
    
    # Initialize dependencies
    from legal_domain_embeddings import LegalDomainEmbeddings
    from phase_2_5_integration import Phase25IntegratedSystem
    
    # Create systems
    phase25_system = Phase25IntegratedSystem()
    embeddings_system = LegalDomainEmbeddings(phase25_system=phase25_system)
    
    # Build embeddings corpus and train
    corpus = embeddings_system.build_training_corpus()
    embeddings_system.fine_tune_embeddings(epochs=2)  # Quick training for testing
    
    # Initialize context-aware search
    search_system = ContextAwareSearch(
        embeddings_system=embeddings_system,
        phase25_system=phase25_system
    )
    
    print("🔍 Context-Aware Search System Test")
    print("=" * 50)
    
    # Test queries with different types and contexts
    test_queries = [
        "২০২৫ অর্থবছরে ইউটিউব আয়ের কর হার কত?",  # Temporal + numerical
        "রিটার্ন দাখিলের প্রক্রিয়া কী?",          # Procedural
        "করমুক্ত সীমা কত টাকা?",                  # Numerical + concept
        "Section 75 এ কী বলা আছে?",             # Concept + section hint
        "TDS rules for professional services",    # Cross-document
        "ধারা ১৬৩ minimum tax সম্পর্কে",          # Bilingual concept
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query}")
        print("-" * (20 + len(str(i))))
        
        # Execute search
        search_response = search_system.search(query)
        
        # Display results
        analysis = search_response["query_analysis"]
        results = search_response["search_results"]
        metadata = search_response["search_metadata"]
        
        print(f"Query Type: {analysis['query_type'].title()}")
        print(f"Context Scope: {analysis['context_scope'].title()}")
        print(f"Temporal Context: {analysis['temporal_context']}")
        print(f"Total Results: {metadata['total_results']}")
        
        # Show top 3 results
        for j, result in enumerate(results[:3], 1):
            print(f"\n  Result {j}:")
            print(f"    📄 Document: {result['document_source']}")
            print(f"    📍 Section: {result['section_reference']}")
            print(f"    🎯 Confidence: {result['confidence_score']:.3f}")
            print(f"    📝 Content: {result['content'][:100]}...")
            print(f"    🔗 Related: {', '.join(result['related_provisions'][:3])}")
    
    # Test context expansion
    print(f"\n📈 Testing Context Expansion:")
    print("-" * 30)
    
    expansion_query = "Section 44 সম্পর্কিত সব বিধান"
    expanded_response = search_system.search(
        expansion_query, 
        context_scope=ContextScope.CROSS_DOCUMENT,
        max_results=5
    )
    
    print(f"Expansion Query: {expansion_query}")
    print(f"Context Scope: {expanded_response['query_analysis']['context_scope']}")
    print(f"Results Found: {expanded_response['search_metadata']['total_results']}")
    
    for i, result in enumerate(expanded_response["search_results"], 1):
        print(f"  {i}. {result['document_source']} - {result['section_reference']} (conf: {result['confidence_score']:.3f})")

if __name__ == "__main__":
    main()