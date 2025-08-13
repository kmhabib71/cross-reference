#!/usr/bin/env python3
"""
Precedence Resolution Engine for Phase 2.3
Handle conflicting legal provisions and establish precedence hierarchy
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Set
import logging
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph_database.graph_database_setup import LegalKnowledgeGraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LegalPrecedenceEngine:
    """
    Advanced precedence resolution engine for Bengali Legal Knowledge Graph
    """
    
    def __init__(self, db_path: str = "bengali_legal_knowledge_graph.db"):
        self.graph_db = LegalKnowledgeGraphDatabase(db_path)
        self._load_existing_graph_data()
        self.precedence_rules = self._define_precedence_rules()
        self.conflicts = []
        self.resolutions = []
        
        logger.info("🔧 Initialized Legal Precedence Engine")
    
    def _load_existing_graph_data(self):
        """Load existing graph data from JSON export"""
        try:
            with open("bengali_legal_knowledge_graph.json", 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            # Load nodes
            for node_data in graph_data.get("nodes", []):
                node_id = node_data["id"]
                node_type = node_data["type"]
                properties = node_data.get("properties", {})
                self.graph_db.add_node(node_id, node_type, properties)
            
            # Load edges
            for edge_data in graph_data.get("edges", []):
                source = edge_data["source"]
                target = edge_data["target"]
                edge_type = edge_data["type"]
                weight = edge_data.get("weight", 1.0)
                properties = edge_data.get("properties", {})
                self.graph_db.add_edge(source, target, edge_type, properties, weight)
            
            logger.info(f"✅ Loaded existing graph for precedence analysis")
            
        except FileNotFoundError:
            logger.warning("⚠️ No existing graph data found")
        except Exception as e:
            logger.error(f"❌ Error loading existing graph data: {str(e)}")
    
    def _define_precedence_rules(self) -> Dict[str, Any]:
        """Define legal precedence rules for Bangladesh tax law"""
        return {
            "legal_hierarchy": {
                "constitution": {
                    "precedence_level": 1,
                    "description": "Constitution of Bangladesh",
                    "overrides": ["act", "rule", "policy", "circular"]
                },
                "act": {
                    "precedence_level": 2,
                    "description": "Parliamentary Acts",
                    "overrides": ["rule", "policy", "circular", "notification"],
                    "examples": ["Income Tax Act", "VAT Act"]
                },
                "ordinance": {
                    "precedence_level": 2,
                    "description": "Presidential Ordinances",
                    "overrides": ["rule", "policy", "circular", "notification"]
                },
                "rule": {
                    "precedence_level": 3,
                    "description": "Rules made under Acts",
                    "overrides": ["policy", "circular", "notification"],
                    "examples": ["Income Tax Rules", "VAT Rules"]
                },
                "regulation": {
                    "precedence_level": 4,
                    "description": "Regulations",
                    "overrides": ["circular", "notification"]
                },
                "policy": {
                    "precedence_level": 5,
                    "description": "Government Policies",
                    "overrides": ["circular", "notification"]
                },
                "circular": {
                    "precedence_level": 6,
                    "description": "Administrative Circulars",
                    "overrides": ["notification"]
                },
                "notification": {
                    "precedence_level": 7,
                    "description": "Official Notifications",
                    "overrides": []
                }
            },
            
            "temporal_precedence": {
                "general_rule": "Later enactment overrides earlier enactment of same level",
                "exceptions": [
                    "Specific provisions override general provisions",
                    "Express provisions override implied provisions",
                    "Substantive law overrides procedural law in case of conflict"
                ]
            },
            
            "conflict_indicators": {
                "direct_conflict": [
                    "contradictory requirements",
                    "mutually exclusive conditions",
                    "different rates for same item",
                    "conflicting definitions"
                ],
                "implicit_conflict": [
                    "overlapping jurisdiction",
                    "ambiguous scope",
                    "undefined terms",
                    "procedural inconsistencies"
                ],
                "bengali_conflict_keywords": [
                    "বিপরীত", "পরস্পরবিরোধী", "অসঙ্গত", "বিরোধপূর্ণ",
                    "ভিন্ন", "আলাদা", "অন্যথায়", "তবে"
                ],
                "english_conflict_keywords": [
                    "contrary", "contradictory", "inconsistent", "conflicting",
                    "different", "however", "except", "unless", "notwithstanding"
                ]
            },
            
            "resolution_strategies": {
                "hierarchy_based": "Apply higher precedence level provision",
                "temporal_based": "Apply later enacted provision of same level",
                "specificity_based": "Apply more specific provision over general",
                "express_over_implied": "Apply express provision over implied",
                "harmonious_construction": "Interpret provisions to avoid conflict if possible"
            }
        }
    
    def detect_legal_conflicts(self) -> Dict[str, Any]:
        """Detect potential conflicts between legal provisions"""
        
        logger.info("🔍 Detecting legal conflicts...")
        
        conflict_analysis = {
            "analysis_date": datetime.now().isoformat(),
            "detected_conflicts": [],
            "potential_conflicts": [],
            "conflict_categories": {
                "direct_conflicts": 0,
                "implicit_conflicts": 0,
                "hierarchical_conflicts": 0,
                "temporal_conflicts": 0
            },
            "conflict_summary": {}
        }
        
        # Get legal entities for conflict analysis
        legal_entities = []
        for entity_type in ["ACT_NODE", "RULE_NODE", "SECTION_NODE"]:
            entities = self.graph_db.query_nodes_by_type(entity_type)
            for entity_id, entity_data in entities:
                legal_entities.append({
                    "id": entity_id,
                    "type": entity_type,
                    "data": entity_data
                })
        
        # Debug: Also get all nodes if legal entity query fails
        if not legal_entities:
            logger.info("   🔍 No legal entities found, checking all nodes...")
            for node_id, node_data in self.graph_db.graph.nodes(data=True):
                node_type = node_data.get('node_type', 'UNKNOWN')
                if node_type in ["ACT_NODE", "RULE_NODE", "SECTION_NODE"]:
                    legal_entities.append({
                        "id": node_id,
                        "type": node_type,
                        "data": node_data
                    })
        
        logger.info(f"   📋 Analyzing {len(legal_entities)} legal entities for conflicts")
        
        # Debug info
        if legal_entities:
            logger.info(f"   🔍 Legal entities found: {[e['id'] for e in legal_entities[:3]]}...")
        else:
            total_nodes = self.graph_db.graph.number_of_nodes()
            logger.info(f"   ⚠️ No legal entities found in {total_nodes} total nodes")
        
        # Analyze pairs of legal entities for conflicts
        for i, entity1 in enumerate(legal_entities):
            for j, entity2 in enumerate(legal_entities[i+1:], i+1):
                conflict = self._analyze_entity_pair_for_conflict(entity1, entity2)
                if conflict:
                    conflict_analysis["detected_conflicts"].append(conflict)
                    
                    # Categorize conflict
                    conflict_type = conflict["conflict_type"]
                    if conflict_type in conflict_analysis["conflict_categories"]:
                        conflict_analysis["conflict_categories"][conflict_type] += 1
                    
                    # Add to conflicts list for resolution
                    self.conflicts.append(conflict)
        
        # Generate conflict summary
        total_conflicts = len(conflict_analysis["detected_conflicts"])
        conflict_analysis["conflict_summary"] = {
            "total_conflicts": total_conflicts,
            "entities_involved": len(set(c["entity1_id"] for c in conflict_analysis["detected_conflicts"]) |
                                    set(c["entity2_id"] for c in conflict_analysis["detected_conflicts"])),
            "conflict_density": total_conflicts / max(1, len(legal_entities) * (len(legal_entities) - 1) / 2),
            "most_common_conflict_type": max(conflict_analysis["conflict_categories"], 
                                           key=conflict_analysis["conflict_categories"].get) if conflict_analysis["conflict_categories"] else None
        }
        
        logger.info(f"✅ Conflict detection complete - Found {total_conflicts} conflicts")
        
        return conflict_analysis
    
    def _analyze_entity_pair_for_conflict(self, entity1: Dict, entity2: Dict) -> Optional[Dict[str, Any]]:
        """Analyze two legal entities for potential conflicts"""
        
        # Skip if same document (less likely to have direct conflicts)
        doc1 = entity1["data"].get("document_id", "")
        doc2 = entity2["data"].get("document_id", "")
        
        # Get text content
        text1 = entity1["data"].get("text", "").lower()
        text2 = entity2["data"].get("text", "").lower()
        
        if not text1 or not text2:
            return None
        
        # Check for conflict indicators
        conflict_indicators = self.precedence_rules["conflict_indicators"]
        
        # Look for explicit conflict keywords
        found_conflicts = []
        
        # Bengali conflict keywords
        for keyword in conflict_indicators["bengali_conflict_keywords"]:
            if keyword in text1 or keyword in text2:
                found_conflicts.append(f"Bengali conflict keyword: {keyword}")
        
        # English conflict keywords
        for keyword in conflict_indicators["english_conflict_keywords"]:
            if keyword in text1 or keyword in text2:
                found_conflicts.append(f"English conflict keyword: {keyword}")
        
        # Check for conflicting amounts/percentages
        amount_pattern = r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:টাকা|taka|শতাংশ|percent|%)'
        amounts1 = re.findall(amount_pattern, text1)
        amounts2 = re.findall(amount_pattern, text2)
        
        if amounts1 and amounts2:
            # Check if dealing with similar subjects but different amounts
            if any(amt1 != amt2 for amt1 in amounts1 for amt2 in amounts2):
                found_conflicts.append(f"Different amounts: {amounts1} vs {amounts2}")
        
        # If conflicts found, create conflict record
        if found_conflicts:
            # Determine conflict type
            conflict_type = "direct_conflicts"
            if any("keyword" in conflict for conflict in found_conflicts):
                if doc1 == doc2:
                    conflict_type = "implicit_conflicts"
                else:
                    conflict_type = "hierarchical_conflicts"
            
            return {
                "entity1_id": entity1["id"],
                "entity2_id": entity2["id"],
                "entity1_type": entity1["type"],
                "entity2_type": entity2["type"],
                "conflict_type": conflict_type,
                "conflict_indicators": found_conflicts,
                "entity1_document": doc1,
                "entity2_document": doc2,
                "confidence": len(found_conflicts) * 0.2,  # Simple confidence scoring
                "detection_method": "keyword_analysis"
            }
        
        return None
    
    def resolve_conflicts(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve detected conflicts using precedence rules"""
        
        logger.info(f"🔧 Resolving {len(conflicts)} detected conflicts...")
        
        resolution_results = {
            "resolution_date": datetime.now().isoformat(),
            "total_conflicts": len(conflicts),
            "resolved_conflicts": [],
            "unresolved_conflicts": [],
            "resolution_methods": {
                "hierarchy_based": 0,
                "temporal_based": 0,
                "specificity_based": 0,
                "harmonious_construction": 0
            }
        }
        
        for conflict in conflicts:
            resolution = self._resolve_single_conflict(conflict)
            
            if resolution["resolved"]:
                resolution_results["resolved_conflicts"].append(resolution)
                method = resolution["resolution_method"]
                if method in resolution_results["resolution_methods"]:
                    resolution_results["resolution_methods"][method] += 1
                
                # Add to resolutions list
                self.resolutions.append(resolution)
                
                # Create precedence edge in graph
                if resolution["winning_entity"] and resolution["losing_entity"]:
                    self._create_precedence_edge(
                        resolution["winning_entity"],
                        resolution["losing_entity"],
                        resolution["resolution_method"],
                        resolution["confidence"]
                    )
            else:
                resolution_results["unresolved_conflicts"].append(resolution)
        
        # Calculate resolution statistics
        resolution_results["resolution_statistics"] = {
            "resolution_rate": len(resolution_results["resolved_conflicts"]) / max(1, len(conflicts)),
            "most_common_method": max(resolution_results["resolution_methods"], 
                                    key=resolution_results["resolution_methods"].get) if any(resolution_results["resolution_methods"].values()) else None,
            "avg_confidence": sum(r["confidence"] for r in resolution_results["resolved_conflicts"]) / max(1, len(resolution_results["resolved_conflicts"]))
        }
        
        logger.info(f"✅ Conflict resolution complete - Resolved {len(resolution_results['resolved_conflicts'])}/{len(conflicts)} conflicts")
        
        return resolution_results
    
    def _resolve_single_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a single conflict using precedence rules"""
        
        entity1_id = conflict["entity1_id"]
        entity2_id = conflict["entity2_id"]
        
        # Get entity data
        entity1_data = self.graph_db.graph.nodes.get(entity1_id, {})
        entity2_data = self.graph_db.graph.nodes.get(entity2_id, {})
        
        resolution = {
            "conflict_id": f"{entity1_id}_vs_{entity2_id}",
            "entity1_id": entity1_id,
            "entity2_id": entity2_id,
            "conflict_type": conflict["conflict_type"],
            "resolved": False,
            "winning_entity": None,
            "losing_entity": None,
            "resolution_method": None,
            "confidence": 0.0,
            "reasoning": "",
            "precedence_created": False
        }
        
        # Method 1: Hierarchy-based resolution
        hierarchy_result = self._apply_hierarchy_resolution(entity1_data, entity2_data, entity1_id, entity2_id)
        if hierarchy_result["resolved"]:
            resolution.update(hierarchy_result)
            resolution["resolution_method"] = "hierarchy_based"
            return resolution
        
        # Method 2: Temporal-based resolution (newer overrides older)
        temporal_result = self._apply_temporal_resolution(entity1_data, entity2_data, entity1_id, entity2_id)
        if temporal_result["resolved"]:
            resolution.update(temporal_result)
            resolution["resolution_method"] = "temporal_based"
            return resolution
        
        # Method 3: Specificity-based resolution
        specificity_result = self._apply_specificity_resolution(entity1_data, entity2_data, entity1_id, entity2_id)
        if specificity_result["resolved"]:
            resolution.update(specificity_result)
            resolution["resolution_method"] = "specificity_based"
            return resolution
        
        # Method 4: Harmonious construction (try to avoid conflict)
        harmonious_result = self._apply_harmonious_construction(entity1_data, entity2_data, entity1_id, entity2_id)
        if harmonious_result["resolved"]:
            resolution.update(harmonious_result)
            resolution["resolution_method"] = "harmonious_construction"
            return resolution
        
        # If no resolution method worked
        resolution["reasoning"] = "Unable to resolve conflict using available precedence rules"
        return resolution
    
    def _apply_hierarchy_resolution(self, entity1_data: Dict, entity2_data: Dict, 
                                   entity1_id: str, entity2_id: str) -> Dict[str, Any]:
        """Apply hierarchy-based conflict resolution"""
        
        # Determine document types
        doc1_type = self._determine_document_type(entity1_data)
        doc2_type = self._determine_document_type(entity2_data)
        
        if not doc1_type or not doc2_type:
            return {"resolved": False}
        
        hierarchy = self.precedence_rules["legal_hierarchy"]
        
        level1 = hierarchy.get(doc1_type, {}).get("precedence_level", 999)
        level2 = hierarchy.get(doc2_type, {}).get("precedence_level", 999)
        
        if level1 != level2:
            # Higher precedence (lower number) wins
            if level1 < level2:
                return {
                    "resolved": True,
                    "winning_entity": entity1_id,
                    "losing_entity": entity2_id,
                    "confidence": 0.9,
                    "reasoning": f"{doc1_type} (level {level1}) takes precedence over {doc2_type} (level {level2})"
                }
            else:
                return {
                    "resolved": True,
                    "winning_entity": entity2_id,
                    "losing_entity": entity1_id,
                    "confidence": 0.9,
                    "reasoning": f"{doc2_type} (level {level2}) takes precedence over {doc1_type} (level {level1})"
                }
        
        return {"resolved": False}
    
    def _apply_temporal_resolution(self, entity1_data: Dict, entity2_data: Dict,
                                  entity1_id: str, entity2_id: str) -> Dict[str, Any]:
        """Apply temporal-based conflict resolution"""
        
        # Extract dates from entity data
        date1 = self._extract_date(entity1_data)
        date2 = self._extract_date(entity2_data)
        
        if date1 and date2 and date1 != date2:
            # Later date wins
            if date1 > date2:
                return {
                    "resolved": True,
                    "winning_entity": entity1_id,
                    "losing_entity": entity2_id,
                    "confidence": 0.8,
                    "reasoning": f"Later provision ({date1}) overrides earlier ({date2})"
                }
            else:
                return {
                    "resolved": True,
                    "winning_entity": entity2_id,
                    "losing_entity": entity1_id,
                    "confidence": 0.8,
                    "reasoning": f"Later provision ({date2}) overrides earlier ({date1})"
                }
        
        return {"resolved": False}
    
    def _apply_specificity_resolution(self, entity1_data: Dict, entity2_data: Dict,
                                     entity1_id: str, entity2_id: str) -> Dict[str, Any]:
        """Apply specificity-based conflict resolution"""
        
        # Calculate specificity based on text content
        text1 = entity1_data.get("text", "")
        text2 = entity2_data.get("text", "")
        
        specificity1 = self._calculate_specificity(text1)
        specificity2 = self._calculate_specificity(text2)
        
        if specificity1 != specificity2:
            # More specific provision wins
            if specificity1 > specificity2:
                return {
                    "resolved": True,
                    "winning_entity": entity1_id,
                    "losing_entity": entity2_id,
                    "confidence": 0.7,
                    "reasoning": f"More specific provision (specificity: {specificity1}) overrides general (specificity: {specificity2})"
                }
            else:
                return {
                    "resolved": True,
                    "winning_entity": entity2_id,
                    "losing_entity": entity1_id,
                    "confidence": 0.7,
                    "reasoning": f"More specific provision (specificity: {specificity2}) overrides general (specificity: {specificity1})"
                }
        
        return {"resolved": False}
    
    def _apply_harmonious_construction(self, entity1_data: Dict, entity2_data: Dict,
                                      entity1_id: str, entity2_id: str) -> Dict[str, Any]:
        """Apply harmonious construction to avoid conflict"""
        
        # Simple harmonious construction: if provisions can coexist, no conflict
        text1 = entity1_data.get("text", "").lower()
        text2 = entity2_data.get("text", "").lower()
        
        # Look for scope differentiators
        scope_indicators = [
            "শর্ত", "condition", "ক্ষেত্রে", "case", "যদি", "if",
            "তবে", "however", "ব্যতিক্রম", "except"
        ]
        
        has_scope1 = any(indicator in text1 for indicator in scope_indicators)
        has_scope2 = any(indicator in text2 for indicator in scope_indicators)
        
        if has_scope1 or has_scope2:
            # Provisions have different scopes, can coexist
            return {
                "resolved": True,
                "winning_entity": None,  # No winner, both can coexist
                "losing_entity": None,
                "confidence": 0.6,
                "reasoning": "Provisions have different scopes and can coexist through harmonious construction"
            }
        
        return {"resolved": False}
    
    def _determine_document_type(self, entity_data: Dict) -> Optional[str]:
        """Determine the type of legal document"""
        
        text = entity_data.get("text", "").lower()
        title = entity_data.get("title", "").lower()
        
        # Check for document type indicators
        if "আইন" in text or "act" in text or "আইন" in title or "act" in title:
            return "act"
        elif "বিধি" in text or "rule" in text or "বিধি" in title or "rule" in title:
            return "rule"
        elif "নীতি" in text or "policy" in text or "নীতি" in title or "policy" in title:
            return "policy"
        elif "পরিপত্র" in text or "circular" in text:
            return "circular"
        elif "বিজ্ঞপ্তি" in text or "notification" in text:
            return "notification"
        
        return None
    
    def _extract_date(self, entity_data: Dict) -> Optional[str]:
        """Extract date from entity data"""
        
        # Check explicit date field
        if "date" in entity_data:
            return entity_data["date"]
        
        # Extract from text
        text = entity_data.get("text", "")
        
        # Look for year patterns
        year_match = re.search(r'(\d{4})', text)
        if year_match:
            return year_match.group(1)
        
        return None
    
    def _calculate_specificity(self, text: str) -> float:
        """Calculate specificity score of legal text"""
        
        if not text:
            return 0.0
        
        specificity = 0.0
        
        # Specific numbers/amounts increase specificity
        number_matches = re.findall(r'\d+', text)
        specificity += len(number_matches) * 0.2
        
        # Specific conditions increase specificity
        condition_words = ["শর্ত", "condition", "যদি", "if", "ক্ষেত্রে", "case"]
        for word in condition_words:
            if word in text.lower():
                specificity += 0.3
        
        # References to specific entities increase specificity
        specific_refs = ["ধারা", "section", "তফসিল", "schedule", "বিধি", "rule"]
        for ref in specific_refs:
            specificity += text.lower().count(ref) * 0.1
        
        return min(specificity, 1.0)  # Cap at 1.0
    
    def _create_precedence_edge(self, winning_entity: str, losing_entity: str, 
                               method: str, confidence: float):
        """Create a precedence edge in the graph"""
        
        if winning_entity and losing_entity:
            success = self.graph_db.add_edge(
                winning_entity, losing_entity, "OVERRIDES",
                {
                    "precedence_method": method,
                    "confidence": confidence,
                    "creation_date": datetime.now().isoformat(),
                    "creation_method": "precedence_engine"
                }
            )
            
            if success:
                logger.debug(f"Created precedence edge: {winning_entity} OVERRIDES {losing_entity}")
    
    def generate_precedence_report(self) -> Dict[str, Any]:
        """Generate comprehensive precedence analysis report"""
        
        logger.info("📋 Generating precedence analysis report...")
        
        # Run conflict detection and resolution
        conflict_analysis = self.detect_legal_conflicts()
        resolution_results = self.resolve_conflicts(self.conflicts)
        
        # Generate comprehensive report
        precedence_report = {
            "report_metadata": {
                "generation_date": datetime.now().isoformat(),
                "phase": "Phase 2.3 - Precedence Resolution",
                "engine_version": "legal_precedence_engine_v1.0"
            },
            
            "conflict_analysis": conflict_analysis,
            "resolution_results": resolution_results,
            
            "precedence_hierarchy": self.precedence_rules["legal_hierarchy"],
            
            "system_performance": {
                "total_entities_analyzed": self.graph_db.graph.number_of_nodes(),
                "conflicts_detected": len(self.conflicts),
                "conflicts_resolved": len(self.resolutions),
                "resolution_rate": len(self.resolutions) / max(1, len(self.conflicts)),
                "precedence_edges_created": sum(1 for u, v, d in self.graph_db.graph.edges(data=True) 
                                              if d.get('edge_type') == 'OVERRIDES')
            },
            
            "recommendations": [
                "Review unresolved conflicts manually",
                "Consider adding more specific precedence rules",
                "Validate precedence decisions with legal experts",
                "Monitor system performance with real legal documents"
            ]
        }
        
        # Save report
        with open("precedence_analysis_report.json", 'w', encoding='utf-8') as f:
            json.dump(precedence_report, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ Precedence analysis report generated")
        
        return precedence_report

def main():
    """Main execution function"""
    logger.info("🚀 Phase 2.3: Precedence Resolution Engine")
    logger.info("=" * 60)
    
    try:
        # Initialize precedence engine
        engine = LegalPrecedenceEngine()
        
        # Generate comprehensive precedence report
        final_report = engine.generate_precedence_report()
        
        logger.info("=" * 60)
        logger.info("✅ Phase 2.3: Precedence Resolution COMPLETE")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   🔍 Conflicts detected: {final_report['system_performance']['conflicts_detected']}")
        logger.info(f"   ✅ Conflicts resolved: {final_report['system_performance']['conflicts_resolved']}")
        logger.info(f"   📈 Resolution rate: {final_report['system_performance']['resolution_rate']:.1%}")
        logger.info(f"   🔗 Precedence edges: {final_report['system_performance']['precedence_edges_created']}")
        
        # Close database
        engine.graph_db.close_database()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Precedence resolution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())