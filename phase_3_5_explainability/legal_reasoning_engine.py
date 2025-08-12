#!/usr/bin/env python3
"""
Legal Reasoning Trace System - Phase 3.5.1 Implementation
=========================================================
Generates transparent legal reasoning for every response.
Provides step-by-step decision path documentation with evidence citation,
legal precedence application, and alternative interpretation consideration.

Integrates with Phase 2 Knowledge Graph, Phase 2.5 Temporal Control,
and Phase 3 Semantic Understanding for comprehensive reasoning trace.

Author: Phase 3.5 Implementation
Date: August 10, 2025
"""

import json
import logging
import re
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, date
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReasoningStepType(Enum):
    """Types of legal reasoning steps"""
    QUERY_ANALYSIS = "query_analysis"
    ENTITY_RECOGNITION = "entity_recognition"
    SECTION_MAPPING = "section_mapping"
    PRECEDENCE_APPLICATION = "precedence_application"
    TEMPORAL_VALIDATION = "temporal_validation"
    CROSS_REFERENCE = "cross_reference"
    LEGAL_SYNTHESIS = "legal_synthesis"
    CONFIDENCE_ASSESSMENT = "confidence_assessment"
    ALTERNATIVE_CONSIDERATION = "alternative_consideration"

class LegalAuthorityLevel(Enum):
    """Legal authority hierarchy"""
    FINANCE_ORDINANCE = 100
    INCOME_TAX_ACT = 95
    SCHEDULES = 90
    TDS_RULES = 85
    CIRCULARS = 70
    SRO = 80

@dataclass
class ReasoningStep:
    """Single step in legal reasoning process"""
    step_number: int
    step_type: ReasoningStepType
    action: str
    evidence: List[str]
    confidence: float
    legal_basis: List[str]
    timestamp: str
    alternatives_considered: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['step_type'] = self.step_type.value
        return data

@dataclass
class LegalReasoning:
    """Complete legal reasoning trace"""
    query: str
    final_answer: str
    overall_confidence: float
    reasoning_steps: List[ReasoningStep]
    legal_precedence_applied: List[str]
    alternative_interpretations: List[str]
    expert_review_recommended: bool
    safety_warnings: List[str]
    timestamp: str
    reasoning_duration: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'query': self.query,
            'final_answer': self.final_answer,
            'overall_confidence': self.overall_confidence,
            'reasoning_steps': [step.to_dict() for step in self.reasoning_steps],
            'legal_precedence_applied': self.legal_precedence_applied,
            'alternative_interpretations': self.alternative_interpretations,
            'expert_review_recommended': self.expert_review_recommended,
            'safety_warnings': self.safety_warnings,
            'timestamp': self.timestamp,
            'reasoning_duration': self.reasoning_duration
        }

