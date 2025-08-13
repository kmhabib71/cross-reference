#!/usr/bin/env python3
"""
Temporal Law Manager for Phase 2.5 - Task 2.5.1
===============================================

Dynamic Legal Version Management system for Bangladesh tax laws.
Handles changing laws across financial years automatically.

Critical Features:
- Auto-detect financial year from Bengali/English queries
- Override hierarchy per financial year
- Backward compatibility for historical queries  
- Change log tracking and version management
- Integration with Phase 2 Knowledge Graph

Author: Phase 2.5 Implementation
Date: August 10, 2025
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, date
from pathlib import Path
import sys

# Import Phase 2 components
sys.path.append(str(Path(__file__).parent.parent / "phase_2_knowledge_graph"))
from legal_knowledge_graph import LegalKnowledgeGraph, GraphNode
from precedence_engine import LegalPrecedenceEngine, LegalProvision

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LegalVersion:
    """Structured legal version with temporal metadata"""
    version_id: str
    document_type: str
    effective_date: date
    expiry_date: Optional[date]
    financial_year: str
    authority_level: int
    provisions: List[Dict[str, Any]]
    changes_from_previous: List[str]
    supersedes: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class TemporalQuery:
    """Temporal query with extracted date information"""
    original_query: str
    extracted_dates: List[str]
    inferred_financial_year: str
    temporal_keywords: List[str]
    confidence: float
    query_type: str  # "current", "historical", "future"

class TemporalLawManager:
    """
    Dynamic Legal Version Management for Bangladesh tax laws.
    
    Core Functionality:
    - Financial year detection from Bengali/English queries
    - Version-aware legal provision lookup
    - Temporal precedence resolution
    - Historical query compatibility
    - Change tracking and impact analysis
    
    Supported Financial Years:
    - FY 2023-24: Income Tax Act 2023 (base)
    - FY 2024-25: Finance Ordinance 2024 modifications
    - FY 2025-26: Finance Ordinance 2025 updates
    - Future years: Extensible architecture
    """
    
    def __init__(self, knowledge_graph: Optional[LegalKnowledgeGraph] = None, 
                 precedence_engine: Optional[LegalPrecedenceEngine] = None):
        """Initialize temporal law manager with Phase 2 integration"""
        self.knowledge_graph = knowledge_graph
        self.precedence_engine = precedence_engine
        
        # Initialize temporal patterns and version database
        self.temporal_patterns = self._init_temporal_patterns()
        self.bengali_numerals = self._init_bengali_numerals()
        self.financial_year_mapping = self._init_financial_year_mapping()
        self.law_versions = self._init_law_versions()
        
        # Current system date for temporal queries
        self.current_date = date.today()
        self.current_financial_year = self._get_current_financial_year()
        
        logger.info(f"Temporal Law Manager initialized for FY {self.current_financial_year}")
    
    def _init_temporal_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for temporal detection"""
        return {
            # Financial Year patterns
            "financial_years": [
                r'(\d{4})-(\d{2,4})\s*অর্থবছর',                    # ২০২৫-২৬ অর্থবছর
                r'FY\s*(\d{4})-(\d{2,4})',                         # FY 2025-26
                r'অর্থবছর\s*(\d{4})-(\d{2,4})',                    # অর্থবছর ২০২৫-২৬
                r'Financial\s*Year\s*(\d{4})-(\d{2,4})',           # Financial Year 2025-26
                r'(\d{4})\s*সালের\s*বাজেট',                       # ২০২৫ সালের বাজেট
                r'(\d{4})\s*budget',                               # 2025 budget
            ],
            
            # Calendar Year patterns
            "calendar_years": [
                r'(\d{4})\s*সাল',                                  # ২০২৫ সাল
                r'year\s*(\d{4})',                                 # year 2025
                r'(\d{4})\s*এ',                                    # ২০২৫ এ
                r'in\s*(\d{4})',                                   # in 2025
            ],
            
            # Relative Time patterns
            "relative_time": [
                r'চলতি\s*অর্থবছর',                                # চলতি অর্থবছর
                r'current\s*financial\s*year',                     # current financial year
                r'এ\s*বছর',                                        # এ বছর
                r'this\s*year',                                    # this year
                r'গত\s*অর্থবছর',                                  # গত অর্থবছর
                r'last\s*financial\s*year',                        # last financial year
                r'আগামী\s*অর্থবছর',                               # আগামী অর্থবছর
                r'next\s*financial\s*year',                        # next financial year
            ],
            
            # Law Change indicators
            "change_indicators": [
                r'নতুন\s*আইন',                                    # নতুন আইন
                r'new\s*law',                                      # new law
                r'সংশোধন',                                        # সংশোধন
                r'amendment',                                      # amendment
                r'পরিবর্তন',                                      # পরিবর্তন
                r'change',                                         # change
                r'আপডেট',                                         # আপডেট
                r'update',                                         # update
            ]
        }
    
    def _init_bengali_numerals(self) -> Dict[str, str]:
        """Initialize Bengali to English numeral mapping"""
        return {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
    
    def _init_financial_year_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Initialize financial year date ranges and metadata"""
        return {
            "2023-24": {
                "start_date": date(2023, 7, 1),
                "end_date": date(2024, 6, 30),
                "primary_law": "income_tax_act_2023",
                "budget_document": "budget_2023",
                "major_changes": ["New Income Tax Act enacted"],
                "is_baseline": True
            },
            "2024-25": {
                "start_date": date(2024, 7, 1),
                "end_date": date(2025, 6, 30),
                "primary_law": "finance_ordinance_2024",
                "budget_document": "budget_2024",
                "major_changes": ["Tax threshold adjustments", "New TDS rules"],
                "is_baseline": False
            },
            "2025-26": {
                "start_date": date(2025, 7, 1),
                "end_date": date(2026, 6, 30),
                "primary_law": "finance_ordinance_2025",
                "budget_document": "budget_2025",
                "major_changes": ["Tax free limit increased to 4 lakh", "Digital tax provisions"],
                "is_baseline": False
            }
        }
    
    def _init_law_versions(self) -> Dict[str, LegalVersion]:
        """Initialize law versions database"""
        versions = {}
        
        # Income Tax Act 2023 (Baseline)
        versions["income_tax_act_2023"] = LegalVersion(
            version_id="ITA_2023_V1",
            document_type="income_tax_act",
            effective_date=date(2023, 7, 1),
            expiry_date=None,  # Permanent base law
            financial_year="2023-24",
            authority_level=95,
            provisions=[
                {
                    "section": "44",
                    "topic": "tax_free_limit",
                    "value": "350000",
                    "text": "করমুক্ত আয়ের সীমা ৩.৫ লক্ষ টাকা"
                },
                {
                    "section": "163",
                    "topic": "minimum_tax",
                    "value": "applicable",
                    "text": "ন্যূনতম কর প্রযোজ্য হবে"
                }
            ],
            changes_from_previous=[],
            supersedes=[],
            metadata={"is_baseline": True, "act_number": "Act No. 48 of 2023"}
        )
        
        # Finance Ordinance 2024
        versions["finance_ordinance_2024"] = LegalVersion(
            version_id="FO_2024_V1",
            document_type="finance_ordinance",
            effective_date=date(2024, 7, 1),
            expiry_date=date(2025, 6, 30),
            financial_year="2024-25",
            authority_level=100,  # Highest authority
            provisions=[
                {
                    "section": "44_override",
                    "topic": "tax_free_limit",
                    "value": "350000",  # Same as 2023
                    "text": "করমুক্ত আয়ের সীমা ৩.৫ লক্ষ টাকা (অপরিবর্তিত)"
                }
            ],
            changes_from_previous=["TDS rate adjustments", "New digital service provisions"],
            supersedes=["income_tax_act_2023"],
            metadata={"ordinance_number": "Ordinance No. 5 of 2024"}
        )
        
        # Finance Ordinance 2025
        versions["finance_ordinance_2025"] = LegalVersion(
            version_id="FO_2025_V1",
            document_type="finance_ordinance",
            effective_date=date(2025, 7, 1),
            expiry_date=date(2026, 6, 30),
            financial_year="2025-26",
            authority_level=100,  # Highest authority
            provisions=[
                {
                    "section": "44_override",
                    "topic": "tax_free_limit", 
                    "value": "400000",  # Increased
                    "text": "করমুক্ত আয়ের সীমা ৪ লক্ষ টাকা (বৃদ্ধি)"
                },
                {
                    "section": "digital_income",
                    "topic": "youtube_income_tax",
                    "value": "business_income",
                    "text": "ইউটিউব আয় ব্যবসায়িক আয় হিসেবে গণ্য"
                }
            ],
            changes_from_previous=[
                "Tax free limit increased from 3.5 lakh to 4 lakh",
                "YouTube income specifically classified as business income",
                "Digital platform tax clarifications"
            ],
            supersedes=["finance_ordinance_2024", "income_tax_act_2023"],
            metadata={"ordinance_number": "Ordinance No. 3 of 2025"}
        )
        
        return versions
    
    def parse_temporal_query(self, query: str) -> TemporalQuery:
        """
        Parse query to extract temporal information
        
        Args:
            query: Legal query in Bengali/English
            
        Returns:
            TemporalQuery with extracted temporal metadata
        """
        logger.debug(f"Parsing temporal query: {query[:50]}...")
        
        # Normalize Bengali numerals to English
        normalized_query = self._normalize_bengali_numerals(query)
        
        # Extract temporal information
        extracted_dates = self._extract_dates(normalized_query)
        financial_year = self._infer_financial_year(normalized_query, extracted_dates)
        temporal_keywords = self._extract_temporal_keywords(normalized_query)
        query_type = self._classify_query_type(temporal_keywords, financial_year)
        confidence = self._calculate_temporal_confidence(extracted_dates, temporal_keywords)
        
        temporal_query = TemporalQuery(
            original_query=query,
            extracted_dates=extracted_dates,
            inferred_financial_year=financial_year,
            temporal_keywords=temporal_keywords,
            confidence=confidence,
            query_type=query_type
        )
        
        logger.info(f"Temporal parsing: FY {financial_year}, Type: {query_type}, Confidence: {confidence:.2f}")
        return temporal_query
    
    def get_applicable_law_version(self, query: str, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get applicable law version for query or date
        
        Args:
            query: Legal query text
            target_date: Optional specific date (uses current date if None)
            
        Returns:
            Applicable law version with metadata
        """
        # Parse temporal information from query
        temporal_query = self.parse_temporal_query(query)
        
        # Determine target date
        if target_date is None:
            if temporal_query.inferred_financial_year:
                # Use financial year from query
                fy_info = self.financial_year_mapping.get(temporal_query.inferred_financial_year)
                if fy_info:
                    target_date = fy_info["start_date"]
                else:
                    target_date = self.current_date
            else:
                target_date = self.current_date
        
        # Find applicable law version for target date
        applicable_version = self._find_law_version_for_date(target_date)
        
        # Get specific provisions if requested
        relevant_provisions = self._find_relevant_provisions(
            applicable_version, 
            temporal_query.original_query
        )
        
        return {
            "applicable_version": applicable_version,
            "target_date": target_date.isoformat(),
            "financial_year": self._date_to_financial_year(target_date),
            "temporal_query": asdict(temporal_query),
            "relevant_provisions": relevant_provisions,
            "precedence_chain": self._build_precedence_chain(applicable_version),
            "metadata": {
                "resolution_method": "temporal_version_control",
                "confidence": temporal_query.confidence,
                "query_type": temporal_query.query_type
            }
        }
    
    def resolve_temporal_conflict(self, conflicting_provisions: List[LegalProvision], 
                                 target_date: date) -> Dict[str, Any]:
        """
        Resolve conflict between provisions using temporal precedence
        
        Args:
            conflicting_provisions: List of conflicting legal provisions
            target_date: Date for which to resolve conflict
            
        Returns:
            Resolution with temporal precedence applied
        """
        logger.info(f"Resolving temporal conflict for date: {target_date}")
        
        # Filter provisions by temporal applicability
        applicable_provisions = []
        for provision in conflicting_provisions:
            if self._is_provision_applicable(provision, target_date):
                applicable_provisions.append(provision)
        
        if not applicable_provisions:
            return {
                "resolution": "no_applicable_provisions",
                "target_date": target_date.isoformat(),
                "message": "No provisions applicable for the specified date"
            }
        
        if len(applicable_provisions) == 1:
            return {
                "resolution": "single_applicable_provision",
                "winning_provision": applicable_provisions[0],
                "target_date": target_date.isoformat(),
                "confidence": 1.0
            }
        
        # Apply temporal precedence rules
        # Rule 1: Later effective date wins
        latest_date = max(p.effective_date for p in applicable_provisions if p.effective_date)
        latest_provisions = [p for p in applicable_provisions 
                           if p.effective_date and p.effective_date == latest_date]
        
        if len(latest_provisions) == 1:
            return {
                "resolution": "temporal_precedence",
                "winning_provision": latest_provisions[0],
                "losing_provisions": [p for p in applicable_provisions if p != latest_provisions[0]],
                "resolution_reason": f"Later effective date: {latest_date}",
                "target_date": target_date.isoformat(),
                "confidence": 0.95
            }
        
        # Rule 2: Use Phase 2 precedence engine for same-date conflicts
        if self.precedence_engine:
            phase2_resolution = self.precedence_engine.resolve_conflict(latest_provisions)
            return {
                "resolution": "authority_precedence",
                "winning_provision": phase2_resolution.winning_provision,
                "losing_provisions": phase2_resolution.losing_provisions,
                "resolution_reason": f"Authority hierarchy: {phase2_resolution.resolution_reason}",
                "target_date": target_date.isoformat(),
                "confidence": phase2_resolution.confidence_score
            }
        
        # Fallback: Highest authority level
        max_authority = max(p.authority_level for p in latest_provisions)
        authority_winners = [p for p in latest_provisions if p.authority_level == max_authority]
        
        return {
            "resolution": "authority_fallback",
            "winning_provision": authority_winners[0],
            "losing_provisions": [p for p in applicable_provisions if p != authority_winners[0]],
            "resolution_reason": f"Highest authority level: {max_authority}",
            "target_date": target_date.isoformat(),
            "confidence": 0.8
        }
    
    def get_law_change_history(self, topic: str, start_year: str = "2023-24", 
                              end_year: Optional[str] = None) -> Dict[str, Any]:
        """
        Get change history for specific legal topic across financial years
        
        Args:
            topic: Legal topic (e.g., "tax_free_limit", "youtube_income_tax")
            start_year: Starting financial year
            end_year: Ending financial year (current if None)
            
        Returns:
            Change history with timeline and impact analysis
        """
        if end_year is None:
            end_year = self.current_financial_year
        
        # Get all versions between start and end years
        relevant_versions = []
        for version_id, version in self.law_versions.items():
            if start_year <= version.financial_year <= end_year:
                relevant_versions.append(version)
        
        # Sort by effective date
        relevant_versions.sort(key=lambda v: v.effective_date)
        
        # Build change timeline for topic
        change_timeline = []
        for version in relevant_versions:
            topic_provisions = [p for p in version.provisions if p.get("topic") == topic]
            
            for provision in topic_provisions:
                change_timeline.append({
                    "financial_year": version.financial_year,
                    "effective_date": version.effective_date.isoformat(),
                    "version_id": version.version_id,
                    "authority_level": version.authority_level,
                    "provision": provision,
                    "changes": version.changes_from_previous
                })
        
        # Analyze changes
        change_analysis = self._analyze_topic_changes(change_timeline, topic)
        
        return {
            "topic": topic,
            "query_period": f"{start_year} to {end_year}",
            "change_timeline": change_timeline,
            "change_analysis": change_analysis,
            "total_changes": len(change_timeline),
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "versions_analyzed": len(relevant_versions)
            }
        }
    
    # Internal utility methods
    def _normalize_bengali_numerals(self, text: str) -> str:
        """Convert Bengali numerals to English"""
        normalized = text
        for bengali, english in self.bengali_numerals.items():
            normalized = normalized.replace(bengali, english)
        return normalized
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract date references from text"""
        dates = []
        
        # Extract financial years
        for pattern in self.temporal_patterns["financial_years"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        year1, year2 = match
                        if len(year2) == 2:  # Convert 25 to 2025
                            year2 = "20" + year2
                        dates.append(f"{year1}-{year2}")
                else:
                    dates.append(match)
        
        # Extract calendar years
        for pattern in self.temporal_patterns["calendar_years"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return dates
    
    def _infer_financial_year(self, text: str, extracted_dates: List[str]) -> str:
        """Infer financial year from text and extracted dates"""
        
        # Check for explicit financial year mentions
        for date_str in extracted_dates:
            if "-" in date_str:  # Financial year format
                # Normalize to standard format
                parts = date_str.split("-")
                if len(parts) == 2:
                    year1 = parts[0]
                    year2 = parts[1]
                    if len(year2) == 2:
                        year2 = "20" + year2
                    fy = f"{year1}-{year2[-2:]}"
                    if fy in self.financial_year_mapping:
                        return fy
        
        # Check for relative time indicators
        text_lower = text.lower()
        if any(pattern in text_lower for pattern in ["চলতি অর্থবছর", "current financial year", "এ বছর", "this year"]):
            return self.current_financial_year
        elif any(pattern in text_lower for pattern in ["গত অর্থবছর", "last financial year"]):
            return self._get_previous_financial_year()
        elif any(pattern in text_lower for pattern in ["আগামী অর্থবছর", "next financial year"]):
            return self._get_next_financial_year()
        
        # Check for calendar year mentions
        for date_str in extracted_dates:
            if date_str.isdigit() and len(date_str) == 4:
                year = int(date_str)
                # Convert calendar year to financial year
                if 2023 <= year <= 2030:  # Reasonable range
                    # FY starts in July, so calendar year maps to FY year-1 to year
                    if year == 2023:
                        return "2023-24"
                    elif year == 2024:
                        return "2024-25"
                    elif year == 2025:
                        return "2025-26"
        
        # Default to current financial year
        return self.current_financial_year
    
    def _extract_temporal_keywords(self, text: str) -> List[str]:
        """Extract temporal keywords from text"""
        keywords = []
        text_lower = text.lower()
        
        for category, patterns in self.temporal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    keywords.append(category)
                    break
        
        return keywords
    
    def _classify_query_type(self, temporal_keywords: List[str], financial_year: str) -> str:
        """Classify query as current, historical, or future"""
        if not temporal_keywords:
            return "current"
        
        if financial_year == self.current_financial_year:
            return "current"
        elif financial_year < self.current_financial_year:
            return "historical"
        else:
            return "future"
    
    def _calculate_temporal_confidence(self, extracted_dates: List[str], 
                                     temporal_keywords: List[str]) -> float:
        """Calculate confidence in temporal parsing"""
        base_confidence = 0.5
        
        # Boost for explicit dates
        if extracted_dates:
            base_confidence += 0.3
        
        # Boost for temporal keywords
        if temporal_keywords:
            base_confidence += 0.2
        
        # Additional boost for multiple indicators
        if len(extracted_dates) > 1 or len(temporal_keywords) > 1:
            base_confidence += 0.1
        
        return min(0.95, base_confidence)
    
    def _find_law_version_for_date(self, target_date: date) -> LegalVersion:
        """Find applicable law version for specific date"""
        
        # Find the most recent version applicable to the target date
        applicable_versions = []
        
        for version_id, version in self.law_versions.items():
            if version.effective_date <= target_date:
                # Check if version has expired
                if version.expiry_date is None or version.expiry_date >= target_date:
                    applicable_versions.append(version)
        
        if not applicable_versions:
            # Fallback to baseline version
            return self.law_versions.get("income_tax_act_2023")
        
        # Sort by effective date (most recent first) and authority level
        applicable_versions.sort(key=lambda v: (v.effective_date, v.authority_level), reverse=True)
        
        return applicable_versions[0]
    
    def _find_relevant_provisions(self, law_version: LegalVersion, query: str) -> List[Dict[str, Any]]:
        """Find provisions relevant to query from law version"""
        query_lower = query.lower()
        relevant_provisions = []
        
        for provision in law_version.provisions:
            provision_text = provision.get("text", "").lower()
            topic = provision.get("topic", "").lower()
            
            # Simple keyword matching
            if any(word in provision_text or word in topic for word in query_lower.split() if len(word) > 3):
                relevant_provisions.append(provision)
        
        return relevant_provisions
    
    def _build_precedence_chain(self, law_version: LegalVersion) -> List[str]:
        """Build precedence chain for law version"""
        chain = [law_version.version_id]
        
        if law_version.supersedes:
            chain.extend(law_version.supersedes)
        
        return chain
    
    def _is_provision_applicable(self, provision: LegalProvision, target_date: date) -> bool:
        """Check if provision is applicable for target date"""
        if provision.effective_date and provision.effective_date > target_date:
            return False
        
        # For now, assume all provisions are applicable if effective date is met
        # Future: Add expiry date checking
        return True
    
    def _analyze_topic_changes(self, change_timeline: List[Dict], topic: str) -> Dict[str, Any]:
        """Analyze changes for specific topic"""
        if not change_timeline:
            return {"no_changes": True}
        
        # Find value changes
        values = []
        for change in change_timeline:
            provision = change.get("provision", {})
            value = provision.get("value", "")
            if value:
                values.append({
                    "financial_year": change["financial_year"],
                    "value": value,
                    "effective_date": change["effective_date"]
                })
        
        # Identify change patterns
        change_analysis = {
            "total_versions": len(change_timeline),
            "value_changes": values,
            "change_pattern": "increasing" if len(values) > 1 and values[-1]["value"] > values[0]["value"] else "stable",
            "last_change": change_timeline[-1]["effective_date"] if change_timeline else None
        }
        
        return change_analysis
    
    def _get_current_financial_year(self) -> str:
        """Get current financial year based on system date"""
        today = self.current_date
        
        # Financial year starts July 1
        if today.month >= 7:
            # July-December: FY starts this year
            fy_start = today.year
        else:
            # January-June: FY started last year
            fy_start = today.year - 1
        
        fy_end = fy_start + 1
        return f"{fy_start}-{str(fy_end)[-2:]}"
    
    def _get_previous_financial_year(self) -> str:
        """Get previous financial year"""
        current_fy = self.current_financial_year
        start_year = int(current_fy.split("-")[0])
        prev_start = start_year - 1
        prev_end = start_year
        return f"{prev_start}-{str(prev_end)[-2:]}"
    
    def _get_next_financial_year(self) -> str:
        """Get next financial year"""
        current_fy = self.current_financial_year
        start_year = int(current_fy.split("-")[0])
        next_start = start_year + 1
        next_end = next_start + 1
        return f"{next_start}-{str(next_end)[-2:]}"
    
    def _date_to_financial_year(self, target_date: date) -> str:
        """Convert date to financial year"""
        if target_date.month >= 7:
            fy_start = target_date.year
        else:
            fy_start = target_date.year - 1
        
        fy_end = fy_start + 1
        return f"{fy_start}-{str(fy_end)[-2:]}"
    
    def export_temporal_data(self, output_path: str) -> None:
        """Export temporal law data to JSON"""
        export_data = {
            "law_versions": {k: asdict(v) for k, v in self.law_versions.items()},
            "financial_year_mapping": {
                k: {
                    **v,
                    "start_date": v["start_date"].isoformat(),
                    "end_date": v["end_date"].isoformat()
                }
                for k, v in self.financial_year_mapping.items()
            },
            "temporal_patterns": self.temporal_patterns,
            "current_financial_year": self.current_financial_year,
            "metadata": {
                "version": "2.5.1",
                "export_date": datetime.now().isoformat(),
                "description": "Temporal Law Version Control Data"
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Temporal data exported to {output_path}")

def main():
    """Test the Temporal Law Manager"""
    manager = TemporalLawManager()
    
    print("🕐 Temporal Law Manager Test")
    print("=" * 50)
    
    # Test queries with different temporal contexts
    test_queries = [
        "২০২৫ অর্থবছরে ইউটিউব আয়ের কর হার কত?",
        "চলতি অর্থবছরে করমুক্ত আয়ের সীমা কত?",
        "আয়কর আইন ২০২৩ অনুযায়ী ন্যূনতম কর কত?",
        "গত বছরের তুলনায় এ বছর কর হার কেমন?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        # Parse temporal information
        temporal_query = manager.parse_temporal_query(query)
        print(f"Financial Year: {temporal_query.inferred_financial_year}")
        print(f"Query Type: {temporal_query.query_type}")
        print(f"Confidence: {temporal_query.confidence:.2f}")
        
        # Get applicable law
        result = manager.get_applicable_law_version(query)
        applicable_version = result["applicable_version"]
        print(f"Applicable Law: {applicable_version.version_id}")
        print(f"Authority Level: {applicable_version.authority_level}")
        print(f"Relevant Provisions: {len(result['relevant_provisions'])}")
    
    # Test change history
    print("\n📈 Change History Test:")
    print("=" * 30)
    
    history = manager.get_law_change_history("tax_free_limit")
    print(f"Topic: {history['topic']}")
    print(f"Total Changes: {history['total_changes']}")
    print(f"Change Pattern: {history['change_analysis'].get('change_pattern', 'unknown')}")
    
    # Export temporal data
    output_path = Path(__file__).parent / "temporal_law_data.json"
    manager.export_temporal_data(str(output_path))
    print(f"\n✅ Temporal data exported to: {output_path}")

if __name__ == "__main__":
    main()