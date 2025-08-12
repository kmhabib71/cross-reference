#!/usr/bin/env python3
"""
False Positive Control System
Phase 1.5 - Advanced Bengali Legal NER Implementation

Prevents wrong section linking through contrastive learning and domain separation.
Implements sophisticated false positive detection and prevention for legal cross-references.
"""

import json
import re
import numpy as np
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from pathlib import Path
import logging
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContrastivePair:
    """Contrastive learning pair for false positive prevention"""
    positive_example: str
    negative_example: str
    negative_similarity: float
    domain_tags: Set[str]
    explanation: str

@dataclass
class FalsePositivePattern:
    """Pattern that commonly causes false positives"""
    pattern: str
    pattern_type: str
    common_mistakes: List[str]
    correct_interpretation: str
    prevention_rules: List[str]
    confidence_penalty: float = 0.3

@dataclass
class DomainSeparationRule:
    """Rule for maintaining domain separation"""
    source_domain: str
    target_domain: str
    separation_strength: float  # 0.0 to 1.0
    blocked_cross_references: List[str]
    warning_patterns: List[str]

class FalsePositiveController:
    """
    False Positive Control System for Bengali Legal NER
    
    Prevents wrong section linking through:
    - Contrastive learning with negative examples
    - Domain separation (VAT vs Income Tax)
    - Pattern-based false positive detection
    - Confidence adjustment based on risk factors
    """
    
    def __init__(self):
        """Initialize False Positive Controller"""
        
        # Initialize contrastive pairs
        self.contrastive_pairs = self._initialize_contrastive_pairs()
        
        # Initialize false positive patterns
        self.false_positive_patterns = self._initialize_false_positive_patterns()
        
        # Initialize domain separation rules
        self.domain_separation_rules = self._initialize_domain_separation_rules()
        
        # Track false positive occurrences
        self.false_positive_history: List[Dict] = []
        
        # Confidence adjustment factors
        self.confidence_adjustments = {
            'domain_mismatch': -0.4,
            'ambiguous_pattern': -0.2,
            'cross_reference_inconsistency': -0.3,
            'temporal_mismatch': -0.25,
            'context_violation': -0.35
        }
        
        logger.info("🛡️ False Positive Controller initialized")
        logger.info(f"🔄 Contrastive pairs: {len(self.contrastive_pairs)}")
        logger.info(f"⚠️ False positive patterns: {len(self.false_positive_patterns)}")
        logger.info(f"🚧 Domain separation rules: {len(self.domain_separation_rules)}")

    def _initialize_contrastive_pairs(self) -> List[ContrastivePair]:
        """Initialize contrastive learning pairs"""
        pairs = [
            # Return filing vs refund processing confusion
            ContrastivePair(
                positive_example="রিটার্ন দাখিল করতে হবে - ধারা ৭৫ অনুযায়ী",
                negative_example="রিটার্ন পাওয়ার জন্য আবেদন - ধারা ৭৫ অনুযায়ী",
                negative_similarity=0.1,
                domain_tags={"income_tax", "filing"},
                explanation="রিটার্ন দাখিল (filing) এবং রিটার্ন প্রাপ্তি (refund) সম্পূর্ণ আলাদা বিষয়"
            ),
            
            # Tax deduction vs tax exemption confusion
            ContrastivePair(
                positive_example="কর কাটা হবে - ধারা ৫২ অনুযায়ী TDS",
                negative_example="কর কাটা যাবে - ধারা ৫২ অনুযায়ী exemption",
                negative_similarity=0.2,
                domain_tags={"income_tax", "deduction"},
                explanation="কর কাটা (deduction) এবং কর ছাড় (exemption) আলাদা ধারণা"
            ),
            
            # VAT vs Income Tax confusion
            ContrastivePair(
                positive_example="আয়কর আইনের ধারা ১৬৩ - ন্যূনতম কর",
                negative_example="ভ্যাট আইনের ধারা ১৬৩ - আয়কর প্রসঙ্গে",
                negative_similarity=0.05,
                domain_tags={"domain_separation"},
                explanation="ভ্যাট এবং আয়করের ধারাসমূহ সম্পূর্ণ আলাদা আইনি কাঠামো"
            ),
            
            # Individual vs Company taxation confusion
            ContrastivePair(
                positive_example="ব্যক্তি করদাতার জন্য ধারা ৪৪ - কর মুক্ত সীমা",
                negative_example="কোম্পানির জন্য ধারা ৪৪ - কর মুক্ত সীমা",
                negative_similarity=0.1,
                domain_tags={"taxpayer_type"},
                explanation="ব্যক্তি এবং কোম্পানির জন্য কর মুক্ত সীমা আলাদা"
            ),
            
            # Advance tax vs regular tax confusion
            ContrastivePair(
                positive_example="অগ্রিম কর - ধারা ১৫৩ অনুযায়ী",
                negative_example="নিয়মিত কর - ধারা ১৫৩ অনুযায়ী",
                negative_similarity=0.15,
                domain_tags={"tax_timing"},
                explanation="অগ্রিম কর এবং নিয়মিত কর প্রদানের নিয়ম ভিন্ন"
            ),
            
            # Capital gain vs business income confusion
            ContrastivePair(
                positive_example="মূলধন লাভ - ধারা ২৭ অনুযায়ী",
                negative_example="ব্যবসায়িক আয় - ধারা ২৭ অনুযায়ী",
                negative_similarity=0.2,
                domain_tags={"income_classification"},
                explanation="মূলধন লাভ এবং ব্যবসায়িক আয়ের কর গণনা পৃথক"
            ),
            
            # Salary vs professional income confusion
            ContrastivePair(
                positive_example="বেতন আয় - ধারা ২১ অনুযায়ী",
                negative_example="পেশাগত আয় - ধারা ২১ অনুযায়ী",
                negative_similarity=0.25,
                domain_tags={"income_classification"},
                explanation="বেতন এবং পেশাগত আয়ের কর কাঠামো ভিন্ন"
            ),
            
            # Current year vs previous year confusion
            ContrastivePair(
                positive_example="২০২৫-২৬ অর্থবছরের নিয়ম",
                negative_example="২০২৪-২৫ অর্থবছরের নিয়ম - ২০২৫-২৬ এ প্রয়োগ",
                negative_similarity=0.1,
                domain_tags={"temporal_accuracy"},
                explanation="বিভিন্ন অর্থবছরের নিয়ম ভিন্ন হতে পারে"
            )
        ]
        
        return pairs

    def _initialize_false_positive_patterns(self) -> List[FalsePositivePattern]:
        """Initialize common false positive patterns"""
        patterns = [
            FalsePositivePattern(
                pattern=r"রিটার্ন\s+(পা|দে|নে)",
                pattern_type="ambiguous_verb",
                common_mistakes=[
                    "রিটার্ন পাওয়া → filing requirement",
                    "রিটার্ন দেওয়া → filing requirement", 
                    "রিটার্ন নেওয়া → filing requirement"
                ],
                correct_interpretation="রিটার্ন দাখিল (filing) vs রিটার্ন প্রাপ্তি (refund) আলাদা",
                prevention_rules=[
                    "রিটার্ন + দাখিল/জমা = filing",
                    "রিটার্ন + প্রাপ্তি/ফেরত = refund",
                    "Context analysis required"
                ],
                confidence_penalty=0.3
            ),
            
            FalsePositivePattern(
                pattern=r"কর\s+কাট",
                pattern_type="ambiguous_phrase",
                common_mistakes=[
                    "কর কাটা → tax exemption",
                    "কর কাটা → tax deduction (TDS)"
                ],
                correct_interpretation="কর কাটা = TDS (deduction), কর ছাড় = exemption",
                prevention_rules=[
                    "কর কাটা = deduction at source (TDS)",
                    "কর ছাড়/মওকুফ = exemption",
                    "Context determines meaning"
                ],
                confidence_penalty=0.25
            ),
            
            FalsePositivePattern(
                pattern=r"ভ্যাট.*আয়কর|আয়কর.*ভ্যাট",
                pattern_type="domain_mixing",
                common_mistakes=[
                    "VAT rules applied to income tax",
                    "Income tax sections for VAT queries"
                ],
                correct_interpretation="ভ্যাট এবং আয়কর সম্পূর্ণ আলাদা আইনি ডোমেইন",
                prevention_rules=[
                    "Block cross-domain references",
                    "Separate VAT and Income Tax processing",
                    "Domain validation required"
                ],
                confidence_penalty=0.5
            ),
            
            FalsePositivePattern(
                pattern=r"মূল্য\s+সংযোজন\s+কর",
                pattern_type="domain_confusion",
                common_mistakes=[
                    "VAT issues in income tax context",
                    "Income tax solutions for VAT queries"
                ],
                correct_interpretation="মূল্য সংযোজন কর (VAT) ≠ আয়কর (Income Tax)",
                prevention_rules=[
                    "Strict domain separation",
                    "VAT queries → VAT knowledge base only",
                    "Clear domain tagging"
                ],
                confidence_penalty=0.6
            ),
            
            FalsePositivePattern(
                pattern=r"(\d{4})-(\d{2,4})",
                pattern_type="temporal_ambiguity",
                common_mistakes=[
                    "Using old year rules for current queries",
                    "Mixing financial year regulations"
                ],
                correct_interpretation="সঠিক অর্থবছর নির্ধারণ জরুরি",
                prevention_rules=[
                    "Extract and validate financial year",
                    "Use current FY rules by default",
                    "Historical queries need special handling"
                ],
                confidence_penalty=0.2
            ),
            
            FalsePositivePattern(
                pattern=r"কোম্পানি.*ব্যক্তি|ব্যক্তি.*কোম্পানি",
                pattern_type="taxpayer_confusion",
                common_mistakes=[
                    "Individual tax rules for companies",
                    "Corporate tax rules for individuals"
                ],
                correct_interpretation="ব্যক্তি এবং কোম্পানির কর নিয়ম আলাদা",
                prevention_rules=[
                    "Determine taxpayer type first",
                    "Apply appropriate tax regime",
                    "Clear taxpayer classification"
                ],
                confidence_penalty=0.35
            )
        ]
        
        return patterns

    def _initialize_domain_separation_rules(self) -> List[DomainSeparationRule]:
        """Initialize domain separation rules"""
        rules = [
            DomainSeparationRule(
                source_domain="income_tax",
                target_domain="vat",
                separation_strength=0.9,
                blocked_cross_references=[
                    "VAT sections in income tax context",
                    "Income tax rates for VAT calculations"
                ],
                warning_patterns=[
                    r"ভ্যাট.*আয়কর",
                    r"মূল্য\s+সংযোজন.*আয়কর",
                    r"VAT.*income\s+tax"
                ]
            ),
            
            DomainSeparationRule(
                source_domain="vat",
                target_domain="income_tax", 
                separation_strength=0.9,
                blocked_cross_references=[
                    "Income tax sections in VAT context",
                    "VAT exemptions for income tax"
                ],
                warning_patterns=[
                    r"আয়কর.*ভ্যাট",
                    r"income\s+tax.*VAT",
                    r"আয়কর.*মূল্য\s+সংযোজন"
                ]
            ),
            
            DomainSeparationRule(
                source_domain="individual_tax",
                target_domain="corporate_tax",
                separation_strength=0.7,
                blocked_cross_references=[
                    "Corporate rates for individual taxpayers",
                    "Individual exemptions for companies"
                ],
                warning_patterns=[
                    r"কোম্পানি.*ব্যক্তি\s+কর",
                    r"ব্যক্তি.*কোম্পানি\s+কর"
                ]
            ),
            
            DomainSeparationRule(
                source_domain="current_fy",
                target_domain="previous_fy",
                separation_strength=0.6,
                blocked_cross_references=[
                    "Old tax rates for current year",
                    "Deprecated rules for current queries"
                ],
                warning_patterns=[
                    r"২০২৩.*২০২৫",
                    r"২০২৪.*২০২৬",
                    r"previous.*current\s+year"
                ]
            )
        ]
        
        return rules

    def check_false_positive_risk(self, 
                                query_text: str,
                                predicted_entities: List[Dict],
                                predicted_sections: List[str]) -> Dict:
        """
        Check for false positive risks in predictions
        
        Args:
            query_text: Input query text
            predicted_entities: NER predicted entities
            predicted_sections: Predicted section references
            
        Returns:
            Risk assessment with adjustments
        """
        logger.info("🔍 Checking false positive risks...")
        
        risk_assessment = {
            'overall_risk': 0.0,
            'risk_factors': [],
            'confidence_adjustments': {},
            'domain_violations': [],
            'pattern_violations': [],
            'recommendations': []
        }
        
        # Check pattern-based false positives
        pattern_risks = self._check_pattern_risks(query_text)
        risk_assessment['pattern_violations'] = pattern_risks
        
        # Check domain separation violations
        domain_risks = self._check_domain_separation(query_text, predicted_sections)
        risk_assessment['domain_violations'] = domain_risks
        
        # Check temporal consistency
        temporal_risks = self._check_temporal_consistency(query_text, predicted_sections)
        
        # Check cross-reference consistency
        reference_risks = self._check_reference_consistency(predicted_entities, predicted_sections)
        
        # Calculate overall risk
        all_risks = pattern_risks + domain_risks + temporal_risks + reference_risks
        risk_assessment['overall_risk'] = min(sum(risk['penalty'] for risk in all_risks), 1.0)
        
        # Generate confidence adjustments
        for risk in all_risks:
            risk_type = risk['type']
            if risk_type in self.confidence_adjustments:
                risk_assessment['confidence_adjustments'][risk_type] = self.confidence_adjustments[risk_type]
        
        # Generate recommendations
        risk_assessment['recommendations'] = self._generate_risk_recommendations(all_risks)
        
        logger.info(f"📊 Overall false positive risk: {risk_assessment['overall_risk']:.2f}")
        return risk_assessment

    def _check_pattern_risks(self, query_text: str) -> List[Dict]:
        """Check for pattern-based false positive risks"""
        risks = []
        
        for pattern in self.false_positive_patterns:
            if re.search(pattern.pattern, query_text, re.IGNORECASE):
                risks.append({
                    'type': 'ambiguous_pattern',
                    'pattern': pattern.pattern,
                    'pattern_type': pattern.pattern_type,
                    'explanation': pattern.correct_interpretation,
                    'penalty': pattern.confidence_penalty,
                    'prevention_rules': pattern.prevention_rules
                })
        
        return risks

    def _check_domain_separation(self, query_text: str, predicted_sections: List[str]) -> List[Dict]:
        """Check for domain separation violations"""
        violations = []
        
        for rule in self.domain_separation_rules:
            for warning_pattern in rule.warning_patterns:
                if re.search(warning_pattern, query_text, re.IGNORECASE):
                    violations.append({
                        'type': 'domain_mismatch',
                        'source_domain': rule.source_domain,
                        'target_domain': rule.target_domain,
                        'separation_strength': rule.separation_strength,
                        'penalty': rule.separation_strength * 0.5,
                        'warning': f"Potential cross-domain contamination: {rule.source_domain} → {rule.target_domain}"
                    })
        
        # Check if predicted sections belong to wrong domain
        for section in predicted_sections:
            if self._is_cross_domain_section(section, query_text):
                violations.append({
                    'type': 'domain_mismatch',
                    'section': section,
                    'penalty': 0.4,
                    'warning': f"Section {section} may not be relevant to query domain"
                })
        
        return violations

    def _check_temporal_consistency(self, query_text: str, predicted_sections: List[str]) -> List[Dict]:
        """Check for temporal consistency violations"""
        risks = []
        
        # Extract financial years mentioned
        fy_pattern = r'(\d{4})-(\d{2,4})'
        fy_matches = re.findall(fy_pattern, query_text)
        
        if fy_matches:
            for start_year, end_year in fy_matches:
                start_year = int(start_year)
                
                # Check if using old rules for current queries
                if start_year < 2024:  # Assuming current is 2025
                    risks.append({
                        'type': 'temporal_mismatch',
                        'detected_fy': f"{start_year}-{end_year}",
                        'penalty': 0.25,
                        'warning': f"Query mentions old financial year {start_year}-{end_year}"
                    })
        
        return risks

    def _check_reference_consistency(self, predicted_entities: List[Dict], predicted_sections: List[str]) -> List[Dict]:
        """Check for cross-reference consistency violations"""
        risks = []
        
        # Check entity-section consistency
        entity_domains = set()
        section_domains = set()
        
        for entity in predicted_entities:
            entity_type = entity.get('type', '')
            if 'VAT' in entity.get('text', '').upper():
                entity_domains.add('vat')
            elif 'আয়কর' in entity.get('text', '') or 'income' in entity.get('text', '').lower():
                entity_domains.add('income_tax')
        
        for section in predicted_sections:
            # Simplified domain detection based on section patterns
            if section.startswith('VAT_'):
                section_domains.add('vat')
            elif section.startswith('ITA_'):
                section_domains.add('income_tax')
        
        # Check for domain mismatches
        if entity_domains and section_domains and not entity_domains.intersection(section_domains):
            risks.append({
                'type': 'context_violation',
                'entity_domains': list(entity_domains),
                'section_domains': list(section_domains),
                'penalty': 0.35,
                'warning': "Entity and section domains do not match"
            })
        
        return risks

    def _is_cross_domain_section(self, section: str, query_text: str) -> bool:
        """Check if section belongs to different domain than query"""
        # Simple heuristic - can be made more sophisticated
        query_lower = query_text.lower()
        
        if 'vat' in section.lower() or 'ভ্যাট' in section:
            return 'আয়কর' in query_text or 'income tax' in query_lower
        
        if 'income' in section.lower() or 'ita_' in section.lower():
            return 'ভ্যাট' in query_text or 'vat' in query_lower
        
        return False

    def _generate_risk_recommendations(self, risks: List[Dict]) -> List[str]:
        """Generate recommendations based on identified risks"""
        recommendations = []
        
        risk_types = set(risk['type'] for risk in risks)
        
        if 'domain_mismatch' in risk_types:
            recommendations.append("Verify that query and predicted sections belong to same legal domain")
            
        if 'ambiguous_pattern' in risk_types:
            recommendations.append("Request clarification for ambiguous terms before providing answer")
            
        if 'temporal_mismatch' in risk_types:
            recommendations.append("Confirm the applicable financial year for accurate information")
            
        if 'context_violation' in risk_types:
            recommendations.append("Review entity-section consistency for contextual accuracy")
        
        # General recommendations for high risk
        overall_risk = sum(risk.get('penalty', 0) for risk in risks)
        if overall_risk > 0.5:
            recommendations.append("Consider requesting additional context or expert review")
            recommendations.append("Provide confidence score and alternative interpretations")
        
        return list(set(recommendations))  # Remove duplicates

    def apply_contrastive_learning(self, query_text: str, candidate_answers: List[Dict]) -> List[Dict]:
        """
        Apply contrastive learning to improve answer selection
        
        Args:
            query_text: Input query
            candidate_answers: List of candidate answers with confidence scores
            
        Returns:
            Adjusted candidate answers with contrastive learning applied
        """
        logger.info("🔄 Applying contrastive learning...")
        
        adjusted_answers = []
        
        for answer in candidate_answers:
            answer_text = answer.get('text', '')
            original_confidence = answer.get('confidence', 0.0)
            
            # Find matching contrastive pairs
            negative_penalty = 0.0
            positive_boost = 0.0
            
            for pair in self.contrastive_pairs:
                # Check if answer matches negative example pattern
                if self._texts_similar(answer_text, pair.negative_example, threshold=0.7):
                    negative_penalty += pair.negative_similarity
                    logger.info(f"⚠️ Negative similarity detected: {pair.explanation}")
                
                # Check if answer matches positive example pattern
                elif self._texts_similar(answer_text, pair.positive_example, threshold=0.8):
                    positive_boost += 0.1  # Small positive boost
                    logger.info(f"✅ Positive similarity detected: {pair.explanation}")
            
            # Apply adjustments
            adjusted_confidence = original_confidence + positive_boost - negative_penalty
            adjusted_confidence = max(0.0, min(1.0, adjusted_confidence))  # Clamp to [0,1]
            
            adjusted_answer = answer.copy()
            adjusted_answer['confidence'] = adjusted_confidence
            adjusted_answer['contrastive_adjustment'] = {
                'original_confidence': original_confidence,
                'positive_boost': positive_boost,
                'negative_penalty': negative_penalty,
                'final_confidence': adjusted_confidence
            }
            
            adjusted_answers.append(adjusted_answer)
        
        # Sort by adjusted confidence
        adjusted_answers.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.info(f"📊 Contrastive learning applied to {len(adjusted_answers)} candidates")
        return adjusted_answers

    def _texts_similar(self, text1: str, text2: str, threshold: float = 0.7) -> bool:
        """Check if two texts are similar based on token overlap"""
        # Simple similarity measure - can be improved with embeddings
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        
        if not tokens1 or not tokens2:
            return False
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        similarity = len(intersection) / len(union) if union else 0.0
        return similarity >= threshold

    def save_false_positive_report(self, output_path: str) -> None:
        """Save false positive analysis report"""
        report = {
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "phase": "Phase_1.5_False_Positive_Control",
                "version": "1.0",
                "total_checks_performed": len(self.false_positive_history)
            },
            "false_positive_statistics": {
                "contrastive_pairs": len(self.contrastive_pairs),
                "false_positive_patterns": len(self.false_positive_patterns),
                "domain_separation_rules": len(self.domain_separation_rules),
                "confidence_adjustment_factors": len(self.confidence_adjustments)
            },
            "contrastive_learning": {
                "domain_coverage": list(set(pair.domain_tags for pair in self.contrastive_pairs if pair.domain_tags)),
                "negative_similarity_range": [
                    min(pair.negative_similarity for pair in self.contrastive_pairs),
                    max(pair.negative_similarity for pair in self.contrastive_pairs)
                ]
            },
            "pattern_analysis": {
                "pattern_types": list(set(pattern.pattern_type for pattern in self.false_positive_patterns)),
                "confidence_penalties": [pattern.confidence_penalty for pattern in self.false_positive_patterns]
            },
            "domain_separation": {
                "protected_domains": list(set(rule.source_domain for rule in self.domain_separation_rules)),
                "separation_strengths": [rule.separation_strength for rule in self.domain_separation_rules]
            },
            "quality_targets": {
                "false_positive_rate": "<2% (target)",
                "domain_separation_accuracy": ">98% (target)",
                "contrastive_learning_effectiveness": ">95% (target)"
            }
        }
        
        output_file = Path(output_path) / "false_positive_control_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 False positive control report saved to {output_file}")

