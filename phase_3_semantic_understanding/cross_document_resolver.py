#!/usr/bin/env python3
"""
Cross-Document Query Resolution System - Phase 3.3 Implementation
===============================================================

Advanced system for answering legal queries that span multiple documents.
Synthesizes responses from Income Tax Act + Schedules + Rules + Circulars
while maintaining legal precedence hierarchy and temporal accuracy.

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
from collections import defaultdict, OrderedDict
from enum import Enum
import itertools

# Import Phase 2, Phase 2.5, and Phase 3 components
sys.path.append(str(Path(__file__).parent.parent / "phase_2_knowledge_graph"))
sys.path.append(str(Path(__file__).parent.parent / "phase_2_5_temporal_control"))

from phase_2_integration import Phase2IntegratedSystem
from phase_2_5_integration import Phase25IntegratedSystem
from legal_domain_embeddings import LegalDomainEmbeddings, LegalConcept
from context_aware_search import ContextAwareSearch, SearchResult, SearchQuery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryComplexity(Enum):
    """Complexity levels for cross-document queries"""
    SIMPLE = "simple"           # Single document, single concept
    MODERATE = "moderate"       # Multiple sections, single document 
    COMPLEX = "complex"         # Multiple documents, multiple concepts
    ENTERPRISE = "enterprise"   # Multi-domain, temporal, procedural

class ResolutionStrategy(Enum):
    """Strategy for resolving cross-document queries"""
    HIERARCHICAL = "hierarchical"      # Apply legal precedence hierarchy
    TEMPORAL_FIRST = "temporal_first"  # Temporal context takes precedence
    COMPREHENSIVE = "comprehensive"    # All relevant sources included
    AUTHORITATIVE = "authoritative"    # Highest authority source only

@dataclass
class DocumentFragment:
    """Fragment of legal document relevant to query"""
    document_id: str
    document_type: str
    section_reference: str
    content: str
    content_bengali: str
    authority_level: int
    effective_date: str
    relevance_score: float
    keywords: List[str]
    related_sections: List[str]

@dataclass
class LegalProvision:
    """Structured legal provision with hierarchy context"""
    provision_id: str
    source_document: str
    section_number: str
    provision_text: str
    provision_text_bengali: str
    legal_authority: int
    temporal_validity: str
    precedence_order: int
    applicability_conditions: List[str]
    cross_references: List[str]

@dataclass
class CrossDocumentQuery:
    """Structured cross-document query"""
    original_query: str
    query_complexity: QueryComplexity
    resolution_strategy: ResolutionStrategy
    required_documents: List[str]
    temporal_context: Optional[str] = None
    legal_concepts: List[str] = None
    procedural_elements: List[str] = None
    numerical_contexts: List[str] = None
    domain_scope: str = "income_tax"

@dataclass
class SynthesizedResponse:
    """Complete synthesized response to cross-document query"""
    query: str
    primary_answer: str
    primary_answer_bengali: str
    supporting_provisions: List[LegalProvision]
    legal_reasoning: List[str]
    confidence_score: float
    completeness_score: float
    authority_sources: Dict[str, int]
    temporal_accuracy: float
    cross_references: List[str]
    caveats_and_conditions: List[str]
    expert_review_recommended: bool
    response_metadata: Dict[str, Any]

class CrossDocumentResolver:
    """
    Cross-Document Query Resolution System for Bangladesh Legal Documents
    
    Features:
    - Multi-document query analysis and resolution
    - Legal hierarchy-aware response synthesis
    - Temporal law version integration from Phase 2.5
    - Semantic search integration from Phase 3.1/3.2  
    - Bengali-English bilingual response generation
    - Comprehensive legal reasoning documentation
    - Expert review recommendations for complex cases
    """
    
    def __init__(self, 
                 search_system: ContextAwareSearch,
                 embeddings_system: LegalDomainEmbeddings,
                 phase2_system: Optional[Phase2IntegratedSystem] = None,
                 phase25_system: Optional[Phase25IntegratedSystem] = None):
        """Initialize cross-document resolver"""
        
        self.search_system = search_system
        self.embeddings_system = embeddings_system
        self.phase2_system = phase2_system
        self.phase25_system = phase25_system
        
        # Legal hierarchy configuration
        self.legal_hierarchy = {
            'finance_ordinance': 100,
            'income_tax_act': 95,
            'schedules': 90,
            'tds_rules': 85,
            'vds_rules': 85, 
            'circulars': 70,
            'sro': 80,
            'notifications': 65
        }
        
        # Resolution configuration
        self.resolution_config = {
            'max_documents_per_query': 10,
            'min_confidence_threshold': 0.7,
            'expert_review_threshold': 0.85,
            'completeness_threshold': 0.8,
            'max_provisions_in_response': 8,
            'temporal_preference_weight': 0.3,
            'authority_weight': 0.4,
            'relevance_weight': 0.3
        }
        
        # Initialize document registry
        self.document_registry = self._initialize_document_registry()
        
        logger.info("Cross-Document Resolver initialized")
    
    def _initialize_document_registry(self) -> Dict[str, Dict]:
        """Initialize comprehensive document registry"""
        
        return {
            # Primary Income Tax Act
            'income_tax_act_2023': {
                'document_type': 'income_tax_act',
                'authority_level': 95,
                'effective_date': '2023-07-01',
                'language_coverage': ['bengali', 'english'],
                'total_sections': 286,
                'key_domains': ['income_classification', 'tax_calculation', 'filing_procedures']
            },
            
            # Finance Ordinances (highest authority)
            'finance_ordinance_2024': {
                'document_type': 'finance_ordinance',
                'authority_level': 100,
                'effective_date': '2024-07-01',
                'expiry_date': '2025-06-30',
                'overrides': ['income_tax_act_2023'],
                'key_domains': ['tax_rates', 'exemptions', 'procedures']
            },
            
            'finance_ordinance_2025': {
                'document_type': 'finance_ordinance',
                'authority_level': 100,
                'effective_date': '2025-07-01',
                'expiry_date': '2026-06-30',
                'overrides': ['income_tax_act_2023', 'finance_ordinance_2024'],
                'key_domains': ['digital_taxation', 'updated_rates', 'new_exemptions']
            },
            
            # Schedules (part of main Act)
            'income_tax_schedules': {
                'document_type': 'schedules',
                'authority_level': 90,
                'effective_date': '2023-07-01',
                'sub_schedules': ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th'],
                'key_domains': ['tax_rates', 'exemptions', 'depreciation', 'investment_allowances']
            },
            
            # Implementation Rules
            'tds_rules_2024': {
                'document_type': 'tds_rules',
                'authority_level': 85,
                'effective_date': '2024-07-01',
                'implements': ['income_tax_act_2023'],
                'key_domains': ['withholding_procedures', 'tax_deduction', 'compliance']
            },
            
            # Interpretive Guidance
            'income_tax_circulars': {
                'document_type': 'circulars',
                'authority_level': 70,
                'effective_date': '2023-07-01',
                'interprets': ['income_tax_act_2023', 'tds_rules_2024'],
                'key_domains': ['interpretations', 'clarifications', 'procedures']
            }
        }
    
    def analyze_query_complexity(self, query: str) -> CrossDocumentQuery:
        """
        Analyze query complexity and determine resolution strategy
        
        Args:
            query: User query string
            
        Returns:
            Structured cross-document query with resolution strategy
        """
        logger.info(f"Analyzing query complexity: {query[:50]}...")
        
        # Extract query components
        temporal_context = self._extract_temporal_indicators(query)
        legal_concepts = self._extract_legal_concepts(query)  
        procedural_elements = self._extract_procedural_elements(query)
        numerical_contexts = self._extract_numerical_contexts(query)
        
        # Determine required documents
        required_documents = self._identify_required_documents(query)
        
        # Assess complexity
        complexity_score = self._calculate_complexity_score(
            len(required_documents), len(legal_concepts), 
            len(procedural_elements), bool(temporal_context)
        )
        
        # Map complexity score to enum
        if complexity_score <= 2:
            query_complexity = QueryComplexity.SIMPLE
        elif complexity_score <= 4:
            query_complexity = QueryComplexity.MODERATE  
        elif complexity_score <= 6:
            query_complexity = QueryComplexity.COMPLEX
        else:
            query_complexity = QueryComplexity.ENTERPRISE
        
        # Determine resolution strategy
        resolution_strategy = self._select_resolution_strategy(
            query_complexity, temporal_context, required_documents
        )
        
        cross_doc_query = CrossDocumentQuery(
            original_query=query,
            query_complexity=query_complexity,
            resolution_strategy=resolution_strategy,
            required_documents=required_documents,
            temporal_context=temporal_context,
            legal_concepts=legal_concepts,
            procedural_elements=procedural_elements,
            numerical_contexts=numerical_contexts
        )
        
        logger.info(f"Query analysis: complexity={query_complexity.value}, " +
                   f"strategy={resolution_strategy.value}, documents={len(required_documents)}")
        
        return cross_doc_query
    
    def _extract_temporal_indicators(self, query: str) -> Optional[str]:
        """Extract temporal context indicators"""
        
        temporal_patterns = [
            r'(\d{4})-(\d{2})\s*অর্থবছর',
            r'FY\s*(\d{4})-(\d{2})',
            r'(\d{4})\s*সাল',
            r'চলতি\s*অর্থবছর',
            r'current\s*financial\s*year',
            r'গত\s*বছর', r'last\s*year',
            r'আগামী\s*বছর', r'next\s*year'
        ]
        
        for pattern in temporal_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_legal_concepts(self, query: str) -> List[str]:
        """Extract legal concepts from query"""
        
        legal_concept_keywords = {
            'tax_calculation': ['কর গণনা', 'tax calculation', 'কর হার', 'tax rate'],
            'exemptions': ['অব্যাহতি', 'exemption', 'করমুক্ত', 'tax free'],
            'filing_obligations': ['রিটার্ন', 'return filing', 'দাখিল', 'filing'],
            'income_classification': ['আয়ের ধরন', 'income type', 'ব্যবসায়িক আয়', 'business income'],
            'deductions': ['কর্তন', 'deduction', 'ছাড়', 'allowance'],
            'penalties': ['জরিমানা', 'penalty', 'শাস্তি', 'punishment'],
            'appeals': ['আপিল', 'appeal', 'পুনর্বিবেচনা', 'revision']
        }
        
        identified_concepts = []
        query_lower = query.lower()
        
        for concept, keywords in legal_concept_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                identified_concepts.append(concept)
        
        return identified_concepts
    
    def _extract_procedural_elements(self, query: str) -> List[str]:
        """Extract procedural elements from query"""
        
        procedural_keywords = {
            'registration': ['নিবন্ধন', 'registration', 'রেজিস্ট্রেশন'],
            'filing': ['দাখিল', 'filing', 'জমা', 'submission'],
            'payment': ['প্রদান', 'payment', 'পরিশোধ'],
            'assessment': ['মূল্যায়ন', 'assessment', 'নিরীক্ষা', 'audit'],
            'appeal': ['আপিল', 'appeal', 'অভিযোগ', 'complaint'],
            'compliance': ['সম্মতি', 'compliance', 'মেনে চলা']
        }
        
        identified_procedures = []
        query_lower = query.lower()
        
        for procedure, keywords in procedural_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                identified_procedures.append(procedure)
        
        return identified_procedures
    
    def _extract_numerical_contexts(self, query: str) -> List[str]:
        """Extract numerical contexts from query"""
        
        numerical_patterns = [
            (r'(\d+(?:\.\d+)?)\s*%', 'percentage'),
            (r'(\d+(?:,\d+)*)\s*টাকা', 'amount_taka'),
            (r'(\d+(?:\.\d+)?)\s*লক্ষ', 'amount_lakh'),
            (r'(\d+(?:\.\d+)?)\s*কোটি', 'amount_crore'),
            (r'(\d{4})-(\d{2})', 'financial_year'),
            (r'(\d+(?:\.\d+)?)\s*বছর', 'years')
        ]
        
        identified_numerical = []
        
        for pattern, context_type in numerical_patterns:
            matches = re.findall(pattern, query)
            if matches:
                identified_numerical.append(f"{context_type}:{len(matches)}")
        
        return identified_numerical
    
    def _identify_required_documents(self, query: str) -> List[str]:
        """Identify which legal documents are required for query"""
        
        document_indicators = {
            'income_tax_act_2023': [
                'আয়কর আইন', 'income tax act', 'ধারা', 'section',
                'ITA 2023', 'Act 2023'
            ],
            'finance_ordinance_2025': [
                'অর্থ অধ্যাদেশ', 'finance ordinance', '২০২৫', '2025',
                'FO 2025', 'বাজেট', 'budget'
            ],
            'income_tax_schedules': [
                'তফসিল', 'schedule', 'তফসিল ৪', 'schedule 4',
                '৪র্থ তফসিল', '4th schedule'
            ],
            'tds_rules_2024': [
                'TDS', 'উৎসে কর কর্তন', 'tax deduction at source',
                'বিধি', 'rules', 'withholding'
            ],
            'income_tax_circulars': [
                'সার্কুলার', 'circular', 'নির্দেশনা', 'instruction',
                'ব্যাখ্যা', 'interpretation'
            ]
        }
        
        required_docs = []
        query_lower = query.lower()
        
        for doc_id, indicators in document_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                required_docs.append(doc_id)
        
        # Default fallback - if no specific document mentioned, include primary sources
        if not required_docs:
            required_docs = ['income_tax_act_2023', 'finance_ordinance_2025']
        
        return required_docs
    
    def _calculate_complexity_score(self, num_documents: int, num_concepts: int, 
                                   num_procedures: int, has_temporal: bool) -> int:
        """Calculate query complexity score"""
        
        score = 0
        score += min(num_documents, 4)  # Max 4 points for documents
        score += min(num_concepts, 3)   # Max 3 points for concepts  
        score += min(num_procedures, 2) # Max 2 points for procedures
        score += 1 if has_temporal else 0 # 1 point for temporal context
        
        return score
    
    def _select_resolution_strategy(self, complexity: QueryComplexity, 
                                   temporal_context: Optional[str],
                                   required_documents: List[str]) -> ResolutionStrategy:
        """Select appropriate resolution strategy"""
        
        if temporal_context:
            return ResolutionStrategy.TEMPORAL_FIRST
        elif complexity in [QueryComplexity.COMPLEX, QueryComplexity.ENTERPRISE]:
            return ResolutionStrategy.COMPREHENSIVE
        elif len(required_documents) == 1:
            return ResolutionStrategy.AUTHORITATIVE
        else:
            return ResolutionStrategy.HIERARCHICAL
    
    def resolve_cross_document_query(self, cross_doc_query: CrossDocumentQuery) -> SynthesizedResponse:
        """
        Resolve cross-document query using comprehensive document analysis
        
        Args:
            cross_doc_query: Structured cross-document query
            
        Returns:
            Synthesized response with legal reasoning
        """
        logger.info(f"Resolving {cross_doc_query.query_complexity.value} query with " +
                   f"{cross_doc_query.resolution_strategy.value} strategy")
        
        # Step 1: Execute search across required documents
        search_results = self._execute_multi_document_search(cross_doc_query)
        
        # Step 2: Extract relevant document fragments
        document_fragments = self._extract_document_fragments(search_results)
        
        # Step 3: Apply temporal context if available
        if cross_doc_query.temporal_context and self.phase25_system:
            document_fragments = self._apply_temporal_filtering(document_fragments, cross_doc_query)
        
        # Step 4: Create legal provisions with hierarchy
        legal_provisions = self._create_legal_provisions(document_fragments)
        
        # Step 5: Apply resolution strategy
        resolved_provisions = self._apply_resolution_strategy(legal_provisions, cross_doc_query)
        
        # Step 6: Synthesize comprehensive response
        synthesized_response = self._synthesize_response(resolved_provisions, cross_doc_query)
        
        # Step 7: Generate legal reasoning
        synthesized_response = self._add_legal_reasoning(synthesized_response, resolved_provisions)
        
        # Step 8: Calculate confidence and completeness scores
        synthesized_response = self._calculate_response_scores(synthesized_response)
        
        logger.info(f"Query resolution complete: confidence={synthesized_response.confidence_score:.3f}, " +
                   f"completeness={synthesized_response.completeness_score:.3f}")
        
        return synthesized_response
    
    def _execute_multi_document_search(self, cross_doc_query: CrossDocumentQuery) -> List[SearchResult]:
        """Execute search across multiple required documents"""
        
        # Execute search with context expansion for comprehensive coverage
        search_response = self.search_system.search(
            cross_doc_query.original_query,
            max_results=self.resolution_config['max_documents_per_query']
        )
        
        # Filter results to include only required documents if specified
        filtered_results = []
        for result_data in search_response['search_results']:
            if not cross_doc_query.required_documents or any(
                doc_id in result_data['document_source'] 
                for doc_id in cross_doc_query.required_documents
            ):
                # Convert back to SearchResult object (simplified)
                search_result = SearchResult(
                    result_id=result_data['result_id'],
                    content=result_data['content'],
                    document_source=result_data['document_source'],
                    section_reference=result_data['section_reference'],
                    concept_matches=[],
                    similarity_score=result_data['similarity_score'],
                    context_relevance=0.8,
                    temporal_relevance=result_data['temporal_relevance'],
                    legal_precedence=result_data['legal_precedence'],
                    explanation=result_data['explanation'],
                    related_provisions=result_data['related_provisions'],
                    confidence_score=result_data['confidence_score']
                )
                filtered_results.append(search_result)
        
        return filtered_results
    
    def _extract_document_fragments(self, search_results: List[SearchResult]) -> List[DocumentFragment]:
        """Extract document fragments from search results"""
        
        fragments = []
        
        for result in search_results:
            # Get full document data (mock implementation)
            doc_data = self.search_system.legal_documents.get(
                result.result_id.split('_', 1)[1] if '_' in result.result_id else result.result_id,
                {}
            )
            
            if doc_data:
                fragment = DocumentFragment(
                    document_id=doc_data.get('document_id', result.result_id),
                    document_type=result.document_source,
                    section_reference=result.section_reference,
                    content=result.content,
                    content_bengali=doc_data.get('content_bengali', ''),
                    authority_level=result.legal_precedence,
                    effective_date=doc_data.get('effective_date', '2023-07-01'),
                    relevance_score=result.confidence_score,
                    keywords=doc_data.get('keywords', []),
                    related_sections=result.related_provisions
                )
                fragments.append(fragment)
        
        return fragments
    
    def _apply_temporal_filtering(self, fragments: List[DocumentFragment], 
                                 cross_doc_query: CrossDocumentQuery) -> List[DocumentFragment]:
        """Apply temporal filtering using Phase 2.5 system"""
        
        if not self.phase25_system:
            return fragments
        
        # Get temporal analysis
        temporal_result = self.phase25_system.process_temporal_query(cross_doc_query.original_query)
        target_financial_year = temporal_result['applicable_law']['financial_year']
        
        # Adjust fragment relevance based on temporal accuracy
        for fragment in fragments:
            doc_year = fragment.effective_date[:4]
            if target_financial_year.startswith(doc_year):
                fragment.relevance_score *= 1.0  # Perfect temporal match
            elif abs(int(target_financial_year[:4]) - int(doc_year)) <= 1:
                fragment.relevance_score *= 0.9  # Adjacent year
            else:
                fragment.relevance_score *= 0.7  # Older version
        
        return fragments
    
    def _create_legal_provisions(self, fragments: List[DocumentFragment]) -> List[LegalProvision]:
        """Create legal provisions from document fragments"""
        
        provisions = []
        
        for i, fragment in enumerate(fragments):
            provision = LegalProvision(
                provision_id=f"provision_{i:03d}_{fragment.document_type}_{fragment.section_reference}",
                source_document=fragment.document_type,
                section_number=fragment.section_reference,
                provision_text=fragment.content,
                provision_text_bengali=fragment.content_bengali,
                legal_authority=fragment.authority_level,
                temporal_validity=fragment.effective_date,
                precedence_order=self.legal_hierarchy.get(fragment.document_type, 50),
                applicability_conditions=[],  # Would be extracted from content
                cross_references=fragment.related_sections
            )
            provisions.append(provision)
        
        return provisions
    
    def _apply_resolution_strategy(self, provisions: List[LegalProvision], 
                                  cross_doc_query: CrossDocumentQuery) -> List[LegalProvision]:
        """Apply resolution strategy to filter and order provisions"""
        
        if cross_doc_query.resolution_strategy == ResolutionStrategy.HIERARCHICAL:
            # Sort by legal precedence
            provisions.sort(key=lambda p: p.precedence_order, reverse=True)
            return provisions[:self.resolution_config['max_provisions_in_response']]
            
        elif cross_doc_query.resolution_strategy == ResolutionStrategy.TEMPORAL_FIRST:
            # Sort by temporal relevance first, then precedence
            provisions.sort(key=lambda p: (p.temporal_validity, p.precedence_order), reverse=True)
            return provisions[:self.resolution_config['max_provisions_in_response']]
            
        elif cross_doc_query.resolution_strategy == ResolutionStrategy.AUTHORITATIVE:
            # Keep only highest authority provisions
            max_authority = max(p.legal_authority for p in provisions)
            return [p for p in provisions if p.legal_authority == max_authority]
            
        else:  # COMPREHENSIVE
            # Include all relevant provisions up to limit
            return provisions[:self.resolution_config['max_provisions_in_response']]
    
    def _synthesize_response(self, provisions: List[LegalProvision], 
                            cross_doc_query: CrossDocumentQuery) -> SynthesizedResponse:
        """Synthesize comprehensive response from legal provisions"""
        
        # Create primary answer by combining provisions
        primary_provisions = provisions[:3]  # Top 3 most relevant
        
        # Generate English answer
        primary_answer = "Based on Bangladesh tax law:\n\n"
        for i, provision in enumerate(primary_provisions, 1):
            primary_answer += f"{i}. {provision.source_document.replace('_', ' ').title()} "
            primary_answer += f"Section {provision.section_number}: "
            primary_answer += f"{provision.provision_text[:200]}...\n\n"
        
        # Generate Bengali answer
        primary_answer_bengali = "বাংলাদেশের কর আইন অনুযায়ী:\n\n"
        for i, provision in enumerate(primary_provisions, 1):
            if provision.provision_text_bengali:
                primary_answer_bengali += f"{i}. {provision.section_number} ধারা: "
                primary_answer_bengali += f"{provision.provision_text_bengali[:200]}...\n\n"
        
        # Extract authority sources
        authority_sources = {}
        for provision in provisions:
            if provision.source_document in authority_sources:
                authority_sources[provision.source_document] = max(
                    authority_sources[provision.source_document],
                    provision.legal_authority
                )
            else:
                authority_sources[provision.source_document] = provision.legal_authority
        
        # Generate cross-references
        cross_references = []
        for provision in provisions:
            cross_references.extend(provision.cross_references)
        cross_references = list(set(cross_references))  # Remove duplicates
        
        # Determine if expert review is recommended
        avg_authority = sum(p.legal_authority for p in provisions) / len(provisions) if provisions else 0
        expert_review_needed = (
            cross_doc_query.query_complexity in [QueryComplexity.COMPLEX, QueryComplexity.ENTERPRISE] or
            avg_authority < self.resolution_config['expert_review_threshold'] * 100
        )
        
        synthesized_response = SynthesizedResponse(
            query=cross_doc_query.original_query,
            primary_answer=primary_answer,
            primary_answer_bengali=primary_answer_bengali,
            supporting_provisions=provisions,
            legal_reasoning=[],  # Will be added in next step
            confidence_score=0.0,  # Will be calculated
            completeness_score=0.0,  # Will be calculated
            authority_sources=authority_sources,
            temporal_accuracy=1.0,  # Will be refined
            cross_references=cross_references,
            caveats_and_conditions=[],
            expert_review_recommended=expert_review_needed,
            response_metadata={
                'query_complexity': cross_doc_query.query_complexity.value,
                'resolution_strategy': cross_doc_query.resolution_strategy.value,
                'total_provisions': len(provisions),
                'primary_provisions': len(primary_provisions),
                'generated_timestamp': datetime.now().isoformat()
            }
        )
        
        return synthesized_response
    
    def _add_legal_reasoning(self, response: SynthesizedResponse, 
                            provisions: List[LegalProvision]) -> SynthesizedResponse:
        """Add comprehensive legal reasoning to response"""
        
        reasoning_steps = []
        
        # Step 1: Query analysis
        reasoning_steps.append(
            f"1. Query Analysis: Identified {response.response_metadata['query_complexity']} query "
            f"requiring {response.response_metadata['total_provisions']} legal provisions."
        )
        
        # Step 2: Document hierarchy application
        if len(response.authority_sources) > 1:
            highest_authority_doc = max(response.authority_sources.keys(), 
                                      key=lambda k: response.authority_sources[k])
            reasoning_steps.append(
                f"2. Legal Hierarchy: Applied precedence with {highest_authority_doc} "
                f"(authority level: {response.authority_sources[highest_authority_doc]}) taking precedence."
            )
        
        # Step 3: Temporal consideration
        if any(p.temporal_validity != '2023-07-01' for p in provisions):
            reasoning_steps.append(
                f"3. Temporal Analysis: Considered multiple law versions with temporal precedence applied."
            )
        
        # Step 4: Cross-reference integration  
        if response.cross_references:
            reasoning_steps.append(
                f"4. Cross-References: Integrated {len(response.cross_references)} related provisions "
                f"for comprehensive coverage."
            )
        
        # Step 5: Synthesis rationale
        reasoning_steps.append(
            f"5. Response Synthesis: Combined {len(response.supporting_provisions)} provisions "
            f"using {response.response_metadata['resolution_strategy']} strategy."
        )
        
        # Add caveats and conditions
        caveats = []
        if response.expert_review_recommended:
            caveats.append("Complex query - professional tax advisor consultation recommended")
        
        if len(response.authority_sources) > 3:
            caveats.append("Multiple legal sources involved - verify current versions")
        
        if any(p.legal_authority < 80 for p in provisions):
            caveats.append("Some provisions from interpretive sources - confirm with primary law")
        
        response.legal_reasoning = reasoning_steps
        response.caveats_and_conditions = caveats
        
        return response
    
    def _calculate_response_scores(self, response: SynthesizedResponse) -> SynthesizedResponse:
        """Calculate confidence and completeness scores for response"""
        
        if not response.supporting_provisions:
            response.confidence_score = 0.0
            response.completeness_score = 0.0
            return response
        
        # Calculate confidence score
        authority_scores = [p.legal_authority / 100.0 for p in response.supporting_provisions]
        avg_authority = sum(authority_scores) / len(authority_scores)
        
        # Adjust for number of sources
        source_diversity = len(response.authority_sources)
        source_bonus = min(source_diversity / 5.0, 0.2)  # Max 0.2 bonus for multiple sources
        
        # Temporal accuracy consideration
        temporal_factor = response.temporal_accuracy
        
        confidence_score = (
            avg_authority * 0.6 +  # Authority weight
            source_bonus +        # Source diversity
            temporal_factor * 0.2 # Temporal accuracy
        )
        response.confidence_score = min(confidence_score, 1.0)
        
        # Calculate completeness score
        expected_concepts = max(len(response.query.split()) // 3, 1)  # Rough estimate
        covered_concepts = len(response.supporting_provisions)
        
        completeness_score = min(covered_concepts / expected_concepts, 1.0)
        response.completeness_score = completeness_score
        
        return response
    
    def resolve_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Main interface for cross-document query resolution
        
        Args:
            query: Legal query string
            **kwargs: Additional resolution parameters
            
        Returns:
            Comprehensive resolution result with legal reasoning
        """
        logger.info(f"Resolving cross-document query: {query[:50]}...")
        
        # Analyze query complexity
        cross_doc_query = self.analyze_query_complexity(query)
        
        # Override parameters with kwargs
        for key, value in kwargs.items():
            if hasattr(cross_doc_query, key):
                setattr(cross_doc_query, key, value)
        
        # Resolve query
        synthesized_response = self.resolve_cross_document_query(cross_doc_query)
        
        # Format comprehensive result
        resolution_result = {
            "query_analysis": {
                "original_query": cross_doc_query.original_query,
                "complexity": cross_doc_query.query_complexity.value,
                "resolution_strategy": cross_doc_query.resolution_strategy.value,
                "required_documents": cross_doc_query.required_documents,
                "temporal_context": cross_doc_query.temporal_context,
                "legal_concepts": cross_doc_query.legal_concepts,
                "procedural_elements": cross_doc_query.procedural_elements
            },
            "synthesized_response": {
                "primary_answer_english": synthesized_response.primary_answer,
                "primary_answer_bengali": synthesized_response.primary_answer_bengali,
                "confidence_score": round(synthesized_response.confidence_score, 3),
                "completeness_score": round(synthesized_response.completeness_score, 3),
                "expert_review_recommended": synthesized_response.expert_review_recommended
            },
            "legal_reasoning": synthesized_response.legal_reasoning,
            "supporting_evidence": [
                {
                    "provision_id": p.provision_id,
                    "source_document": p.source_document,
                    "section_reference": p.section_number,
                    "legal_authority": p.legal_authority,
                    "content_preview": p.provision_text[:150] + "..." if len(p.provision_text) > 150 else p.provision_text
                }
                for p in synthesized_response.supporting_provisions
            ],
            "authority_sources": synthesized_response.authority_sources,
            "cross_references": synthesized_response.cross_references,
            "caveats_and_conditions": synthesized_response.caveats_and_conditions,
            "resolution_metadata": {
                "total_provisions": len(synthesized_response.supporting_provisions),
                "temporal_accuracy": round(synthesized_response.temporal_accuracy, 3),
                "phase2_integration": bool(self.phase2_system),
                "phase25_integration": bool(self.phase25_system),
                "resolution_timestamp": datetime.now().isoformat()
            }
        }
        
        logger.info(f"Cross-document resolution complete: confidence={synthesized_response.confidence_score:.3f}")
        
        return resolution_result

