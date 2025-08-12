#!/usr/bin/env python3
"""
Legal Change Impact Tracker for Phase 2.5 - Task 2.5.2
=======================================================

Track how new laws affect existing provisions with comprehensive impact analysis.

Core Features:
- Override relationship tracking
- Deprecation analysis with impact assessment
- Effective date management with transition periods
- Cascade impact analysis for dependent provisions
- Integration with Temporal Law Manager

Author: Phase 2.5 Implementation
Date: August 10, 2025
"""

import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, date, timedelta
from pathlib import Path
from enum import Enum
import sys

# Import Phase 2.5 components
from temporal_law_manager import TemporalLawManager, LegalVersion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChangeType(Enum):
    """Types of legal changes"""
    OVERRIDE = "override"           # New law overrides old law
    AMENDMENT = "amendment"         # Modification of existing law
    DEPRECATION = "deprecation"     # Law becomes invalid
    ADDITION = "addition"           # New provision added
    CLARIFICATION = "clarification" # Interpretive guidance
    SUSPENSION = "suspension"       # Temporary suspension
    REVIVAL = "revival"            # Previously suspended law revived

class ImpactSeverity(Enum):
    """Severity levels for change impact"""
    CRITICAL = "critical"      # Major legal change affecting core provisions
    HIGH = "high"             # Significant change affecting multiple provisions
    MEDIUM = "medium"         # Moderate change affecting specific areas
    LOW = "low"               # Minor change with limited impact
    INFORMATIONAL = "info"    # Clarification without legal impact

@dataclass
class LegalChange:
    """Structured legal change with impact metadata"""
    change_id: str
    change_type: ChangeType
    source_provision: Dict[str, Any]    # New/changed provision
    target_provision: Optional[Dict[str, Any]]  # Original provision being changed
    effective_date: date
    expiry_date: Optional[date]
    impact_severity: ImpactSeverity
    description: str
    legal_basis: str
    affected_sections: List[str]
    cascade_effects: List[str]
    transition_period: Optional[int]  # Days for transition
    metadata: Dict[str, Any]

@dataclass
class ImpactAnalysis:
    """Comprehensive impact analysis result"""
    analysis_id: str
    change: LegalChange
    direct_impacts: List[Dict[str, Any]]
    indirect_impacts: List[Dict[str, Any]]
    stakeholder_effects: Dict[str, List[str]]
    compliance_requirements: List[str]
    implementation_timeline: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    confidence_score: float

