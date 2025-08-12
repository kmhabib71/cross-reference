#!/usr/bin/env python3
"""
Expert Validation Panel Framework - Phase 4.4 Implementation
===========================================================
Professional validation system by qualified Bangladesh tax lawyers for ensuring
legal accuracy and compliance. Manages expert panels, validation workflows,
and professional review processes for AI-generated tax advice.

Features structured expert recruitment, blind validation protocols, consensus
mechanisms, and continuous professional feedback integration.

Author: Phase 4 Implementation
Date: August 11, 2025
Target: >95% expert validation accuracy with professional consensus
"""

import json
import logging
import hashlib
from typing import Dict, List, Tuple, Optional, Any, Union, Set
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExpertLevel(Enum):
    """Expert qualification levels"""
    JUNIOR = "junior"          # 2-5 years experience
    SENIOR = "senior"          # 5-10 years experience  
    PRINCIPAL = "principal"    # 10+ years experience
    SPECIALIST = "specialist"  # Domain-specific expertise

class ExpertiseArea(Enum):
    """Areas of tax law expertise"""
    INDIVIDUAL_TAX = "individual_tax"
    CORPORATE_TAX = "corporate_tax"
    TDS_VAT = "tds_vat"
    APPEALS_LITIGATION = "appeals_litigation"
    INTERNATIONAL_TAX = "international_tax"
    TAX_PLANNING = "tax_planning"
    COMPLIANCE = "compliance"
    AUDIT_INVESTIGATION = "audit_investigation"

class ValidationStatus(Enum):
    """Validation review status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    CONSENSUS_REQUIRED = "consensus_required"

class ValidationDecision(Enum):
    """Expert validation decisions"""
    ACCURATE = "accurate"          # Fully accurate response
    MOSTLY_ACCURATE = "mostly_accurate"  # Minor issues only
    PARTIALLY_ACCURATE = "partially_accurate"  # Some accuracy concerns
    INACCURATE = "inaccurate"     # Significant accuracy issues
    DANGEROUS = "dangerous"        # Could cause harm - immediate escalation

class ConflictResolution(Enum):
    """Methods for resolving expert disagreements"""
    SENIOR_OVERRIDE = "senior_override"    # Senior expert decision final
    CONSENSUS_VOTE = "consensus_vote"      # Majority vote among panel
    ESCALATION = "escalation"              # Escalate to specialist panel
    REVISED_REVIEW = "revised_review"      # Additional expert review

@dataclass
class ExpertProfile:
    """Professional expert profile"""
    expert_id: str
    name: str
    email: str
    phone: str
    level: ExpertLevel
    expertise_areas: List[ExpertiseArea]
    
    # Professional credentials
    bar_registration: str
    years_experience: int
    current_firm: str
    professional_certifications: List[str]
    
    # System integration
    joined_date: datetime
    last_active: datetime
    total_validations: int = 0
    accuracy_score: float = 0.0  # How often their decisions align with consensus
    avg_response_time: float = 0.0  # Hours to complete validation
    
    # Specialization scores (0-1) - system calculated
    specialization_scores: Dict[str, float] = field(default_factory=dict)
    
    # Status and availability
    active: bool = True
    available_hours: Dict[str, List[str]] = field(default_factory=dict)  # Day -> ["09:00-12:00", ...]
    max_weekly_validations: int = 20

@dataclass
class ValidationRequest:
    """Individual validation request"""
    request_id: str
    timestamp: datetime
    
    # Query and response data (anonymized)
    query_hash: str  # Hashed for privacy
    query_category: ExpertiseArea
    query_complexity: float  # 0-1 scale
    ai_response: str
    ai_confidence: float
    
    # Legal context
    relevant_sections: List[str]
    financial_year: str
    estimated_stakes: str  # "low", "medium", "high"
    
    # Assignment
    assigned_experts: List[str]  # List of expert_ids
    required_consensus: int = 2  # Number of experts needed
    priority: int = 3  # 1-5 (5=highest)
    
    # Status tracking
    status: ValidationStatus = ValidationStatus.PENDING
    created_by: str = "system"

@dataclass
class ExpertValidation:
    """Individual expert's validation of a request"""
    validation_id: str
    request_id: str
    expert_id: str
    timestamp: datetime
    
    # Expert assessment
    decision: ValidationDecision
    confidence_level: float  # Expert's confidence in their decision (0-1)
    
    # Detailed feedback
    accuracy_score: float  # 0-1 overall accuracy assessment
    completeness_score: float  # 0-1 completeness assessment
    professional_quality: float  # 0-1 professional standard assessment
    
    # Specific feedback
    legal_accuracy_comments: str
    citation_accuracy_comments: str
    professional_format_comments: str
    improvement_suggestions: List[str]
    
    # Critical issues identification
    critical_errors: List[str] = field(default_factory=list)
    safety_concerns: List[str] = field(default_factory=list)
    
    # Review metadata
    time_spent_minutes: int = 0
    reviewed_sources: List[str] = field(default_factory=list)

