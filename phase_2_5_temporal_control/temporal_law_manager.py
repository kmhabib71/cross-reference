#!/usr/bin/env python3
"""
Temporal Law Manager for Phase 2.5 - Fresh Implementation
========================================================

Dynamic Legal Version Management system for Bangladesh tax laws.
Built on our working Phase 2 knowledge graph foundation.

Critical Features:
- Auto-detect financial year from Bengali/English queries
- Override hierarchy per financial year (Finance Ordinance > Income Tax Act > Rules)
- Version-aware legal lookup system
- Backward compatibility for historical queries
- Integration with Phase 2 knowledge graph (69 nodes, 562 edges)

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
import sys

# Import our working Phase 2 components
sys.path.append(str(Path(__file__).parent.parent / "phase_2_knowledge_graph"))
from graph_database_setup import LegalKnowledgeGraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FinancialYear:
    """Financial year representation for Bangladesh legal system"""
    start_year: int
    end_year: int
    bengali_notation: str
    english_notation: str
    
    def __str__(self):
        return f"FY {self.start_year}-{str(self.end_year)[2:]}"
    
    @property
    def date_range(self) -> Tuple[date, date]:
        """Return date range for this financial year"""
        return (
            date(self.start_year, 7, 1),  # July 1st start
            date(self.end_year, 6, 30)    # June 30th end
        )

@dataclass
class LawVersion:
    """Legal document version with temporal information"""
    document_id: str
    version: str
    authority_level: int  # 100=Finance Ordinance, 90=Act, 80=Rules, 70=Circulars
    effective_date: date
    expiry_date: Optional[date]
    financial_year: FinancialYear
    document_type: str  # "finance_ordinance", "income_tax_act", "rules", "circular"
    
class TemporalLawManager:
    """
    Temporal Law Manager - Phase 2.5 Fresh Implementation
    Handles changing laws across financial years automatically
    """
    
    def __init__(self, knowledge_graph_db: Optional[LegalKnowledgeGraphDatabase] = None):
        """Initialize with our Phase 2 knowledge graph"""
        # Use the main Phase 2 database
        phase2_db_path = str(Path(__file__).parent.parent / "phase_2_knowledge_graph" / "bengali_legal_knowledge_graph.db")
        self.graph_db = knowledge_graph_db or LegalKnowledgeGraphDatabase(phase2_db_path)
        self.financial_years = self._initialize_financial_years()
        self.law_versions = self._initialize_law_versions()
        
        logger.info("🔧 Initialized Temporal Law Manager")
        logger.info(f"📊 Connected to knowledge graph: {self.graph_db.graph.number_of_nodes()} nodes, {self.graph_db.graph.number_of_edges()} edges")
    
    def _initialize_financial_years(self) -> Dict[str, FinancialYear]:
        """Initialize financial year mappings"""
        return {
            "2023-24": FinancialYear(2023, 2024, "২০২৩-২৪", "FY 2023-24"),
            "2024-25": FinancialYear(2024, 2025, "২০২৪-২৫", "FY 2024-25"),
            "2025-26": FinancialYear(2025, 2026, "২০২৫-২৬", "FY 2025-26"),
        }
    
    def _initialize_law_versions(self) -> Dict[str, List[LawVersion]]:
        """
        Initialize law version hierarchy per financial year
        
        Authority Hierarchy (as per roadmap):
        100 = Finance Ordinance (highest authority)
        90 = Income Tax Act (primary law)
        80 = Rules (implementing regulations)
        70 = Circulars (interpretive guidance)
        """
        law_versions = {}
        
        # FY 2023-24 (Base year)
        law_versions["2023-24"] = [
            LawVersion(
                document_id="income_tax_act_2023",
                version="v1.0",
                authority_level=90,
                effective_date=date(2023, 7, 1),
                expiry_date=None,
                financial_year=self.financial_years["2023-24"],
                document_type="income_tax_act"
            ),
            LawVersion(
                document_id="tds_rules_2023",
                version="v1.0",
                authority_level=80,
                effective_date=date(2023, 7, 1),
                expiry_date=None,
                financial_year=self.financial_years["2023-24"],
                document_type="rules"
            ),
            LawVersion(
                document_id="tax_circular_2023",
                version="v1.0",
                authority_level=70,
                effective_date=date(2023, 7, 1),
                expiry_date=date(2024, 6, 30),
                financial_year=self.financial_years["2023-24"],
                document_type="circular"
            )
        ]
        
        # FY 2024-25 (Finance Ordinance introduced)
        law_versions["2024-25"] = [
            LawVersion(
                document_id="finance_ordinance_2024",
                version="v1.0",
                authority_level=100,  # Highest authority - overrides everything
                effective_date=date(2024, 7, 1),
                expiry_date=date(2025, 6, 30),
                financial_year=self.financial_years["2024-25"],
                document_type="finance_ordinance"
            ),
            LawVersion(
                document_id="income_tax_act_2023",
                version="v1.1", 
                authority_level=90,  # Primary law but overridden by Finance Ordinance
                effective_date=date(2023, 7, 1),
                expiry_date=None,
                financial_year=self.financial_years["2024-25"],
                document_type="income_tax_act"
            ),
            LawVersion(
                document_id="tds_rules_2024",
                version="v1.0",
                authority_level=80,  # Rules implementing the laws
                effective_date=date(2024, 7, 1),
                expiry_date=None,
                financial_year=self.financial_years["2024-25"],
                document_type="rules"
            ),
            LawVersion(
                document_id="tax_circular_2024",
                version="v1.0",
                authority_level=70,  # Interpretive guidance
                effective_date=date(2024, 7, 1),
                expiry_date=date(2025, 6, 30),
                financial_year=self.financial_years["2024-25"],
                document_type="circular"
            )
        ]
        
        # FY 2025-26 (Current year with latest changes)
        law_versions["2025-26"] = [
            LawVersion(
                document_id="finance_ordinance_2025",
                version="v1.0",
                authority_level=100,  # Latest Finance Ordinance - supreme authority
                effective_date=date(2025, 7, 1),
                expiry_date=date(2026, 6, 30),
                financial_year=self.financial_years["2025-26"],
                document_type="finance_ordinance"
            ),
            LawVersion(
                document_id="income_tax_act_2023",
                version="v1.2",  # Updated version
                authority_level=90,  # Primary law
                effective_date=date(2023, 7, 1),
                expiry_date=None,
                financial_year=self.financial_years["2025-26"],
                document_type="income_tax_act"
            ),
            LawVersion(
                document_id="tds_rules_2025",
                version="v1.0",
                authority_level=80,  # Latest rules
                effective_date=date(2025, 7, 1),
                expiry_date=None,
                financial_year=self.financial_years["2025-26"],
                document_type="rules"
            ),
            LawVersion(
                document_id="tax_circular_2025",
                version="v1.0",
                authority_level=70,  # Latest circulars
                effective_date=date(2025, 7, 1),
                expiry_date=date(2026, 6, 30),
                financial_year=self.financial_years["2025-26"],
                document_type="circular"
            )
        ]
        
        return law_versions
    
    def detect_financial_year(self, query: str) -> Optional[FinancialYear]:
        """
        Enhanced auto-detection of financial year from Bengali/English query
        
        Examples:
        - "২০২৫ অর্থবছরে" → FY 2025-26
        - "FY 2024-25" → FY 2024-25  
        - "২০২৪-২৫ অর্থবছর" → FY 2024-25
        - "চলতি অর্থবছরে" → Current FY
        - "আগামী বছর" → Next FY
        """
        
        # Enhanced Bengali patterns with more variations
        bengali_patterns = [
            # Standard patterns
            r'(\d{4})\s*অর্থবছর[েয়]?',  # ২০২৫ অর্থবছর/অর্থবছরে
            r'(\d{4})-(\d{2,4})\s*অর্থবছর[েয়]?',  # ২০২৪-২৫ অর্থবছর
            r'অর্থবছর\s*(\d{4})',  # অর্থবছর ২০২৫
            r'(\d{4})\s*সাল[েয়]?',  # ২০২৫ সাল/সালে
            r'(\d{4})-(\d{2,4})\s*সাল[েয়]?',  # ২০২৪-২৫ সালে
            
            # Relative patterns
            r'চলতি\s*অর্থবছর[েয়]?',  # চলতি অর্থবছর/অর্থবছরে (current FY)
            r'বর্তমান\s*অর্থবছর[েয়]?',  # বর্তমান অর্থবছর (current FY)
            r'আগামী\s*অর্থবছর[েয়]?',  # আগামী অর্থবছর (next FY)
            r'পরবর্তী\s*অর্থবছর[েয়]?',  # পরবর্তী অর্থবছর (next FY)
            r'গত\s*অর্থবছর[েয়]?',  # গত অর্থবছর (last FY)
        ]
        
        # Enhanced English patterns
        english_patterns = [
            r'FY\s*(\d{4})-(\d{2,4})',  # FY 2025-26
            r'Financial\s*Year\s*(\d{4})-(\d{2,4})',  # Financial Year 2025-26
            r'(\d{4})-(\d{2,4})\s*financial\s*year',  # 2025-26 financial year
            r'fiscal\s*year\s*(\d{4})-(\d{2,4})',  # fiscal year 2025-26
            r'(\d{4})-(\d{2})\s*FY',  # 2025-26 FY
            
            # Relative patterns
            r'current\s*financial\s*year',  # current financial year
            r'this\s*FY',  # this FY
            r'next\s*FY',  # next FY
            r'previous\s*FY',  # previous FY
        ]
        
        # Handle relative patterns first (Bengali)
        relative_bengali = {
            r'চলতি\s*অর্থবছর[েয়]?': 0,      # current FY
            r'বর্তমান\s*অর্থবছর[েয়]?': 0,   # current FY
            r'আগামী\s*অর্থবছর[েয়]?': 1,     # next FY
            r'পরবর্তী\s*অর্থবছর[েয়]?': 1,   # next FY
            r'গত\s*অর্থবছর[েয়]?': -1,       # last FY
        }
        
        for pattern, offset in relative_bengali.items():
            if re.search(pattern, query):
                return self._get_relative_fy(offset)
        
        # Handle relative patterns (English)
        relative_english = {
            r'current\s*financial\s*year': 0,  # current FY
            r'this\s*FY': 0,                   # this FY
            r'next\s*FY': 1,                   # next FY
            r'previous\s*FY': -1,              # previous FY
        }
        
        for pattern, offset in relative_english.items():
            if re.search(pattern, query, re.IGNORECASE):
                return self._get_relative_fy(offset)
        
        # Try specific year patterns (Bengali)
        for pattern in bengali_patterns[:5]:  # Skip relative patterns
            match = re.search(pattern, query)
            if match and match.groups():
                try:
                    year = int(match.group(1))
                    # Convert to FY format (July to June)
                    fy_key = f"{year}-{str(year+1)[2:]}"
                    if fy_key in self.financial_years:
                        return self.financial_years[fy_key]
                except (ValueError, IndexError):
                    continue
        
        # Try specific year patterns (English)
        for pattern in english_patterns[:5]:  # Skip relative patterns
            match = re.search(pattern, query, re.IGNORECASE)
            if match and match.groups():
                try:
                    start_year = int(match.group(1))
                    end_year_part = match.group(2) if len(match.groups()) > 1 else str(start_year + 1)[2:]
                    
                    # Handle 2-digit or 4-digit end year
                    if len(end_year_part) == 2:
                        end_year = int(f"20{end_year_part}")
                    else:
                        end_year = int(end_year_part)
                    
                    fy_key = f"{start_year}-{str(end_year)[2:]}"
                    if fy_key in self.financial_years:
                        return self.financial_years[fy_key]
                except (ValueError, IndexError):
                    continue
        
        # Default to current financial year if no explicit year mentioned
        return self._get_current_fy()
    
    def _get_relative_fy(self, offset: int) -> FinancialYear:
        """Get financial year relative to current (0=current, 1=next, -1=previous)"""
        current_fy = self._get_current_fy()
        
        if offset == 0:
            return current_fy
        elif offset == 1:
            # Next FY
            if current_fy.start_year == 2025:
                # Would be 2026-27, but we only have up to 2025-26
                return self.financial_years["2025-26"]
            else:
                next_key = f"{current_fy.start_year + 1}-{str(current_fy.end_year + 1)[2:]}"
                return self.financial_years.get(next_key, current_fy)
        elif offset == -1:
            # Previous FY
            if current_fy.start_year == 2023:
                return current_fy  # Can't go back further
            else:
                prev_key = f"{current_fy.start_year - 1}-{str(current_fy.end_year - 1)[2:]}"
                return self.financial_years.get(prev_key, current_fy)
        
        return current_fy
    
    def _get_current_fy(self) -> FinancialYear:
        """Determine current financial year based on today's date"""
        current_date = datetime.now().date()
        
        for fy in self.financial_years.values():
            start_date, end_date = fy.date_range
            if start_date <= current_date <= end_date:
                return fy
        
        # Fallback to latest financial year
        return self.financial_years["2025-26"]
    
    def get_applicable_laws(self, financial_year: FinancialYear, topic: Optional[str] = None) -> List[LawVersion]:
        """
        Get applicable laws for a financial year, sorted by authority level
        
        Authority hierarchy:
        100 = Finance Ordinance (highest)
        90 = Income Tax Act  
        80 = Rules
        70 = Circulars (lowest)
        """
        fy_key = f"{financial_year.start_year}-{str(financial_year.end_year)[2:]}"
        
        if fy_key not in self.law_versions:
            logger.warning(f"⚠️ No law versions found for FY {fy_key}")
            return []
        
        laws = self.law_versions[fy_key]
        
        # Sort by authority level (highest first)
        laws.sort(key=lambda x: x.authority_level, reverse=True)
        
        logger.info(f"📚 Found {len(laws)} applicable laws for {financial_year}")
        for law in laws:
            logger.info(f"   📄 {law.document_type} (Authority: {law.authority_level})")
        
        return laws
    
    def resolve_query(self, query: str) -> Dict[str, Any]:
        """
        Main query resolution function
        
        Example:
        Query: "২০২৫ অর্থবছরে ইউটিউব আয়ের কর হার কত?"
        Returns: Uses Finance Ordinance 2025 rates (correct)
        """
        
        # Step 1: Detect financial year
        financial_year = self.detect_financial_year(query)
        logger.info(f"🗓️ Detected financial year: {financial_year}")
        
        # Step 2: Get applicable laws for that year
        applicable_laws = self.get_applicable_laws(financial_year)
        
        # Step 3: Search in knowledge graph with temporal context
        relevant_nodes = self._search_knowledge_graph(query, applicable_laws)
        
        # Step 4: Apply override hierarchy
        final_answer = self._apply_override_hierarchy(relevant_nodes, applicable_laws)
        
        return {
            "query": query,
            "financial_year": {
                "detected": str(financial_year),
                "bengali": financial_year.bengali_notation,
                "english": financial_year.english_notation
            },
            "applicable_laws": [
                {
                    "document": law.document_id,
                    "type": law.document_type,
                    "authority": law.authority_level,
                    "version": law.version
                }
                for law in applicable_laws
            ],
            "resolution": final_answer,
            "timestamp": datetime.now().isoformat()
        }
    
    def _search_knowledge_graph(self, query: str, applicable_laws: List[LawVersion]) -> List[Dict]:
        """Search knowledge graph considering temporal context"""
        
        # Get relevant document IDs for this time period
        relevant_doc_ids = [law.document_id for law in applicable_laws]
        
        # Search nodes in knowledge graph
        relevant_nodes = []
        
        for node_id, node_data in self.graph_db.graph.nodes(data=True):
            # Check if node belongs to temporally relevant documents
            node_doc = node_data.get('document_id', '')
            if any(doc_id in node_doc for doc_id in relevant_doc_ids):
                # Basic keyword matching for now
                node_text = node_data.get('text', '').lower()
                query_words = query.lower().split()
                
                # Simple relevance scoring
                matches = sum(1 for word in query_words if word in node_text)
                if matches > 0:
                    relevant_nodes.append({
                        'node_id': node_id,
                        'node_data': node_data,
                        'relevance_score': matches,
                        'document_source': node_doc
                    })
        
        # Sort by relevance
        relevant_nodes.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"🔍 Found {len(relevant_nodes)} relevant nodes in knowledge graph")
        return relevant_nodes[:10]  # Return top 10
    
    def _apply_override_hierarchy(self, nodes: List[Dict], laws: List[LawVersion]) -> Dict[str, Any]:
        """Apply temporal override hierarchy to determine final answer"""
        
        if not nodes:
            return {
                "status": "no_relevant_information",
                "message": "No relevant information found in knowledge graph"
            }
        
        # Group nodes by document type and apply hierarchy
        doc_hierarchy = {}
        for law in laws:
            doc_hierarchy[law.document_id] = law.authority_level
        
        # Find highest authority source with relevant information
        best_node = None
        highest_authority = 0
        
        for node in nodes:
            doc_source = node['document_source']
            authority = max([level for doc, level in doc_hierarchy.items() if doc in doc_source], default=0)
            
            if authority > highest_authority:
                highest_authority = authority
                best_node = node
        
        if best_node:
            return {
                "status": "resolved",
                "answer_source": best_node['document_source'],
                "authority_level": highest_authority,
                "content": best_node['node_data'].get('text', ''),
                "node_id": best_node['node_id'],
                "relevance_score": best_node['relevance_score']
            }
        
        return {
            "status": "unresolved",
            "message": "Could not determine authoritative answer"
        }