class LegalChangeTracker:
    """
    Comprehensive legal change impact analysis system.
    
    Capabilities:
    - Track legal changes across financial years
    - Analyze direct and indirect impacts
    - Identify cascade effects on related provisions
    - Generate stakeholder impact assessments
    - Provide compliance guidance and timelines
    - Risk assessment for legal changes
    """
    
    def __init__(self, temporal_manager: Optional[TemporalLawManager] = None):
        """Initialize legal change tracker"""
        self.temporal_manager = temporal_manager or TemporalLawManager()
        self.tracked_changes: Dict[str, LegalChange] = {}
        self.impact_analyses: Dict[str, ImpactAnalysis] = {}
        
        # Initialize change detection rules and impact patterns
        self.change_detection_rules = self._init_change_detection_rules()
        self.impact_patterns = self._init_impact_patterns()
        self.stakeholder_mapping = self._init_stakeholder_mapping()
        
        # Load existing changes from temporal manager
        self._load_historical_changes()
        
        logger.info("Legal Change Tracker initialized")
    
    def _init_change_detection_rules(self) -> Dict[str, Any]:
        """Initialize rules for detecting different types of changes"""
        return {
            "override_indicators": [
                "overrides", "supersedes", "replaces", "বাতিল", "পরিবর্তন",
                "replaces the provision", "shall not apply", "is hereby amended"
            ],
            "amendment_indicators": [
                "amended", "modified", "সংশোধন", "পরিবর্তিত",
                "is hereby substituted", "shall read as follows"
            ],
            "deprecation_indicators": [
                "repealed", "abolished", "discontinued", "বাতিল", "রহিত",
                "shall cease to have effect", "is hereby repealed"
            ],
            "addition_indicators": [
                "new section", "inserted", "added", "নতুন ধারা", "সংযোজন",
                "is hereby inserted", "new provision"
            ],
            "value_change_patterns": [
                r'(\d+(?:,\d+)*)\s*টাকা.*?(\d+(?:,\d+)*)\s*টাকা',  # Amount changes
                r'(\d+(?:\.\d+)?)\s*%.*?(\d+(?:\.\d+)?)\s*%',      # Rate changes
                r'(\d{4}-\d{2}).*?(\d{4}-\d{2})',                 # Year changes
            ]
        }
    
    def _init_impact_patterns(self) -> Dict[str, Any]:
        """Initialize patterns for impact analysis"""
        return {
            "high_impact_topics": [
                "tax_free_limit", "tax_rates", "penalty_provisions",
                "filing_deadlines", "minimum_tax"
            ],
            "cascade_relationships": {
                "tax_free_limit": ["tax_calculation", "return_filing_requirement", "advance_tax"],
                "tax_rates": ["tax_calculation", "withholding_tax", "minimum_tax"],
                "filing_deadlines": ["penalty_calculation", "late_filing_fee"],
                "minimum_tax": ["tax_calculation", "corporate_tax"]
            },
            "stakeholder_impact_map": {
                "individual_taxpayers": ["tax_free_limit", "tax_rates", "filing_requirements"],
                "corporate_taxpayers": ["corporate_tax", "minimum_tax", "advance_tax"],
                "tax_practitioners": ["all_changes"],
                "nbr_officials": ["compliance_procedures", "penalty_provisions"]
            }
        }
    
    def _init_stakeholder_mapping(self) -> Dict[str, List[str]]:
        """Initialize stakeholder categories and interests"""
        return {
            "individual_taxpayers": [
                "Personal income tax rates",
                "Tax-free income limits", 
                "Filing requirements and deadlines",
                "Penalty and fine provisions"
            ],
            "corporate_taxpayers": [
                "Corporate tax rates",
                "Minimum tax provisions",
                "Advance tax requirements",
                "TDS/withholding tax rules"
            ],
            "tax_practitioners": [
                "All tax law changes",
                "Procedural modifications",
                "Compliance requirements",
                "Professional responsibility rules"
            ],
            "nbr_officials": [
                "Assessment procedures",
                "Audit and investigation powers",
                "Penalty enforcement guidelines",
                "Administrative rules"
            ],
            "digital_platform_operators": [
                "Digital service tax",
                "Online income reporting",
                "Platform-specific regulations",
                "TDS on digital payments"
            ]
        }
    
    def detect_legal_changes(self, new_version: LegalVersion, 
                           previous_version: LegalVersion) -> List[LegalChange]:
        """
        Detect changes between law versions
        
        Args:
            new_version: New law version
            previous_version: Previous law version to compare against
            
        Returns:
            List of detected legal changes
        """
        logger.info(f"Detecting changes: {new_version.version_id} vs {previous_version.version_id}")
        
        detected_changes = []
        
        # Compare provisions
        new_provisions = {p.get("section", p.get("topic", "")): p for p in new_version.provisions}
        old_provisions = {p.get("section", p.get("topic", "")): p for p in previous_version.provisions}
        
        # Detect overrides and amendments
        for section_key, new_provision in new_provisions.items():
            old_provision = old_provisions.get(section_key)
            
            if old_provision:
                # Compare provisions for changes
                change = self._compare_provisions(
                    new_provision, old_provision, 
                    new_version, previous_version
                )
                if change:
                    detected_changes.append(change)
            else:
                # New provision added
                change = self._create_addition_change(
                    new_provision, new_version
                )
                detected_changes.append(change)
        
        # Detect deprecations (provisions in old but not in new)
        for section_key, old_provision in old_provisions.items():
            if section_key not in new_provisions:
                change = self._create_deprecation_change(
                    old_provision, previous_version, new_version
                )
                detected_changes.append(change)
        
        # Process version-level changes
        if new_version.changes_from_previous:
            for change_description in new_version.changes_from_previous:
                metadata_change = self._create_metadata_change(
                    change_description, new_version, previous_version
                )
                detected_changes.append(metadata_change)
        
        logger.info(f"Detected {len(detected_changes)} changes")
        return detected_changes
    
    def analyze_change_impact(self, change: LegalChange) -> ImpactAnalysis:
        """
        Perform comprehensive impact analysis for a legal change
        
        Args:
            change: Legal change to analyze
            
        Returns:
            Comprehensive impact analysis
        """
        logger.info(f"Analyzing impact for change: {change.change_id}")
        
        # Direct impact analysis
        direct_impacts = self._analyze_direct_impacts(change)
        
        # Indirect impact analysis (cascade effects)
        indirect_impacts = self._analyze_indirect_impacts(change)
        
        # Stakeholder effect analysis
        stakeholder_effects = self._analyze_stakeholder_effects(change)
        
        # Compliance requirements
        compliance_requirements = self._identify_compliance_requirements(change)
        
        # Implementation timeline
        implementation_timeline = self._create_implementation_timeline(change)
        
        # Risk assessment
        risk_assessment = self._assess_change_risks(change)
        
        # Calculate confidence score
        confidence_score = self._calculate_impact_confidence(
            direct_impacts, indirect_impacts, change
        )
        
        analysis = ImpactAnalysis(
            analysis_id=f"impact_{change.change_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            change=change,
            direct_impacts=direct_impacts,
            indirect_impacts=indirect_impacts,
            stakeholder_effects=stakeholder_effects,
            compliance_requirements=compliance_requirements,
            implementation_timeline=implementation_timeline,
            risk_assessment=risk_assessment,
            confidence_score=confidence_score
        )
        
        self.impact_analyses[analysis.analysis_id] = analysis
        
        logger.info(f"Impact analysis complete: {len(direct_impacts)} direct, {len(indirect_impacts)} indirect impacts")
        return analysis
    
    def track_change_implementation(self, change_id: str, 
                                  status_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track implementation status of a legal change
        
        Args:
            change_id: ID of change to track
            status_updates: Implementation status information
            
        Returns:
            Updated implementation tracking data
        """
        if change_id not in self.tracked_changes:
            raise ValueError(f"Change {change_id} not found in tracking system")
        
        change = self.tracked_changes[change_id]
        
        # Update tracking metadata
        if "implementation_tracking" not in change.metadata:
            change.metadata["implementation_tracking"] = []
        
        tracking_update = {
            "update_date": datetime.now().isoformat(),
            "status": status_updates.get("status", "unknown"),
            "completion_percentage": status_updates.get("completion_percentage", 0),
            "notes": status_updates.get("notes", ""),
            "stakeholder_feedback": status_updates.get("stakeholder_feedback", []),
            "implementation_challenges": status_updates.get("challenges", [])
        }
        
        change.metadata["implementation_tracking"].append(tracking_update)
        
        return {
            "change_id": change_id,
            "current_status": tracking_update["status"],
            "implementation_progress": tracking_update["completion_percentage"],
            "last_updated": tracking_update["update_date"],
            "tracking_history": change.metadata["implementation_tracking"]
        }
    
    def generate_change_report(self, financial_year: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive change report for financial year
        
        Args:
            financial_year: Target financial year (current if None)
            
        Returns:
            Comprehensive change report
        """
        if financial_year is None:
            financial_year = self.temporal_manager.current_financial_year
        
        logger.info(f"Generating change report for FY {financial_year}")
        
        # Filter changes for financial year
        fy_changes = [
            change for change in self.tracked_changes.values()
            if self._change_affects_financial_year(change, financial_year)
        ]
        
        # Group changes by type and severity
        changes_by_type = self._group_changes_by_type(fy_changes)
        changes_by_severity = self._group_changes_by_severity(fy_changes)
        
        # Analyze overall impact
        overall_impact = self._analyze_overall_impact(fy_changes)
        
        # Generate stakeholder summary
        stakeholder_summary = self._generate_stakeholder_summary(fy_changes)
        
        # Implementation status summary
        implementation_status = self._summarize_implementation_status(fy_changes)
        
        report = {
            "financial_year": financial_year,
            "report_date": datetime.now().isoformat(),
            "summary": {
                "total_changes": len(fy_changes),
                "by_type": changes_by_type,
                "by_severity": changes_by_severity,
                "implementation_rate": implementation_status.get("completion_rate", 0)
            },
            "detailed_changes": [asdict(change) for change in fy_changes],
            "overall_impact_assessment": overall_impact,
            "stakeholder_impact_summary": stakeholder_summary,
            "implementation_status": implementation_status,
            "recommendations": self._generate_change_recommendations(fy_changes),
            "metadata": {
                "report_version": "2.5.2",
                "generated_by": "Legal Change Tracker",
                "analysis_confidence": self._calculate_report_confidence(fy_changes)
            }
        }
        
        logger.info(f"Change report generated: {len(fy_changes)} changes analyzed")
        return report
    
    # Internal analysis methods
    def _load_historical_changes(self) -> None:
        """Load historical changes from temporal manager"""
        # Create changes based on temporal manager's law versions
        versions = list(self.temporal_manager.law_versions.values())
        versions.sort(key=lambda v: v.effective_date)
        
        for i in range(1, len(versions)):
            current_version = versions[i]
            previous_version = versions[i-1]
            
            changes = self.detect_legal_changes(current_version, previous_version)
            for change in changes:
                self.tracked_changes[change.change_id] = change
    
    def _compare_provisions(self, new_provision: Dict, old_provision: Dict,
                          new_version: LegalVersion, old_version: LegalVersion) -> Optional[LegalChange]:
        """Compare two provisions and detect changes"""
        
        # Check for value changes
        old_value = old_provision.get("value", "")
        new_value = new_provision.get("value", "")
        
        if old_value != new_value:
            change_type = ChangeType.OVERRIDE if new_version.authority_level > old_version.authority_level else ChangeType.AMENDMENT
            severity = self._assess_change_severity(old_provision.get("topic", ""), old_value, new_value)
            
            change = LegalChange(
                change_id=f"change_{new_version.version_id}_{old_provision.get('section', hash(str(old_provision)))}",
                change_type=change_type,
                source_provision=new_provision,
                target_provision=old_provision,
                effective_date=new_version.effective_date,
                expiry_date=new_version.expiry_date,
                impact_severity=severity,
                description=f"Changed {old_provision.get('topic', 'provision')} from {old_value} to {new_value}",
                legal_basis=new_version.version_id,
                affected_sections=[old_provision.get("section", "unknown")],
                cascade_effects=self._identify_cascade_effects(old_provision.get("topic", "")),
                transition_period=self._calculate_transition_period(change_type, severity),
                metadata={
                    "old_version": old_version.version_id,
                    "new_version": new_version.version_id,
                    "comparison_date": datetime.now().isoformat()
                }
            )
            
            return change
        
        return None
    
    def _create_addition_change(self, new_provision: Dict, new_version: LegalVersion) -> LegalChange:
        """Create change record for new provision"""
        return LegalChange(
            change_id=f"addition_{new_version.version_id}_{new_provision.get('section', hash(str(new_provision)))}",
            change_type=ChangeType.ADDITION,
            source_provision=new_provision,
            target_provision=None,
            effective_date=new_version.effective_date,
            expiry_date=new_version.expiry_date,
            impact_severity=self._assess_addition_severity(new_provision),
            description=f"Added new provision: {new_provision.get('topic', 'unknown')}",
            legal_basis=new_version.version_id,
            affected_sections=[new_provision.get("section", "new")],
            cascade_effects=[],
            transition_period=30,  # Standard 30-day notice period
            metadata={
                "provision_type": "addition",
                "version": new_version.version_id
            }
        )
    
    def _create_deprecation_change(self, old_provision: Dict, old_version: LegalVersion, 
                                 new_version: LegalVersion) -> LegalChange:
        """Create change record for deprecated provision"""
        return LegalChange(
            change_id=f"deprecation_{new_version.version_id}_{old_provision.get('section', hash(str(old_provision)))}",
            change_type=ChangeType.DEPRECATION,
            source_provision=None,
            target_provision=old_provision,
            effective_date=new_version.effective_date,
            expiry_date=None,
            impact_severity=self._assess_deprecation_severity(old_provision),
            description=f"Deprecated provision: {old_provision.get('topic', 'unknown')}",
            legal_basis=new_version.version_id,
            affected_sections=[old_provision.get("section", "unknown")],
            cascade_effects=self._identify_cascade_effects(old_provision.get("topic", "")),
            transition_period=90,  # 90-day deprecation notice
            metadata={
                "deprecated_from": old_version.version_id,
                "deprecation_reason": "not_included_in_new_version"
            }
        )
    
    def _create_metadata_change(self, change_description: str, new_version: LegalVersion, 
                              old_version: LegalVersion) -> LegalChange:
        """Create change record from metadata description"""
        return LegalChange(
            change_id=f"metadata_{new_version.version_id}_{hash(change_description)}",
            change_type=ChangeType.CLARIFICATION,
            source_provision={"text": change_description, "type": "metadata"},
            target_provision=None,
            effective_date=new_version.effective_date,
            expiry_date=new_version.expiry_date,
            impact_severity=ImpactSeverity.LOW,
            description=change_description,
            legal_basis=new_version.version_id,
            affected_sections=[],
            cascade_effects=[],
            transition_period=0,
            metadata={
                "source": "version_metadata",
                "change_description": change_description
            }
        )
    
    def _analyze_direct_impacts(self, change: LegalChange) -> List[Dict[str, Any]]:
        """Analyze direct impacts of a legal change"""
        impacts = []
        
        # Impact on affected sections
        for section in change.affected_sections:
            impacts.append({
                "impact_type": "section_modification",
                "affected_entity": f"Section {section}",
                "impact_description": f"{change.change_type.value} affects section {section}",
                "severity": change.impact_severity.value
            })
        
        # Impact based on change type
        if change.change_type == ChangeType.OVERRIDE:
            impacts.append({
                "impact_type": "legal_precedence",
                "affected_entity": "Legal hierarchy",
                "impact_description": "New provision overrides previous legal interpretation",
                "severity": change.impact_severity.value
            })
        
        return impacts
    
    def _analyze_indirect_impacts(self, change: LegalChange) -> List[Dict[str, Any]]:
        """Analyze indirect/cascade impacts of a legal change"""
        impacts = []
        
        # Cascade effects
        for effect in change.cascade_effects:
            impacts.append({
                "impact_type": "cascade_effect",
                "affected_entity": effect,
                "impact_description": f"Change cascades to {effect}",
                "severity": "medium"
            })
        
        # Related provision impacts
        if change.target_provision:
            topic = change.target_provision.get("topic", "")
            if topic in self.impact_patterns["cascade_relationships"]:
                related_areas = self.impact_patterns["cascade_relationships"][topic]
                for area in related_areas:
                    impacts.append({
                        "impact_type": "related_provision",
                        "affected_entity": area,
                        "impact_description": f"Indirect impact on {area}",
                        "severity": "low"
                    })
        
        return impacts
    
    def _analyze_stakeholder_effects(self, change: LegalChange) -> Dict[str, List[str]]:
        """Analyze effects on different stakeholder groups"""
        effects = {}
        
        change_topic = change.source_provision.get("topic", "") if change.source_provision else ""
        if not change_topic and change.target_provision:
            change_topic = change.target_provision.get("topic", "")
        
        for stakeholder, interests in self.stakeholder_mapping.items():
            stakeholder_effects = []
            
            # Check if change affects stakeholder interests
            if "all_changes" in interests or change_topic in interests:
                stakeholder_effects.append(f"Direct impact from {change.description}")
            
            # Check indirect effects
            for effect in change.cascade_effects:
                if effect in interests:
                    stakeholder_effects.append(f"Indirect impact through {effect}")
            
            if stakeholder_effects:
                effects[stakeholder] = stakeholder_effects
        
        return effects
    
    def _identify_compliance_requirements(self, change: LegalChange) -> List[str]:
        """Identify compliance requirements resulting from change"""
        requirements = []
        
        if change.change_type == ChangeType.ADDITION:
            requirements.append("Review new provision requirements")
            requirements.append("Update compliance procedures")
        
        if change.change_type == ChangeType.OVERRIDE:
            requirements.append("Discontinue old procedures")
            requirements.append("Implement new procedures")
            requirements.append("Staff training on changes")
        
        if change.impact_severity in [ImpactSeverity.CRITICAL, ImpactSeverity.HIGH]:
            requirements.append("Immediate compliance review required")
            requirements.append("Stakeholder notification mandatory")
        
        if change.transition_period and change.transition_period > 0:
            requirements.append(f"Transition period compliance ({change.transition_period} days)")
        
        return requirements
    
    def _create_implementation_timeline(self, change: LegalChange) -> Dict[str, Any]:
        """Create implementation timeline for change"""
        timeline = {
            "effective_date": change.effective_date.isoformat(),
            "transition_period_days": change.transition_period or 0,
            "milestones": []
        }
        
        if change.transition_period:
            # Create milestone dates
            effective_date = change.effective_date
            
            # Announcement milestone (30 days before)
            announcement_date = effective_date - timedelta(days=min(30, change.transition_period))
            timeline["milestones"].append({
                "date": announcement_date.isoformat(),
                "milestone": "Change announcement",
                "description": "Official announcement of legal change"
            })
            
            # Preparation milestone (mid-transition)
            if change.transition_period > 30:
                prep_date = effective_date - timedelta(days=change.transition_period // 2)
                timeline["milestones"].append({
                    "date": prep_date.isoformat(),
                    "milestone": "Preparation phase",
                    "description": "Stakeholder preparation and system updates"
                })
            
            # Implementation milestone
            timeline["milestones"].append({
                "date": effective_date.isoformat(),
                "milestone": "Implementation",
                "description": "Change becomes effective"
            })
        
        return timeline
    
    def _assess_change_risks(self, change: LegalChange) -> Dict[str, Any]:
        """Assess risks associated with change"""
        risks = {
            "compliance_risk": "medium",
            "implementation_risk": "medium", 
            "stakeholder_impact_risk": "medium",
            "legal_interpretation_risk": "low",
            "mitigation_strategies": []
        }
        
        # Assess based on severity
        if change.impact_severity == ImpactSeverity.CRITICAL:
            risks["compliance_risk"] = "high"
            risks["stakeholder_impact_risk"] = "high"
            risks["mitigation_strategies"].extend([
                "Immediate stakeholder notification",
                "Emergency compliance review",
                "Legal expert consultation"
            ])
        
        # Assess based on change type
        if change.change_type == ChangeType.OVERRIDE:
            risks["legal_interpretation_risk"] = "medium"
            risks["mitigation_strategies"].append("Clear precedence documentation")
        
        if change.transition_period and change.transition_period < 30:
            risks["implementation_risk"] = "high"
            risks["mitigation_strategies"].append("Expedited implementation process")
        
        return risks
    
    # Utility methods
    def _assess_change_severity(self, topic: str, old_value: str, new_value: str) -> ImpactSeverity:
        """Assess severity of a change"""
        if topic in self.impact_patterns["high_impact_topics"]:
            return ImpactSeverity.HIGH
        
        # Check for significant numerical changes
        if old_value.isdigit() and new_value.isdigit():
            old_num = int(old_value)
            new_num = int(new_value)
            change_percent = abs(new_num - old_num) / old_num if old_num > 0 else 1
            
            if change_percent > 0.2:  # >20% change
                return ImpactSeverity.HIGH
            elif change_percent > 0.1:  # >10% change
                return ImpactSeverity.MEDIUM
        
        return ImpactSeverity.LOW
    
    def _assess_addition_severity(self, provision: Dict) -> ImpactSeverity:
        """Assess severity of new provision"""
        topic = provision.get("topic", "")
        
        if topic in self.impact_patterns["high_impact_topics"]:
            return ImpactSeverity.HIGH
        
        if "penalty" in provision.get("text", "").lower():
            return ImpactSeverity.MEDIUM
        
        return ImpactSeverity.LOW
    
    def _assess_deprecation_severity(self, provision: Dict) -> ImpactSeverity:
        """Assess severity of deprecated provision"""
        topic = provision.get("topic", "")
        
        if topic in self.impact_patterns["high_impact_topics"]:
            return ImpactSeverity.HIGH
        
        return ImpactSeverity.MEDIUM
    
    def _identify_cascade_effects(self, topic: str) -> List[str]:
        """Identify cascade effects for a topic"""
        return self.impact_patterns["cascade_relationships"].get(topic, [])
    
    def _calculate_transition_period(self, change_type: ChangeType, severity: ImpactSeverity) -> int:
        """Calculate appropriate transition period in days"""
        base_periods = {
            ChangeType.ADDITION: 30,
            ChangeType.OVERRIDE: 60,
            ChangeType.AMENDMENT: 45,
            ChangeType.DEPRECATION: 90,
            ChangeType.CLARIFICATION: 0
        }
        
        base = base_periods.get(change_type, 30)
        
        # Adjust based on severity
        if severity == ImpactSeverity.CRITICAL:
            return base + 30
        elif severity == ImpactSeverity.HIGH:
            return base + 15
        
        return base
    
    def _calculate_impact_confidence(self, direct_impacts: List, indirect_impacts: List, 
                                   change: LegalChange) -> float:
        """Calculate confidence score for impact analysis"""
        base_confidence = 0.7
        
        # Boost for comprehensive analysis
        if direct_impacts:
            base_confidence += 0.1
        if indirect_impacts:
            base_confidence += 0.1
        
        # Boost for high-confidence change types
        if change.change_type in [ChangeType.OVERRIDE, ChangeType.ADDITION]:
            base_confidence += 0.1
        
        return min(0.95, base_confidence)
    
    # Report generation methods
    def _change_affects_financial_year(self, change: LegalChange, financial_year: str) -> bool:
        """Check if change affects specific financial year"""
        fy_info = self.temporal_manager.financial_year_mapping.get(financial_year)
        if not fy_info:
            return False
        
        return (fy_info["start_date"] <= change.effective_date <= fy_info["end_date"])
    
    def _group_changes_by_type(self, changes: List[LegalChange]) -> Dict[str, int]:
        """Group changes by type"""
        groups = {}
        for change in changes:
            change_type = change.change_type.value
            groups[change_type] = groups.get(change_type, 0) + 1
        return groups
    
    def _group_changes_by_severity(self, changes: List[LegalChange]) -> Dict[str, int]:
        """Group changes by severity"""
        groups = {}
        for change in changes:
            severity = change.impact_severity.value
            groups[severity] = groups.get(severity, 0) + 1
        return groups
    
    def _analyze_overall_impact(self, changes: List[LegalChange]) -> Dict[str, Any]:
        """Analyze overall impact of all changes"""
        critical_changes = sum(1 for c in changes if c.impact_severity == ImpactSeverity.CRITICAL)
        high_changes = sum(1 for c in changes if c.impact_severity == ImpactSeverity.HIGH)
        
        overall_severity = "low"
        if critical_changes > 0:
            overall_severity = "critical"
        elif high_changes > 3:
            overall_severity = "high"
        elif high_changes > 0:
            overall_severity = "medium"
        
        return {
            "overall_severity": overall_severity,
            "critical_changes": critical_changes,
            "high_impact_changes": high_changes,
            "total_affected_sections": len(set(s for c in changes for s in c.affected_sections)),
            "implementation_complexity": "high" if len(changes) > 10 else "medium"
        }
    
    def _generate_stakeholder_summary(self, changes: List[LegalChange]) -> Dict[str, Any]:
        """Generate stakeholder impact summary"""
        stakeholder_impacts = {}
        
        for change in changes:
            for stakeholder, effects in self._analyze_stakeholder_effects(change).items():
                if stakeholder not in stakeholder_impacts:
                    stakeholder_impacts[stakeholder] = []
                stakeholder_impacts[stakeholder].extend(effects)
        
        return stakeholder_impacts
    
    def _summarize_implementation_status(self, changes: List[LegalChange]) -> Dict[str, Any]:
        """Summarize implementation status"""
        total_changes = len(changes)
        implemented_changes = 0
        
        for change in changes:
            tracking = change.metadata.get("implementation_tracking", [])
            if tracking:
                latest_status = tracking[-1].get("status", "unknown")
                if latest_status in ["completed", "implemented"]:
                    implemented_changes += 1
        
        completion_rate = implemented_changes / total_changes if total_changes > 0 else 0
        
        return {
            "total_changes": total_changes,
            "implemented_changes": implemented_changes,
            "completion_rate": completion_rate,
            "pending_changes": total_changes - implemented_changes
        }
    
    def _generate_change_recommendations(self, changes: List[LegalChange]) -> List[str]:
        """Generate recommendations based on changes"""
        recommendations = []
        
        critical_changes = [c for c in changes if c.impact_severity == ImpactSeverity.CRITICAL]
        if critical_changes:
            recommendations.append("Immediate attention required for critical changes")
            recommendations.append("Establish change management team for critical implementations")
        
        high_impact_changes = [c for c in changes if c.impact_severity == ImpactSeverity.HIGH]
        if len(high_impact_changes) > 5:
            recommendations.append("Consider phased implementation approach for multiple high-impact changes")
        
        recommendations.append("Regular stakeholder communication recommended")
        recommendations.append("Monitor implementation progress and adjust timelines as needed")
        
        return recommendations
    
    def _calculate_report_confidence(self, changes: List[LegalChange]) -> float:
        """Calculate overall confidence for report"""
        if not changes:
            return 0.0
        
        # Average confidence of individual impact analyses
        total_confidence = 0
        analyzed_changes = 0
        
        for change in changes:
            # Find corresponding impact analysis
            analysis = next((a for a in self.impact_analyses.values() 
                           if a.change.change_id == change.change_id), None)
            if analysis:
                total_confidence += analysis.confidence_score
                analyzed_changes += 1
        
        if analyzed_changes == 0:
            return 0.7  # Default confidence
        
        return total_confidence / analyzed_changes
    
    def export_change_data(self, output_path: str) -> None:
        """Export change tracking data to JSON"""
        export_data = {
            "tracked_changes": {k: asdict(v) for k, v in self.tracked_changes.items()},
            "impact_analyses": {k: asdict(v) for k, v in self.impact_analyses.items()},
            "change_detection_rules": self.change_detection_rules,
            "impact_patterns": self.impact_patterns,
            "stakeholder_mapping": self.stakeholder_mapping,
            "metadata": {
                "version": "2.5.2",
                "export_date": datetime.now().isoformat(),
                "total_changes": len(self.tracked_changes),
                "total_analyses": len(self.impact_analyses)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Change tracking data exported to {output_path}")

def main():
    """Test the Legal Change Tracker"""
    tracker = LegalChangeTracker()
    
    print("📊 Legal Change Tracker Test")
    print("=" * 50)
    
    # Test change detection
    print(f"Total tracked changes: {len(tracker.tracked_changes)}")
    
    # Test impact analysis for first change
    if tracker.tracked_changes:
        first_change = next(iter(tracker.tracked_changes.values()))
        print(f"\nAnalyzing change: {first_change.change_id}")
        print(f"Change type: {first_change.change_type.value}")
        print(f"Impact severity: {first_change.impact_severity.value}")
        
        # Perform impact analysis
        analysis = tracker.analyze_change_impact(first_change)
        print(f"Direct impacts: {len(analysis.direct_impacts)}")
        print(f"Indirect impacts: {len(analysis.indirect_impacts)}")
        print(f"Affected stakeholders: {len(analysis.stakeholder_effects)}")
        print(f"Analysis confidence: {analysis.confidence_score:.2f}")
    
    # Generate change report
    print(f"\n📈 Generating Change Report...")
    report = tracker.generate_change_report()
    
    print(f"Financial Year: {report['financial_year']}")
    print(f"Total Changes: {report['summary']['total_changes']}")
    print(f"Changes by Type: {report['summary']['by_type']}")
    print(f"Changes by Severity: {report['summary']['by_severity']}")
    print(f"Overall Impact: {report['overall_impact_assessment']['overall_severity']}")
    
    # Export change data
    output_path = Path(__file__).parent / "legal_change_data.json"
    tracker.export_change_data(str(output_path))
    print(f"\n✅ Change tracking data exported to: {output_path}")

if __name__ == "__main__":
    main()