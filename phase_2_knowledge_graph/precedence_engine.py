#!/usr/bin/env python3
"""
Legal Precedence Engine for Phase 2 - Task 2.3
==============================================

Automatic conflict resolution system for Bangladesh tax laws.
Implements legal hierarchy: Finance Ordinance > Income Tax Act > Schedules > Rules > Circulars

Features:
- Multi-layered precedence hierarchy
- Temporal precedence (newer laws override older)
- Specific vs general provisions handling
- Conflict detection and resolution
- Evidence-based resolution scoring
- Integration with Knowledge Graph

Author: Phase 2 Implementation
Date: August 10, 2025
"""

import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, date
from pathlib import Path
import re

from legal_knowledge_graph import LegalKnowledgeGraph, GraphNode, GraphRelationship

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LegalProvision:
    """Structured legal provision with precedence metadata"""
    provision_id: str
    text: str
    document_type: str
    authority_level: int
    effective_date: Optional[date] = None
    section_number: Optional[str] = None
    is_specific: bool = False  # Specific provisions override general ones
    is_exception: bool = False  # Exception provisions have higher precedence
    temporal_scope: Optional[str] = None  # "permanent", "temporary", "financial_year"
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ConflictResolution:
    """Resolution result for conflicting provisions"""
    winning_provision: LegalProvision
    losing_provisions: List[LegalProvision]
    resolution_reason: str
    confidence_score: float
    authority_chain: List[str]
    temporal_analysis: Dict[str, Any]
    evidence: List[str]

