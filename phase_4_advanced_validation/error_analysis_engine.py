#!/usr/bin/env python3
"""
Error Analysis & Correction System - Phase 4.3 Implementation
=============================================================
Systematic error pattern recognition, root cause analysis, and iterative correction
recommendations for Bangladesh AI Tax Lawyer system. Identifies accuracy gaps,
analyzes failure modes, and provides systematic improvement strategies.

Features automated error classification, root cause analysis, correction tracking,
and continuous improvement recommendations with regression testing framework.

Author: Phase 4 Implementation
Date: August 10, 2025
Target: >95% precision through systematic error elimination
"""

import json
import logging
import re
from typing import Dict, List, Tuple, Optional, Any, Union, Set
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOT_AVAILABLE = True
except (ImportError, AttributeError) as e:
    PLOT_AVAILABLE = False
    print(f"⚠️ Plotting disabled due to: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ErrorCategory(Enum):
    """Categories of system errors"""
    CITATION_ERROR = "citation_error"              # Wrong legal reference
    CONTENT_INACCURACY = "content_inaccuracy"      # Factually incorrect information
    TEMPORAL_ERROR = "temporal_error"              # Wrong law version/FY
    PRECEDENCE_ERROR = "precedence_error"          # Wrong legal hierarchy
    COMPLETENESS_ERROR = "completeness_error"      # Missing relevant provisions
    CONFIDENCE_ERROR = "confidence_error"          # Miscalibrated confidence
    LANGUAGE_ERROR = "language_error"              # Bengali/English errors
    FORMATTING_ERROR = "formatting_error"          # Professional format issues
    SAFETY_ERROR = "safety_error"                  # Safety system failures
    INTEGRATION_ERROR = "integration_error"        # Phase integration issues

class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"      # Could cause legal/financial damage
    MAJOR = "major"           # Significant accuracy impact
    MINOR = "minor"           # Small quality issues
    COSMETIC = "cosmetic"     # Formatting/style issues

class RootCause(Enum):
    """Root cause categories"""
    DATA_QUALITY = "data_quality"                  # Poor source data
    ALGORITHM_LIMITATION = "algorithm_limitation"   # AI model limitations
    INTEGRATION_FAILURE = "integration_failure"    # Phase integration issues
    TEMPORAL_COMPLEXITY = "temporal_complexity"    # Complex temporal logic
    LINGUISTIC_COMPLEXITY = "linguistic_complexity" # Bengali language complexity
    EDGE_CASE_HANDLING = "edge_case_handling"      # Unusual scenarios
    CONFIDENCE_CALIBRATION = "confidence_calibration" # Confidence scoring issues
    SAFETY_SYSTEM = "safety_system"               # Safety mechanism failures
    KNOWLEDGE_GAP = "knowledge_gap"               # Missing legal knowledge
    PROCESSING_ERROR = "processing_error"         # System processing issues

@dataclass
class ErrorInstance:
    """Individual error instance"""
    error_id: str
    timestamp: datetime
    category: ErrorCategory
    severity: ErrorSeverity
    query: str
    expected_answer: str
    actual_answer: str
    confidence_score: float
    error_description: str
    affected_components: List[str]
    root_causes: List[RootCause]
    legal_domain: str
    
    # Analysis fields
    impact_score: float = 0.0
    reproducible: bool = False
    fixed: bool = False
    fix_description: Optional[str] = None
    fix_timestamp: Optional[datetime] = None

@dataclass
class ErrorPattern:
    """Recurring error pattern"""
    pattern_id: str
    pattern_name: str
    category: ErrorCategory
    frequency: int
    affected_queries: List[str]
    common_root_causes: List[RootCause]
    pattern_description: str
    fix_priority: int  # 1-5 (5 = highest)
    estimated_fix_effort: str  # "low", "medium", "high"
    fix_recommendations: List[str]

@dataclass
class CorrectionStrategy:
    """Systematic correction strategy"""
    strategy_id: str
    strategy_name: str
    target_error_categories: List[ErrorCategory]
    target_root_causes: List[RootCause]
    implementation_steps: List[str]
    expected_improvement: float  # Expected precision improvement %
    implementation_effort: str   # "low", "medium", "high"
    risk_assessment: str
    success_metrics: List[str]

@dataclass
class RegressionTestCase:
    """Regression testing case"""
    test_id: str
    original_error_id: str
    query: str
    expected_behavior: str
    test_status: str  # "pending", "passed", "failed"
    last_test_date: Optional[datetime] = None
    test_results: List[Dict] = field(default_factory=list)

class ErrorAnalysisEngine:
    """
    Comprehensive error analysis and correction system for Bangladesh AI Tax Lawyer
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize error analysis engine"""
        self.config = self._load_config(config_path)
        
        # Error tracking
        self.error_instances: List[ErrorInstance] = []
        self.error_patterns: List[ErrorPattern] = []
        self.correction_strategies: List[CorrectionStrategy] = []
        self.regression_tests: List[RegressionTestCase] = []
        
        # Analysis data
        self.error_trends = defaultdict(list)
        self.accuracy_history = []
        self.fix_effectiveness = {}
        
        # Bengali error patterns
        self.bengali_error_patterns = self._initialize_bengali_patterns()
        
        # Legal domain mappings
        self.legal_domains = {
            "individual_tax": "ব্যক্তিগত কর",
            "corporate_tax": "কর্পোরেট কর", 
            "tds": "উৎসে কর কর্তন",
            "advance_tax": "অগ্রিম কর",
            "exemptions": "অব্যাহতি",
            "appeals": "আপিল"
        }
        
        logger.info("Error Analysis Engine initialized successfully")

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load error analysis configuration"""
        default_config = {
            "error_thresholds": {
                "critical_threshold": 0.95,    # >95% confidence but wrong
                "major_threshold": 0.85,       # >85% confidence but wrong
                "pattern_frequency": 5,        # 5+ occurrences = pattern
                "fix_priority_threshold": 3    # Priority 3+ gets immediate attention
            },
            "analysis_windows": {
                "trend_window": 30,           # 30 days for trend analysis
                "pattern_window": 100,        # 100 queries for pattern detection
                "regression_window": 14       # 14 days for regression testing
            },
            "bengali_analysis": {
                "enable_linguistic_analysis": True,
                "common_mistakes": ["তারিখ", "পরিমাণ", "হার", "নিয়ম"],
                "critical_terms": ["কর", "আয়কর", "ভ্যাট", "জরিমানা"]
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config

    def _initialize_bengali_patterns(self) -> Dict[str, List[str]]:
        """Initialize Bengali-specific error patterns"""
        return {
            "temporal_errors": [
                r"আর্থিক বছর\s*\d{4}-\d{2,4}",
                r"কর বছর\s*\d{4}-\d{2,4}",
                r"\d{1,2}/\d{1,2}/\d{4}",
                r"তারিখ.*ভুল",
                r"সময়.*ভুল"
            ],
            "citation_errors": [
                r"ধারা\s*\d+",
                r"সূচি\s*\d+",
                r"নিয়ম\s*\d+",
                r"বিধি\s*\d+",
                r"অধ্যায়\s*\d+"
            ],
            "amount_errors": [
                r"টাকা\s*\d+",
                r"৳\s*\d+",
                r"লক্ষ",
                r"কোটি",
                r"হাজার"
            ],
            "rate_errors": [
                r"\d+\s*%",
                r"শতাংশ",
                r"হার\s*\d+",
                r"কর.*হার"
            ]
        }

    def analyze_error(self, query: str, expected_answer: str, actual_answer: str, 
                     confidence_score: float, system_metadata: Dict) -> ErrorInstance:
        """
        Analyze individual error instance and classify
        
        Args:
            query: User query that failed
            expected_answer: Correct answer 
            actual_answer: System's incorrect answer
            confidence_score: System confidence score
            system_metadata: Additional system information
            
        Returns:
            ErrorInstance with complete analysis
        """
        error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.error_instances):04d}"
        
        # Classify error category and severity
        category = self._classify_error_category(expected_answer, actual_answer, system_metadata)
        severity = self._determine_error_severity(category, confidence_score, query)
        
        # Identify root causes
        root_causes = self._identify_root_causes(category, query, expected_answer, 
                                               actual_answer, system_metadata)
        
        # Determine affected components
        affected_components = self._identify_affected_components(system_metadata, root_causes)
        
        # Calculate impact score
        impact_score = self._calculate_impact_score(category, severity, confidence_score)
        
        # Determine legal domain
        legal_domain = self._identify_legal_domain(query)
        
        error_instance = ErrorInstance(
            error_id=error_id,
            timestamp=datetime.now(),
            category=category,
            severity=severity,
            query=query,
            expected_answer=expected_answer,
            actual_answer=actual_answer,
            confidence_score=confidence_score,
            error_description=self._generate_error_description(category, expected_answer, actual_answer),
            affected_components=affected_components,
            root_causes=root_causes,
            legal_domain=legal_domain,
            impact_score=impact_score,
            reproducible=True  # Will be verified in testing
        )
        
        self.error_instances.append(error_instance)
        logger.info(f"Analyzed error {error_id}: {category.value} - {severity.value}")
        
        return error_instance

    def _classify_error_category(self, expected: str, actual: str, metadata: Dict) -> ErrorCategory:
        """Classify error into appropriate category"""
        
        # Check for citation errors (wrong legal references)
        if self._has_citation_mismatch(expected, actual):
            return ErrorCategory.CITATION_ERROR
        
        # Check for temporal errors (wrong FY/dates)
        if self._has_temporal_mismatch(expected, actual):
            return ErrorCategory.TEMPORAL_ERROR
        
        # Check for confidence calibration errors
        confidence = metadata.get('confidence_score', 0.0)
        if confidence > 0.9 and self._is_major_content_error(expected, actual):
            return ErrorCategory.CONFIDENCE_ERROR
        
        # Check for precedence errors (wrong legal hierarchy)
        if self._has_precedence_error(expected, actual):
            return ErrorCategory.PRECEDENCE_ERROR
        
        # Check for completeness errors (missing information)
        if self._is_incomplete_answer(expected, actual):
            return ErrorCategory.COMPLETENESS_ERROR
        
        # Check for Bengali language errors
        if self._has_language_error(expected, actual):
            return ErrorCategory.LANGUAGE_ERROR
        
        # Check for safety system failures
        if self._is_safety_failure(expected, actual, metadata):
            return ErrorCategory.SAFETY_ERROR
        
        # Default to content inaccuracy
        return ErrorCategory.CONTENT_INACCURACY

    def _has_citation_mismatch(self, expected: str, actual: str) -> bool:
        """Check for legal citation mismatches"""
        # Extract citations from both answers
        citation_patterns = [
            r'ধারা\s*(\d+)',
            r'সূচি\s*(\d+)', 
            r'নিয়ম\s*(\d+)',
            r'Section\s*(\d+)',
            r'Schedule\s*(\d+)'
        ]
        
        expected_citations = set()
        actual_citations = set()
        
        for pattern in citation_patterns:
            expected_citations.update(re.findall(pattern, expected, re.IGNORECASE))
            actual_citations.update(re.findall(pattern, actual, re.IGNORECASE))
        
        # Check for significant citation differences
        if expected_citations and actual_citations:
            overlap = expected_citations.intersection(actual_citations)
            total_unique = expected_citations.union(actual_citations)
            if len(overlap) / len(total_unique) < 0.7:  # <70% citation overlap
                return True
        
        return False

    def _has_temporal_mismatch(self, expected: str, actual: str) -> bool:
        """Check for financial year or date mismatches"""
        fy_patterns = [
            r'(\d{4})-(\d{2,4})',
            r'আর্থিক বছর.*(\d{4})',
            r'FY.*(\d{4})'
        ]
        
        for pattern in fy_patterns:
            expected_matches = re.findall(pattern, expected)
            actual_matches = re.findall(pattern, actual)
            
            if expected_matches != actual_matches and expected_matches and actual_matches:
                return True
        
        return False

    def _determine_error_severity(self, category: ErrorCategory, confidence: float, query: str) -> ErrorSeverity:
        """Determine error severity based on category and context"""
        
        # Critical errors - could cause legal/financial damage
        if category in [ErrorCategory.SAFETY_ERROR, ErrorCategory.CITATION_ERROR]:
            return ErrorSeverity.CRITICAL
        
        # High confidence but wrong = major error
        if confidence > 0.9 and category in [ErrorCategory.CONTENT_INACCURACY, 
                                             ErrorCategory.PRECEDENCE_ERROR]:
            return ErrorSeverity.MAJOR
        
        # Check for high-stakes query topics
        high_stakes_keywords = [
            "জরিমানা", "দণ্ড", "penalty", "fine", "criminal", "prosecution",
            "আপিল", "appeal", "court", "tribunal", "লক্ষ", "কোটি", "million"
        ]
        
        if any(keyword in query.lower() for keyword in high_stakes_keywords):
            return ErrorSeverity.MAJOR if confidence > 0.7 else ErrorSeverity.MINOR
        
        # Formatting and language errors are usually minor
        if category in [ErrorCategory.FORMATTING_ERROR, ErrorCategory.LANGUAGE_ERROR]:
            return ErrorSeverity.MINOR if confidence < 0.8 else ErrorSeverity.MAJOR
        
        # Default classification
        if confidence > 0.8:
            return ErrorSeverity.MAJOR
        elif confidence > 0.6:
            return ErrorSeverity.MINOR
        else:
            return ErrorSeverity.COSMETIC

    def _identify_root_causes(self, category: ErrorCategory, query: str, expected: str, 
                            actual: str, metadata: Dict) -> List[RootCause]:
        """Identify potential root causes for the error"""
        root_causes = []
        
        # Algorithm limitation indicators
        if category == ErrorCategory.CONFIDENCE_ERROR:
            root_causes.append(RootCause.CONFIDENCE_CALIBRATION)
        
        # Data quality issues
        if self._has_data_quality_indicators(expected, actual, metadata):
            root_causes.append(RootCause.DATA_QUALITY)
        
        # Bengali linguistic complexity
        if self._is_complex_bengali_query(query):
            root_causes.append(RootCause.LINGUISTIC_COMPLEXITY)
        
        # Temporal complexity
        if self._has_temporal_complexity(query):
            root_causes.append(RootCause.TEMPORAL_COMPLEXITY)
        
        # Edge case handling
        if self._is_edge_case(query, metadata):
            root_causes.append(RootCause.EDGE_CASE_HANDLING)
        
        # Integration failures
        if self._has_integration_issues(metadata):
            root_causes.append(RootCause.INTEGRATION_FAILURE)
        
        # Knowledge gaps
        if category == ErrorCategory.COMPLETENESS_ERROR:
            root_causes.append(RootCause.KNOWLEDGE_GAP)
        
        # Safety system issues
        if category == ErrorCategory.SAFETY_ERROR:
            root_causes.append(RootCause.SAFETY_SYSTEM)
        
        return root_causes if root_causes else [RootCause.ALGORITHM_LIMITATION]

    def identify_error_patterns(self, min_frequency: int = 5) -> List[ErrorPattern]:
        """
        Identify recurring error patterns from accumulated error data
        
        Args:
            min_frequency: Minimum occurrences to consider as pattern
            
        Returns:
            List of identified error patterns
        """
        if len(self.error_instances) < min_frequency:
            logger.warning(f"Not enough errors ({len(self.error_instances)}) to identify patterns")
            return []
        
        # Group errors by various criteria
        category_groups = defaultdict(list)
        root_cause_groups = defaultdict(list)  
        domain_groups = defaultdict(list)
        query_similarity_groups = defaultdict(list)
        
        for error in self.error_instances:
            category_groups[error.category].append(error)
            domain_groups[error.legal_domain].append(error)
            
            for root_cause in error.root_causes:
                root_cause_groups[root_cause].append(error)
            
            # Group by query similarity (simplified)
            query_key = self._get_query_similarity_key(error.query)
            query_similarity_groups[query_key].append(error)
        
        patterns = []
        
        # Identify category-based patterns
        for category, errors in category_groups.items():
            if len(errors) >= min_frequency:
                pattern = self._create_pattern_from_errors(
                    f"PATTERN_{category.value}_{len(patterns):03d}",
                    f"Recurring {category.value} errors",
                    category,
                    errors
                )
                patterns.append(pattern)
        
        # Identify root cause patterns
        for root_cause, errors in root_cause_groups.items():
            if len(errors) >= min_frequency:
                # Find most common category for this root cause
                common_category = Counter([e.category for e in errors]).most_common(1)[0][0]
                
                pattern = self._create_pattern_from_errors(
                    f"PATTERN_RC_{root_cause.value}_{len(patterns):03d}",
                    f"Errors caused by {root_cause.value}",
                    common_category,
                    errors
                )
                patterns.append(pattern)
        
        # Identify domain-specific patterns
        for domain, errors in domain_groups.items():
            if len(errors) >= min_frequency:
                common_category = Counter([e.category for e in errors]).most_common(1)[0][0]
                
                pattern = self._create_pattern_from_errors(
                    f"PATTERN_DOM_{domain}_{len(patterns):03d}",
                    f"Errors in {domain} domain",
                    common_category,
                    errors
                )
                patterns.append(pattern)
        
        self.error_patterns.extend(patterns)
        logger.info(f"Identified {len(patterns)} new error patterns")
        
        return patterns

    def _create_pattern_from_errors(self, pattern_id: str, pattern_name: str, 
                                  category: ErrorCategory, errors: List[ErrorInstance]) -> ErrorPattern:
        """Create error pattern from group of similar errors"""
        
        # Calculate frequency and affected queries
        frequency = len(errors)
        affected_queries = [e.query[:100] + "..." if len(e.query) > 100 else e.query 
                          for e in errors[:10]]  # Limit to first 10 for readability
        
        # Find common root causes
        root_cause_counter = Counter()
        for error in errors:
            root_cause_counter.update(error.root_causes)
        
        common_root_causes = [rc for rc, count in root_cause_counter.most_common(3)]
        
        # Generate pattern description
        pattern_description = self._generate_pattern_description(category, common_root_causes, errors)
        
        # Determine fix priority (1-5, 5=highest)
        fix_priority = self._calculate_fix_priority(category, errors)
        
        # Estimate fix effort
        estimated_effort = self._estimate_fix_effort(common_root_causes, frequency)
        
        # Generate fix recommendations
        fix_recommendations = self._generate_fix_recommendations(category, common_root_causes, errors)
        
        return ErrorPattern(
            pattern_id=pattern_id,
            pattern_name=pattern_name,
            category=category,
            frequency=frequency,
            affected_queries=affected_queries,
            common_root_causes=common_root_causes,
            pattern_description=pattern_description,
            fix_priority=fix_priority,
            estimated_fix_effort=estimated_effort,
            fix_recommendations=fix_recommendations
        )

    def generate_correction_strategies(self) -> List[CorrectionStrategy]:
        """
        Generate systematic correction strategies based on identified patterns
        
        Returns:
            List of prioritized correction strategies
        """
        if not self.error_patterns:
            logger.warning("No error patterns identified. Running pattern identification first...")
            self.identify_error_patterns()
        
        strategies = []
        
        # Strategy 1: Citation Accuracy Improvement
        citation_errors = [p for p in self.error_patterns if p.category == ErrorCategory.CITATION_ERROR]
        if citation_errors:
            strategy = CorrectionStrategy(
                strategy_id="STRAT_CITATION_001",
                strategy_name="Legal Citation Accuracy Enhancement",
                target_error_categories=[ErrorCategory.CITATION_ERROR],
                target_root_causes=[RootCause.DATA_QUALITY, RootCause.KNOWLEDGE_GAP],
                implementation_steps=[
                    "1. Audit and validate all legal references in knowledge base",
                    "2. Implement citation verification system with government databases",
                    "3. Add real-time citation validation during response generation",
                    "4. Create citation accuracy regression tests",
                    "5. Implement citation confidence scoring"
                ],
                expected_improvement=5.0,  # 5% precision improvement expected
                implementation_effort="high",
                risk_assessment="low - improves system reliability",
                success_metrics=[
                    "Citation accuracy >99%",
                    "Zero critical citation errors",
                    "Legal reference validation coverage >95%"
                ]
            )
            strategies.append(strategy)
        
        # Strategy 2: Temporal Accuracy Improvement
        temporal_errors = [p for p in self.error_patterns if p.category == ErrorCategory.TEMPORAL_ERROR]
        if temporal_errors:
            strategy = CorrectionStrategy(
                strategy_id="STRAT_TEMPORAL_001",
                strategy_name="Financial Year and Date Accuracy Enhancement",
                target_error_categories=[ErrorCategory.TEMPORAL_ERROR],
                target_root_causes=[RootCause.TEMPORAL_COMPLEXITY, RootCause.ALGORITHM_LIMITATION],
                implementation_steps=[
                    "1. Enhance temporal validation in Phase 2.5 integration",
                    "2. Implement automatic financial year detection and validation",
                    "3. Add temporal context awareness to query processing",
                    "4. Create comprehensive temporal testing scenarios",
                    "5. Implement temporal confidence penalties for ambiguous dates"
                ],
                expected_improvement=3.0,
                implementation_effort="medium", 
                risk_assessment="low - builds on existing Phase 2.5 work",
                success_metrics=[
                    "Temporal accuracy >98%",
                    "Financial year detection accuracy >99%",
                    "Zero temporal errors on high-confidence responses"
                ]
            )
            strategies.append(strategy)
        
        # Strategy 3: Confidence Calibration Enhancement
        confidence_errors = [p for p in self.error_patterns if p.category == ErrorCategory.CONFIDENCE_ERROR]
        if confidence_errors:
            strategy = CorrectionStrategy(
                strategy_id="STRAT_CONFIDENCE_001", 
                strategy_name="Multi-Factor Confidence Calibration Optimization",
                target_error_categories=[ErrorCategory.CONFIDENCE_ERROR],
                target_root_causes=[RootCause.CONFIDENCE_CALIBRATION, RootCause.ALGORITHM_LIMITATION],
                implementation_steps=[
                    "1. Analyze confidence vs accuracy correlation patterns",
                    "2. Implement dynamic confidence threshold adjustment",
                    "3. Add uncertainty quantification to confidence scoring",
                    "4. Enhance safety trigger sensitivity for overconfident responses",
                    "5. Implement confidence calibration feedback loop"
                ],
                expected_improvement=2.5,
                implementation_effort="medium",
                risk_assessment="low - improves system safety",
                success_metrics=[
                    "Confidence-accuracy correlation >95%",
                    "Overconfidence errors <1%",
                    "Safety trigger accuracy >99%"
                ]
            )
            strategies.append(strategy)
        
        # Strategy 4: Bengali Language Processing Enhancement
        language_errors = [p for p in self.error_patterns if p.category == ErrorCategory.LANGUAGE_ERROR]
        if language_errors:
            strategy = CorrectionStrategy(
                strategy_id="STRAT_BENGALI_001",
                strategy_name="Bengali Legal Language Processing Optimization",
                target_error_categories=[ErrorCategory.LANGUAGE_ERROR],
                target_root_causes=[RootCause.LINGUISTIC_COMPLEXITY, RootCause.DATA_QUALITY],
                implementation_steps=[
                    "1. Expand Bengali legal terminology dictionary",
                    "2. Enhance Bengali number and date processing",
                    "3. Improve Bengali legal writing style validation", 
                    "4. Add context-aware Bengali translation verification",
                    "5. Implement Bengali legal phrase pattern recognition"
                ],
                expected_improvement=1.5,
                implementation_effort="medium",
                risk_assessment="low - improves user experience",
                success_metrics=[
                    "Bengali terminology accuracy >98%",
                    "Zero Bengali formatting errors",
                    "Professional Bengali writing score >95%"
                ]
            )
            strategies.append(strategy)
        
        # Strategy 5: Completeness Enhancement
        completeness_errors = [p for p in self.error_patterns if p.category == ErrorCategory.COMPLETENESS_ERROR]
        if completeness_errors:
            strategy = CorrectionStrategy(
                strategy_id="STRAT_COMPLETENESS_001",
                strategy_name="Legal Analysis Completeness Optimization",
                target_error_categories=[ErrorCategory.COMPLETENESS_ERROR],
                target_root_causes=[RootCause.KNOWLEDGE_GAP, RootCause.ALGORITHM_LIMITATION],
                implementation_steps=[
                    "1. Implement comprehensive legal provision checklist validation",
                    "2. Enhance cross-reference discovery in Phase 2 integration",
                    "3. Add completeness scoring to response generation",
                    "4. Implement related provision suggestion system",
                    "5. Create completeness regression testing framework"
                ],
                expected_improvement=2.0,
                implementation_effort="high",
                risk_assessment="low - improves legal advice quality",
                success_metrics=[
                    "Completeness score >96%",
                    "Related provision coverage >90%", 
                    "Zero incomplete high-confidence responses"
                ]
            )
            strategies.append(strategy)
        
        # Sort strategies by expected improvement and fix priority
        strategies.sort(key=lambda s: s.expected_improvement, reverse=True)
        
        self.correction_strategies = strategies
        logger.info(f"Generated {len(strategies)} correction strategies")
        
        return strategies

    def create_regression_tests(self, fixed_errors: List[str]) -> List[RegressionTestCase]:
        """
        Create regression test cases from fixed errors to prevent recurrence
        
        Args:
            fixed_errors: List of error IDs that have been fixed
            
        Returns:
            List of regression test cases
        """
        regression_tests = []
        
        for error_id in fixed_errors:
            # Find the error instance
            error = next((e for e in self.error_instances if e.error_id == error_id), None)
            if not error:
                logger.warning(f"Error {error_id} not found for regression test creation")
                continue
            
            test_case = RegressionTestCase(
                test_id=f"REGTEST_{error_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                original_error_id=error_id,
                query=error.query,
                expected_behavior=error.expected_answer,
                test_status="pending"
            )
            
            regression_tests.append(test_case)
            logger.info(f"Created regression test {test_case.test_id} for error {error_id}")
        
        self.regression_tests.extend(regression_tests)
        return regression_tests

    def run_regression_tests(self, system_interface) -> Dict[str, Any]:
        """
        Run regression tests to ensure fixed errors don't recur
        
        Args:
            system_interface: Interface to the main AI system for testing
            
        Returns:
            Test results summary
        """
        test_results = {
            "total_tests": len(self.regression_tests),
            "passed": 0,
            "failed": 0,
            "pending": 0,
            "failed_tests": [],
            "execution_time": datetime.now()
        }
        
        pending_tests = [t for t in self.regression_tests if t.test_status == "pending"]
        
        for test in pending_tests:
            try:
                # Run the test query through the system
                result = system_interface.process_query(test.query)
                
                # Compare with expected behavior (simplified comparison)
                passed = self._compare_test_results(result, test.expected_behavior)
                
                test.test_status = "passed" if passed else "failed"
                test.last_test_date = datetime.now()
                
                test_result = {
                    "test_id": test.test_id,
                    "query": test.query[:100] + "..." if len(test.query) > 100 else test.query,
                    "passed": passed,
                    "actual_result": result[:200] + "..." if len(str(result)) > 200 else str(result),
                    "timestamp": test.last_test_date.isoformat()
                }
                
                test.test_results.append(test_result)
                
                if passed:
                    test_results["passed"] += 1
                else:
                    test_results["failed"] += 1
                    test_results["failed_tests"].append(test_result)
                
                logger.info(f"Regression test {test.test_id}: {'PASSED' if passed else 'FAILED'}")
                
            except Exception as e:
                test.test_status = "failed"
                test.last_test_date = datetime.now()
                test_results["failed"] += 1
                
                error_result = {
                    "test_id": test.test_id,
                    "query": test.query[:100] + "..." if len(test.query) > 100 else test.query,
                    "passed": False,
                    "error": str(e),
                    "timestamp": test.last_test_date.isoformat()
                }
                
                test.test_results.append(error_result)
                test_results["failed_tests"].append(error_result)
                
                logger.error(f"Regression test {test.test_id} failed with error: {e}")
        
        # Update pending count
        test_results["pending"] = len([t for t in self.regression_tests if t.test_status == "pending"])
        
        logger.info(f"Regression testing complete: {test_results['passed']} passed, {test_results['failed']} failed, {test_results['pending']} pending")
        
        return test_results

    def generate_improvement_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive error analysis and improvement report
        
        Returns:
            Detailed report with analysis, patterns, and recommendations
        """
        report = {
            "report_metadata": {
                "generated_date": datetime.now().isoformat(),
                "total_errors_analyzed": len(self.error_instances),
                "patterns_identified": len(self.error_patterns),
                "correction_strategies": len(self.correction_strategies),
                "analysis_period": self._calculate_analysis_period()
            },
            "error_summary": self._generate_error_summary(),
            "pattern_analysis": self._generate_pattern_analysis(),
            "root_cause_analysis": self._generate_root_cause_analysis(),
            "correction_recommendations": self._generate_correction_recommendations(),
            "priority_actions": self._generate_priority_actions(),
            "estimated_improvements": self._calculate_estimated_improvements(),
            "implementation_roadmap": self._generate_implementation_roadmap()
        }
        
        logger.info("Generated comprehensive error analysis and improvement report")
        return report

    def _generate_error_summary(self) -> Dict[str, Any]:
        """Generate error summary statistics"""
        if not self.error_instances:
            return {"message": "No errors to analyze"}
        
        # Category distribution
        category_counts = Counter([e.category for e in self.error_instances])
        
        # Severity distribution  
        severity_counts = Counter([e.severity for e in self.error_instances])
        
        # Root cause distribution
        root_cause_counts = Counter()
        for error in self.error_instances:
            root_cause_counts.update(error.root_causes)
        
        # Domain distribution
        domain_counts = Counter([e.legal_domain for e in self.error_instances])
        
        # Average impact score
        avg_impact = np.mean([e.impact_score for e in self.error_instances])
        
        return {
            "total_errors": len(self.error_instances),
            "category_distribution": dict(category_counts),
            "severity_distribution": dict(severity_counts),
            "root_cause_distribution": dict(root_cause_counts.most_common(10)),
            "domain_distribution": dict(domain_counts),
            "average_impact_score": round(avg_impact, 2),
            "high_impact_errors": len([e for e in self.error_instances if e.impact_score > 0.8]),
            "fixed_errors": len([e for e in self.error_instances if e.fixed])
        }

    def _generate_pattern_analysis(self) -> Dict[str, Any]:
        """Generate error pattern analysis"""
        if not self.error_patterns:
            return {"message": "No patterns identified"}
        
        # Pattern frequency distribution
        frequency_dist = [p.frequency for p in self.error_patterns]
        
        # Fix priority distribution
        priority_dist = Counter([p.fix_priority for p in self.error_patterns])
        
        # Effort distribution
        effort_dist = Counter([p.estimated_fix_effort for p in self.error_patterns])
        
        # Top patterns by frequency
        top_patterns = sorted(self.error_patterns, key=lambda p: p.frequency, reverse=True)[:5]
        
        return {
            "total_patterns": len(self.error_patterns),
            "average_frequency": round(np.mean(frequency_dist), 1),
            "max_frequency": max(frequency_dist),
            "priority_distribution": dict(priority_dist),
            "effort_distribution": dict(effort_dist),
            "top_patterns": [
                {
                    "pattern_name": p.pattern_name,
                    "frequency": p.frequency,
                    "category": p.category.value,
                    "fix_priority": p.fix_priority
                }
                for p in top_patterns
            ]
        }

    def _generate_root_cause_analysis(self) -> Dict[str, Any]:
        """Generate root cause analysis"""
        root_cause_counts = Counter()
        root_cause_impact = defaultdict(list)
        
        for error in self.error_instances:
            root_cause_counts.update(error.root_causes)
            for rc in error.root_causes:
                root_cause_impact[rc].append(error.impact_score)
        
        # Calculate average impact per root cause
        root_cause_avg_impact = {
            rc: np.mean(impacts) for rc, impacts in root_cause_impact.items()
        }
        
        # Top root causes by frequency
        top_causes = root_cause_counts.most_common(10)
        
        # High-impact root causes
        high_impact_causes = sorted(
            root_cause_avg_impact.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_root_causes": len(root_cause_counts),
            "top_causes_by_frequency": [
                {"root_cause": rc.value, "frequency": freq, "avg_impact": round(root_cause_avg_impact[rc], 2)}
                for rc, freq in top_causes
            ],
            "high_impact_causes": [
                {"root_cause": rc.value, "avg_impact": round(impact, 2), "frequency": root_cause_counts[rc]}
                for rc, impact in high_impact_causes
            ]
        }

    def _generate_priority_actions(self) -> List[Dict[str, Any]]:
        """Generate priority actions based on analysis"""
        priority_actions = []
        
        # Critical errors requiring immediate attention
        critical_errors = [e for e in self.error_instances if e.severity == ErrorSeverity.CRITICAL]
        if critical_errors:
            priority_actions.append({
                "priority": 1,
                "action": f"Fix {len(critical_errors)} critical errors immediately",
                "impact": "Prevent potential legal/financial damage",
                "timeline": "Within 24 hours"
            })
        
        # High-frequency patterns
        high_freq_patterns = [p for p in self.error_patterns if p.frequency >= 10 and p.fix_priority >= 4]
        if high_freq_patterns:
            priority_actions.append({
                "priority": 2,
                "action": f"Address {len(high_freq_patterns)} high-frequency error patterns",
                "impact": f"Reduce error rate by estimated {sum(p.frequency for p in high_freq_patterns)} occurrences",
                "timeline": "Within 1 week"
            })
        
        # High-impact root causes
        if hasattr(self, 'correction_strategies') and self.correction_strategies:
            top_strategy = max(self.correction_strategies, key=lambda s: s.expected_improvement)
            priority_actions.append({
                "priority": 3,
                "action": f"Implement {top_strategy.strategy_name}",
                "impact": f"Expected {top_strategy.expected_improvement}% precision improvement",
                "timeline": f"Implementation effort: {top_strategy.implementation_effort}"
            })
        
        # Confidence calibration
        confidence_errors = [e for e in self.error_instances if e.category == ErrorCategory.CONFIDENCE_ERROR]
        if len(confidence_errors) > 5:
            priority_actions.append({
                "priority": 4,
                "action": "Recalibrate confidence scoring system",
                "impact": "Improve user trust and safety",
                "timeline": "Within 2 weeks"
            })
        
        return sorted(priority_actions, key=lambda x: x["priority"])

    # Helper methods for error classification and analysis
    def _is_major_content_error(self, expected: str, actual: str) -> bool:
        """Check if content difference is significant"""
        # Simplified content comparison - could be enhanced with semantic similarity
        return len(set(expected.split()) - set(actual.split())) > len(expected.split()) * 0.3

    def _has_precedence_error(self, expected: str, actual: str) -> bool:
        """Check for legal precedence/hierarchy errors"""
        precedence_keywords = [
            "Finance Ordinance", "অর্থ অধ্যাদেশ",
            "Income Tax Act", "আয়কর আইন", 
            "Rules", "বিধিমালা",
            "Circular", "সার্কুলার"
        ]
        
        # Check if precedence keywords appear differently
        for keyword in precedence_keywords:
            if keyword in expected and keyword in actual:
                # Could add more sophisticated precedence checking
                pass
        
        return False  # Simplified implementation

    def _is_incomplete_answer(self, expected: str, actual: str) -> bool:
        """Check if answer is significantly incomplete"""
        return len(actual) < len(expected) * 0.6

    def _has_language_error(self, expected: str, actual: str) -> bool:
        """Check for Bengali language errors"""
        # Check for common Bengali language mistakes
        bengali_errors = [
            r"[০-৯].*[0-9]",  # Mixed Bengali and English numbers
            r"তারিখ.*\d{1,2}/\d{1,2}/\d{4}",  # Wrong date format
            r"টাকা.*[0-9,]+\s*[০-৯]"  # Mixed currency formats
        ]
        
        for pattern in bengali_errors:
            if re.search(pattern, actual):
                return True
        
        return False

    def _is_safety_failure(self, expected: str, actual: str, metadata: Dict) -> bool:
        """Check for safety system failures"""
        # Check if high-risk content was not properly flagged
        high_risk_keywords = [
            "criminal", "জরিমানা", "দণ্ড", "prosecution", "penalty"
        ]
        
        has_high_risk = any(keyword in expected.lower() or keyword in actual.lower() 
                          for keyword in high_risk_keywords)
        
        safety_triggered = metadata.get('safety_triggered', False)
        confidence = metadata.get('confidence_score', 0.0)
        
        # Safety failure if high-risk content but no safety trigger or too high confidence
        return has_high_risk and (not safety_triggered or confidence > 0.95)

    def _calculate_impact_score(self, category: ErrorCategory, severity: ErrorSeverity, 
                              confidence: float) -> float:
        """Calculate error impact score (0-1)"""
        base_scores = {
            ErrorSeverity.CRITICAL: 1.0,
            ErrorSeverity.MAJOR: 0.7,
            ErrorSeverity.MINOR: 0.4,
            ErrorSeverity.COSMETIC: 0.1
        }
        
        base_score = base_scores[severity]
        
        # Increase impact if high confidence but wrong
        confidence_penalty = max(0, (confidence - 0.5) * 0.5)
        
        # Category-specific adjustments
        category_multipliers = {
            ErrorCategory.SAFETY_ERROR: 1.2,
            ErrorCategory.CITATION_ERROR: 1.1,
            ErrorCategory.CONFIDENCE_ERROR: 1.1,
            ErrorCategory.FORMATTING_ERROR: 0.8
        }
        
        multiplier = category_multipliers.get(category, 1.0)
        
        return min(1.0, (base_score + confidence_penalty) * multiplier)

    def _identify_legal_domain(self, query: str) -> str:
        """Identify legal domain from query"""
        domain_keywords = {
            "individual_tax": ["ব্যক্তিগত", "personal", "individual", "salary", "বেতন"],
            "corporate_tax": ["কোম্পানি", "corporate", "business", "ব্যবসায়"],
            "tds": ["উৎসে কর", "TDS", "deduction", "source"],
            "advance_tax": ["অগ্রিম কর", "advance tax", "advance"],
            "exemptions": ["অব্যাহতি", "exemption", "deduction"],
            "appeals": ["আপিল", "appeal", "tribunal", "আদালত"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword.lower() in query.lower() for keyword in keywords):
                return domain
        
        return "general"

    def _get_query_similarity_key(self, query: str) -> str:
        """Get similarity key for query grouping (simplified)"""
        # Extract key terms and create similarity key
        key_terms = re.findall(r'\b\w+\b', query.lower())
        key_terms = [term for term in key_terms if len(term) > 3][:5]  # Top 5 significant terms
        return "_".join(sorted(key_terms))

    def _generate_error_description(self, category: ErrorCategory, expected: str, actual: str) -> str:
        """Generate human-readable error description"""
        descriptions = {
            ErrorCategory.CITATION_ERROR: "Legal reference mismatch between expected and actual citations",
            ErrorCategory.CONTENT_INACCURACY: "Factually incorrect information provided in response",
            ErrorCategory.TEMPORAL_ERROR: "Wrong financial year, date, or law version used",
            ErrorCategory.PRECEDENCE_ERROR: "Incorrect legal hierarchy or precedence applied",
            ErrorCategory.COMPLETENESS_ERROR: "Response missing relevant legal provisions or information",
            ErrorCategory.CONFIDENCE_ERROR: "Confidence score not calibrated with actual accuracy",
            ErrorCategory.LANGUAGE_ERROR: "Bengali language formatting or terminology errors",
            ErrorCategory.FORMATTING_ERROR: "Professional response format issues",
            ErrorCategory.SAFETY_ERROR: "Safety system failed to trigger appropriate warnings",
            ErrorCategory.INTEGRATION_ERROR: "System component integration failure"
        }
        
        base_description = descriptions.get(category, "Unclassified error")
        
        # Add specific details based on content analysis
        if len(expected) > 200:
            expected_snippet = expected[:200] + "..."
        else:
            expected_snippet = expected
            
        if len(actual) > 200:
            actual_snippet = actual[:200] + "..."
        else:
            actual_snippet = actual
        
        return f"{base_description}. Expected content pattern: '{expected_snippet}'. Actual content pattern: '{actual_snippet}'"

    def _identify_affected_components(self, metadata: Dict, root_causes: List[RootCause]) -> List[str]:
        """Identify which system components are affected"""
        components = []
        
        # Phase-specific component mapping
        if RootCause.DATA_QUALITY in root_causes:
            components.extend(["Phase 2 Knowledge Graph", "Data Sources"])
        
        if RootCause.TEMPORAL_COMPLEXITY in root_causes:
            components.append("Phase 2.5 Temporal Control")
        
        if RootCause.LINGUISTIC_COMPLEXITY in root_causes:
            components.append("Phase 3 Semantic Understanding")
        
        if RootCause.CONFIDENCE_CALIBRATION in root_causes:
            components.append("Phase 3.5 Confidence Engine")
        
        if RootCause.INTEGRATION_FAILURE in root_causes:
            components.append("System Integration Layer")
        
        if RootCause.SAFETY_SYSTEM in root_causes:
            components.append("Safety & Validation System")
        
        # Add metadata-derived components
        if 'phase_errors' in metadata:
            components.extend(metadata['phase_errors'])
        
        return list(set(components)) if components else ["General System"]

    def save_analysis_results(self, output_path: str = "phase_4_error_analysis_results.json"):
        """Save complete error analysis results to file"""
        results = {
            "analysis_metadata": {
                "generated_date": datetime.now().isoformat(),
                "total_errors": len(self.error_instances),
                "total_patterns": len(self.error_patterns),
                "total_strategies": len(self.correction_strategies),
                "analysis_version": "Phase 4.3"
            },
            "error_instances": [asdict(error) for error in self.error_instances],
            "error_patterns": [asdict(pattern) for pattern in self.error_patterns],
            "correction_strategies": [asdict(strategy) for strategy in self.correction_strategies],
            "regression_tests": [asdict(test) for test in self.regression_tests],
            "analysis_summary": self.generate_improvement_report()
        }
        
        # Convert datetime objects to strings for JSON serialization
        def datetime_converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            return obj
        
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=datetime_converter)
        
        logger.info(f"Error analysis results saved to {output_file}")
        
        return str(output_file)

# Helper functions for detailed analysis components

def _has_data_quality_indicators(expected: str, actual: str, metadata: Dict) -> bool:
    """Check for data quality issues"""
    # Look for signs of poor data quality
    indicators = [
        "source unavailable" in actual.lower(),
        "information not found" in actual.lower(),
        "ডেটা পাওয়া যায়নি" in actual,
        len(actual.strip()) < 50,  # Very short responses may indicate missing data
        metadata.get('source_quality_score', 1.0) < 0.7
    ]
    return any(indicators)

def _is_complex_bengali_query(query: str) -> bool:
    """Check if query has complex Bengali linguistic patterns"""
    complex_patterns = [
        r"[০-৯]{4}-[০-৯]{2}",  # Bengali financial year format
        r"তারিখ.*[০-৯]{1,2}.*[০-৯]{4}",  # Bengali date patterns
        r"লক্ষ|কোটি",  # Large number words
        r"যদি.*তাহলে",  # Complex conditional Bengali
        r"কিন্তু.*যদিও"  # Complex conjunctions
    ]
    
    return any(re.search(pattern, query) for pattern in complex_patterns)

def _has_temporal_complexity(query: str) -> bool:
    """Check for temporal complexity in query"""
    temporal_indicators = [
        "previous year", "গত বছর", "আগের বছর",
        "current year", "চলতি বছর", "বর্তমান বছর", 
        "financial year", "আর্থিক বছর",
        "before", "after", "আগে", "পরে",
        "changed", "বদল", "পরিবর্তন"
    ]
    
    return any(indicator.lower() in query.lower() for indicator in temporal_indicators)

def _is_edge_case(query: str, metadata: Dict) -> bool:
    """Check if query represents an edge case"""
    edge_indicators = [
        # Unusual amounts or thresholds
        "399999", "400000", "400001",  # Around tax thresholds
        "exactly", "ঠিক", "সরাসরি",
        # Unusual circumstances
        "exception", "অব্যতিক্রম", "বিশেষ",
        "rare case", "বিরল", "অস্বাভাবিক",
        # Complex scenarios
        len(query) > 300,  # Very long queries
        metadata.get('complexity_score', 0.0) > 0.8
    ]
    
    return any(indicator in str(query).lower() if isinstance(indicator, str) else indicator for indicator in edge_indicators)

def _has_integration_issues(metadata: Dict) -> bool:
    """Check for integration issues between phases"""
    integration_indicators = [
        metadata.get('phase_2_error', False),
        metadata.get('phase_2_5_error', False), 
        metadata.get('phase_3_error', False),
        metadata.get('phase_3_5_error', False),
        metadata.get('integration_latency', 0) > 1000,  # >1s integration time
        'timeout' in str(metadata.get('errors', [])).lower()
    ]
    
    return any(integration_indicators)

if __name__ == "__main__":
    # Example usage and testing
    print("Error Analysis & Correction System - Phase 4.3")
    print("=" * 60)
    
    # Initialize the engine
    engine = ErrorAnalysisEngine()
    
    # Example error analysis
    sample_error = engine.analyze_error(
        query="আমার বেতন ৫ লক্ষ টাকা, কত কর দিতে হবে?",
        expected_answer="বার্ষিক বেতন ৫ লক্ষ টাকার জন্য প্রযোজ্য কর হার ধারা ৫২ অনুযায়ী ১০%...",
        actual_answer="বেতনের উপর ২০% কর দিতে হবে ধারা ৪০ অনুযায়ী...",
        confidence_score=0.92,
        system_metadata={
            'phase_2_confidence': 0.85,
            'citation_count': 2,
            'processing_time': 150
        }
    )
    
    print(f"Sample error analyzed: {sample_error.error_id}")
    print(f"Category: {sample_error.category.value}")
    print(f"Severity: {sample_error.severity.value}")
    print(f"Root causes: {[rc.value for rc in sample_error.root_causes]}")
    
    # Demonstrate pattern identification
    # (Would need more errors in practice)
    patterns = engine.identify_error_patterns(min_frequency=1)
    print(f"\nIdentified {len(patterns)} patterns")
    
    # Generate correction strategies
    strategies = engine.generate_correction_strategies()
    print(f"Generated {len(strategies)} correction strategies")
    
    # Generate improvement report
    report = engine.generate_improvement_report()
    print(f"\nGenerated improvement report with {len(report)} sections")
    
    # Save results
    output_file = engine.save_analysis_results("test_error_analysis_results.json")
    print(f"Results saved to: {output_file}")