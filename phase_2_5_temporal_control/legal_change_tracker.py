#!/usr/bin/env python3
"""
Legal Change Tracker for Phase 2.5 - Fresh Implementation
=========================================================

Legal Change Impact Analysis system for Bangladesh tax laws.
Tracks how new laws affect existing provisions across financial years.

Critical Features:
- Track law version changes across financial years
- Analyze impact of new provisions on existing ones
- Detect override relationships and deprecations
- Generate stakeholder impact assessments
- Integration with Phase 2 knowledge graph

Author: Phase 2.5 Fresh Implementation
Date: August 13, 2025
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, date
from pathlib import Path
from enum import Enum
import sys

# Import our working Phase 2 components and temporal manager
sys.path.append(str(Path(__file__).parent.parent / "phase_2_knowledge_graph"))
from graph_database_setup import LegalKnowledgeGraphDatabase
from temporal_law_manager import TemporalLawManager, FinancialYear, LawVersion

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChangeType(Enum):
    """Types of legal changes"""
    OVERRIDE = "override"           # New law overrides existing provision
    AMENDMENT = "amendment"         # Existing law modified
    DEPRECATION = "deprecation"     # Old provision no longer valid
    ADDITION = "addition"           # New provision added
    CLARIFICATION = "clarification" # Interpretation clarified
    SUSPENSION = "suspension"       # Temporarily suspended

class ImpactSeverity(Enum):
    """Severity levels for change impact"""
    CRITICAL = "critical"           # Major changes affecting core provisions
    HIGH = "high"                   # Significant changes requiring attention
    MEDIUM = "medium"               # Moderate changes with limited scope
    LOW = "low"                     # Minor changes or clarifications
    INFORMATIONAL = "informational" # Information only, no action needed

class StakeholderType(Enum):
    """Types of stakeholders affected by changes"""
    INDIVIDUAL_TAXPAYERS = "individual_taxpayers"
    CORPORATE_TAXPAYERS = "corporate_taxpayers"
    TAX_PRACTITIONERS = "tax_practitioners"
    NBR_OFFICIALS = "nbr_officials"
    JUDICIARY = "judiciary"

@dataclass
class LegalChange:
    """Represents a change in legal provisions"""
    change_id: str
    change_type: ChangeType
    source_law: LawVersion      # Law making the change
    affected_law: LawVersion    # Law being changed
    affected_section: Optional[str]
    description: str
    impact_severity: ImpactSeverity
    effective_date: date
    financial_year: FinancialYear
    stakeholders_affected: List[StakeholderType]
    compliance_changes: List[str]
    confidence_score: float     # 0.0-1.0 confidence in analysis

@dataclass
class ChangeImpactAnalysis:
    """Comprehensive analysis of a legal change"""
    change: LegalChange
    cascade_effects: List[str]          # Other provisions affected
    stakeholder_impact: Dict[str, str]  # Impact per stakeholder type
    implementation_timeline: List[str]  # Required actions with dates
    risk_assessment: Dict[str, Any]     # Risk analysis
    recommendations: List[str]          # Recommended actions

class LegalChangeTracker:
    """
    Legal Change Impact Analysis system - Phase 2.5 Fresh Implementation
    Tracks how new laws affect existing provisions across financial years
    """
    
    def __init__(self, temporal_manager: Optional[TemporalLawManager] = None):
        """Initialize with temporal law manager"""
        self.temporal_manager = temporal_manager or TemporalLawManager()
        self.changes: Dict[str, LegalChange] = {}
        self.impact_analyses: Dict[str, ChangeImpactAnalysis] = {}
        
        # Initialize change tracking data
        self._initialize_change_database()
        
        logger.info("🔧 Initialized Legal Change Tracker")
        logger.info(f"📊 Connected to temporal manager with {len(self.temporal_manager.financial_years)} financial years")
    
    def _initialize_change_database(self):
        """Initialize database of legal changes across financial years"""
        
        # Track changes from FY 2023-24 to 2024-25
        self._track_fy_2024_25_changes()
        
        # Track changes from FY 2024-25 to 2025-26
        self._track_fy_2025_26_changes()
        
        logger.info(f"📋 Initialized {len(self.changes)} legal changes across financial years")
    
    def _track_fy_2024_25_changes(self):
        """Track changes introduced in FY 2024-25"""
        
        fy_2023_24 = self.temporal_manager.financial_years["2023-24"]
        fy_2024_25 = self.temporal_manager.financial_years["2024-25"]
        
        # Finance Ordinance 2024 introduced (NEW)
        finance_ordinance_2024 = LawVersion(
            document_id="finance_ordinance_2024",
            version="v1.0",
            authority_level=100,
            effective_date=date(2024, 7, 1),
            expiry_date=date(2025, 6, 30),
            financial_year=fy_2024_25,
            document_type="finance_ordinance"
        )
        
        # Income Tax Act updated
        income_tax_act_updated = LawVersion(
            document_id="income_tax_act_2023",
            version="v1.1",
            authority_level=90,
            effective_date=date(2023, 7, 1),
            expiry_date=None,
            financial_year=fy_2024_25,
            document_type="income_tax_act"
        )
        
        # Change 1: Finance Ordinance overrides Income Tax rates
        change_1 = LegalChange(
            change_id="FO_2024_OVERRIDE_ITA_RATES",
            change_type=ChangeType.OVERRIDE,
            source_law=finance_ordinance_2024,
            affected_law=income_tax_act_updated,
            affected_section="Section 44 (Tax Rates)",
            description="Finance Ordinance 2024 introduces new tax rate structure overriding Income Tax Act rates",
            impact_severity=ImpactSeverity.CRITICAL,
            effective_date=date(2024, 7, 1),
            financial_year=fy_2024_25,
            stakeholders_affected=[
                StakeholderType.INDIVIDUAL_TAXPAYERS,
                StakeholderType.CORPORATE_TAXPAYERS,
                StakeholderType.TAX_PRACTITIONERS
            ],
            compliance_changes=[
                "Update tax calculation systems",
                "Revise withholding tax rates",
                "Modify tax return forms"
            ],
            confidence_score=0.95
        )
        
        # Change 2: TDS Rules updated to reflect ordinance
        change_2 = LegalChange(
            change_id="TDS_RULES_2024_AMENDMENT",
            change_type=ChangeType.AMENDMENT,
            source_law=finance_ordinance_2024,
            affected_law=LawVersion(
                document_id="tds_rules_2024",
                version="v1.0",
                authority_level=80,
                effective_date=date(2024, 7, 1),
                expiry_date=None,
                financial_year=fy_2024_25,
                document_type="rules"
            ),
            affected_section="Rule 15 (TDS Rates)",
            description="TDS Rules updated to implement Finance Ordinance 2024 rate changes",
            impact_severity=ImpactSeverity.HIGH,
            effective_date=date(2024, 7, 1),
            financial_year=fy_2024_25,
            stakeholders_affected=[
                StakeholderType.CORPORATE_TAXPAYERS,
                StakeholderType.TAX_PRACTITIONERS,
                StakeholderType.NBR_OFFICIALS
            ],
            compliance_changes=[
                "Update TDS software",
                "Retrain TDS operators",
                "Issue new TDS certificates"
            ],
            confidence_score=0.88
        )
        
        self.changes[change_1.change_id] = change_1
        self.changes[change_2.change_id] = change_2
    
    def _track_fy_2025_26_changes(self):
        """Track changes introduced in FY 2025-26"""
        
        fy_2025_26 = self.temporal_manager.financial_years["2025-26"]
        
        # Finance Ordinance 2025 (Latest)
        finance_ordinance_2025 = LawVersion(
            document_id="finance_ordinance_2025",
            version="v1.0",
            authority_level=100,
            effective_date=date(2025, 7, 1),
            expiry_date=date(2026, 6, 30),
            financial_year=fy_2025_26,
            document_type="finance_ordinance"
        )
        
        # Income Tax Act further updated
        income_tax_act_2025 = LawVersion(
            document_id="income_tax_act_2023",
            version="v1.2",
            authority_level=90,
            effective_date=date(2023, 7, 1),
            expiry_date=None,
            financial_year=fy_2025_26,
            document_type="income_tax_act"
        )
        
        # Change 3: Digital tax provisions added
        change_3 = LegalChange(
            change_id="DIGITAL_TAX_2025_ADDITION",
            change_type=ChangeType.ADDITION,
            source_law=finance_ordinance_2025,
            affected_law=income_tax_act_2025,
            affected_section="Section 82C (Digital Services Tax)",
            description="New provisions for taxation of digital services and YouTube income",
            impact_severity=ImpactSeverity.HIGH,
            effective_date=date(2025, 7, 1),
            financial_year=fy_2025_26,
            stakeholders_affected=[
                StakeholderType.INDIVIDUAL_TAXPAYERS,
                StakeholderType.CORPORATE_TAXPAYERS,
                StakeholderType.TAX_PRACTITIONERS
            ],
            compliance_changes=[
                "Register for digital tax compliance",
                "Implement new accounting systems",
                "File additional digital income returns"
            ],
            confidence_score=0.92
        )
        
        # Change 4: Exemption threshold increased
        change_4 = LegalChange(
            change_id="EXEMPTION_THRESHOLD_2025",
            change_type=ChangeType.AMENDMENT,
            source_law=finance_ordinance_2025,
            affected_law=income_tax_act_2025,
            affected_section="Section 44 (Tax-free Income)",
            description="Tax exemption threshold increased from ৳3,50,000 to ৳4,00,000",
            impact_severity=ImpactSeverity.MEDIUM,
            effective_date=date(2025, 7, 1),
            financial_year=fy_2025_26,
            stakeholders_affected=[
                StakeholderType.INDIVIDUAL_TAXPAYERS,
                StakeholderType.TAX_PRACTITIONERS
            ],
            compliance_changes=[
                "Update tax calculation software",
                "Revise salary structures",
                "Modify withholding calculations"
            ],
            confidence_score=0.90
        )
        
        # Change 5: Old circular deprecated
        change_5 = LegalChange(
            change_id="OLD_CIRCULAR_2024_DEPRECATION",
            change_type=ChangeType.DEPRECATION,
            source_law=finance_ordinance_2025,
            affected_law=LawVersion(
                document_id="tax_circular_2024",
                version="v1.0",
                authority_level=70,
                effective_date=date(2024, 7, 1),
                expiry_date=date(2025, 6, 30),
                financial_year=self.temporal_manager.financial_years["2024-25"],
                document_type="circular"
            ),
            affected_section="Circular 05/2024 (Online Payment)",
            description="Previous online payment guidelines superseded by new Finance Ordinance provisions",
            impact_severity=ImpactSeverity.LOW,
            effective_date=date(2025, 7, 1),
            financial_year=fy_2025_26,
            stakeholders_affected=[
                StakeholderType.TAX_PRACTITIONERS,
                StakeholderType.NBR_OFFICIALS
            ],
            compliance_changes=[
                "Stop referencing old circular",
                "Update training materials",
                "Use new payment procedures"
            ],
            confidence_score=0.85
        )
        
        self.changes[change_3.change_id] = change_3
        self.changes[change_4.change_id] = change_4
        self.changes[change_5.change_id] = change_5
    
    def analyze_change_impact(self, change_id: str) -> ChangeImpactAnalysis:
        """
        Perform comprehensive impact analysis for a legal change
        
        Args:
            change_id: ID of the change to analyze
            
        Returns:
            Comprehensive impact analysis with stakeholder effects
        """
        
        if change_id not in self.changes:
            raise ValueError(f"Change {change_id} not found")
        
        change = self.changes[change_id]
        
        # Generate cascade effects analysis
        cascade_effects = self._analyze_cascade_effects(change)
        
        # Analyze stakeholder impact
        stakeholder_impact = self._analyze_stakeholder_impact(change)
        
        # Generate implementation timeline
        implementation_timeline = self._generate_implementation_timeline(change)
        
        # Perform risk assessment
        risk_assessment = self._assess_risks(change)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(change)
        
        analysis = ChangeImpactAnalysis(
            change=change,
            cascade_effects=cascade_effects,
            stakeholder_impact=stakeholder_impact,
            implementation_timeline=implementation_timeline,
            risk_assessment=risk_assessment,
            recommendations=recommendations
        )
        
        self.impact_analyses[change_id] = analysis
        logger.info(f"📊 Completed impact analysis for change {change_id}")
        
        return analysis
    
    def _analyze_cascade_effects(self, change: LegalChange) -> List[str]:
        """Analyze how change affects other provisions"""
        
        effects = []
        
        if change.change_type == ChangeType.OVERRIDE:
            effects.extend([
                f"All provisions in {change.affected_law.document_id} subordinate to {change.source_law.document_id}",
                f"Related rules and circulars may need revision",
                f"Precedent cases based on old law may be questioned"
            ])
            
        elif change.change_type == ChangeType.AMENDMENT:
            effects.extend([
                f"Dependent provisions in same document require review",
                f"Cross-references from other documents need updating",
                f"Forms and procedures may need modification"
            ])
            
        elif change.change_type == ChangeType.ADDITION:
            effects.extend([
                f"New compliance requirements across related provisions",
                f"Existing exemptions may need review",
                f"Administrative procedures require updates"
            ])
            
        elif change.change_type == ChangeType.DEPRECATION:
            effects.extend([
                f"References to deprecated provision must be removed",
                f"Alternative provisions need identification",
                f"Transition arrangements may be required"
            ])
        
        return effects
    
    def _analyze_stakeholder_impact(self, change: LegalChange) -> Dict[str, str]:
        """Analyze impact on different stakeholder groups"""
        
        impact = {}
        
        if StakeholderType.INDIVIDUAL_TAXPAYERS in change.stakeholders_affected:
            if change.change_type == ChangeType.OVERRIDE and "tax rate" in change.description.lower():
                impact["Individual Taxpayers"] = "Must recalculate tax liability using new rates, potential refund/additional payment required"
            elif change.change_type == ChangeType.ADDITION and "digital" in change.description.lower():
                impact["Individual Taxpayers"] = "New compliance obligations for digital income, registration and reporting required"
            elif "exemption threshold" in change.description.lower():
                impact["Individual Taxpayers"] = "Potential tax savings due to increased exemption limit, revised withholding applicable"
        
        if StakeholderType.CORPORATE_TAXPAYERS in change.stakeholders_affected:
            if change.change_type == ChangeType.OVERRIDE:
                impact["Corporate Taxpayers"] = "Update tax computation systems, revise advance tax payments, modify payroll systems"
            elif change.change_type == ChangeType.ADDITION:
                impact["Corporate Taxpayers"] = "Implement new compliance systems, train staff on new requirements, review business processes"
        
        if StakeholderType.TAX_PRACTITIONERS in change.stakeholders_affected:
            impact["Tax Practitioners"] = "Professional training required, update client advisory systems, revise standard procedures and forms"
        
        if StakeholderType.NBR_OFFICIALS in change.stakeholders_affected:
            impact["NBR Officials"] = "Staff training on new provisions, update assessment procedures, modify audit guidelines"
        
        if StakeholderType.JUDICIARY in change.stakeholders_affected:
            impact["Judiciary"] = "Awareness of new legal framework, revised interpretation guidelines, precedent implications"
        
        return impact
    
    def _generate_implementation_timeline(self, change: LegalChange) -> List[str]:
        """Generate implementation timeline with milestones"""
        
        timeline = []
        effective_date = change.effective_date
        
        # Pre-implementation phase
        timeline.append(f"T-30 days ({effective_date.replace(day=1).strftime('%B %Y')}): Initial awareness and planning")
        timeline.append(f"T-15 days ({effective_date.replace(day=15).strftime('%B %d, %Y')}): System updates and staff training")
        
        # Implementation
        timeline.append(f"T-Day ({effective_date.strftime('%B %d, %Y')}): New provisions become effective")
        
        # Post-implementation
        timeline.append(f"T+15 days: Monitor compliance and address initial issues")
        timeline.append(f"T+30 days: First assessment of implementation effectiveness")
        timeline.append(f"T+90 days: Comprehensive review and adjustment if needed")
        
        # Specific milestones based on change type
        if change.change_type == ChangeType.ADDITION:
            timeline.append("T+180 days: Full compliance assessment and reporting")
            
        elif change.change_type == ChangeType.OVERRIDE:
            timeline.append("T+60 days: Reconcile old vs new law applications")
            
        return timeline
    
    def _assess_risks(self, change: LegalChange) -> Dict[str, Any]:
        """Assess implementation and compliance risks"""
        
        risks = {
            "compliance_risk": "medium",
            "implementation_complexity": "medium", 
            "stakeholder_resistance": "low",
            "system_impact": "medium",
            "legal_uncertainty": "low"
        }
        
        # Adjust based on change characteristics
        if change.impact_severity == ImpactSeverity.CRITICAL:
            risks["compliance_risk"] = "high"
            risks["implementation_complexity"] = "high"
            risks["system_impact"] = "high"
            
        elif change.impact_severity == ImpactSeverity.HIGH:
            risks["compliance_risk"] = "medium-high"
            risks["implementation_complexity"] = "medium-high"
            
        if change.change_type == ChangeType.OVERRIDE:
            risks["legal_uncertainty"] = "medium"
            risks["stakeholder_resistance"] = "medium"
            
        elif change.change_type == ChangeType.ADDITION:
            risks["implementation_complexity"] = "high"
            risks["system_impact"] = "high"
        
        # Risk mitigation strategies
        risks["mitigation_strategies"] = [
            "Phased implementation approach",
            "Comprehensive stakeholder training",
            "Regular monitoring and feedback collection",
            "Clear communication of changes and timelines"
        ]
        
        return risks
    
    def _generate_recommendations(self, change: LegalChange) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # General recommendations
        recommendations.extend([
            "Establish clear communication plan for all stakeholders",
            "Develop comprehensive training materials",
            "Monitor implementation progress with regular checkpoints"
        ])
        
        # Specific to change type
        if change.change_type == ChangeType.OVERRIDE:
            recommendations.extend([
                "Create comparison guides showing old vs new provisions",
                "Establish transition period guidance",
                "Provide legal clarity on conflict resolution"
            ])
            
        elif change.change_type == ChangeType.ADDITION:
            recommendations.extend([
                "Develop step-by-step compliance guides",
                "Create template forms and procedures", 
                "Establish help desk for implementation questions"
            ])
            
        elif change.change_type == ChangeType.AMENDMENT:
            recommendations.extend([
                "Highlight specific changes from previous version",
                "Update all cross-referencing documents",
                "Provide redlined versions showing modifications"
            ])
        
        # Severity-based recommendations
        if change.impact_severity in [ImpactSeverity.CRITICAL, ImpactSeverity.HIGH]:
            recommendations.extend([
                "Consider phased rollout to manage complexity",
                "Establish dedicated support team",
                "Create contingency plans for implementation issues"
            ])
        
        return recommendations
    
    def get_changes_for_financial_year(self, financial_year: FinancialYear) -> List[LegalChange]:
        """Get all changes for a specific financial year"""
        
        fy_key = f"{financial_year.start_year}-{str(financial_year.end_year)[2:]}"
        changes = [change for change in self.changes.values() 
                  if f"{change.financial_year.start_year}-{str(change.financial_year.end_year)[2:]}" == fy_key]
        
        logger.info(f"📋 Found {len(changes)} changes for {financial_year}")
        return changes
    
    def get_changes_affecting_provision(self, provision_id: str) -> List[LegalChange]:
        """Get all changes affecting a specific legal provision"""
        
        changes = [change for change in self.changes.values()
                  if provision_id in change.affected_law.document_id or 
                     (change.affected_section and provision_id in change.affected_section)]
        
        logger.info(f"📋 Found {len(changes)} changes affecting provision {provision_id}")
        return changes
    
    def export_change_analysis(self, output_path: str) -> Dict[str, Any]:
        """Export comprehensive change analysis to JSON"""
        
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_changes": len(self.changes),
                "financial_years_covered": list(self.temporal_manager.financial_years.keys()),
                "analysis_confidence": sum(c.confidence_score for c in self.changes.values()) / len(self.changes)
            },
            "changes": {},
            "impact_analyses": {},
            "summary_statistics": self._generate_summary_statistics()
        }
        
        # Export changes (with proper date serialization)
        for change_id, change in self.changes.items():
            # Convert dataclasses to dict with date handling
            source_law_dict = asdict(change.source_law)
            source_law_dict["effective_date"] = change.source_law.effective_date.isoformat()
            if change.source_law.expiry_date:
                source_law_dict["expiry_date"] = change.source_law.expiry_date.isoformat()
            
            affected_law_dict = asdict(change.affected_law)
            affected_law_dict["effective_date"] = change.affected_law.effective_date.isoformat()
            if change.affected_law.expiry_date:
                affected_law_dict["expiry_date"] = change.affected_law.expiry_date.isoformat()
            
            export_data["changes"][change_id] = {
                "change_id": change.change_id,
                "change_type": change.change_type.value,
                "affected_section": change.affected_section,
                "description": change.description,
                "impact_severity": change.impact_severity.value,
                "effective_date": change.effective_date.isoformat(),
                "stakeholders_affected": [s.value for s in change.stakeholders_affected],
                "compliance_changes": change.compliance_changes,
                "confidence_score": change.confidence_score,
                "source_law": source_law_dict,
                "affected_law": affected_law_dict,
                "financial_year": {
                    "start_year": change.financial_year.start_year,
                    "end_year": change.financial_year.end_year,
                    "bengali_notation": change.financial_year.bengali_notation,
                    "english_notation": change.financial_year.english_notation
                }
            }
        
        # Export analyses if available
        for analysis_id, analysis in self.impact_analyses.items():
            export_data["impact_analyses"][analysis_id] = {
                "change_id": analysis.change.change_id,
                "cascade_effects": analysis.cascade_effects,
                "stakeholder_impact": analysis.stakeholder_impact,
                "implementation_timeline": analysis.implementation_timeline,
                "risk_assessment": analysis.risk_assessment,
                "recommendations": analysis.recommendations
            }
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Exported change analysis to {output_path}")
        return export_data
    
    def _generate_summary_statistics(self) -> Dict[str, Any]:
        """Generate summary statistics for all changes"""
        
        stats = {
            "change_types": {},
            "impact_severity": {},
            "stakeholder_coverage": {},
            "financial_year_distribution": {},
            "average_confidence": 0.0
        }
        
        # Count change types
        for change in self.changes.values():
            change_type = change.change_type.value
            stats["change_types"][change_type] = stats["change_types"].get(change_type, 0) + 1
            
            # Count impact severity
            severity = change.impact_severity.value
            stats["impact_severity"][severity] = stats["impact_severity"].get(severity, 0) + 1
            
            # Count financial year distribution
            fy_key = f"{change.financial_year.start_year}-{str(change.financial_year.end_year)[2:]}"
            stats["financial_year_distribution"][fy_key] = stats["financial_year_distribution"].get(fy_key, 0) + 1
            
            # Count stakeholder types
            for stakeholder in change.stakeholders_affected:
                stakeholder_type = stakeholder.value
                stats["stakeholder_coverage"][stakeholder_type] = stats["stakeholder_coverage"].get(stakeholder_type, 0) + 1
        
        # Calculate average confidence
        if self.changes:
            stats["average_confidence"] = sum(c.confidence_score for c in self.changes.values()) / len(self.changes)
        
        return stats

def main():
    """Test the legal change tracker"""
    
    print("🚀 Testing Legal Change Tracker - Phase 2.5 Fresh Implementation")
    print("=" * 70)
    
    # Initialize tracker
    tracker = LegalChangeTracker()
    
    print(f"\n📊 Change Tracking Statistics:")
    print(f"   • Total Changes: {len(tracker.changes)}")
    print(f"   • Financial Years: {len(tracker.temporal_manager.financial_years)}")
    
    # Test change analysis
    print(f"\n🔍 Testing Change Impact Analysis:")
    
    test_changes = [
        "FO_2024_OVERRIDE_ITA_RATES",
        "DIGITAL_TAX_2025_ADDITION", 
        "EXEMPTION_THRESHOLD_2025"
    ]
    
    for change_id in test_changes:
        print(f"\n📝 Analyzing: {change_id}")
        print("-" * 50)
        
        analysis = tracker.analyze_change_impact(change_id)
        
        print(f"🎯 Change Type: {analysis.change.change_type.value}")
        print(f"⚠️ Impact Severity: {analysis.change.impact_severity.value}")
        print(f"👥 Stakeholders: {len(analysis.change.stakeholders_affected)}")
        print(f"🔗 Cascade Effects: {len(analysis.cascade_effects)}")
        print(f"💡 Recommendations: {len(analysis.recommendations)}")
        print(f"📈 Confidence: {analysis.change.confidence_score:.1%}")
    
    # Test financial year filtering
    print(f"\n📅 Changes by Financial Year:")
    for fy_key, fy in tracker.temporal_manager.financial_years.items():
        changes = tracker.get_changes_for_financial_year(fy)
        print(f"   • {fy_key}: {len(changes)} changes")
    
    # Export analysis
    output_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_2_5_temporal_control/legal_change_analysis.json"
    export_data = tracker.export_change_analysis(output_path)
    
    print(f"\n✅ Legal Change Tracker testing complete!")
    print(f"📁 Analysis exported to: legal_change_analysis.json")
    print(f"📊 Average confidence: {export_data['metadata']['analysis_confidence']:.1%}")

if __name__ == "__main__":
    main()