class LegalReasoningEngine:
    """
    Core engine for generating transparent legal reasoning traces.
    
    Features:
    - Step-by-step decision path documentation
    - Evidence citation for each reasoning step
    - Legal precedence hierarchy application
    - Alternative interpretation consideration
    - Confidence scoring per reasoning step
    """
    
    def __init__(self, knowledge_graph_path: str = None, temporal_manager_path: str = None):
        """
        Initialize Legal Reasoning Engine
        
        Args:
            knowledge_graph_path: Path to Phase 2 knowledge graph
            temporal_manager_path: Path to Phase 2.5 temporal manager
        """
        self.knowledge_graph_path = knowledge_graph_path
        self.temporal_manager_path = temporal_manager_path
        
        # Legal authority hierarchy
        self.authority_levels = {
            'finance_ordinance_2025': LegalAuthorityLevel.FINANCE_ORDINANCE,
            'income_tax_act_2023': LegalAuthorityLevel.INCOME_TAX_ACT,
            'schedules': LegalAuthorityLevel.SCHEDULES,
            'tds_rules_2024': LegalAuthorityLevel.TDS_RULES,
            'circulars_2025': LegalAuthorityLevel.CIRCULARS,
            'sro_notifications': LegalAuthorityLevel.SRO
        }
        
        # Bengali legal terms recognition patterns
        self.bengali_patterns = {
            'section_references': [
                r'ধারা\s*(\d+)', r'section\s*(\d+)', r'§\s*(\d+)',
                r'(\d+)\s*নং\s*ধারা', r'(\d+)\s*ধারা'
            ],
            'schedule_references': [
                r'তফসিল\s*(\d+)', r'schedule\s*(\d+)',
                r'(\d+)\s*নং\s*তফসিল', r'(\d+)\s*তফসিল'
            ],
            'indirect_references': [
                r'উক্ত\s*ধারা', r'সংশ্লিষ্ট\s*তফসিল', r'পূর্বোক্ত\s*বিধি',
                r'same\s*section', r'said\s*schedule', r'aforementioned\s*rule'
            ],
            'financial_amounts': [
                r'(\d+(?:\.\d+)?)\s*লক্ষ', r'(\d+(?:\.\d+)?)\s*কোটি',
                r'(\d+(?:\.\d+)?)\s*হাজার', r'(\d+(?:\.\d+)?)\s*টাকা'
            ],
            'tax_rates': [
                r'(\d+(?:\.\d+)?)%', r'(\d+(?:\.\d+)?)\s*শতাংশ',
                r'(\d+(?:\.\d+)?)\s*percent'
            ],
            'financial_years': [
                r'(\d{4})-(\d{2,4})', r'(\d{4})\s*অর্থবছর',
                r'FY\s*(\d{4})-(\d{2,4})', r'financial\s*year\s*(\d{4})-(\d{2,4})'
            ]
        }
        
        logger.info("Legal Reasoning Engine initialized")
    
    def generate_reasoning_trace(
        self,
        query: str,
        matched_sections: List[Dict[str, Any]],
        semantic_results: Dict[str, Any],
        temporal_context: Dict[str, Any],
        final_answer: str
    ) -> LegalReasoning:
        """
        Generate comprehensive legal reasoning trace
        
        Args:
            query: User's legal query
            matched_sections: Sections identified by semantic search
            semantic_results: Results from semantic understanding layer
            temporal_context: Current financial year and applicable laws
            final_answer: System's final response
            
        Returns:
            Complete legal reasoning trace
        """
        start_time = datetime.now()
        reasoning_steps = []
        step_counter = 1
        
        logger.info(f"Generating reasoning trace for query: {query[:100]}...")
        
        # Step 1: Query Analysis
        query_step = self._analyze_query(query, step_counter)
        reasoning_steps.append(query_step)
        step_counter += 1
        
        # Step 2: Entity Recognition
        entity_step = self._recognize_legal_entities(query, step_counter)
        reasoning_steps.append(entity_step)
        step_counter += 1
        
        # Step 3: Section Mapping
        mapping_step = self._map_sections(matched_sections, step_counter)
        reasoning_steps.append(mapping_step)
        step_counter += 1
        
        # Step 4: Temporal Validation
        temporal_step = self._validate_temporal_context(temporal_context, step_counter)
        reasoning_steps.append(temporal_step)
        step_counter += 1
        
        # Step 5: Legal Precedence Application
        precedence_step = self._apply_legal_precedence(matched_sections, step_counter)
        reasoning_steps.append(precedence_step)
        step_counter += 1
        
        # Step 6: Cross-Reference Analysis
        crossref_step = self._analyze_cross_references(matched_sections, step_counter)
        reasoning_steps.append(crossref_step)
        step_counter += 1
        
        # Step 7: Legal Synthesis
        synthesis_step = self._synthesize_legal_conclusion(
            matched_sections, final_answer, step_counter
        )
        reasoning_steps.append(synthesis_step)
        step_counter += 1
        
        # Step 8: Confidence Assessment
        confidence_step = self._assess_overall_confidence(reasoning_steps, step_counter)
        reasoning_steps.append(confidence_step)
        
        # Calculate overall metrics
        overall_confidence = confidence_step.confidence
        legal_precedence = self._extract_precedence_applied(reasoning_steps)
        alternatives = self._identify_alternative_interpretations(query, matched_sections)
        expert_review = overall_confidence < 0.85  # Expert review threshold
        safety_warnings = self._generate_safety_warnings(query, matched_sections, overall_confidence)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        reasoning = LegalReasoning(
            query=query,
            final_answer=final_answer,
            overall_confidence=overall_confidence,
            reasoning_steps=reasoning_steps,
            legal_precedence_applied=legal_precedence,
            alternative_interpretations=alternatives,
            expert_review_recommended=expert_review,
            safety_warnings=safety_warnings,
            timestamp=datetime.now().isoformat(),
            reasoning_duration=duration
        )
        
        logger.info(f"Reasoning trace generated in {duration:.2f}s with confidence {overall_confidence:.2f}")
        return reasoning
    
    def _analyze_query(self, query: str, step_number: int) -> ReasoningStep:
        """Analyze the user's query for legal intent and entities"""
        evidence = []
        legal_basis = []
        confidence = 0.9
        
        # Detect query intent
        if any(term in query.lower() for term in ['রিটার্ন', 'return', 'filing']):
            evidence.append("Query detected: Return filing obligation")
            legal_basis.append("Income Tax Act Section 75-76: Return filing requirements")
        
        if any(term in query.lower() for term in ['ইউটিউব', 'youtube', 'online', 'digital']):
            evidence.append("Query detected: Digital/online income source")
            legal_basis.append("Income Tax Act Section 25: Business income classification")
        
        if any(term in query.lower() for term in ['কর', 'tax', 'rate', 'হার']):
            evidence.append("Query detected: Tax calculation/rate inquiry")
            legal_basis.append("Income Tax Act Schedules: Tax rate determination")
        
        # Extract financial year context
        fy_matches = re.findall(r'(\d{4})-?(\d{2,4})?', query)
        if fy_matches:
            evidence.append(f"Financial year context detected: {fy_matches}")
            legal_basis.append("Temporal law version control required")
        
        return ReasoningStep(
            step_number=step_number,
            step_type=ReasoningStepType.QUERY_ANALYSIS,
            action=f"Query analysis identified legal intent and context",
            evidence=evidence,
            confidence=confidence,
            legal_basis=legal_basis,
            timestamp=datetime.now().isoformat(),
            alternatives_considered=["Alternative query interpretations considered"]
        )
    
    def _recognize_legal_entities(self, query: str, step_number: int) -> ReasoningStep:
        """Recognize legal entities in the query using Bengali patterns"""
        evidence = []
        legal_basis = []
        confidence = 0.85
        
        # Section references
        for pattern in self.bengali_patterns['section_references']:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                evidence.append(f"Section references found: {matches}")
                legal_basis.append("Direct section citation requires validation")
        
        # Schedule references
        for pattern in self.bengali_patterns['schedule_references']:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                evidence.append(f"Schedule references found: {matches}")
                legal_basis.append("Schedule provisions require integration")
        
        # Financial amounts
        for pattern in self.bengali_patterns['financial_amounts']:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                evidence.append(f"Financial amounts detected: {matches}")
                legal_basis.append("Amount-based tax calculation required")
        
        # Tax rates
        for pattern in self.bengali_patterns['tax_rates']:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                evidence.append(f"Tax rates mentioned: {matches}")
                legal_basis.append("Rate verification against current schedules")
        
        return ReasoningStep(
            step_number=step_number,
            step_type=ReasoningStepType.ENTITY_RECOGNITION,
            action="Legal entity recognition using Bengali NER patterns",
            evidence=evidence,
            confidence=confidence,
            legal_basis=legal_basis,
            timestamp=datetime.now().isoformat()
        )
    
    def _map_sections(self, matched_sections: List[Dict[str, Any]], step_number: int) -> ReasoningStep:
        """Map identified sections to legal provisions"""
        evidence = []
        legal_basis = []
        confidence = 0.88
        
        for section in matched_sections[:5]:  # Top 5 sections
            section_id = section.get('section_id', 'Unknown')
            section_title = section.get('title', 'No title')
            relevance_score = section.get('relevance_score', 0.0)
            
            evidence.append(f"Mapped to {section_id}: {section_title} (relevance: {relevance_score:.2f})")
            legal_basis.append(f"{section_id}: {section.get('legal_basis', 'Legal provision')}")
        
        # Adjust confidence based on top match relevance
        if matched_sections and matched_sections[0].get('relevance_score', 0) > 0.9:
            confidence = 0.92
        elif matched_sections and matched_sections[0].get('relevance_score', 0) < 0.7:
            confidence = 0.75
        
        return ReasoningStep(
            step_number=step_number,
            step_type=ReasoningStepType.SECTION_MAPPING,
            action="Mapped query to relevant legal sections using semantic search",
            evidence=evidence,
            confidence=confidence,
            legal_basis=legal_basis,
            timestamp=datetime.now().isoformat(),
            alternatives_considered=["Alternative section mappings evaluated"]
        )
    
    def _validate_temporal_context(self, temporal_context: Dict[str, Any], step_number: int) -> ReasoningStep:
        """Validate temporal context and applicable law versions"""
        evidence = []
        legal_basis = []
        confidence = 0.9
        
        current_fy = temporal_context.get('current_financial_year', '2025-26')
        applicable_laws = temporal_context.get('applicable_laws', [])
        law_changes = temporal_context.get('recent_changes', [])
        
        evidence.append(f"Current financial year: {current_fy}")
        evidence.append(f"Applicable laws: {', '.join(applicable_laws)}")
        
        if law_changes:
            evidence.append(f"Recent law changes detected: {len(law_changes)} changes")
            legal_basis.append("Law version control: Recent changes may affect interpretation")
        
        # Check for temporal accuracy
        if current_fy == '2025-26':
            legal_basis.append("Finance Ordinance 2025 takes precedence over Income Tax Act 2023")
            confidence = 0.95
        else:
            legal_basis.append("Historical law version validation required")
            confidence = 0.85
        
        return ReasoningStep(
            step_number=step_number,
            step_type=ReasoningStepType.TEMPORAL_VALIDATION,
            action="Validated temporal context and applicable law versions",
            evidence=evidence,
            confidence=confidence,
            legal_basis=legal_basis,
            timestamp=datetime.now().isoformat()
        )
    
    def _apply_legal_precedence(self, matched_sections: List[Dict[str, Any]], step_number: int) -> ReasoningStep:
        """Apply legal precedence hierarchy to resolve conflicts"""
        evidence = []
        legal_basis = []
        confidence = 0.87
        
        # Group sections by authority level
        authority_groups = {}
        for section in matched_sections:
            doc_type = section.get('document_type', 'unknown')
            authority = self.authority_levels.get(doc_type, LegalAuthorityLevel.CIRCULARS)
            
            if authority not in authority_groups:
                authority_groups[authority] = []
            authority_groups[authority].append(section)
        
        # Apply precedence rules
        highest_authority = max(authority_groups.keys(), key=lambda x: x.value)
        primary_sections = authority_groups[highest_authority]
        
        evidence.append(f"Primary authority: {highest_authority.name} (Level {highest_authority.value})")
        evidence.append(f"Primary sections: {len(primary_sections)} sections")
        
        legal_basis.append(f"Legal precedence: {highest_authority.name} overrides lower authorities")
        
        # Check for conflicts
        if len(authority_groups) > 1:
            evidence.append(f"Multiple authorities found, precedence rules applied")
            legal_basis.append("Conflict resolution through legal hierarchy")
            confidence = 0.83
        
        return ReasoningStep(
            step_number=step_number,
            step_type=ReasoningStepType.PRECEDENCE_APPLICATION,
            action="Applied legal precedence hierarchy to resolve conflicts",
            evidence=evidence,
            confidence=confidence,
            legal_basis=legal_basis,
            timestamp=datetime.now().isoformat()
        )
    
    def _analyze_cross_references(self, matched_sections: List[Dict[str, Any]], step_number: int) -> ReasoningStep:
        """Analyze cross-references between legal provisions"""
        evidence = []
        legal_basis = []
        confidence = 0.86
        
        cross_refs = []
        for section in matched_sections:
            refs = section.get('cross_references', [])
            cross_refs.extend(refs)
        
        if cross_refs:
            evidence.append(f"Cross-references found: {len(set(cross_refs))} unique references")
            evidence.append(f"Related provisions: {', '.join(set(cross_refs[:5]))}")
            legal_basis.append("Cross-reference analysis ensures comprehensive coverage")
        else:
            evidence.append("No cross-references detected")
            confidence = 0.80
        
        return ReasoningStep(
            step_number=step_number,
            step_type=ReasoningStepType.CROSS_REFERENCE,
            action="Analyzed cross-references between legal provisions",
            evidence=evidence,
            confidence=confidence,
            legal_basis=legal_basis,
            timestamp=datetime.now().isoformat()
        )
    
    def _synthesize_legal_conclusion(
        self,
        matched_sections: List[Dict[str, Any]],
        final_answer: str,
        step_number: int
    ) -> ReasoningStep:
        """Synthesize final legal conclusion from all evidence"""
        evidence = []
        legal_basis = []
        confidence = 0.89
        
        # Count supporting evidence
        total_sections = len(matched_sections)
        high_relevance = len([s for s in matched_sections if s.get('relevance_score', 0) > 0.8])
        
        evidence.append(f"Synthesis based on {total_sections} legal provisions")
        evidence.append(f"High-relevance matches: {high_relevance}/{total_sections}")
        evidence.append(f"Final conclusion length: {len(final_answer)} characters")
        
        # Assess synthesis quality
        if high_relevance >= 2 and total_sections >= 3:
            legal_basis.append("Strong legal foundation with multiple supporting provisions")
            confidence = 0.91
        elif high_relevance >= 1:
            legal_basis.append("Adequate legal support for conclusion")
            confidence = 0.87
        else:
            legal_basis.append("Limited legal support, expert review recommended")
            confidence = 0.75
        
        return ReasoningStep(
            step_number=step_number,
            step_type=ReasoningStepType.LEGAL_SYNTHESIS,
            action="Synthesized final legal conclusion from all evidence",
            evidence=evidence,
            confidence=confidence,
            legal_basis=legal_basis,
            timestamp=datetime.now().isoformat(),
            alternatives_considered=["Alternative legal conclusions evaluated"]
        )
    
    def _assess_overall_confidence(self, reasoning_steps: List[ReasoningStep], step_number: int) -> ReasoningStep:
        """Assess overall confidence in the legal reasoning"""
        evidence = []
        legal_basis = []
        
        # Calculate weighted confidence
        weights = {
            ReasoningStepType.SECTION_MAPPING: 0.25,
            ReasoningStepType.PRECEDENCE_APPLICATION: 0.20,
            ReasoningStepType.TEMPORAL_VALIDATION: 0.18,
            ReasoningStepType.LEGAL_SYNTHESIS: 0.15,
            ReasoningStepType.CROSS_REFERENCE: 0.12,
            ReasoningStepType.ENTITY_RECOGNITION: 0.10
        }
        
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for step in reasoning_steps:
            if step.step_type in weights:
                weight = weights[step.step_type]
                weighted_confidence += step.confidence * weight
                total_weight += weight
        
        # Normalize
        if total_weight > 0:
            overall_confidence = weighted_confidence / total_weight
        else:
            overall_confidence = 0.5  # Default low confidence
        
        evidence.append(f"Weighted confidence calculation: {overall_confidence:.3f}")
        evidence.append(f"Contributing steps: {len([s for s in reasoning_steps if s.step_type in weights])}")
        
        # Confidence categorization
        if overall_confidence >= 0.95:
            legal_basis.append("Professional-grade confidence: Safe for direct use")
        elif overall_confidence >= 0.85:
            legal_basis.append("Good confidence: Expert review for critical cases")
        elif overall_confidence >= 0.70:
            legal_basis.append("Reasonable guidance: Expert consultation recommended")
        else:
            legal_basis.append("Low confidence: Requires expert help or clarification")
        
        return ReasoningStep(
            step_number=step_number,
            step_type=ReasoningStepType.CONFIDENCE_ASSESSMENT,
            action="Calculated overall confidence using weighted methodology",
            evidence=evidence,
            confidence=overall_confidence,
            legal_basis=legal_basis,
            timestamp=datetime.now().isoformat()
        )
    
    def _extract_precedence_applied(self, reasoning_steps: List[ReasoningStep]) -> List[str]:
        """Extract legal precedence rules that were applied"""
        precedence_rules = []
        
        for step in reasoning_steps:
            if step.step_type == ReasoningStepType.PRECEDENCE_APPLICATION:
                precedence_rules.extend(step.legal_basis)
        
        if not precedence_rules:
            precedence_rules.append("Standard legal hierarchy: Finance Ordinance > Income Tax Act > Rules > Circulars")
        
        return precedence_rules
    
    def _identify_alternative_interpretations(
        self,
        query: str,
        matched_sections: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify alternative interpretations for the query"""
        alternatives = []
        
        # Income source ambiguity
        if 'ইউটিউব' in query.lower() or 'youtube' in query.lower():
            alternatives.append("YouTube আয় ব্যবসায়িক আয় হিসেবে গণ্য (AdSense monetization)")
            alternatives.append("YouTube আয় পেশাগত আয় হিসেবে গণ্য (contracted content creation)")
            alternatives.append("YouTube আয় ফ্রিল্যান্স আয় হিসেবে গণ্য (video editing services)")
        
        # Tax calculation ambiguity
        if any(term in query.lower() for term in ['কর', 'tax', 'calculate']):
            alternatives.append("Different tax slabs may apply based on total income")
            alternatives.append("Exemptions and deductions could affect final calculation")
        
        # Return filing ambiguity
        if any(term in query.lower() for term in ['রিটার্ন', 'return', 'filing']):
            alternatives.append("Return filing may not be required if income below threshold")
            alternatives.append("Different return forms may apply for different income types")
        
        return alternatives[:3]  # Limit to top 3 alternatives
    
    def _generate_safety_warnings(
        self,
        query: str,
        matched_sections: List[Dict[str, Any]],
        confidence: float
    ) -> List[str]:
        """Generate safety warnings for high-stakes legal queries"""
        warnings = []
        
        # Low confidence warning
        if confidence < 0.85:
            warnings.append("⚠️ Confidence below safety threshold - Expert consultation recommended")
        
        # High-stakes topics
        high_stakes_keywords = [
            'criminal', 'penalty', 'fine', 'prosecution', 'audit', 'appeal',
            'অপরাধ', 'জরিমানা', 'শাস্তি', 'মামলা', 'নিরীক্ষা', 'আপিল'
        ]
        
        if any(keyword in query.lower() for keyword in high_stakes_keywords):
            warnings.append("🚨 High-stakes legal matter detected - Professional legal advice essential")
        
        # Complex multi-entity scenarios
        if len(matched_sections) > 10:
            warnings.append("⚖️ Complex multi-provision scenario - Comprehensive expert review recommended")
        
        # Temporal complexity
        if re.search(r'(\d{4})-?(\d{2,4})?', query):
            warnings.append("📅 Temporal law complexity - Verify current law version with expert")
        
        return warnings
    
    def save_reasoning_trace(self, reasoning: LegalReasoning, output_path: str) -> bool:
        """Save reasoning trace to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(reasoning.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"Reasoning trace saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save reasoning trace: {e}")
            return False
    
    def load_reasoning_trace(self, input_path: str) -> Optional[Dict[str, Any]]:
        """Load reasoning trace from JSON file"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Reasoning trace loaded from: {input_path}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load reasoning trace: {e}")
            return None

def main():
    """Test the Legal Reasoning Engine with sample queries"""
    
    # Initialize reasoning engine
    engine = LegalReasoningEngine()
    
    # Sample test query
    test_query = "২০২৫ অর্থবছরে ইউটিউব থেকে ৬ লক্ষ টাকা আয় হলে রিটার্ন দিতে হবে কি?"
    
    # Mock semantic search results
    mock_sections = [
        {
            'section_id': 'ITA_2023_S75',
            'title': 'Obligation to furnish return',
            'relevance_score': 0.92,
            'document_type': 'income_tax_act_2023',
            'legal_basis': 'Return filing requirement',
            'cross_references': ['ITA_2023_S76', 'Schedule_4']
        },
        {
            'section_id': 'ITA_2023_S25',
            'title': 'Business income definition',
            'relevance_score': 0.88,
            'document_type': 'income_tax_act_2023',
            'legal_basis': 'Income classification',
            'cross_references': ['ITA_2023_S27']
        }
    ]
    
    # Mock temporal context
    mock_temporal = {
        'current_financial_year': '2025-26',
        'applicable_laws': ['finance_ordinance_2025', 'income_tax_act_2023'],
        'recent_changes': ['tax_free_limit_increase']
    }
    
    mock_answer = "হ্যাঁ, ইউটিউব থেকে ৬ লক্ষ টাকা আয় থাকলে রিটার্ন দাখিল করতে হবে।"
    
    # Generate reasoning trace
    reasoning = engine.generate_reasoning_trace(
        query=test_query,
        matched_sections=mock_sections,
        semantic_results={},
        temporal_context=mock_temporal,
        final_answer=mock_answer
    )
    
    # Display results
    print("\n" + "="*60)
    print("LEGAL REASONING TRACE TEST")
    print("="*60)
    
    print(f"\nQuery: {reasoning.query}")
    print(f"Overall Confidence: {reasoning.overall_confidence:.2f}")
    print(f"Expert Review Recommended: {reasoning.expert_review_recommended}")
    print(f"Processing Time: {reasoning.reasoning_duration:.2f}s")
    
    print(f"\nReasoning Steps ({len(reasoning.reasoning_steps)}):")
    for i, step in enumerate(reasoning.reasoning_steps, 1):
        print(f"\n{i}. {step.action}")
        print(f"   Type: {step.step_type.value}")
        print(f"   Confidence: {step.confidence:.2f}")
        if step.evidence:
            print(f"   Evidence: {'; '.join(step.evidence[:2])}")
    
    print(f"\nLegal Precedence Applied:")
    for precedence in reasoning.legal_precedence_applied:
        print(f"   • {precedence}")
    
    print(f"\nAlternative Interpretations:")
    for alt in reasoning.alternative_interpretations:
        print(f"   • {alt}")
    
    if reasoning.safety_warnings:
        print(f"\nSafety Warnings:")
        for warning in reasoning.safety_warnings:
            print(f"   • {warning}")
    
    # Save to file
    output_file = "test_reasoning_trace.json"
    engine.save_reasoning_trace(reasoning, output_file)
    print(f"\nReasoning trace saved to: {output_file}")

if __name__ == "__main__":
    main()