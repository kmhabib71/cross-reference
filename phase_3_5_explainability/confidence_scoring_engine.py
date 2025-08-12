#!/usr/bin/env python3
"""
Multi-Factor Confidence Scoring System - Phase 3.5.2 Implementation
==================================================================
Assigns precise confidence scores to legal advice using weighted multi-factor analysis.
Implements safety thresholds with expert referral triggers for critical legal matters.

Integrates with Legal Reasoning Engine and provides calibrated confidence metrics
for professional-grade legal advice reliability assessment.

Author: Phase 3.5 Implementation
Date: August 10, 2025
"""

import json
import logging
import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, date
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Confidence level categories with thresholds"""
    PROFESSIONAL_GRADE = "professional_grade"    # 95-100%: Safe for direct use
    GOOD_ADVICE = "good_advice"                  # 85-94%: Expert review for critical cases
    REASONABLE_GUIDANCE = "reasonable_guidance"   # 70-84%: Expert consultation recommended
    LOW_CONFIDENCE = "low_confidence"            # <70%: Requires expert help

class SafetyTrigger(Enum):
    """Safety trigger types for expert referral"""
    LOW_CONFIDENCE = "low_confidence"
    HIGH_STAKES_TOPIC = "high_stakes_topic"
    CONTRADICTORY_PROVISIONS = "contradictory_provisions"
    TEMPORAL_CONFUSION = "temporal_confusion"
    COMPLEX_SCENARIO = "complex_scenario"
    CRIMINAL_IMPLICATIONS = "criminal_implications"

@dataclass
class ConfidenceFactors:
    """Individual confidence factors with weights"""
    section_match_confidence: float = 0.0      # How well query matches sections (30%)
    precedence_clarity: float = 0.0            # Clear legal hierarchy (25%)
    temporal_accuracy: float = 0.0             # Correct law version used (20%)
    completeness_score: float = 0.0            # All relevant provisions found (15%)
    consistency_score: float = 0.0             # Internal consistency (10%)
    ambiguity_penalty: float = 0.0             # Penalty for ambiguous cases (-10%)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class ConfidenceScore:
    """Complete confidence assessment"""
    overall_confidence: float
    confidence_level: ConfidenceLevel
    factors: ConfidenceFactors
    safety_triggers: List[SafetyTrigger]
    expert_review_recommended: bool
    safety_warnings: List[str]
    calculation_details: Dict[str, Any]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'overall_confidence': self.overall_confidence,
            'confidence_level': self.confidence_level.value,
            'factors': self.factors.to_dict(),
            'safety_triggers': [trigger.value for trigger in self.safety_triggers],
            'expert_review_recommended': self.expert_review_recommended,
            'safety_warnings': self.safety_warnings,
            'calculation_details': self.calculation_details,
            'timestamp': self.timestamp
        }

class ConfidenceScoringEngine:
    """
    Multi-factor confidence scoring engine for legal advice reliability.
    
    Features:
    - Weighted factor analysis with legal domain expertise
    - Safety thresholds with expert referral triggers
    - Calibrated confidence metrics for professional standards
    - Temporal law version impact assessment
    - Cross-validation with reasoning trace analysis
    """
    
    def __init__(self):
        """Initialize Confidence Scoring Engine"""
        
        # Confidence factor weights (must sum to 1.0)
        self.factor_weights = {
            'section_match_confidence': 0.30,  # Primary factor: how well sections match
            'precedence_clarity': 0.25,        # Legal hierarchy clarity
            'temporal_accuracy': 0.20,         # Correct law version
            'completeness_score': 0.15,        # Comprehensive coverage
            'consistency_score': 0.10,         # Internal consistency
            'ambiguity_penalty': -0.10         # Penalty for ambiguity
        }
        
        # Safety thresholds
        self.safety_thresholds = {
            'expert_referral': 0.85,           # Below this: expert consultation
            'professional_grade': 0.95,        # Above this: professional quality
            'critical_matters': 0.90,          # High-stakes topics threshold
            'temporal_accuracy': 0.85          # Temporal law confusion threshold
        }
        
        # High-stakes keywords requiring elevated thresholds
        self.high_stakes_keywords = {
            'english': [
                'criminal', 'penalty', 'fine', 'prosecution', 'audit', 'appeal',
                'evasion', 'fraud', 'imprisonment', 'violation', 'offense'
            ],
            'bengali': [
                'অপরাধ', 'জরিমানা', 'শাস্তি', 'মামলা', 'নিরীক্ষা', 'আপিল',
                'ফাঁকি', 'প্রতারণা', 'কারাদণ্ড', 'লঙ্ঘন', 'অপরাধমূলক'
            ]
        }
        
        # Complex scenario indicators
        self.complexity_indicators = [
            'multiple_income_sources', 'multi_entity_structure', 'international_transactions',
            'corporate_individual_mix', 'temporal_complexity', 'conflicting_provisions'
        ]
        
        logger.info("Confidence Scoring Engine initialized")
    
    def calculate_confidence_score(
        self,
        query: str,
        matched_sections: List[Dict[str, Any]],
        reasoning_trace: Dict[str, Any],
        temporal_context: Dict[str, Any],
        semantic_results: Dict[str, Any]
    ) -> ConfidenceScore:
        """
        Calculate comprehensive confidence score for legal advice
        
        Args:
            query: User's legal query
            matched_sections: Sections matched by semantic search
            reasoning_trace: Output from legal reasoning engine
            temporal_context: Current law version context
            semantic_results: Semantic understanding results
            
        Returns:
            Complete confidence assessment
        """
        logger.info("Calculating confidence score for legal advice")
        
        # Calculate individual factors
        factors = ConfidenceFactors()
        
        # Factor 1: Section Match Confidence (30%)
        factors.section_match_confidence = self._calculate_section_match_confidence(
            matched_sections, semantic_results
        )
        
        # Factor 2: Legal Precedence Clarity (25%)
        factors.precedence_clarity = self._calculate_precedence_clarity(
            matched_sections, reasoning_trace
        )
        
        # Factor 3: Temporal Accuracy (20%)
        factors.temporal_accuracy = self._calculate_temporal_accuracy(
            query, temporal_context, reasoning_trace
        )
        
        # Factor 4: Completeness Score (15%)
        factors.completeness_score = self._calculate_completeness_score(
            query, matched_sections, reasoning_trace
        )
        
        # Factor 5: Consistency Score (10%)
        factors.consistency_score = self._calculate_consistency_score(
            matched_sections, reasoning_trace
        )
        
        # Factor 6: Ambiguity Penalty (-10%)
        factors.ambiguity_penalty = self._calculate_ambiguity_penalty(
            query, matched_sections, reasoning_trace
        )
        
        # Calculate weighted overall confidence
        overall_confidence = self._calculate_weighted_confidence(factors)
        
        # Determine confidence level
        confidence_level = self._determine_confidence_level(overall_confidence)
        
        # Identify safety triggers
        safety_triggers = self._identify_safety_triggers(
            query, overall_confidence, matched_sections, reasoning_trace
        )
        
        # Generate safety warnings
        safety_warnings = self._generate_safety_warnings(
            safety_triggers, confidence_level, overall_confidence
        )
        
        # Determine expert review recommendation
        expert_review = self._should_recommend_expert_review(
            overall_confidence, safety_triggers, confidence_level
        )
        
        # Create calculation details
        calculation_details = {
            'factor_weights': self.factor_weights,
            'weighted_contributions': {
                'section_match': factors.section_match_confidence * self.factor_weights['section_match_confidence'],
                'precedence_clarity': factors.precedence_clarity * self.factor_weights['precedence_clarity'],
                'temporal_accuracy': factors.temporal_accuracy * self.factor_weights['temporal_accuracy'],
                'completeness': factors.completeness_score * self.factor_weights['completeness_score'],
                'consistency': factors.consistency_score * self.factor_weights['consistency_score'],
                'ambiguity_penalty': factors.ambiguity_penalty * abs(self.factor_weights['ambiguity_penalty'])
            },
            'safety_thresholds_applied': self.safety_thresholds,
            'calculation_timestamp': datetime.now().isoformat()
        }
        
        confidence_score = ConfidenceScore(
            overall_confidence=overall_confidence,
            confidence_level=confidence_level,
            factors=factors,
            safety_triggers=safety_triggers,
            expert_review_recommended=expert_review,
            safety_warnings=safety_warnings,
            calculation_details=calculation_details,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Confidence score calculated: {overall_confidence:.3f} ({confidence_level.value})")
        return confidence_score
    
    def _calculate_section_match_confidence(
        self,
        matched_sections: List[Dict[str, Any]],
        semantic_results: Dict[str, Any]
    ) -> float:
        """Calculate confidence based on section matching quality"""
        if not matched_sections:
            return 0.0
        
        # Base confidence on top match relevance
        top_match_relevance = matched_sections[0].get('relevance_score', 0.0)
        
        # Boost for multiple high-quality matches
        high_quality_matches = len([
            s for s in matched_sections[:5] 
            if s.get('relevance_score', 0.0) > 0.8
        ])
        
        # Penalty for low relevance scores
        avg_relevance = np.mean([
            s.get('relevance_score', 0.0) for s in matched_sections[:3]
        ])
        
        # Calculate base confidence
        base_confidence = min(top_match_relevance * 1.1, 1.0)
        
        # Apply modifiers
        quality_boost = min(high_quality_matches * 0.05, 0.15)
        relevance_factor = avg_relevance * 0.1
        
        confidence = base_confidence + quality_boost + relevance_factor
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_precedence_clarity(
        self,
        matched_sections: List[Dict[str, Any]],
        reasoning_trace: Dict[str, Any]
    ) -> float:
        """Calculate confidence based on legal precedence clarity"""
        
        # Check for conflicting authorities
        authorities = set()
        for section in matched_sections:
            doc_type = section.get('document_type', 'unknown')
            authorities.add(doc_type)
        
        # High confidence for single clear authority
        if len(authorities) == 1:
            primary_authority = list(authorities)[0]
            if primary_authority in ['finance_ordinance_2025', 'income_tax_act_2023']:
                return 0.95
            return 0.85
        
        # Moderate confidence for clear hierarchy
        if 'finance_ordinance_2025' in authorities:
            return 0.90  # Finance ordinance overrides others
        elif 'income_tax_act_2023' in authorities and len(authorities) <= 3:
            return 0.85  # Clear hierarchy with main act
        
        # Lower confidence for complex authority mix
        if len(authorities) > 3:
            return 0.70  # Complex multi-authority scenario
        
        return 0.75  # Default for moderate complexity
    
    def _calculate_temporal_accuracy(
        self,
        query: str,
        temporal_context: Dict[str, Any],
        reasoning_trace: Dict[str, Any]
    ) -> float:
        """Calculate confidence based on temporal law accuracy"""
        
        current_fy = temporal_context.get('current_financial_year', '2025-26')
        applicable_laws = temporal_context.get('applicable_laws', [])
        recent_changes = temporal_context.get('recent_changes', [])
        
        # High confidence for current FY with recent ordinance
        if current_fy == '2025-26' and 'finance_ordinance_2025' in applicable_laws:
            base_confidence = 0.95
        elif current_fy == '2025-26':
            base_confidence = 0.90
        else:
            base_confidence = 0.80  # Historical queries have more uncertainty
        
        # Penalty for recent changes that might affect interpretation
        if recent_changes:
            change_penalty = min(len(recent_changes) * 0.02, 0.10)
            base_confidence -= change_penalty
        
        # Check for temporal confusion in query
        import re
        fy_mentions = len(re.findall(r'(\d{4})-?(\d{2,4})?', query))
        if fy_mentions > 1:
            base_confidence -= 0.05  # Multiple years mentioned
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _calculate_completeness_score(
        self,
        query: str,
        matched_sections: List[Dict[str, Any]],
        reasoning_trace: Dict[str, Any]
    ) -> float:
        """Calculate confidence based on answer completeness"""
        
        # Analyze query complexity
        query_entities = self._count_query_entities(query)
        
        # Count cross-references found
        total_cross_refs = 0
        for section in matched_sections:
            cross_refs = section.get('cross_references', [])
            total_cross_refs += len(cross_refs)
        
        # Base score on coverage
        if query_entities <= 2:
            required_sections = 2
        elif query_entities <= 4:
            required_sections = 3
        else:
            required_sections = 5
        
        section_coverage = min(len(matched_sections) / required_sections, 1.0)
        
        # Boost for cross-reference completeness
        cross_ref_boost = min(total_cross_refs * 0.02, 0.15)
        
        # Check reasoning trace completeness
        reasoning_steps = reasoning_trace.get('reasoning_steps', [])
        step_completeness = min(len(reasoning_steps) / 8, 1.0)  # Expect 8 standard steps
        
        completeness = (section_coverage * 0.6 + 
                       step_completeness * 0.3 + 
                       cross_ref_boost * 0.1)
        
        return min(max(completeness, 0.0), 1.0)
    
    def _calculate_consistency_score(
        self,
        matched_sections: List[Dict[str, Any]],
        reasoning_trace: Dict[str, Any]
    ) -> float:
        """Calculate confidence based on internal consistency"""
        
        # Check for contradictory sections
        contradictions = 0
        section_themes = []
        
        for section in matched_sections[:5]:
            title = section.get('title', '').lower()
            if 'exemption' in title and 'taxable' in [s.get('title', '').lower() for s in matched_sections]:
                contradictions += 1
            section_themes.append(title)
        
        # Penalty for contradictions
        contradiction_penalty = contradictions * 0.15
        
        # Check reasoning step consistency
        reasoning_steps = reasoning_trace.get('reasoning_steps', [])
        confidence_variance = 0.0
        
        if reasoning_steps:
            confidences = [step.get('confidence', 0.5) for step in reasoning_steps]
            if len(confidences) > 1:
                confidence_variance = np.var(confidences)
        
        # High variance in step confidence indicates inconsistency
        variance_penalty = min(confidence_variance * 0.5, 0.20)
        
        base_consistency = 0.90
        consistency = base_consistency - contradiction_penalty - variance_penalty
        
        return min(max(consistency, 0.0), 1.0)
    
    def _calculate_ambiguity_penalty(
        self,
        query: str,
        matched_sections: List[Dict[str, Any]],
        reasoning_trace: Dict[str, Any]
    ) -> float:
        """Calculate penalty for ambiguous situations (returns positive penalty value)"""
        
        penalty = 0.0
        
        # Ambiguous income source keywords
        ambiguous_terms = [
            'ইউটিউব', 'youtube', 'online', 'digital', 'freelance', 'consulting'
        ]
        
        for term in ambiguous_terms:
            if term in query.lower():
                penalty += 0.02
        
        # Multiple possible interpretations
        alternatives = reasoning_trace.get('alternative_interpretations', [])
        if len(alternatives) > 2:
            penalty += len(alternatives) * 0.01
        
        # Vague query language
        vague_terms = ['কিছু', 'some', 'maybe', 'perhaps', 'might', 'could']
        for term in vague_terms:
            if term in query.lower():
                penalty += 0.01
        
        # Missing critical details
        if len(query.split()) < 8:  # Very short query
            penalty += 0.03
        
        return min(penalty, 0.20)  # Cap penalty at 20%
    
    def _calculate_weighted_confidence(self, factors: ConfidenceFactors) -> float:
        """Calculate weighted overall confidence score"""
        
        weighted_sum = (
            factors.section_match_confidence * self.factor_weights['section_match_confidence'] +
            factors.precedence_clarity * self.factor_weights['precedence_clarity'] +
            factors.temporal_accuracy * self.factor_weights['temporal_accuracy'] +
            factors.completeness_score * self.factor_weights['completeness_score'] +
            factors.consistency_score * self.factor_weights['consistency_score'] -
            factors.ambiguity_penalty * abs(self.factor_weights['ambiguity_penalty'])
        )
        
        # Ensure result is in valid range
        return min(max(weighted_sum, 0.0), 1.0)
    
    def _determine_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determine confidence level category"""
        if confidence >= 0.95:
            return ConfidenceLevel.PROFESSIONAL_GRADE
        elif confidence >= 0.85:
            return ConfidenceLevel.GOOD_ADVICE
        elif confidence >= 0.70:
            return ConfidenceLevel.REASONABLE_GUIDANCE
        else:
            return ConfidenceLevel.LOW_CONFIDENCE
    
    def _identify_safety_triggers(
        self,
        query: str,
        confidence: float,
        matched_sections: List[Dict[str, Any]],
        reasoning_trace: Dict[str, Any]
    ) -> List[SafetyTrigger]:
        """Identify safety triggers requiring expert referral"""
        triggers = []
        
        # Low confidence trigger
        if confidence < self.safety_thresholds['expert_referral']:
            triggers.append(SafetyTrigger.LOW_CONFIDENCE)
        
        # High-stakes topic detection
        all_keywords = self.high_stakes_keywords['english'] + self.high_stakes_keywords['bengali']
        if any(keyword in query.lower() for keyword in all_keywords):
            triggers.append(SafetyTrigger.HIGH_STAKES_TOPIC)
        
        # Criminal implications
        criminal_keywords = ['criminal', 'fraud', 'evasion', 'অপরাধমূলক', 'প্রতারণা', 'ফাঁকি']
        if any(keyword in query.lower() for keyword in criminal_keywords):
            triggers.append(SafetyTrigger.CRIMINAL_IMPLICATIONS)
        
        # Contradictory provisions
        doc_types = set(section.get('document_type') for section in matched_sections)
        if len(doc_types) > 3:  # Multiple conflicting authorities
            triggers.append(SafetyTrigger.CONTRADICTORY_PROVISIONS)
        
        # Temporal confusion
        import re
        fy_mentions = len(re.findall(r'(\d{4})-?(\d{2,4})?', query))
        if fy_mentions > 1:
            triggers.append(SafetyTrigger.TEMPORAL_CONFUSION)
        
        # Complex scenario
        if len(matched_sections) > 8 or len(reasoning_trace.get('reasoning_steps', [])) > 10:
            triggers.append(SafetyTrigger.COMPLEX_SCENARIO)
        
        return triggers
    
    def _generate_safety_warnings(
        self,
        triggers: List[SafetyTrigger],
        confidence_level: ConfidenceLevel,
        confidence: float
    ) -> List[str]:
        """Generate appropriate safety warnings"""
        warnings = []
        
        if SafetyTrigger.LOW_CONFIDENCE in triggers:
            warnings.append(f"⚠️ Confidence ({confidence:.1%}) below safety threshold - Expert consultation recommended")
        
        if SafetyTrigger.HIGH_STAKES_TOPIC in triggers:
            warnings.append("🚨 High-stakes legal matter detected - Professional legal advice essential")
        
        if SafetyTrigger.CRIMINAL_IMPLICATIONS in triggers:
            warnings.append("⚖️ Criminal tax implications - Immediate professional legal consultation required")
        
        if SafetyTrigger.CONTRADICTORY_PROVISIONS in triggers:
            warnings.append("📋 Multiple conflicting legal provisions - Expert interpretation needed")
        
        if SafetyTrigger.TEMPORAL_CONFUSION in triggers:
            warnings.append("📅 Temporal law complexity detected - Verify current law version with expert")
        
        if SafetyTrigger.COMPLEX_SCENARIO in triggers:
            warnings.append("🔍 Complex multi-provision scenario - Comprehensive expert review recommended")
        
        # General confidence level warning
        if confidence_level == ConfidenceLevel.LOW_CONFIDENCE:
            warnings.append("🔴 Low confidence result - Clarification or expert help required")
        elif confidence_level == ConfidenceLevel.REASONABLE_GUIDANCE:
            warnings.append("🟡 Reasonable guidance provided - Consider expert consultation for critical decisions")
        
        return warnings
    
    def _should_recommend_expert_review(
        self,
        confidence: float,
        triggers: List[SafetyTrigger],
        confidence_level: ConfidenceLevel
    ) -> bool:
        """Determine if expert review should be recommended"""
        
        # Always recommend for low confidence
        if confidence < self.safety_thresholds['expert_referral']:
            return True
        
        # Always recommend for criminal implications
        if SafetyTrigger.CRIMINAL_IMPLICATIONS in triggers:
            return True
        
        # Recommend for high-stakes topics with medium confidence
        if (SafetyTrigger.HIGH_STAKES_TOPIC in triggers and 
            confidence < self.safety_thresholds['critical_matters']):
            return True
        
        # Recommend for multiple safety triggers
        if len(triggers) >= 2:
            return True
        
        # Recommend for complex scenarios with moderate confidence
        if (SafetyTrigger.COMPLEX_SCENARIO in triggers and 
            confidence_level != ConfidenceLevel.PROFESSIONAL_GRADE):
            return True
        
        return False
    
    def _count_query_entities(self, query: str) -> int:
        """Count legal entities mentioned in query"""
        entity_count = 0
        
        # Count sections
        import re
        section_patterns = [r'ধারা\s*\d+', r'section\s*\d+']
        for pattern in section_patterns:
            entity_count += len(re.findall(pattern, query, re.IGNORECASE))
        
        # Count schedules
        schedule_patterns = [r'তফসিল\s*\d+', r'schedule\s*\d+']
        for pattern in schedule_patterns:
            entity_count += len(re.findall(pattern, query, re.IGNORECASE))
        
        # Count amounts
        amount_patterns = [r'\d+\s*লক্ষ', r'\d+\s*কোটি', r'\d+\s*টাকা']
        for pattern in amount_patterns:
            entity_count += len(re.findall(pattern, query, re.IGNORECASE))
        
        return max(entity_count, 1)  # Minimum 1 entity
    
    def calibrate_confidence(
        self,
        historical_predictions: List[Tuple[float, bool]],
        target_accuracy: float = 0.90
    ) -> Dict[str, float]:
        """
        Calibrate confidence thresholds based on historical accuracy
        
        Args:
            historical_predictions: List of (confidence, was_correct) tuples
            target_accuracy: Target accuracy for confidence calibration
            
        Returns:
            Updated safety thresholds
        """
        if not historical_predictions:
            return self.safety_thresholds
        
        # Group predictions by confidence ranges
        confidence_ranges = {
            'high': [(c, correct) for c, correct in historical_predictions if c >= 0.90],
            'medium': [(c, correct) for c, correct in historical_predictions if 0.70 <= c < 0.90],
            'low': [(c, correct) for c, correct in historical_predictions if c < 0.70]
        }
        
        # Calculate actual accuracy for each range
        calibrated_thresholds = self.safety_thresholds.copy()
        
        for range_name, predictions in confidence_ranges.items():
            if predictions:
                actual_accuracy = sum(correct for _, correct in predictions) / len(predictions)
                avg_confidence = sum(conf for conf, _ in predictions) / len(predictions)
                
                logger.info(f"{range_name.title()} confidence range: "
                          f"avg={avg_confidence:.3f}, accuracy={actual_accuracy:.3f}")
                
                # Adjust thresholds if accuracy is below target
                if actual_accuracy < target_accuracy:
                    adjustment = (target_accuracy - actual_accuracy) * 0.5
                    if range_name == 'high':
                        calibrated_thresholds['professional_grade'] += adjustment
                    elif range_name == 'medium':
                        calibrated_thresholds['expert_referral'] += adjustment
        
        logger.info(f"Confidence calibration complete. Updated thresholds: {calibrated_thresholds}")
        return calibrated_thresholds
    
    def save_confidence_score(self, score: ConfidenceScore, output_path: str) -> bool:
        """Save confidence score to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(score.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"Confidence score saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save confidence score: {e}")
            return False

def main():
    """Test the Confidence Scoring Engine"""
    
    # Initialize scoring engine
    engine = ConfidenceScoringEngine()
    
    # Sample test data
    test_query = "২০২৫ অর্থবছরে ইউটিউব থেকে ৬ লক্ষ টাকা আয় হলে রিটার্ন দিতে হবে কি?"
    
    mock_sections = [
        {
            'section_id': 'ITA_2023_S75',
            'title': 'Obligation to furnish return',
            'relevance_score': 0.92,
            'document_type': 'income_tax_act_2023',
            'cross_references': ['ITA_2023_S76']
        },
        {
            'section_id': 'FO_2025_S5',
            'title': 'Tax-free threshold amendment',
            'relevance_score': 0.88,
            'document_type': 'finance_ordinance_2025',
            'cross_references': ['ITA_2023_S44']
        }
    ]
    
    mock_reasoning = {
        'reasoning_steps': [
            {'step_type': 'query_analysis', 'confidence': 0.90},
            {'step_type': 'section_mapping', 'confidence': 0.92},
            {'step_type': 'precedence_application', 'confidence': 0.88},
            {'step_type': 'temporal_validation', 'confidence': 0.95},
            {'step_type': 'legal_synthesis', 'confidence': 0.89}
        ],
        'alternative_interpretations': [
            'Could be professional income', 'Could be freelance income'
        ]
    }
    
    mock_temporal = {
        'current_financial_year': '2025-26',
        'applicable_laws': ['finance_ordinance_2025', 'income_tax_act_2023'],
        'recent_changes': ['tax_free_limit_increase']
    }
    
    # Calculate confidence score
    confidence_score = engine.calculate_confidence_score(
        query=test_query,
        matched_sections=mock_sections,
        reasoning_trace=mock_reasoning,
        temporal_context=mock_temporal,
        semantic_results={}
    )
    
    # Display results
    print("\n" + "="*60)
    print("CONFIDENCE SCORING ENGINE TEST")
    print("="*60)
    
    print(f"\nQuery: {test_query}")
    print(f"Overall Confidence: {confidence_score.overall_confidence:.3f} ({confidence_score.overall_confidence:.1%})")
    print(f"Confidence Level: {confidence_score.confidence_level.value}")
    print(f"Expert Review Recommended: {confidence_score.expert_review_recommended}")
    
    print(f"\nConfidence Factors:")
    factors_dict = confidence_score.factors.to_dict()
    for factor, value in factors_dict.items():
        print(f"   {factor}: {value:.3f}")
    
    print(f"\nWeighted Contributions:")
    for factor, contribution in confidence_score.calculation_details['weighted_contributions'].items():
        print(f"   {factor}: {contribution:.3f}")
    
    if confidence_score.safety_triggers:
        print(f"\nSafety Triggers:")
        for trigger in confidence_score.safety_triggers:
            print(f"   • {trigger.value}")
    
    if confidence_score.safety_warnings:
        print(f"\nSafety Warnings:")
        for warning in confidence_score.safety_warnings:
            print(f"   • {warning}")
    
    # Save results
    output_file = "test_confidence_score.json"
    engine.save_confidence_score(confidence_score, output_file)
    print(f"\nConfidence score saved to: {output_file}")

if __name__ == "__main__":
    main()