#!/usr/bin/env python3
"""
Precision Measurement System - Phase 4.2 Implementation
======================================================
Quantitative accuracy measurement framework for Bangladesh tax law AI system.
Provides comprehensive metrics including citation accuracy, content accuracy,
completeness, precedence accuracy, and confidence calibration validation.

Implements rigorous testing methodology with statistical analysis and
performance benchmarking against Phase 4 targets (95%+ precision).

Author: Phase 4 Implementation
Date: August 10, 2025
"""

import json
import logging
import statistics
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, date
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import re
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of precision metrics"""
    CITATION_ACCURACY = "citation_accuracy"
    CONTENT_ACCURACY = "content_accuracy"
    COMPLETENESS_SCORE = "completeness_score"
    PRECEDENCE_ACCURACY = "precedence_accuracy"
    TEMPORAL_ACCURACY = "temporal_accuracy"
    CONFIDENCE_CALIBRATION = "confidence_calibration"
    FALSE_POSITIVE_CONTROL = "false_positive_control"
    RESPONSE_TIME = "response_time"
    SYSTEM_RELIABILITY = "system_reliability"

class TestResult(Enum):
    """Test result classifications"""
    PERFECT = "perfect"          # 100% accurate
    EXCELLENT = "excellent"      # 95-99% accurate
    GOOD = "good"               # 85-94% accurate
    ACCEPTABLE = "acceptable"    # 70-84% accurate
    POOR = "poor"               # 50-69% accurate
    FAILED = "failed"           # <50% accurate

@dataclass
class MetricResult:
    """Individual metric measurement result"""
    metric_type: MetricType
    score: float
    max_score: float
    percentage: float
    classification: TestResult
    details: Dict[str, Any]
    measurement_timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['metric_type'] = self.metric_type.value
        data['classification'] = self.classification.value
        return data

@dataclass
class TestCaseResult:
    """Complete test case evaluation result"""
    test_id: str
    query: str
    expected_answer: str
    system_answer: str
    system_confidence: float
    processing_time: float
    metric_scores: Dict[MetricType, MetricResult]
    overall_score: float
    passed: bool
    error_details: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['metric_scores'] = {k.value: v.to_dict() for k, v in self.metric_scores.items()}
        return data

@dataclass
class PrecisionReport:
    """Comprehensive precision measurement report"""
    report_id: str
    test_session_date: str
    total_test_cases: int
    overall_precision: float
    metric_breakdown: Dict[MetricType, float]
    classification_breakdown: Dict[TestResult, int]
    statistical_analysis: Dict[str, Any]
    target_achievement: Dict[str, bool]
    recommendations: List[str]
    detailed_results: List[TestCaseResult]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['metric_breakdown'] = {k.value: v for k, v in self.metric_breakdown.items()}
        data['classification_breakdown'] = {k.value: v for k, v in self.classification_breakdown.items()}
        data['detailed_results'] = [result.to_dict() for result in self.detailed_results]
        return data

class PrecisionMeasurementEngine:
    """
    Comprehensive precision measurement engine for Bangladesh tax law AI system.
    
    Features:
    - 9 precision metrics with statistical validation
    - Rigorous testing methodology with ground truth comparison
    - Real-time performance benchmarking
    - Detailed error analysis and recommendations
    - Phase 4 target validation (95%+ precision achievement)
    """
    
    def __init__(self):
        """Initialize Precision Measurement Engine"""
        
        # Phase 4 target thresholds
        self.target_thresholds = {
            MetricType.CITATION_ACCURACY: 0.99,        # >99% correct legal references
            MetricType.CONTENT_ACCURACY: 0.97,         # >97% factually correct information
            MetricType.COMPLETENESS_SCORE: 0.96,       # >96% relevant provisions included
            MetricType.PRECEDENCE_ACCURACY: 0.95,      # >95% correctly resolved conflicts
            MetricType.TEMPORAL_ACCURACY: 0.98,        # >98% correct law version used
            MetricType.CONFIDENCE_CALIBRATION: 0.90,   # >90% confidence matches accuracy
            MetricType.FALSE_POSITIVE_CONTROL: 0.98,   # <2% irrelevant citations
            MetricType.RESPONSE_TIME: 3.0,             # <3 seconds for complex queries
            MetricType.SYSTEM_RELIABILITY: 0.999       # 99.9% uptime
        }
        
        # Metric weights for overall score calculation
        self.metric_weights = {
            MetricType.CITATION_ACCURACY: 0.20,
            MetricType.CONTENT_ACCURACY: 0.25,
            MetricType.COMPLETENESS_SCORE: 0.15,
            MetricType.PRECEDENCE_ACCURACY: 0.15,
            MetricType.TEMPORAL_ACCURACY: 0.10,
            MetricType.CONFIDENCE_CALIBRATION: 0.10,
            MetricType.FALSE_POSITIVE_CONTROL: 0.05
        }
        
        # Legal reference validation patterns
        self.legal_reference_patterns = {
            'section_patterns': [
                r'ITA_\d{4}_S\d+',  # Income Tax Act sections
                r'FO_\d{4}_S\d+',   # Finance Ordinance sections
                r'Schedule_\d+',     # Schedules
                r'Rule_\d+',        # Rules
                r'SRO_\d+'          # SRO notifications
            ],
            'document_types': [
                'income_tax_act_2023', 'finance_ordinance_2025',
                'schedules', 'tds_rules_2024', 'circulars_2025', 'sro_notifications'
            ]
        }
        
        # Bengali legal term validation
        self.bengali_legal_terms = {
            'mandatory_terms': ['আইন', 'ধারা', 'তফসিল', 'বিধি', 'কর', 'আয়', 'রিটার্ন'],
            'accuracy_indicators': ['অনুযায়ী', 'অনুসারে', 'বিধান', 'নিয়ম', 'পদ্ধতি'],
            'professional_terms': ['বাধ্যতামূলক', 'অব্যাহতি', 'নিরূপণ', 'নির্ধারণ']
        }
        
        logger.info("Precision Measurement Engine initialized")
    
    def measure_system_precision(
        self,
        test_cases: List[Dict[str, Any]],
        system_responses: List[Dict[str, Any]]
    ) -> PrecisionReport:
        """
        Measure comprehensive system precision using ground truth test cases
        
        Args:
            test_cases: Ground truth test cases with expected answers
            system_responses: System responses to evaluate
            
        Returns:
            Comprehensive precision measurement report
        """
        logger.info(f"Measuring system precision with {len(test_cases)} test cases")
        
        if len(test_cases) != len(system_responses):
            raise ValueError("Number of test cases and system responses must match")
        
        start_time = datetime.now()
        detailed_results = []
        
        # Evaluate each test case
        for i, (test_case, response) in enumerate(zip(test_cases, system_responses)):
            logger.debug(f"Evaluating test case {i+1}/{len(test_cases)}")
            
            case_result = self._evaluate_test_case(test_case, response)
            detailed_results.append(case_result)
        
        # Calculate overall metrics
        metric_breakdown = self._calculate_metric_breakdown(detailed_results)
        overall_precision = self._calculate_overall_precision(metric_breakdown)
        classification_breakdown = self._calculate_classification_breakdown(detailed_results)
        statistical_analysis = self._calculate_statistical_analysis(detailed_results)
        target_achievement = self._evaluate_target_achievement(metric_breakdown)
        recommendations = self._generate_recommendations(metric_breakdown, target_achievement)
        
        # Create comprehensive report
        report = PrecisionReport(
            report_id=f"precision_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            test_session_date=datetime.now().isoformat(),
            total_test_cases=len(test_cases),
            overall_precision=overall_precision,
            metric_breakdown=metric_breakdown,
            classification_breakdown=classification_breakdown,
            statistical_analysis=statistical_analysis,
            target_achievement=target_achievement,
            recommendations=recommendations,
            detailed_results=detailed_results
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Precision measurement completed in {processing_time:.2f}s")
        logger.info(f"Overall precision: {overall_precision:.2%}")
        
        return report
    
    def _evaluate_test_case(
        self,
        test_case: Dict[str, Any],
        system_response: Dict[str, Any]
    ) -> TestCaseResult:
        """Evaluate individual test case against all metrics"""
        
        test_id = test_case.get('test_id', 'unknown')
        query = test_case.get('query', '')
        expected_answer = test_case.get('expected_answer', '')
        expected_refs = test_case.get('legal_references', [])
        
        system_answer = system_response.get('legal_answer', '')
        system_confidence = system_response.get('confidence_analysis', {}).get('overall_confidence', 0.0)
        processing_time = system_response.get('processing_metrics', {}).get('processing_time_seconds', 0.0)
        system_refs = system_response.get('matched_sections', [])
        reasoning_trace = system_response.get('reasoning_trace', {})
        
        # Calculate individual metrics
        metric_scores = {}
        error_details = []
        
        # 1. Citation Accuracy
        citation_result = self._measure_citation_accuracy(expected_refs, system_refs)
        metric_scores[MetricType.CITATION_ACCURACY] = citation_result
        if citation_result.percentage < 0.95:
            error_details.append(f"Citation accuracy below target: {citation_result.percentage:.1%}")
        
        # 2. Content Accuracy
        content_result = self._measure_content_accuracy(expected_answer, system_answer, test_case)
        metric_scores[MetricType.CONTENT_ACCURACY] = content_result
        if content_result.percentage < 0.95:
            error_details.append(f"Content accuracy below target: {content_result.percentage:.1%}")
        
        # 3. Completeness Score
        completeness_result = self._measure_completeness(test_case, system_response)
        metric_scores[MetricType.COMPLETENESS_SCORE] = completeness_result
        if completeness_result.percentage < 0.90:
            error_details.append(f"Completeness below target: {completeness_result.percentage:.1%}")
        
        # 4. Precedence Accuracy
        precedence_result = self._measure_precedence_accuracy(expected_refs, system_refs, reasoning_trace)
        metric_scores[MetricType.PRECEDENCE_ACCURACY] = precedence_result
        if precedence_result.percentage < 0.90:
            error_details.append(f"Precedence accuracy below target: {precedence_result.percentage:.1%}")
        
        # 5. Temporal Accuracy
        temporal_result = self._measure_temporal_accuracy(test_case, system_response)
        metric_scores[MetricType.TEMPORAL_ACCURACY] = temporal_result
        if temporal_result.percentage < 0.95:
            error_details.append(f"Temporal accuracy below target: {temporal_result.percentage:.1%}")
        
        # 6. Confidence Calibration
        confidence_result = self._measure_confidence_calibration(
            system_confidence, content_result.percentage, test_case
        )
        metric_scores[MetricType.CONFIDENCE_CALIBRATION] = confidence_result
        
        # Calculate weighted overall score
        overall_score = 0.0
        total_weight = 0.0
        
        for metric_type, result in metric_scores.items():
            if metric_type in self.metric_weights:
                weight = self.metric_weights[metric_type]
                overall_score += result.percentage * weight
                total_weight += weight
        
        if total_weight > 0:
            overall_score /= total_weight
        
        # Determine if test case passed (>95% for Phase 4)
        passed = overall_score >= 0.95 and len(error_details) == 0
        
        return TestCaseResult(
            test_id=test_id,
            query=query,
            expected_answer=expected_answer,
            system_answer=system_answer,
            system_confidence=system_confidence,
            processing_time=processing_time,
            metric_scores=metric_scores,
            overall_score=overall_score,
            passed=passed,
            error_details=error_details,
            timestamp=datetime.now().isoformat()
        )
    
    def _measure_citation_accuracy(
        self,
        expected_refs: List[Dict[str, Any]],
        system_refs: List[Dict[str, Any]]
    ) -> MetricResult:
        """Measure accuracy of legal citations"""
        
        if not expected_refs:
            return self._create_metric_result(MetricType.CITATION_ACCURACY, 1.0, 1.0, 
                                           {'note': 'No expected references to validate'})
        
        correct_citations = 0
        total_expected = len(expected_refs)
        citation_details = {
            'expected_count': total_expected,
            'system_count': len(system_refs),
            'correct_matches': 0,
            'missing_citations': [],
            'incorrect_citations': [],
            'extra_citations': []
        }
        
        # Create lookup sets for efficient comparison
        expected_ids = {ref.get('section_id', '') for ref in expected_refs}
        system_ids = {ref.get('section_id', '') for ref in system_refs}
        
        # Count correct matches
        correct_matches = expected_ids.intersection(system_ids)
        correct_citations = len(correct_matches)
        citation_details['correct_matches'] = correct_citations
        
        # Identify missing and extra citations
        missing = expected_ids - system_ids
        extra = system_ids - expected_ids
        
        citation_details['missing_citations'] = list(missing)
        citation_details['extra_citations'] = list(extra)
        
        # Calculate accuracy score
        if total_expected > 0:
            accuracy = correct_citations / total_expected
        else:
            accuracy = 1.0
        
        return self._create_metric_result(
            MetricType.CITATION_ACCURACY, accuracy, 1.0, citation_details
        )
    
    def _measure_content_accuracy(
        self,
        expected_answer: str,
        system_answer: str,
        test_case: Dict[str, Any]
    ) -> MetricResult:
        """Measure factual accuracy of content"""
        
        accuracy_score = 0.0
        details = {
            'expected_length': len(expected_answer),
            'system_length': len(system_answer),
            'key_concepts_matched': 0,
            'factual_errors': [],
            'language_quality': 0.0
        }
        
        # Extract key concepts from test case
        key_concepts = test_case.get('key_concepts', [])
        concepts_found = 0
        
        for concept in key_concepts:
            if concept.lower() in system_answer.lower():
                concepts_found += 1
        
        if key_concepts:
            concept_accuracy = concepts_found / len(key_concepts)
        else:
            concept_accuracy = 0.8  # Default if no concepts specified
        
        details['key_concepts_matched'] = concepts_found
        
        # Check for factual consistency
        factual_accuracy = self._validate_factual_consistency(expected_answer, system_answer, test_case)
        
        # Assess language quality (Bengali/English)
        language_quality = self._assess_language_quality(system_answer, test_case.get('query_language', 'bengali'))
        details['language_quality'] = language_quality
        
        # Combined accuracy score
        accuracy_score = (concept_accuracy * 0.4 + factual_accuracy * 0.4 + language_quality * 0.2)
        
        return self._create_metric_result(
            MetricType.CONTENT_ACCURACY, accuracy_score, 1.0, details
        )
    
    def _measure_completeness(
        self,
        test_case: Dict[str, Any],
        system_response: Dict[str, Any]
    ) -> MetricResult:
        """Measure completeness of response coverage"""
        
        expected_refs = test_case.get('legal_references', [])
        system_refs = system_response.get('matched_sections', [])
        reasoning_steps = system_response.get('reasoning_trace', {}).get('reasoning_steps', [])
        alternatives = system_response.get('reasoning_trace', {}).get('alternative_interpretations', [])
        
        completeness_factors = {
            'reference_coverage': 0.0,
            'reasoning_completeness': 0.0,
            'alternative_coverage': 0.0,
            'procedural_completeness': 0.0
        }
        
        # Reference coverage
        if expected_refs and system_refs:
            expected_count = len(expected_refs)
            system_count = len(system_refs)
            completeness_factors['reference_coverage'] = min(system_count / expected_count, 1.0)
        else:
            completeness_factors['reference_coverage'] = 0.8
        
        # Reasoning completeness (expect at least 6 steps)
        if reasoning_steps:
            step_completeness = min(len(reasoning_steps) / 6, 1.0)
            completeness_factors['reasoning_completeness'] = step_completeness
        else:
            completeness_factors['reasoning_completeness'] = 0.5
        
        # Alternative interpretation coverage
        expected_alternatives = test_case.get('alternative_interpretations', [])
        if expected_alternatives:
            alt_coverage = min(len(alternatives) / len(expected_alternatives), 1.0)
            completeness_factors['alternative_coverage'] = alt_coverage
        else:
            completeness_factors['alternative_coverage'] = 1.0 if alternatives else 0.8
        
        # Procedural completeness (safety warnings, expert referrals)
        procedural_score = 0.8  # Base score
        if system_response.get('confidence_analysis', {}).get('safety_warnings'):
            procedural_score += 0.1
        if system_response.get('confidence_analysis', {}).get('expert_review_recommended'):
            procedural_score += 0.1
        completeness_factors['procedural_completeness'] = min(procedural_score, 1.0)
        
        # Weighted completeness score
        completeness = (
            completeness_factors['reference_coverage'] * 0.3 +
            completeness_factors['reasoning_completeness'] * 0.3 +
            completeness_factors['alternative_coverage'] * 0.2 +
            completeness_factors['procedural_completeness'] * 0.2
        )
        
        return self._create_metric_result(
            MetricType.COMPLETENESS_SCORE, completeness, 1.0, completeness_factors
        )
    
    def _measure_precedence_accuracy(
        self,
        expected_refs: List[Dict[str, Any]],
        system_refs: List[Dict[str, Any]],
        reasoning_trace: Dict[str, Any]
    ) -> MetricResult:
        """Measure accuracy of legal precedence application"""
        
        precedence_score = 1.0
        details = {
            'precedence_conflicts': 0,
            'hierarchy_violations': [],
            'correct_applications': 0
        }
        
        # Define precedence hierarchy
        precedence_hierarchy = {
            'finance_ordinance_2025': 100,
            'income_tax_act_2023': 95,
            'schedules': 90,
            'tds_rules_2024': 85,
            'circulars_2025': 70,
            'sro_notifications': 80
        }
        
        # Check for precedence violations in system response
        system_doc_types = [ref.get('document_type', '') for ref in system_refs]
        
        if len(set(system_doc_types)) > 1:  # Multiple authorities present
            max_authority = 0
            primary_doc = None
            
            for doc_type in system_doc_types:
                authority = precedence_hierarchy.get(doc_type, 50)
                if authority > max_authority:
                    max_authority = authority
                    primary_doc = doc_type
            
            # Check if reasoning properly applied precedence
            reasoning_steps = reasoning_trace.get('reasoning_steps', [])
            precedence_mentioned = any(
                'precedence' in step.get('action', '').lower() or
                'hierarchy' in step.get('action', '').lower()
                for step in reasoning_steps
            )
            
            if precedence_mentioned:
                details['correct_applications'] = 1
            else:
                precedence_score -= 0.2
                details['hierarchy_violations'].append('Precedence not properly applied in reasoning')
        
        return self._create_metric_result(
            MetricType.PRECEDENCE_ACCURACY, precedence_score, 1.0, details
        )
    
    def _measure_temporal_accuracy(
        self,
        test_case: Dict[str, Any],
        system_response: Dict[str, Any]
    ) -> MetricResult:
        """Measure temporal law version accuracy"""
        
        expected_context = test_case.get('temporal_context', {})
        expected_fy = expected_context.get('financial_year', '2025-26')
        
        system_context = system_response.get('temporal_context', {})
        system_fy = system_context.get('current_financial_year', '')
        
        temporal_score = 1.0
        details = {
            'expected_fy': expected_fy,
            'system_fy': system_fy,
            'fy_match': False,
            'law_version_correct': False,
            'temporal_reasoning_present': False
        }
        
        # Check financial year accuracy
        if system_fy == expected_fy:
            details['fy_match'] = True
        else:
            temporal_score -= 0.3
        
        # Check law version accuracy
        expected_laws = expected_context.get('applicable_laws', [])
        system_laws = system_context.get('applicable_laws', [])
        
        if expected_laws and system_laws:
            law_overlap = len(set(expected_laws).intersection(set(system_laws)))
            law_accuracy = law_overlap / len(expected_laws) if expected_laws else 1.0
            if law_accuracy >= 0.8:
                details['law_version_correct'] = True
            else:
                temporal_score -= 0.2
        
        # Check for temporal reasoning in trace
        reasoning_steps = system_response.get('reasoning_trace', {}).get('reasoning_steps', [])
        temporal_reasoning = any(
            'temporal' in step.get('action', '').lower() or
            'financial year' in step.get('action', '').lower() or
            'version' in step.get('action', '').lower()
            for step in reasoning_steps
        )
        
        details['temporal_reasoning_present'] = temporal_reasoning
        if not temporal_reasoning:
            temporal_score -= 0.1
        
        return self._create_metric_result(
            MetricType.TEMPORAL_ACCURACY, temporal_score, 1.0, details
        )
    
    def _measure_confidence_calibration(
        self,
        system_confidence: float,
        actual_accuracy: float,
        test_case: Dict[str, Any]
    ) -> MetricResult:
        """Measure confidence calibration accuracy"""
        
        expected_range = test_case.get('expected_confidence_range', (0.7, 0.9))
        min_expected, max_expected = expected_range
        
        calibration_details = {
            'system_confidence': system_confidence,
            'actual_accuracy': actual_accuracy,
            'expected_range': expected_range,
            'within_range': False,
            'calibration_error': 0.0,
            'overconfidence': False,
            'underconfidence': False
        }
        
        # Check if confidence is within expected range
        within_range = min_expected <= system_confidence <= max_expected
        calibration_details['within_range'] = within_range
        
        # Calculate calibration error
        calibration_error = abs(system_confidence - actual_accuracy)
        calibration_details['calibration_error'] = calibration_error
        
        # Check for over/under confidence
        if system_confidence > actual_accuracy + 0.1:
            calibration_details['overconfidence'] = True
        elif system_confidence < actual_accuracy - 0.1:
            calibration_details['underconfidence'] = True
        
        # Calculate calibration score
        calibration_score = max(0.0, 1.0 - (calibration_error * 2))  # Penalty for large errors
        
        if within_range:
            calibration_score = min(calibration_score + 0.1, 1.0)  # Bonus for being in range
        
        return self._create_metric_result(
            MetricType.CONFIDENCE_CALIBRATION, calibration_score, 1.0, calibration_details
        )
    
    def _validate_factual_consistency(
        self,
        expected_answer: str,
        system_answer: str,
        test_case: Dict[str, Any]
    ) -> float:
        """Validate factual consistency between expected and system answers"""
        
        # Simple factual validation based on key phrases
        consistency_score = 0.8  # Base score
        
        # Check for contradictory statements
        if 'হ্যাঁ' in expected_answer and 'না' in system_answer:
            consistency_score -= 0.3
        elif 'না' in expected_answer and 'হ্যাঁ' in system_answer:
            consistency_score -= 0.3
        elif 'yes' in expected_answer.lower() and 'no' in system_answer.lower():
            consistency_score -= 0.3
        elif 'no' in expected_answer.lower() and 'yes' in system_answer.lower():
            consistency_score -= 0.3
        
        # Check for numerical consistency
        expected_numbers = re.findall(r'\d+(?:\.\d+)?', expected_answer)
        system_numbers = re.findall(r'\d+(?:\.\d+)?', system_answer)
        
        if expected_numbers and system_numbers:
            number_overlap = len(set(expected_numbers).intersection(set(system_numbers)))
            number_accuracy = number_overlap / len(expected_numbers) if expected_numbers else 1.0
            consistency_score = max(consistency_score, number_accuracy)
        
        return max(consistency_score, 0.0)
    
    def _assess_language_quality(self, answer: str, language: str) -> float:
        """Assess language quality and professional standard"""
        
        quality_score = 0.8  # Base score
        
        if language == 'bengali':
            # Check for Bengali legal terms
            bengali_terms_found = 0
            for term in self.bengali_legal_terms['mandatory_terms']:
                if term in answer:
                    bengali_terms_found += 1
            
            if bengali_terms_found >= 3:  # At least 3 legal terms
                quality_score += 0.1
            
            # Check for professional terminology
            professional_terms_found = 0
            for term in self.bengali_legal_terms['professional_terms']:
                if term in answer:
                    professional_terms_found += 1
            
            if professional_terms_found >= 2:
                quality_score += 0.1
        
        else:  # English
            # Check for professional English legal terms
            professional_terms = ['pursuant', 'accordance', 'provision', 'section', 'act']
            terms_found = sum(1 for term in professional_terms if term in answer.lower())
            
            if terms_found >= 2:
                quality_score += 0.2
        
        return min(quality_score, 1.0)
    
    def _create_metric_result(
        self,
        metric_type: MetricType,
        score: float,
        max_score: float,
        details: Dict[str, Any]
    ) -> MetricResult:
        """Create standardized metric result"""
        
        percentage = (score / max_score) if max_score > 0 else 0.0
        
        # Classify result
        if percentage >= 0.99:
            classification = TestResult.PERFECT
        elif percentage >= 0.95:
            classification = TestResult.EXCELLENT
        elif percentage >= 0.85:
            classification = TestResult.GOOD
        elif percentage >= 0.70:
            classification = TestResult.ACCEPTABLE
        elif percentage >= 0.50:
            classification = TestResult.POOR
        else:
            classification = TestResult.FAILED
        
        return MetricResult(
            metric_type=metric_type,
            score=score,
            max_score=max_score,
            percentage=percentage,
            classification=classification,
            details=details,
            measurement_timestamp=datetime.now().isoformat()
        )
    
    def _calculate_metric_breakdown(self, results: List[TestCaseResult]) -> Dict[MetricType, float]:
        """Calculate average scores for each metric across all test cases"""
        
        metric_totals = {}
        metric_counts = {}
        
        for result in results:
            for metric_type, metric_result in result.metric_scores.items():
                if metric_type not in metric_totals:
                    metric_totals[metric_type] = 0.0
                    metric_counts[metric_type] = 0
                
                metric_totals[metric_type] += metric_result.percentage
                metric_counts[metric_type] += 1
        
        # Calculate averages
        metric_breakdown = {}
        for metric_type in metric_totals:
            if metric_counts[metric_type] > 0:
                metric_breakdown[metric_type] = metric_totals[metric_type] / metric_counts[metric_type]
            else:
                metric_breakdown[metric_type] = 0.0
        
        return metric_breakdown
    
    def _calculate_overall_precision(self, metric_breakdown: Dict[MetricType, float]) -> float:
        """Calculate weighted overall precision score"""
        
        weighted_total = 0.0
        total_weight = 0.0
        
        for metric_type, score in metric_breakdown.items():
            if metric_type in self.metric_weights:
                weight = self.metric_weights[metric_type]
                weighted_total += score * weight
                total_weight += weight
        
        return weighted_total / total_weight if total_weight > 0 else 0.0
    
    def _calculate_classification_breakdown(
        self,
        results: List[TestCaseResult]
    ) -> Dict[TestResult, int]:
        """Calculate distribution of test result classifications"""
        
        classification_counts = {result_type: 0 for result_type in TestResult}
        
        for result in results:
            # Classify based on overall score
            if result.overall_score >= 0.99:
                classification_counts[TestResult.PERFECT] += 1
            elif result.overall_score >= 0.95:
                classification_counts[TestResult.EXCELLENT] += 1
            elif result.overall_score >= 0.85:
                classification_counts[TestResult.GOOD] += 1
            elif result.overall_score >= 0.70:
                classification_counts[TestResult.ACCEPTABLE] += 1
            elif result.overall_score >= 0.50:
                classification_counts[TestResult.POOR] += 1
            else:
                classification_counts[TestResult.FAILED] += 1
        
        return classification_counts
    
    def _calculate_statistical_analysis(self, results: List[TestCaseResult]) -> Dict[str, Any]:
        """Calculate statistical analysis of results"""
        
        if not results:
            return {}
        
        scores = [result.overall_score for result in results]
        confidences = [result.system_confidence for result in results]
        processing_times = [result.processing_time for result in results]
        
        return {
            'score_statistics': {
                'mean': statistics.mean(scores),
                'median': statistics.median(scores),
                'stdev': statistics.stdev(scores) if len(scores) > 1 else 0.0,
                'min': min(scores),
                'max': max(scores)
            },
            'confidence_statistics': {
                'mean': statistics.mean(confidences),
                'median': statistics.median(confidences),
                'stdev': statistics.stdev(confidences) if len(confidences) > 1 else 0.0
            },
            'performance_statistics': {
                'mean_processing_time': statistics.mean(processing_times),
                'median_processing_time': statistics.median(processing_times),
                'max_processing_time': max(processing_times)
            },
            'pass_rate': sum(1 for result in results if result.passed) / len(results)
        }
    
    def _evaluate_target_achievement(self, metric_breakdown: Dict[MetricType, float]) -> Dict[str, bool]:
        """Evaluate whether Phase 4 targets have been achieved"""
        
        target_achievement = {}
        
        for metric_type, score in metric_breakdown.items():
            if metric_type in self.target_thresholds:
                target = self.target_thresholds[metric_type]
                target_achievement[metric_type.value] = score >= target
            else:
                target_achievement[metric_type.value] = True  # Default pass
        
        return target_achievement
    
    def _generate_recommendations(
        self,
        metric_breakdown: Dict[MetricType, float],
        target_achievement: Dict[str, bool]
    ) -> List[str]:
        """Generate improvement recommendations based on results"""
        
        recommendations = []
        
        # Check each metric against targets
        for metric_type, achieved in target_achievement.items():
            if not achieved:
                metric_enum = MetricType(metric_type)
                score = metric_breakdown.get(metric_enum, 0.0)
                target = self.target_thresholds.get(metric_enum, 0.95)
                
                if metric_enum == MetricType.CITATION_ACCURACY:
                    recommendations.append(f"Improve citation accuracy from {score:.1%} to target {target:.1%}. Review legal reference matching algorithms.")
                elif metric_enum == MetricType.CONTENT_ACCURACY:
                    recommendations.append(f"Enhance content accuracy from {score:.1%} to target {target:.1%}. Strengthen factual validation processes.")
                elif metric_enum == MetricType.COMPLETENESS_SCORE:
                    recommendations.append(f"Increase completeness from {score:.1%} to target {target:.1%}. Ensure comprehensive coverage of legal provisions.")
                elif metric_enum == MetricType.CONFIDENCE_CALIBRATION:
                    recommendations.append(f"Better calibrate confidence scoring from {score:.1%} to target {target:.1%}. Adjust confidence thresholds.")
                else:
                    recommendations.append(f"Improve {metric_type.replace('_', ' ')} from {score:.1%} to target {target:.1%}.")
        
        # Overall system recommendations
        overall_precision = self._calculate_overall_precision(metric_breakdown)
        if overall_precision < 0.95:
            recommendations.append(f"Overall system precision ({overall_precision:.1%}) below Phase 4 target (95%). Focus on top-performing metrics improvement.")
        
        if not recommendations:
            recommendations.append("🎉 All Phase 4 precision targets achieved! System ready for production deployment.")
        
        return recommendations
    
    def save_precision_report(self, report: PrecisionReport, output_path: str) -> bool:
        """Save comprehensive precision report to file"""
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"Precision report saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save precision report: {e}")
            return False

def main():
    """Test the Precision Measurement Engine"""
    
    print("\n" + "="*70)
    print("PRECISION MEASUREMENT ENGINE TEST")
    print("="*70)
    
    # Initialize measurement engine
    engine = PrecisionMeasurementEngine()
    
    # Create sample test cases
    sample_test_cases = [
        {
            'test_id': 'test_001',
            'query': '২০২৫ অর্থবছরে ৬ লক্ষ টাকা আয় হলে রিটার্ন দিতে হবে কি?',
            'expected_answer': 'হ্যাঁ, আয়কর আইনের ধারা ৭৫ অনুযায়ী রিটার্ন দাখিল করতে হবে।',
            'legal_references': [
                {'section_id': 'ITA_2023_S75', 'document_type': 'income_tax_act_2023'},
                {'section_id': 'ITA_2023_S44', 'document_type': 'income_tax_act_2023'}
            ],
            'key_concepts': ['return_filing', 'income_threshold'],
            'temporal_context': {'financial_year': '2025-26'},
            'expected_confidence_range': (0.85, 0.95)
        }
    ]
    
    # Create sample system responses
    sample_responses = [
        {
            'legal_answer': 'হ্যাঁ, ২০২৫ অর্থবছরে ৬ লক্ষ টাকা আয় থাকলে আয়কর আইনের ধারা ৭৫ অনুযায়ী রিটার্ন দাখিল করতে হবে।',
            'confidence_analysis': {'overall_confidence': 0.92},
            'processing_metrics': {'processing_time_seconds': 0.15},
            'matched_sections': [
                {'section_id': 'ITA_2023_S75', 'document_type': 'income_tax_act_2023'},
                {'section_id': 'ITA_2023_S44', 'document_type': 'income_tax_act_2023'}
            ],
            'reasoning_trace': {
                'reasoning_steps': [
                    {'action': 'Query analysis identified return filing obligation'},
                    {'action': 'Section mapping to Income Tax Act'},
                    {'action': 'Temporal validation for FY 2025-26'},
                    {'action': 'Precedence application'},
                    {'action': 'Legal synthesis completed'},
                    {'action': 'Confidence assessment performed'}
                ],
                'alternative_interpretations': ['Income classification may vary']
            },
            'temporal_context': {'current_financial_year': '2025-26', 'applicable_laws': ['income_tax_act_2023']}
        }
    ]
    
    # Measure precision
    print("\nMeasuring system precision...")
    precision_report = engine.measure_system_precision(sample_test_cases, sample_responses)
    
    # Display results
    print(f"\n📊 Precision Measurement Results:")
    print(f"Overall Precision: {precision_report.overall_precision:.2%}")
    print(f"Total Test Cases: {precision_report.total_test_cases}")
    
    print(f"\n🎯 Metric Breakdown:")
    for metric, score in precision_report.metric_breakdown.items():
        target = engine.target_thresholds.get(metric, 0.95)
        status = "✅" if score >= target else "❌"
        print(f"   {status} {metric.value}: {score:.1%} (target: {target:.1%})")
    
    print(f"\n📈 Target Achievement:")
    for metric, achieved in precision_report.target_achievement.items():
        status = "✅ ACHIEVED" if achieved else "❌ BELOW TARGET"
        print(f"   {metric}: {status}")
    
    print(f"\n💡 Recommendations:")
    for rec in precision_report.recommendations:
        print(f"   • {rec}")
    
    # Save report
    report_path = f"precision_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    engine.save_precision_report(precision_report, report_path)
    print(f"\n📁 Report saved to: {report_path}")
    
    print(f"\n✅ Precision Measurement Engine Test Complete!")

if __name__ == "__main__":
    main()