def main():
    """Test the Cross-Document Resolver system"""
    
    # Initialize all dependent systems
    from legal_domain_embeddings import LegalDomainEmbeddings
    from context_aware_search import ContextAwareSearch
    from phase_2_5_integration import Phase25IntegratedSystem
    
    # Create Phase 2.5 system
    phase25_system = Phase25IntegratedSystem()
    
    # Create embeddings system and train
    embeddings_system = LegalDomainEmbeddings(phase25_system=phase25_system)
    corpus = embeddings_system.build_training_corpus()
    embeddings_system.fine_tune_embeddings(epochs=2)
    
    # Create search system
    search_system = ContextAwareSearch(
        embeddings_system=embeddings_system,
        phase25_system=phase25_system
    )
    
    # Create cross-document resolver
    resolver = CrossDocumentResolver(
        search_system=search_system,
        embeddings_system=embeddings_system,
        phase25_system=phase25_system
    )
    
    print("📄 Cross-Document Query Resolution System Test")
    print("=" * 60)
    
    # Test queries with increasing complexity
    test_queries = [
        # Simple query
        "২০২৫ অর্থবছরে করমুক্ত আয়ের সীমা কত?",
        
        # Moderate complexity
        "ইউটিউব আয়ের জন্য রিটার্ন দাখিল কতভাবে করবো?",
        
        # Complex cross-document query
        "একজন ইউটিউবার ৬ লক্ষ টাকা আয় করলে তার কর গণনা, রিটার্ন দাখিল এবং TDS নিয়ম কী?",
        
        # Enterprise-level query
        "২০২৪ থেকে ২০২৫ অর্থবছরে ডিজিটাল প্ল্যাটফর্ম আয়ের কর আইনের পরিবর্তন এবং সামগ্রিক প্রভাব বিশ্লেষণ"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query}")
        print("-" * (20 + len(str(i)) + len(query[:30])))
        
        # Resolve query
        result = resolver.resolve_query(query)
        
        # Display results
        analysis = result["query_analysis"]
        response = result["synthesized_response"]
        reasoning = result["legal_reasoning"]
        
        print(f"Complexity: {analysis['complexity'].title()}")
        print(f"Strategy: {analysis['resolution_strategy'].title()}")
        print(f"Required Documents: {len(analysis['required_documents'])}")
        print(f"Legal Concepts: {len(analysis['legal_concepts'])}")
        
        print(f"\nConfidence: {response['confidence_score']:.3f}")
        print(f"Completeness: {response['completeness_score']:.3f}")
        print(f"Expert Review: {'Recommended' if response['expert_review_recommended'] else 'Not Required'}")
        
        print(f"\nLegal Reasoning ({len(reasoning)} steps):")
        for step in reasoning[:3]:  # Show first 3 reasoning steps
            print(f"  • {step}")
        
        print(f"\nSupporting Evidence: {len(result['supporting_evidence'])} provisions")
        for j, evidence in enumerate(result['supporting_evidence'][:2], 1):  # Show top 2
            print(f"  {j}. {evidence['source_document']} Section {evidence['section_reference']}")
            print(f"     Authority: {evidence['legal_authority']}, Content: {evidence['content_preview'][:80]}...")
        
        if result['caveats_and_conditions']:
            print(f"\nCaveats: {'; '.join(result['caveats_and_conditions'])}")
    
    # Test resolution strategy comparison
    print(f"\n📊 Resolution Strategy Comparison:")
    print("-" * 35)
    
    comparison_query = "Section 44 এবং Finance Ordinance 2025 এর করমুক্ত সীমা"
    
    strategies = [
        ResolutionStrategy.HIERARCHICAL,
        ResolutionStrategy.COMPREHENSIVE,  
        ResolutionStrategy.AUTHORITATIVE
    ]
    
    for strategy in strategies:
        result = resolver.resolve_query(
            comparison_query, 
            resolution_strategy=strategy
        )
        
        print(f"\n{strategy.value.title()} Strategy:")
        print(f"  Provisions: {len(result['supporting_evidence'])}")
        print(f"  Confidence: {result['synthesized_response']['confidence_score']:.3f}")
        print(f"  Authority Sources: {len(result['authority_sources'])}")

if __name__ == "__main__":
    main()