def main():
    """Test the temporal law manager"""
    
    print("🚀 Testing Temporal Law Manager - Phase 2.5 Fresh Implementation")
    print("=" * 70)
    
    # Initialize manager
    manager = TemporalLawManager()
    
    # Enhanced test queries
    test_queries = [
        "২০২৫ অর্থবছরে ইউটিউব আয়ের কর হার কত?",  # Bengali with year
        "What is the tax rate for FY 2024-25?",           # English with year
        "চলতি অর্থবছরে কর হার কত?",                      # Bengali relative (current)
        "আগামী অর্থবছরে কি পরিবর্তন হবে?",               # Bengali relative (next)
        "গত অর্থবছরের নিয়ম কি ছিল?",                    # Bengali relative (previous)
        "What is the current financial year tax rate?",   # English relative
        "আয়কর আইন ২০২৩ এর ধারা ১৬৩",                     # No year specified
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 50)
        
        result = manager.resolve_query(query)
        
        print(f"🗓️ Financial Year: {result['financial_year']['english']}")
        print(f"📚 Applicable Laws: {len(result['applicable_laws'])}")
        for law in result['applicable_laws']:
            print(f"   • {law['type']} (Authority: {law['authority']})")
        
        print(f"✅ Resolution: {result['resolution']['status']}")
        if result['resolution']['status'] == 'resolved':
            print(f"📄 Source: {result['resolution']['answer_source']}")
    
    print(f"\n✅ Temporal Law Manager testing complete!")
    
if __name__ == "__main__":
    main()