class LegalPrecedenceEngine:
    """
    Comprehensive legal precedence resolution system for Bangladesh tax laws.
    
    Precedence Hierarchy:
    1. Finance Ordinance (Authority: 100) - Overrides all other laws
    2. Income Tax Act 2023 (Authority: 95) - Primary legislation
    3. Schedules (Authority: 90) - Part of primary legislation
    4. TDS Rules (Authority: 85) - Implementing regulations
    5. SRO Orders (Authority: 80) - Specific notifications
    6. Circulars (Authority: 70) - Interpretive guidance
    
    Additional Rules:
    - Newer laws override older laws (temporal precedence)
    - Specific provisions override general provisions
    - Exception provisions override regular provisions
    - Emergency provisions have temporary higher authority
    """
    
    def __init__(self, knowledge_graph: Optional[LegalKnowledgeGraph] = None):
        """Initialize precedence engine with knowledge graph integration"""
        self.knowledge_graph = knowledge_graph
        self.precedence_hierarchy = self._init_precedence_hierarchy()
        self.temporal_rules = self._init_temporal_rules()
        self.special_rules = self._init_special_rules()
        
        logger.info("Legal Precedence Engine initialized")
    
    def _init_precedence_hierarchy(self) -> Dict[str, Dict[str, Any]]:
        """Initialize legal precedence hierarchy"""
        return {
            'finance_ordinance': {
                'authority_level': 100,
                'overrides': ['income_tax_act', 'schedules', 'tds_rules', 'sro_orders', 'circulars'],
                'keywords': ['finance ordinance', 'অর্থ অধ্যাদেশ', 'budget', 'বাজেট'],
                'temporal_authority': 'high'  # Always current year
            },
            'income_tax_act': {
                'authority_level': 95,
                'overrides': ['schedules', 'tds_rules', 'circulars'],
                'keywords': ['income tax act', 'আয়কর আইন', 'ITA 2023'],
                'temporal_authority': 'medium'  # Updated every few years
            },
            'schedules': {
                'authority_level': 90,
                'overrides': ['tds_rules', 'circulars'],
                'keywords': ['schedule', 'তফসিল', 'annexure'],
                'temporal_authority': 'medium'  # Part of main act
            },
            'tds_rules': {
                'authority_level': 85,
                'overrides': ['circulars'],
                'keywords': ['tds rules', 'টিডিএস বিধি', 'withholding tax'],
                'temporal_authority': 'high'  # Updated annually
            },
            'sro_orders': {
                'authority_level': 80,
                'overrides': ['circulars'],
                'keywords': ['sro', 'এসআরও', 'notification'],
                'temporal_authority': 'high'  # Specific notifications
            },
            'circulars': {
                'authority_level': 70,
                'overrides': [],
                'keywords': ['circular', 'সার্কুলার', 'memorandum'],
                'temporal_authority': 'low'  # Interpretive guidance only
            }
        }
    
    def _init_temporal_rules(self) -> Dict[str, Any]:
        """Initialize temporal precedence rules"""
        return {
            'financial_year_rule': 'Current FY provisions override previous FY',
            'amendment_rule': 'Later amendments override earlier versions', 
            'sunset_clause': 'Temporary provisions expire automatically',
            'emergency_rule': 'Emergency provisions have temporary highest authority'
        }
    
    def _init_special_rules(self) -> Dict[str, Any]:
        """Initialize special precedence rules"""
        return {
            'specific_over_general': 'Specific provisions override general provisions',
            'exception_rule': 'Exception provisions override regular provisions', 
            'penalty_rule': 'Penalty provisions have enhanced authority',
            'procedural_rule': 'Procedural rules follow substantive law',
            'retrospective_rule': 'Retrospective provisions have special handling'
        }
    
    def resolve_conflict(self, conflicting_provisions: List[LegalProvision]) -> ConflictResolution:
        """
        Resolve conflict between multiple legal provisions
        
        Args:
            conflicting_provisions: List of provisions that conflict with each other
            
        Returns:
            ConflictResolution with winning provision and detailed reasoning
        """
        logger.info(f"Resolving conflict between {len(conflicting_provisions)} provisions")
        
        if not conflicting_provisions:
            raise ValueError("No provisions provided for conflict resolution")
        
        if len(conflicting_provisions) == 1:
            return ConflictResolution(
                winning_provision=conflicting_provisions[0],
                losing_provisions=[],
                resolution_reason="Only one provision provided",
                confidence_score=1.0,
                authority_chain=[conflicting_provisions[0].document_type],
                temporal_analysis={},
                evidence=["No conflict detected"]
            )
        
        # Step 1: Authority-based resolution
        authority_resolution = self._resolve_by_authority(conflicting_provisions)
        
        # Step 2: Temporal resolution (if authority is tied)
        temporal_resolution = self._resolve_by_temporal_precedence(authority_resolution['candidates'])
        
        # Step 3: Specificity resolution (if still tied)
        specificity_resolution = self._resolve_by_specificity(temporal_resolution['candidates'])
        
        # Step 4: Exception rule resolution (final tie-breaker)
        final_resolution = self._resolve_by_special_rules(specificity_resolution['candidates'])
        
        # Build comprehensive resolution result
        winning_provision = final_resolution['winner']
        losing_provisions = [p for p in conflicting_provisions if p != winning_provision]
        
        resolution = ConflictResolution(
            winning_provision=winning_provision,
            losing_provisions=losing_provisions,
            resolution_reason=self._build_resolution_reason(
                authority_resolution, temporal_resolution, 
                specificity_resolution, final_resolution
            ),
            confidence_score=self._calculate_confidence_score(
                authority_resolution, temporal_resolution, specificity_resolution
            ),
            authority_chain=self._build_authority_chain(winning_provision),
            temporal_analysis=temporal_resolution,
            evidence=self._build_evidence_list(
                authority_resolution, temporal_resolution, specificity_resolution
            )
        )
        
        logger.info(f"Conflict resolved: {winning_provision.document_type} provision wins")
        return resolution
    
    def _resolve_by_authority(self, provisions: List[LegalProvision]) -> Dict[str, Any]:
        """Resolve conflict based on authority hierarchy"""
        max_authority = max(p.authority_level for p in provisions)
        highest_authority_provisions = [p for p in provisions if p.authority_level == max_authority]
        
        return {
            'candidates': highest_authority_provisions,
            'eliminated': [p for p in provisions if p.authority_level < max_authority],
            'resolution_method': 'authority_hierarchy',
            'details': f"Authority level {max_authority} provisions selected"
        }
    
    def _resolve_by_temporal_precedence(self, provisions: List[LegalProvision]) -> Dict[str, Any]:
        """Resolve conflict based on temporal precedence (newer wins)"""
        if len(provisions) <= 1:
            return {
                'candidates': provisions,
                'eliminated': [],
                'resolution_method': 'temporal_precedence',
                'details': 'No temporal conflict'
            }
        
        # Filter provisions with effective dates
        dated_provisions = [p for p in provisions if p.effective_date]
        undated_provisions = [p for p in provisions if not p.effective_date]
        
        if not dated_provisions:
            return {
                'candidates': provisions,
                'eliminated': [],
                'resolution_method': 'temporal_precedence',
                'details': 'No effective dates available for temporal resolution'
            }
        
        # Find most recent effective date
        latest_date = max(p.effective_date for p in dated_provisions)
        latest_provisions = [p for p in dated_provisions if p.effective_date == latest_date]
        
        # Include undated provisions (assume current)
        latest_provisions.extend(undated_provisions)
        
        eliminated = [p for p in provisions if p not in latest_provisions]
        
        return {
            'candidates': latest_provisions,
            'eliminated': eliminated,
            'resolution_method': 'temporal_precedence',
            'details': f"Latest effective date: {latest_date}",
            'latest_date': latest_date
        }
    
    def _resolve_by_specificity(self, provisions: List[LegalProvision]) -> Dict[str, Any]:
        """Resolve conflict based on specificity (specific beats general)"""
        if len(provisions) <= 1:
            return {
                'candidates': provisions,
                'eliminated': [],
                'resolution_method': 'specificity',
                'details': 'No specificity conflict'
            }
        
        specific_provisions = [p for p in provisions if p.is_specific]
        general_provisions = [p for p in provisions if not p.is_specific]
        
        if specific_provisions:
            return {
                'candidates': specific_provisions,
                'eliminated': general_provisions,
                'resolution_method': 'specificity',
                'details': f"{len(specific_provisions)} specific provisions override {len(general_provisions)} general provisions"
            }
        
        return {
            'candidates': provisions,
            'eliminated': [],
            'resolution_method': 'specificity', 
            'details': 'All provisions are general'
        }
    
    def _resolve_by_special_rules(self, provisions: List[LegalProvision]) -> Dict[str, Any]:
        """Apply special rules as final tie-breaker"""
        if len(provisions) <= 1:
            return {
                'winner': provisions[0] if provisions else None,
                'resolution_method': 'special_rules',
                'details': 'Single or no provision'
            }
        
        # Rule 1: Exception provisions win
        exception_provisions = [p for p in provisions if p.is_exception]
        if exception_provisions:
            return {
                'winner': exception_provisions[0],
                'resolution_method': 'exception_rule',
                'details': 'Exception provision takes precedence'
            }
        
        # Rule 2: Penalty provisions (higher authority)
        penalty_provisions = [p for p in provisions if 'penalty' in p.text.lower() or 'জরিমানা' in p.text]
        if penalty_provisions:
            return {
                'winner': penalty_provisions[0],
                'resolution_method': 'penalty_rule',
                'details': 'Penalty provision has enhanced authority'
            }
        
        # Rule 3: Procedural vs substantive (substantive wins)
        substantive_provisions = [p for p in provisions if self._is_substantive_provision(p)]
        if substantive_provisions and len(substantive_provisions) < len(provisions):
            return {
                'winner': substantive_provisions[0],
                'resolution_method': 'substantive_rule',
                'details': 'Substantive provision overrides procedural'
            }
        
        # Final fallback: First provision (arbitrary but consistent)
        return {
            'winner': provisions[0],
            'resolution_method': 'fallback',
            'details': 'Arbitrary selection after all rules applied'
        }
    
    def _is_substantive_provision(self, provision: LegalProvision) -> bool:
        """Check if provision is substantive (vs procedural)"""
        substantive_keywords = ['tax rate', 'exemption', 'deduction', 'liability', 'কর হার', 'অব্যাহতি']
        procedural_keywords = ['filing', 'return', 'procedure', 'process', 'দাখিল', 'পদ্ধতি']
        
        text_lower = provision.text.lower()
        
        substantive_score = sum(1 for keyword in substantive_keywords if keyword in text_lower)
        procedural_score = sum(1 for keyword in procedural_keywords if keyword in text_lower)
        
        return substantive_score > procedural_score
    
    def _build_resolution_reason(self, authority_res: Dict, temporal_res: Dict, 
                                specificity_res: Dict, final_res: Dict) -> str:
        """Build human-readable resolution reason"""
        reasons = []
        
        if authority_res['eliminated']:
            reasons.append(f"Authority hierarchy: {authority_res['details']}")
        
        if temporal_res['eliminated']:
            reasons.append(f"Temporal precedence: {temporal_res['details']}")
        
        if specificity_res['eliminated']:
            reasons.append(f"Specificity rule: {specificity_res['details']}")
        
        reasons.append(f"Final resolution: {final_res['details']}")
        
        return " | ".join(reasons)
    
    def _calculate_confidence_score(self, authority_res: Dict, temporal_res: Dict, 
                                  specificity_res: Dict) -> float:
        """Calculate confidence score for resolution"""
        base_confidence = 0.5
        
        # Authority resolution adds high confidence
        if authority_res['eliminated']:
            base_confidence += 0.3
        
        # Temporal resolution adds medium confidence
        if temporal_res['eliminated']:
            base_confidence += 0.2
        
        # Specificity resolution adds medium confidence
        if specificity_res['eliminated']:
            base_confidence += 0.15
        
        # Cap at maximum confidence
        return min(0.95, base_confidence)
    
    def _build_authority_chain(self, provision: LegalProvision) -> List[str]:
        """Build authority chain for winning provision"""
        doc_type = provision.document_type
        hierarchy_info = self.precedence_hierarchy.get(doc_type, {})
        
        chain = [doc_type]
        overrides = hierarchy_info.get('overrides', [])
        chain.extend(overrides)
        
        return chain
    
    def _build_evidence_list(self, authority_res: Dict, temporal_res: Dict, 
                           specificity_res: Dict) -> List[str]:
        """Build evidence list for resolution"""
        evidence = []
        
        evidence.append(f"Authority analysis: {authority_res['details']}")
        evidence.append(f"Temporal analysis: {temporal_res['details']}")
        evidence.append(f"Specificity analysis: {specificity_res['details']}")
        
        return evidence
    
    def classify_provision(self, text: str, document_type: str, 
                          effective_date: Optional[date] = None) -> LegalProvision:
        """Classify text as legal provision with precedence metadata"""
        
        # Determine authority level
        authority_level = self.precedence_hierarchy.get(document_type, {}).get('authority_level', 50)
        
        # Extract section number if present
        section_match = re.search(r'ধারা\s*(\d+[ক-ঙ]?)|Section\s*(\d+[A-Z]?)', text)
        section_number = section_match.group(1) or section_match.group(2) if section_match else None
        
        # Determine if specific provision
        is_specific = self._is_specific_provision(text)
        
        # Determine if exception provision
        is_exception = self._is_exception_provision(text)
        
        # Determine temporal scope
        temporal_scope = self._determine_temporal_scope(text, document_type)
        
        provision = LegalProvision(
            provision_id=f"{document_type}_{hash(text) % 10000}",
            text=text,
            document_type=document_type,
            authority_level=authority_level,
            effective_date=effective_date,
            section_number=section_number,
            is_specific=is_specific,
            is_exception=is_exception,
            temporal_scope=temporal_scope,
            metadata={
                'classification_version': '2.3.0',
                'auto_classified': True
            }
        )
        
        return provision
    
    def _is_specific_provision(self, text: str) -> bool:
        """Check if provision is specific (vs general)"""
        specific_indicators = [
            'specific', 'particular', 'নির্দিষ্ট', 'বিশেষ',
            r'\d+\%',  # Specific percentages
            r'\d+\s*লক্ষ',  # Specific amounts
            'except', 'provided that', 'তবে', 'ব্যতিত'
        ]
        
        text_lower = text.lower()
        return any(re.search(indicator, text_lower) for indicator in specific_indicators)
    
    def _is_exception_provision(self, text: str) -> bool:
        """Check if provision is an exception"""
        exception_indicators = [
            'except', 'exception', 'ব্যতিত', 'ব্যতিক্রম',
            'provided that', 'তবে প্রদত্ত',
            'notwithstanding', 'সত্ত্বেও'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in exception_indicators)
    
    def _determine_temporal_scope(self, text: str, document_type: str) -> str:
        """Determine temporal scope of provision"""
        if any(word in text.lower() for word in ['temporary', 'interim', 'অস্থায়ী']):
            return 'temporary'
        elif any(word in text.lower() for word in ['financial year', 'অর্থবছর']):
            return 'financial_year'
        elif document_type == 'finance_ordinance':
            return 'financial_year'  # Budget provisions are typically annual
        else:
            return 'permanent'
    
    def get_precedence_analysis(self, provision: LegalProvision) -> Dict[str, Any]:
        """Get detailed precedence analysis for a provision"""
        doc_type = provision.document_type
        hierarchy_info = self.precedence_hierarchy.get(doc_type, {})
        
        return {
            'provision_id': provision.provision_id,
            'authority_level': provision.authority_level,
            'document_type': doc_type,
            'overrides': hierarchy_info.get('overrides', []),
            'overridden_by': [k for k, v in self.precedence_hierarchy.items() 
                             if doc_type in v.get('overrides', [])],
            'temporal_authority': hierarchy_info.get('temporal_authority', 'unknown'),
            'is_specific': provision.is_specific,
            'is_exception': provision.is_exception,
            'temporal_scope': provision.temporal_scope,
            'effective_date': provision.effective_date.isoformat() if provision.effective_date else None
        }
    
    def export_precedence_rules(self, output_path: str) -> None:
        """Export precedence rules and hierarchy to JSON"""
        export_data = {
            'precedence_hierarchy': self.precedence_hierarchy,
            'temporal_rules': self.temporal_rules,
            'special_rules': self.special_rules,
            'metadata': {
                'version': '2.3.0',
                'export_date': datetime.now().isoformat(),
                'description': 'Bangladesh Tax Law Precedence Rules'
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Precedence rules exported to {output_path}")

def main():
    """Test the Legal Precedence Engine"""
    engine = LegalPrecedenceEngine()
    
    # Create test provisions with conflicts
    provisions = [
        LegalProvision(
            provision_id="finance_ord_2025_01",
            text="২০২৫ অর্থবছরে ৪ লক্ষ টাকা পর্যন্ত আয় করমুক্ত।",
            document_type="finance_ordinance",
            authority_level=100,
            effective_date=date(2025, 7, 1),
            section_number="44",
            is_specific=True
        ),
        LegalProvision(
            provision_id="income_tax_act_44",
            text="আয়কর আইন ২০২৩ অনুযায়ী ৩.৫ লক্ষ টাকা পর্যন্ত আয় করমুক্ত।",
            document_type="income_tax_act", 
            authority_level=95,
            effective_date=date(2023, 7, 1),
            section_number="44"
        ),
        LegalProvision(
            provision_id="circular_interpretation",
            text="কর অব্যাহতি সংক্রান্ত ব্যাখ্যা: আয়ের সীমা ৩ লক্ষ টাকা।",
            document_type="circulars",
            authority_level=70,
            effective_date=date(2024, 1, 1)
        )
    ]
    
    # Resolve conflict
    resolution = engine.resolve_conflict(provisions)
    
    print("🎯 Precedence Engine Test Results:")
    print("=" * 60)
    print(f"Winning Provision: {resolution.winning_provision.provision_id}")
    print(f"Document Type: {resolution.winning_provision.document_type}")
    print(f"Authority Level: {resolution.winning_provision.authority_level}")
    print(f"Text: {resolution.winning_provision.text}")
    print()
    print(f"Resolution Reason: {resolution.resolution_reason}")
    print(f"Confidence Score: {resolution.confidence_score:.2f}")
    print(f"Authority Chain: {' > '.join(resolution.authority_chain)}")
    print()
    print("Evidence:")
    for i, evidence in enumerate(resolution.evidence, 1):
        print(f"  {i}. {evidence}")
    
    # Test precedence analysis
    print("\n📊 Precedence Analysis:")
    analysis = engine.get_precedence_analysis(resolution.winning_provision)
    for key, value in analysis.items():
        print(f"  {key}: {value}")
    
    # Export precedence rules
    output_path = Path(__file__).parent / "precedence_rules.json"
    engine.export_precedence_rules(str(output_path))

if __name__ == "__main__":
    main()