def main():
    """Main function for testing false positive control"""
    logger.info("🛡️ Testing False Positive Control System")
    
    controller = FalsePositiveController()
    
    # Test queries with potential false positives
    test_cases = [
        {
            "query": "আমার রিটার্ন পেতে কত সময় লাগবে?",
            "entities": [{"text": "রিটার্ন", "type": "RETURN_RELATED"}],
            "sections": ["ITA_2023_S75"],
            "expected_risk": "high",  # Should detect filing vs refund confusion
        },
        {
            "query": "ভ্যাট এর ক্ষেত্রে আয়কর আইনের ধারা ১৬৩ কি প্রযোজ্য?",
            "entities": [{"text": "ভ্যাট", "type": "TAX_TYPE"}, {"text": "ধারা ১৬৩", "type": "SECTION_DIRECT"}],
            "sections": ["ITA_2023_S163"],
            "expected_risk": "very_high",  # Should detect domain mismatch
        },
        {
            "query": "আমার ইউটিউব আয়ের জন্য কোম্পানির কর হার কত?",
            "entities": [{"text": "ইউটিউব আয়", "type": "INCOME_SOURCE"}, {"text": "কোম্পানি", "type": "TAXPAYER_TYPE"}],
            "sections": ["ITA_2023_S25"],
            "expected_risk": "medium",  # Individual income vs company taxation
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n--- Test Case {i} ---")
        logger.info(f"Query: {test_case['query']}")
        
        # Check false positive risk
        risk_assessment = controller.check_false_positive_risk(
            test_case["query"],
            test_case["entities"],
            test_case["sections"]
        )
        
        logger.info(f"Overall risk: {risk_assessment['overall_risk']:.2f}")
        logger.info(f"Risk factors: {len(risk_assessment['pattern_violations']) + len(risk_assessment['domain_violations'])}")
        
        if risk_assessment['recommendations']:
            logger.info("Recommendations:")
            for rec in risk_assessment['recommendations']:
                logger.info(f"  • {rec}")
        
        # Test contrastive learning
        candidate_answers = [
            {"text": "রিটার্ন দাখিল করতে হবে", "confidence": 0.8},
            {"text": "রিটার্ন পাওয়া যাবে", "confidence": 0.7}
        ]
        
        adjusted = controller.apply_contrastive_learning(test_case["query"], candidate_answers)
        logger.info(f"Adjusted confidences: {[a['confidence'] for a in adjusted]}")
    
    # Save report
    controller.save_false_positive_report("./")
    
    logger.info("✅ False positive control testing completed")

if __name__ == "__main__":
    main()