@dataclass
class ConsensusResult:
    """Final consensus result for a validation request"""
    request_id: str
    timestamp: datetime
    
    # Consensus decision
    final_decision: ValidationDecision
    consensus_confidence: float  # 0-1 confidence in consensus
    participating_experts: List[str]
    
    # Aggregated scores
    avg_accuracy_score: float
    avg_completeness_score: float
    avg_professional_quality: float
    
    # Conflict resolution (non-default fields)
    had_conflicts: bool
    consolidated_feedback: str
    priority_improvements: List[str]
    critical_issues: List[str]
    
    # Optional fields with defaults (must come after non-default fields)
    resolution_method: Optional[ConflictResolution] = None
    affects_system_confidence: bool = False
    recommended_system_changes: List[str] = field(default_factory=list)

class ExpertValidationSystem:
    """
    Professional expert validation system for Bangladesh AI Tax Lawyer
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize expert validation system"""
        self.config = self._load_config(config_path)
        
        # Expert management
        self.experts: Dict[str, ExpertProfile] = {}
        self.validation_requests: Dict[str, ValidationRequest] = {}
        self.expert_validations: Dict[str, ExpertValidation] = {}
        self.consensus_results: Dict[str, ConsensusResult] = {}
        
        # Operational data
        self.assignment_history = defaultdict(list)
        self.expert_performance = defaultdict(dict)
        self.validation_metrics = defaultdict(float)
        
        # Load existing data if available
        self._load_existing_data()
        
        logger.info("Expert Validation System initialized successfully")

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load expert validation configuration"""
        default_config = {
            "validation_thresholds": {
                "consensus_agreement": 0.8,      # 80% agreement for consensus
                "critical_escalation": 0.3,     # <30% accuracy triggers escalation
                "priority_response_hours": 24,   # High priority response time
                "standard_response_hours": 72    # Standard response time
            },
            "expert_requirements": {
                "min_experience_years": 2,
                "max_concurrent_validations": 10,
                "required_certifications": ["Bar Registration", "Tax Law Certificate"],
                "performance_review_interval": 90  # days
            },
            "assignment_rules": {
                "expertise_matching_weight": 0.4,
                "availability_weight": 0.3,
                "workload_balance_weight": 0.2,
                "performance_weight": 0.1
            },
            "quality_standards": {
                "min_accuracy_score": 0.85,
                "min_completeness_score": 0.90,
                "min_professional_quality": 0.95,
                "consensus_threshold": 0.8
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config

    def register_expert(self, name: str, email: str, phone: str, level: ExpertLevel,
                       expertise_areas: List[ExpertiseArea], bar_registration: str,
                       years_experience: int, current_firm: str,
                       certifications: List[str]) -> str:
        """
        Register new expert with the validation panel
        
        Args:
            name: Expert's full name
            email: Professional email address
            phone: Contact phone number
            level: Professional level (junior/senior/principal/specialist)
            expertise_areas: List of expertise areas
            bar_registration: Bar association registration number
            years_experience: Years of professional experience
            current_firm: Current law firm/organization
            certifications: Professional certifications
            
        Returns:
            Expert ID for system reference
        """
        # Generate unique expert ID
        expert_id = f"EXP_{datetime.now().strftime('%Y%m%d')}_{len(self.experts):04d}"
        
        # Validate expert qualifications
        if years_experience < self.config["expert_requirements"]["min_experience_years"]:
            raise ValueError(f"Minimum {self.config['expert_requirements']['min_experience_years']} years experience required")
        
        # Check for required certifications
        required_certs = self.config["expert_requirements"]["required_certifications"]
        if not any(req_cert in certifications for req_cert in required_certs):
            raise ValueError(f"Must have one of: {required_certs}")
        
        # Create expert profile
        expert = ExpertProfile(
            expert_id=expert_id,
            name=name,
            email=email,
            phone=phone,
            level=level,
            expertise_areas=expertise_areas,
            bar_registration=bar_registration,
            years_experience=years_experience,
            current_firm=current_firm,
            professional_certifications=certifications,
            joined_date=datetime.now(),
            last_active=datetime.now()
        )
        
        # Initialize specialization scores
        for area in expertise_areas:
            base_score = 0.7 if level == ExpertLevel.JUNIOR else 0.8 if level == ExpertLevel.SENIOR else 0.9
            expert.specialization_scores[area.value] = base_score
        
        self.experts[expert_id] = expert
        
        logger.info(f"Registered expert {expert_id}: {name} ({level.value}) - {len(expertise_areas)} expertise areas")
        
        return expert_id

    def submit_validation_request(self, query: str, ai_response: str, ai_confidence: float,
                                relevant_sections: List[str], financial_year: str,
                                category: ExpertiseArea, complexity: float = 0.5,
                                priority: int = 3, estimated_stakes: str = "medium") -> str:
        """
        Submit AI response for expert validation
        
        Args:
            query: Original user query (will be hashed for privacy)
            ai_response: AI-generated response to validate
            ai_confidence: AI system's confidence score
            relevant_sections: Relevant legal sections/acts
            financial_year: Applicable financial year
            category: Primary expertise area needed
            complexity: Query complexity (0-1)
            priority: Validation priority (1-5)
            estimated_stakes: Financial/legal stakes ("low", "medium", "high")
            
        Returns:
            Request ID for tracking
        """
        # Generate request ID
        request_id = f"VR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.validation_requests):04d}"
        
        # Hash query for privacy
        query_hash = hashlib.sha256(query.encode('utf-8')).hexdigest()[:16]
        
        # Determine required consensus based on stakes and complexity
        required_consensus = self._calculate_required_consensus(complexity, estimated_stakes, priority)
        
        # Create validation request
        request = ValidationRequest(
            request_id=request_id,
            timestamp=datetime.now(),
            query_hash=query_hash,
            query_category=category,
            query_complexity=complexity,
            ai_response=ai_response,
            ai_confidence=ai_confidence,
            relevant_sections=relevant_sections,
            financial_year=financial_year,
            estimated_stakes=estimated_stakes,
            assigned_experts=[],  # Will be populated by assignment
            required_consensus=required_consensus,
            priority=priority,
            status=ValidationStatus.PENDING
        )
        
        self.validation_requests[request_id] = request
        
        # Automatically assign experts
        assigned_experts = self._assign_experts(request)
        request.assigned_experts = assigned_experts
        request.status = ValidationStatus.IN_REVIEW
        
        logger.info(f"Submitted validation request {request_id} - assigned to {len(assigned_experts)} experts")
        
        return request_id

    def _calculate_required_consensus(self, complexity: float, estimated_stakes: str, priority: int) -> int:
        """Calculate number of experts needed for consensus"""
        base_consensus = 2
        
        # Increase for high complexity
        if complexity > 0.8:
            base_consensus += 1
        
        # Increase for high stakes
        if estimated_stakes == "high":
            base_consensus += 1
        
        # Increase for high priority
        if priority >= 4:
            base_consensus += 1
        
        return min(base_consensus, 5)  # Cap at 5 experts

    def _assign_experts(self, request: ValidationRequest) -> List[str]:
        """Intelligently assign experts to validation request"""
        # Filter eligible experts
        eligible_experts = []
        
        for expert_id, expert in self.experts.items():
            if not expert.active:
                continue
                
            # Check expertise match
            if request.query_category not in expert.expertise_areas:
                continue
            
            # Check availability
            current_workload = len([r for r in self.validation_requests.values() 
                                  if expert_id in r.assigned_experts and r.status == ValidationStatus.IN_REVIEW])
            
            if current_workload >= expert.max_weekly_validations:
                continue
            
            eligible_experts.append(expert_id)
        
        if len(eligible_experts) < request.required_consensus:
            logger.warning(f"Not enough eligible experts for request {request.request_id}")
            # Assign available experts anyway
            return eligible_experts[:request.required_consensus]
        
        # Score experts for this request
        expert_scores = {}
        
        for expert_id in eligible_experts:
            expert = self.experts[expert_id]
            score = 0.0
            
            # Expertise matching
            expertise_score = expert.specialization_scores.get(request.query_category.value, 0.5)
            score += expertise_score * self.config["assignment_rules"]["expertise_matching_weight"]
            
            # Availability (lower workload = higher score)
            current_workload = len([r for r in self.validation_requests.values() 
                                  if expert_id in r.assigned_experts and r.status == ValidationStatus.IN_REVIEW])
            availability_score = 1.0 - (current_workload / expert.max_weekly_validations)
            score += availability_score * self.config["assignment_rules"]["availability_weight"]
            
            # Performance (higher accuracy = higher score)
            performance_score = expert.accuracy_score if expert.accuracy_score > 0 else 0.8  # Default for new experts
            score += performance_score * self.config["assignment_rules"]["performance_weight"]
            
            # Workload balance (prefer experts with fewer recent assignments)
            recent_assignments = len(self.assignment_history[expert_id][-10:])  # Last 10 assignments
            balance_score = 1.0 - (recent_assignments / 10.0)
            score += balance_score * self.config["assignment_rules"]["workload_balance_weight"]
            
            expert_scores[expert_id] = score
        
        # Select top experts
        sorted_experts = sorted(expert_scores.items(), key=lambda x: x[1], reverse=True)
        assigned_experts = [expert_id for expert_id, score in sorted_experts[:request.required_consensus]]
        
        # Update assignment history
        for expert_id in assigned_experts:
            self.assignment_history[expert_id].append({
                'request_id': request.request_id,
                'timestamp': datetime.now(),
                'category': request.query_category.value
            })
        
        return assigned_experts

    def submit_expert_validation(self, request_id: str, expert_id: str, decision: ValidationDecision,
                                confidence_level: float, accuracy_score: float, completeness_score: float,
                                professional_quality: float, legal_accuracy_comments: str,
                                citation_accuracy_comments: str, professional_format_comments: str,
                                improvement_suggestions: List[str], time_spent_minutes: int,
                                critical_errors: List[str] = None, safety_concerns: List[str] = None,
                                reviewed_sources: List[str] = None) -> str:
        """
        Submit expert validation for a request
        
        Args:
            request_id: Validation request ID
            expert_id: Expert submitting validation
            decision: Overall validation decision
            confidence_level: Expert's confidence in decision (0-1)
            accuracy_score: Legal accuracy assessment (0-1)
            completeness_score: Completeness assessment (0-1)
            professional_quality: Professional quality assessment (0-1)
            legal_accuracy_comments: Comments on legal accuracy
            citation_accuracy_comments: Comments on citation accuracy
            professional_format_comments: Comments on professional format
            improvement_suggestions: List of improvement suggestions
            time_spent_minutes: Time spent on validation
            critical_errors: List of critical errors identified
            safety_concerns: List of safety concerns
            reviewed_sources: Sources reviewed during validation
            
        Returns:
            Validation ID
        """
        # Validate request exists and expert is assigned
        if request_id not in self.validation_requests:
            raise ValueError(f"Validation request {request_id} not found")
        
        request = self.validation_requests[request_id]
        if expert_id not in request.assigned_experts:
            raise ValueError(f"Expert {expert_id} not assigned to request {request_id}")
        
        # Check if expert already submitted validation
        existing_validation = next(
            (v for v in self.expert_validations.values() 
             if v.request_id == request_id and v.expert_id == expert_id),
            None
        )
        if existing_validation:
            raise ValueError(f"Expert {expert_id} already validated request {request_id}")
        
        # Generate validation ID
        validation_id = f"VAL_{request_id}_{expert_id}_{datetime.now().strftime('%H%M%S')}"
        
        # Create validation
        validation = ExpertValidation(
            validation_id=validation_id,
            request_id=request_id,
            expert_id=expert_id,
            timestamp=datetime.now(),
            decision=decision,
            confidence_level=confidence_level,
            accuracy_score=accuracy_score,
            completeness_score=completeness_score,
            professional_quality=professional_quality,
            legal_accuracy_comments=legal_accuracy_comments,
            citation_accuracy_comments=citation_accuracy_comments,
            professional_format_comments=professional_format_comments,
            improvement_suggestions=improvement_suggestions or [],
            critical_errors=critical_errors or [],
            safety_concerns=safety_concerns or [],
            time_spent_minutes=time_spent_minutes,
            reviewed_sources=reviewed_sources or []
        )
        
        self.expert_validations[validation_id] = validation
        
        # Update expert statistics
        expert = self.experts[expert_id]
        expert.total_validations += 1
        expert.last_active = datetime.now()
        
        # Update average response time
        time_since_assignment = (datetime.now() - request.timestamp).total_seconds() / 3600  # hours
        if expert.avg_response_time == 0:
            expert.avg_response_time = time_since_assignment
        else:
            expert.avg_response_time = (expert.avg_response_time + time_since_assignment) / 2
        
        logger.info(f"Expert {expert_id} submitted validation {validation_id} for request {request_id}")
        
        # Check if consensus can be reached
        self._check_and_process_consensus(request_id)
        
        return validation_id

    def _check_and_process_consensus(self, request_id: str):
        """Check if consensus is reached and process result"""
        request = self.validation_requests[request_id]
        
        # Get all validations for this request
        validations = [v for v in self.expert_validations.values() if v.request_id == request_id]
        
        if len(validations) < request.required_consensus:
            return  # Not enough validations yet
        
        # Check for dangerous decisions (immediate escalation)
        dangerous_validations = [v for v in validations if v.decision == ValidationDecision.DANGEROUS]
        if dangerous_validations:
            self._escalate_dangerous_response(request_id, dangerous_validations)
            return
        
        # Process consensus
        consensus_result = self._calculate_consensus(request_id, validations)
        
        # Store consensus result
        self.consensus_results[request_id] = consensus_result
        
        # Update request status
        request.status = ValidationStatus.COMPLETED
        
        # Update expert performance scores
        self._update_expert_performance(validations, consensus_result)
        
        logger.info(f"Consensus reached for request {request_id}: {consensus_result.final_decision.value}")

    def _calculate_consensus(self, request_id: str, validations: List[ExpertValidation]) -> ConsensusResult:
        """Calculate consensus from expert validations"""
        request = self.validation_requests[request_id]
        
        # Count decisions
        decision_counts = Counter([v.decision for v in validations])
        
        # Calculate agreement threshold
        agreement_threshold = self.config["validation_thresholds"]["consensus_agreement"]
        required_agreement = max(2, int(len(validations) * agreement_threshold))
        
        # Determine final decision
        most_common_decision, count = decision_counts.most_common(1)[0]
        
        had_conflicts = count < len(validations)  # Not unanimous
        consensus_confidence = count / len(validations)
        
        # Handle conflicts
        resolution_method = None
        if had_conflicts and count < required_agreement:
            # Try conflict resolution
            final_decision, resolution_method = self._resolve_conflicts(validations, decision_counts)
        else:
            final_decision = most_common_decision
        
        # Aggregate scores
        avg_accuracy = np.mean([v.accuracy_score for v in validations])
        avg_completeness = np.mean([v.completeness_score for v in validations])
        avg_professional_quality = np.mean([v.professional_quality for v in validations])
        
        # Consolidate feedback
        consolidated_feedback = self._consolidate_feedback(validations)
        priority_improvements = self._extract_priority_improvements(validations)
        critical_issues = self._extract_critical_issues(validations)
        
        # Determine system impact
        affects_system_confidence = (
            final_decision in [ValidationDecision.INACCURATE, ValidationDecision.DANGEROUS] or
            avg_accuracy < self.config["quality_standards"]["min_accuracy_score"]
        )
        
        recommended_system_changes = self._generate_system_recommendations(validations, final_decision)
        
        return ConsensusResult(
            request_id=request_id,
            timestamp=datetime.now(),
            final_decision=final_decision,
            consensus_confidence=consensus_confidence,
            participating_experts=[v.expert_id for v in validations],
            avg_accuracy_score=avg_accuracy,
            avg_completeness_score=avg_completeness,
            avg_professional_quality=avg_professional_quality,
            had_conflicts=had_conflicts,
            resolution_method=resolution_method,
            consolidated_feedback=consolidated_feedback,
            priority_improvements=priority_improvements,
            critical_issues=critical_issues,
            affects_system_confidence=affects_system_confidence,
            recommended_system_changes=recommended_system_changes
        )

    def _resolve_conflicts(self, validations: List[ExpertValidation], 
                          decision_counts: Counter) -> Tuple[ValidationDecision, ConflictResolution]:
        """Resolve conflicts between expert decisions"""
        
        # Strategy 1: Senior expert override
        senior_validations = []
        for validation in validations:
            expert = self.experts[validation.expert_id]
            if expert.level in [ExpertLevel.PRINCIPAL, ExpertLevel.SPECIALIST]:
                senior_validations.append(validation)
        
        if senior_validations:
            senior_decisions = [v.decision for v in senior_validations]
            senior_consensus = Counter(senior_decisions).most_common(1)[0]
            if senior_consensus[1] > len(senior_validations) * 0.6:  # 60% senior agreement
                return senior_consensus[0], ConflictResolution.SENIOR_OVERRIDE
        
        # Strategy 2: Weighted consensus by confidence
        weighted_decisions = defaultdict(float)
        for validation in validations:
            expert = self.experts[validation.expert_id]
            weight = validation.confidence_level * (expert.accuracy_score if expert.accuracy_score > 0 else 0.8)
            weighted_decisions[validation.decision] += weight
        
        best_weighted_decision = max(weighted_decisions.items(), key=lambda x: x[1])[0]
        return best_weighted_decision, ConflictResolution.CONSENSUS_VOTE

    def generate_validation_report(self, request_id: str) -> Dict[str, Any]:
        """Generate detailed validation report for a request"""
        if request_id not in self.validation_requests:
            raise ValueError(f"Request {request_id} not found")
        
        request = self.validation_requests[request_id]
        validations = [v for v in self.expert_validations.values() if v.request_id == request_id]
        consensus = self.consensus_results.get(request_id)
        
        # Expert details
        expert_details = []
        for validation in validations:
            expert = self.experts[validation.expert_id]
            expert_details.append({
                "expert_level": expert.level.value,
                "expertise_areas": [area.value for area in expert.expertise_areas],
                "years_experience": expert.years_experience,
                "decision": validation.decision.value,
                "confidence": validation.confidence_level,
                "accuracy_score": validation.accuracy_score,
                "completeness_score": validation.completeness_score,
                "professional_quality": validation.professional_quality,
                "time_spent_minutes": validation.time_spent_minutes
            })
        
        # Quality metrics
        quality_metrics = {
            "avg_accuracy": np.mean([v.accuracy_score for v in validations]),
            "avg_completeness": np.mean([v.completeness_score for v in validations]),
            "avg_professional_quality": np.mean([v.professional_quality for v in validations]),
            "consensus_reached": consensus is not None,
            "consensus_confidence": consensus.consensus_confidence if consensus else 0.0
        }
        
        # Recommendations
        recommendations = {
            "priority_improvements": consensus.priority_improvements if consensus else [],
            "critical_issues": consensus.critical_issues if consensus else [],
            "system_changes": consensus.recommended_system_changes if consensus else []
        }
        
        report = {
            "request_metadata": {
                "request_id": request_id,
                "category": request.query_category.value,
                "complexity": request.query_complexity,
                "ai_confidence": request.ai_confidence,
                "estimated_stakes": request.estimated_stakes,
                "financial_year": request.financial_year
            },
            "validation_summary": {
                "status": request.status.value,
                "required_consensus": request.required_consensus,
                "received_validations": len(validations),
                "final_decision": consensus.final_decision.value if consensus else "pending",
                "had_conflicts": consensus.had_conflicts if consensus else False
            },
            "expert_validations": expert_details,
            "quality_metrics": quality_metrics,
            "consolidated_feedback": consensus.consolidated_feedback if consensus else "",
            "recommendations": recommendations,
            "report_generated": datetime.now().isoformat()
        }
        
        return report

    def get_system_performance_metrics(self) -> Dict[str, Any]:
        """Get overall system performance metrics"""
        total_requests = len(self.validation_requests)
        completed_requests = len([r for r in self.validation_requests.values() 
                                if r.status == ValidationStatus.COMPLETED])
        
        if completed_requests == 0:
            return {"message": "No completed validations yet"}
        
        # Decision distribution
        completed_consensus = [c for c in self.consensus_results.values()]
        decision_distribution = Counter([c.final_decision for c in completed_consensus])
        
        # Quality metrics
        avg_accuracy = np.mean([c.avg_accuracy_score for c in completed_consensus])
        avg_completeness = np.mean([c.avg_completeness_score for c in completed_consensus])
        avg_professional_quality = np.mean([c.avg_professional_quality for c in completed_consensus])
        
        # Expert performance
        active_experts = len([e for e in self.experts.values() if e.active])
        avg_response_time = np.mean([e.avg_response_time for e in self.experts.values() if e.avg_response_time > 0])
        
        # System impact
        system_impact_cases = len([c for c in completed_consensus if c.affects_system_confidence])
        
        return {
            "overall_metrics": {
                "total_requests": total_requests,
                "completed_requests": completed_requests,
                "completion_rate": completed_requests / total_requests,
                "active_experts": active_experts,
                "avg_response_time_hours": round(avg_response_time, 1)
            },
            "quality_metrics": {
                "avg_accuracy_score": round(avg_accuracy, 3),
                "avg_completeness_score": round(avg_completeness, 3),
                "avg_professional_quality": round(avg_professional_quality, 3),
                "system_impact_cases": system_impact_cases,
                "system_impact_rate": system_impact_cases / completed_requests
            },
            "decision_distribution": dict(decision_distribution),
            "meets_quality_standards": {
                "accuracy": avg_accuracy >= self.config["quality_standards"]["min_accuracy_score"],
                "completeness": avg_completeness >= self.config["quality_standards"]["min_completeness_score"],
                "professional_quality": avg_professional_quality >= self.config["quality_standards"]["min_professional_quality"]
            }
        }

    def save_validation_data(self, output_path: str = "expert_validation_results.json"):
        """Save all validation data to file"""
        data = {
            "system_metadata": {
                "generated_date": datetime.now().isoformat(),
                "total_experts": len(self.experts),
                "total_requests": len(self.validation_requests),
                "total_validations": len(self.expert_validations),
                "system_version": "Phase 4.4"
            },
            "experts": [asdict(expert) for expert in self.experts.values()],
            "validation_requests": [asdict(request) for request in self.validation_requests.values()],
            "expert_validations": [asdict(validation) for validation in self.expert_validations.values()],
            "consensus_results": [asdict(consensus) for consensus in self.consensus_results.values()],
            "performance_metrics": self.get_system_performance_metrics()
        }
        
        # Convert datetime objects for JSON serialization
        def datetime_converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            return obj
        
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=datetime_converter)
        
        logger.info(f"Expert validation data saved to {output_file}")
        return str(output_file)

    # Helper methods for internal processing
    def _escalate_dangerous_response(self, request_id: str, dangerous_validations: List[ExpertValidation]):
        """Handle dangerous response escalation"""
        request = self.validation_requests[request_id]
        request.status = ValidationStatus.ESCALATED
        
        # Create emergency consensus result
        consensus = ConsensusResult(
            request_id=request_id,
            timestamp=datetime.now(),
            final_decision=ValidationDecision.DANGEROUS,
            consensus_confidence=1.0,
            participating_experts=[v.expert_id for v in dangerous_validations],
            avg_accuracy_score=0.0,
            avg_completeness_score=0.0, 
            avg_professional_quality=0.0,
            had_conflicts=False,
            consolidated_feedback="DANGEROUS RESPONSE IDENTIFIED - IMMEDIATE SYSTEM REVIEW REQUIRED",
            priority_improvements=["Immediate system safety review"],
            critical_issues=[v.safety_concerns for v in dangerous_validations],
            affects_system_confidence=True,
            recommended_system_changes=["Emergency safety system review", "Response generation suspension"]
        )
        
        self.consensus_results[request_id] = consensus
        
        logger.critical(f"DANGEROUS response identified in request {request_id} - escalated immediately")

    def _consolidate_feedback(self, validations: List[ExpertValidation]) -> str:
        """Consolidate expert feedback into unified response"""
        all_comments = []
        
        for validation in validations:
            comments = [
                f"Legal Accuracy: {validation.legal_accuracy_comments}",
                f"Citation Accuracy: {validation.citation_accuracy_comments}",
                f"Professional Format: {validation.professional_format_comments}"
            ]
            all_comments.extend(comments)
        
        # Extract common themes (simplified)
        consolidated = "Expert consensus feedback: " + " | ".join(all_comments[:3])  # Limit for readability
        return consolidated

    def _extract_priority_improvements(self, validations: List[ExpertValidation]) -> List[str]:
        """Extract priority improvements from expert feedback"""
        all_improvements = []
        for validation in validations:
            all_improvements.extend(validation.improvement_suggestions)
        
        # Count frequency and return most common
        improvement_counts = Counter(all_improvements)
        return [improvement for improvement, count in improvement_counts.most_common(5)]

    def _extract_critical_issues(self, validations: List[ExpertValidation]) -> List[str]:
        """Extract critical issues from expert feedback"""
        all_issues = []
        for validation in validations:
            all_issues.extend(validation.critical_errors)
            all_issues.extend(validation.safety_concerns)
        
        return list(set(all_issues))  # Remove duplicates

    def _generate_system_recommendations(self, validations: List[ExpertValidation], 
                                       final_decision: ValidationDecision) -> List[str]:
        """Generate system improvement recommendations"""
        recommendations = []
        
        if final_decision == ValidationDecision.INACCURATE:
            recommendations.append("Review AI response generation for accuracy")
        
        if final_decision == ValidationDecision.DANGEROUS:
            recommendations.append("Emergency safety system review required")
        
        # Check for common issues across validations
        low_accuracy = any(v.accuracy_score < 0.8 for v in validations)
        if low_accuracy:
            recommendations.append("Enhance legal accuracy validation")
        
        low_completeness = any(v.completeness_score < 0.8 for v in validations)
        if low_completeness:
            recommendations.append("Improve response completeness checking")
        
        return recommendations

    def _update_expert_performance(self, validations: List[ExpertValidation], consensus: ConsensusResult):
        """Update expert performance scores based on consensus"""
        for validation in validations:
            expert = self.experts[validation.expert_id]
            
            # Calculate alignment with consensus
            alignment_score = 1.0 if validation.decision == consensus.final_decision else 0.0
            
            # Update accuracy score (running average)
            if expert.accuracy_score == 0:
                expert.accuracy_score = alignment_score
            else:
                expert.accuracy_score = (expert.accuracy_score * 0.9) + (alignment_score * 0.1)

    def _load_existing_data(self):
        """Load existing validation data if available"""
        # Implementation would load from persistent storage
        # For now, start with empty state
        pass

if __name__ == "__main__":
    # Example usage and testing
    print("Expert Validation Panel Framework - Phase 4.4")
    print("=" * 60)
    
    # Initialize system
    system = ExpertValidationSystem()
    
    # Register sample experts
    expert1_id = system.register_expert(
        name="Dr. Mahmud Rahman",
        email="mahmud.rahman@taxlaw.bd",
        phone="+880-1711-123456",
        level=ExpertLevel.PRINCIPAL,
        expertise_areas=[ExpertiseArea.INDIVIDUAL_TAX, ExpertiseArea.CORPORATE_TAX],
        bar_registration="BAR-2010-1234",
        years_experience=15,
        current_firm="Rahman & Associates",
        certifications=["Bar Registration", "Tax Law Certificate", "CA (Bangladesh)"]
    )
    
    expert2_id = system.register_expert(
        name="Adv. Fatima Khatun",
        email="fatima.khatun@legalbd.com", 
        phone="+880-1712-789012",
        level=ExpertLevel.SENIOR,
        expertise_areas=[ExpertiseArea.TDS_VAT, ExpertiseArea.COMPLIANCE],
        bar_registration="BAR-2015-5678",
        years_experience=8,
        current_firm="Dhaka Legal Services",
        certifications=["Bar Registration", "Tax Law Certificate"]
    )
    
    print(f"Registered expert 1: {expert1_id}")
    print(f"Registered expert 2: {expert2_id}")
    
    # Submit sample validation request
    request_id = system.submit_validation_request(
        query="আমার বার্ষিক আয় ৮ লক্ষ টাকা। কত কর দিতে হবে?",
        ai_response="বার্ষিক আয় ৮ লক্ষ টাকার জন্য আয়কর আইন ২০২৩ এর ধারা ৫২ অনুযায়ী প্রযোজ্য কর হার ১৫%...",
        ai_confidence=0.87,
        relevant_sections=["Section 52", "1st Schedule Part 1"],
        financial_year="2024-25",
        category=ExpertiseArea.INDIVIDUAL_TAX,
        complexity=0.6,
        priority=3,
        estimated_stakes="medium"
    )
    
    print(f"Submitted validation request: {request_id}")
    
    # Example expert validation submission
    validation_id = system.submit_expert_validation(
        request_id=request_id,
        expert_id=expert1_id,
        decision=ValidationDecision.ACCURATE,
        confidence_level=0.95,
        accuracy_score=0.92,
        completeness_score=0.88,
        professional_quality=0.95,
        legal_accuracy_comments="Legal references are accurate and current",
        citation_accuracy_comments="Section 52 correctly cited",
        professional_format_comments="Professional format meets standards",
        improvement_suggestions=["Could include specific tax calculation steps"],
        time_spent_minutes=25,
        reviewed_sources=["Income Tax Act 2023", "1st Schedule"]
    )
    
    print(f"Expert validation submitted: {validation_id}")
    
    # Generate validation report
    report = system.generate_validation_report(request_id)
    print(f"Generated validation report - Status: {report['validation_summary']['status']}")
    
    # Get system performance metrics
    metrics = system.get_system_performance_metrics()
    print(f"System performance: {metrics}")
    
    # Save results
    output_file = system.save_validation_data("test_expert_validation_results.json")
    print(f"Results saved to: {output_file}")