#!/usr/bin/env python3
"""
Legal Hierarchy Engine for Phase 2.3
Implement automatic resolution of legal document hierarchy for Bangladesh tax law
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

class LegalHierarchyEngine:
    """
    Advanced hierarchy resolution engine for Bengali Legal Knowledge Graph
    """
    
    def __init__(self, db_path: str = "bengali_legal_knowledge_graph.db"):
        self.graph_db = LegalKnowledgeGraphDatabase(db_path)
        self._load_existing_graph_data()
        self.hierarchy_rules = self._define_hierarchy_framework()
        self.hierarchy_map = {}
        self.authority_chains = []
        
        logger.info("🔧 Initialized Legal Hierarchy Engine")
    
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
            
            logger.info(f"✅ Loaded existing graph for hierarchy analysis")
            
        except FileNotFoundError:
            logger.warning("⚠️ No existing graph data found")
        except Exception as e:
            logger.error(f"❌ Error loading existing graph data: {str(e)}")
    
    def _define_hierarchy_framework(self) -> Dict[str, Any]:
        """Define comprehensive legal hierarchy framework for Bangladesh"""
        return {
            "constitutional_hierarchy": {
                "levels": {
                    1: {
                        "name": "Constitution",
                        "bengali_name": "সংবিধান",
                        "authority": "Constitutional Assembly",
                        "scope": "Supreme law of Bangladesh",
                        "amendment_process": "Constitutional amendment procedure"
                    },
                    2: {
                        "name": "Parliamentary Acts",
                        "bengali_name": "সংসদীয় আইন",
                        "authority": "Parliament of Bangladesh",
                        "scope": "Primary legislation",
                        "examples": ["Income Tax Act", "VAT Act", "Customs Act"]
                    },
                    3: {
                        "name": "Presidential Ordinances",
                        "bengali_name": "রাষ্ট্রপতির অধ্যাদেশ",
                        "authority": "President of Bangladesh",
                        "scope": "Emergency legislation when Parliament not in session",
                        "validity": "Temporary unless ratified by Parliament"
                    },
                    4: {
                        "name": "Rules and Regulations",
                        "bengali_name": "বিধি ও প্রবিধান",
                        "authority": "Government ministries and departments",
                        "scope": "Implementation details for Acts",
                        "examples": ["Income Tax Rules", "VAT Rules"]
                    },
                    5: {
                        "name": "Government Policies",
                        "bengali_name": "সরকারি নীতিমালা",
                        "authority": "Cabinet and ministries",
                        "scope": "Policy guidance and directives"
                    },
                    6: {
                        "name": "Circulars and Notifications",
                        "bengali_name": "পরিপত্র ও বিজ্ঞপ্তি",
                        "authority": "Administrative departments",
                        "scope": "Operational instructions and clarifications"
                    },
                    7: {
                        "name": "Administrative Orders",
                        "bengali_name": "প্রশাসনিক আদেশ",
                        "authority": "Department heads and officials",
                        "scope": "Day-to-day administrative decisions"
                    }
                }
            },
            
            "tax_specific_hierarchy": {
                "income_tax": {
                    "primary_act": "Income Tax Act, 2023",
                    "rules": "Income Tax Rules, 2024",
                    "authority": "National Board of Revenue (NBR)",
                    "circulars": "NBR circulars and SROs",
                    "interpretations": "Tax tribunal decisions"
                },
                "vat": {
                    "primary_act": "Value Added Tax Act, 2012",
                    "rules": "VAT Rules, 2016",
                    "authority": "National Board of Revenue (NBR)",
                    "circulars": "NBR circulars and SROs"
                },
                "customs": {
                    "primary_act": "Customs Act, 1969",
                    "rules": "Customs Rules",
                    "authority": "National Board of Revenue (NBR)",
                    "tariff_schedule": "Customs Tariff Schedule"
                }
            },
            
            "hierarchy_indicators": {
                "bengali_authority_keywords": [
                    "সংবিধান", "সংসদ", "রাষ্ট্রপতি", "সরকার", "মন্ত্রণালয়",
                    "বোর্ড", "কমিশন", "আদালত", "ট্রাইব্যুনাল"
                ],
                "english_authority_keywords": [
                    "constitution", "parliament", "president", "government", "ministry",
                    "board", "commission", "court", "tribunal"
                ],
                "subordination_keywords": {
                    "bengali": ["অধীন", "অনুসারে", "ভিত্তিতে", "কর্তৃক প্রণীত"],
                    "english": ["under", "pursuant to", "in accordance with", "made by"]
                }
            },
            
            "authority_mapping": {
                "Parliament": {
                    "bengali": "জাতীয় সংসদ",
                    "hierarchy_level": 2,
                    "powers": ["Primary legislation", "Budget approval", "Constitutional amendments"]
                },
                "President": {
                    "bengali": "রাষ্ট্রপতি",
                    "hierarchy_level": 3,
                    "powers": ["Ordinances", "Assent to bills", "Emergency powers"]
                },
                "National Board of Revenue": {
                    "bengali": "জাতীয় রাজস্ব বোর্ড",
                    "hierarchy_level": 4,
                    "powers": ["Tax rules", "Revenue collection", "Tax administration"]
                },
                "Ministry of Finance": {
                    "bengali": "অর্থ মন্ত্রণালয়",
                    "hierarchy_level": 4,
                    "powers": ["Financial policies", "Budget preparation", "Tax policy"]
                }
            }
        }
    
    def analyze_document_hierarchy(self) -> Dict[str, Any]:
        """Analyze the hierarchy of legal documents in the graph"""
        
        logger.info("🔍 Analyzing legal document hierarchy...")
        
        hierarchy_analysis = {
            "analysis_date": datetime.now().isoformat(),
            "document_levels": {},
            "authority_chains": [],
            "hierarchy_conflicts": [],
            "orphaned_documents": [],
            "hierarchy_completeness": 0.0
        }
        
        # Get all legal documents
        documents = self.graph_db.query_nodes_by_type("DOCUMENT_NODE")
        acts = self._get_legal_entities_by_type("ACT_NODE")
        rules = self._get_legal_entities_by_type("RULE_NODE")
        sections = self._get_legal_entities_by_type("SECTION_NODE")
        
        all_legal_entities = documents + acts + rules + sections
        
        logger.info(f"   📋 Analyzing {len(all_legal_entities)} legal entities")
        
        # Classify each entity by hierarchy level
        for entity_id, entity_data in all_legal_entities:
            level = self._determine_hierarchy_level(entity_data)
            authority = self._extract_authority(entity_data)
            
            hierarchy_analysis["document_levels"][entity_id] = {
                "hierarchy_level": level,
                "authority": authority,
                "document_type": entity_data.get('node_type', 'UNKNOWN'),
                "title": entity_data.get('title', entity_data.get('text', '')[:50]),
                "date": entity_data.get('date', 'unknown')
            }
        
        # Build authority chains
        hierarchy_analysis["authority_chains"] = self._build_authority_chains(
            hierarchy_analysis["document_levels"]
        )
        
        # Identify hierarchy conflicts
        hierarchy_analysis["hierarchy_conflicts"] = self._identify_hierarchy_conflicts(
            hierarchy_analysis["document_levels"]
        )
        
        # Find orphaned documents (no clear hierarchy)
        hierarchy_analysis["orphaned_documents"] = [
            entity_id for entity_id, data in hierarchy_analysis["document_levels"].items()
            if data["hierarchy_level"] == 0
        ]
        
        # Calculate completeness
        total_entities = len(hierarchy_analysis["document_levels"])
        entities_with_hierarchy = sum(
            1 for data in hierarchy_analysis["document_levels"].values()
            if data["hierarchy_level"] > 0
        )
        hierarchy_analysis["hierarchy_completeness"] = entities_with_hierarchy / max(1, total_entities)
        
        logger.info(f"✅ Hierarchy analysis complete - {entities_with_hierarchy}/{total_entities} entities classified")
        
        return hierarchy_analysis
    
    def _get_legal_entities_by_type(self, node_type: str) -> List[Tuple[str, Dict]]:
        """Get legal entities by type with fallback"""
        entities = self.graph_db.query_nodes_by_type(node_type)
        
        # Fallback: check all nodes if query returns empty
        if not entities:
            entities = []
            for node_id, node_data in self.graph_db.graph.nodes(data=True):
                if node_data.get('node_type') == node_type:
                    entities.append((node_id, node_data))
        
        return entities
    
    def _determine_hierarchy_level(self, entity_data: Dict) -> int:
        """Determine the hierarchy level of a legal entity"""
        
        text = (entity_data.get('text', '') + ' ' + 
                entity_data.get('title', '')).lower()
        
        # Check for constitutional references
        if any(word in text for word in ['সংবিধান', 'constitution']):
            return 1
        
        # Check for act indicators
        if any(word in text for word in ['আইন', 'act']) and 'rule' not in text:
            # Parliamentary acts
            if any(word in text for word in ['সংসদ', 'parliament']):
                return 2
            # General acts
            return 2
        
        # Check for ordinance indicators
        if any(word in text for word in ['অধ্যাদেশ', 'ordinance']):
            return 3
        
        # Check for rules and regulations
        if any(word in text for word in ['বিধি', 'বিধিমালা', 'rule', 'regulation']):
            return 4
        
        # Check for policies
        if any(word in text for word in ['নীতি', 'নীতিমালা', 'policy']):
            return 5
        
        # Check for circulars and notifications
        if any(word in text for word in ['পরিপত্র', 'বিজ্ঞপ্তি', 'circular', 'notification']):
            return 6
        
        # Check for administrative orders
        if any(word in text for word in ['আদেশ', 'order']):
            return 7
        
        # Unknown hierarchy
        return 0
    
    def _extract_authority(self, entity_data: Dict) -> Optional[str]:
        """Extract the issuing authority from entity data"""
        
        # Check explicit authority field
        if 'authority' in entity_data:
            return entity_data['authority']
        
        text = (entity_data.get('text', '') + ' ' + 
                entity_data.get('title', '')).lower()
        
        # Check for specific authorities
        authority_mapping = self.hierarchy_rules['authority_mapping']
        
        for authority_en, data in authority_mapping.items():
            authority_bn = data['bengali'].lower()
            if authority_bn in text or authority_en.lower() in text:
                return authority_en
        
        # Extract from text patterns
        for keyword in self.hierarchy_rules['hierarchy_indicators']['bengali_authority_keywords']:
            if keyword in text:
                # Try to extract authority name around the keyword
                pattern = f'{keyword}[^।]*'
                match = re.search(pattern, text)
                if match:
                    return match.group(0)[:50]  # Limit length
        
        return None
    
    def _build_authority_chains(self, document_levels: Dict) -> List[Dict[str, Any]]:
        """Build authority chains showing hierarchy relationships"""
        
        chains = []
        
        # Group documents by authority
        by_authority = {}
        for entity_id, data in document_levels.items():
            authority = data['authority'] or 'Unknown'
            if authority not in by_authority:
                by_authority[authority] = []
            by_authority[authority].append((entity_id, data))
        
        # Build chains for each authority
        for authority, entities in by_authority.items():
            if len(entities) > 1:
                # Sort by hierarchy level
                sorted_entities = sorted(entities, key=lambda x: x[1]['hierarchy_level'])
                
                chain = {
                    "authority": authority,
                    "chain_length": len(sorted_entities),
                    "entities": [
                        {
                            "entity_id": entity_id,
                            "level": data['hierarchy_level'],
                            "type": data['document_type'],
                            "title": data['title']
                        }
                        for entity_id, data in sorted_entities
                    ]
                }
                chains.append(chain)
        
        return chains
    
    def _identify_hierarchy_conflicts(self, document_levels: Dict) -> List[Dict[str, Any]]:
        """Identify potential hierarchy conflicts"""
        
        conflicts = []
        
        # Check for entities at same level from same authority with different dates
        by_level_authority = {}
        
        for entity_id, data in document_levels.items():
            key = (data['hierarchy_level'], data['authority'])
            if key not in by_level_authority:
                by_level_authority[key] = []
            by_level_authority[key].append((entity_id, data))
        
        for (level, authority), entities in by_level_authority.items():
            if len(entities) > 1 and level > 0:  # Skip unknown level
                # Check for temporal conflicts
                dated_entities = [(eid, data) for eid, data in entities if data['date'] != 'unknown']
                
                if len(dated_entities) > 1:
                    # Sort by date
                    dated_entities.sort(key=lambda x: x[1]['date'])
                    
                    for i in range(len(dated_entities) - 1):
                        entity1_id, entity1_data = dated_entities[i]
                        entity2_id, entity2_data = dated_entities[i + 1]
                        
                        conflict = {
                            "conflict_type": "temporal_hierarchy_conflict",
                            "entity1_id": entity1_id,
                            "entity2_id": entity2_id,
                            "hierarchy_level": level,
                            "authority": authority,
                            "entity1_date": entity1_data['date'],
                            "entity2_date": entity2_data['date'],
                            "resolution": f"Later document ({entity2_id}) should take precedence"
                        }
                        conflicts.append(conflict)
        
        return conflicts
    
    def build_hierarchy_graph(self) -> Dict[str, Any]:
        """Build explicit hierarchy relationships in the graph"""
        
        logger.info("🔧 Building hierarchy relationships in graph...")
        
        # Get hierarchy analysis
        hierarchy_analysis = self.analyze_document_hierarchy()
        
        hierarchy_results = {
            "build_date": datetime.now().isoformat(),
            "hierarchy_edges_created": 0,
            "authority_relationships": 0,
            "temporal_relationships": 0,
            "subordination_relationships": 0
        }
        
        # Create authority-based hierarchy edges
        for chain in hierarchy_analysis["authority_chains"]:
            entities = chain["entities"]
            
            # Create HIERARCHY edges between levels
            for i in range(len(entities) - 1):
                higher_entity = entities[i]  # Lower level number = higher authority
                lower_entity = entities[i + 1]
                
                if higher_entity['level'] < lower_entity['level']:
                    success = self.graph_db.add_edge(
                        higher_entity['entity_id'],
                        lower_entity['entity_id'],
                        "HIERARCHY",
                        {
                            "hierarchy_type": "authority_based",
                            "higher_level": higher_entity['level'],
                            "lower_level": lower_entity['level'],
                            "authority": chain["authority"],
                            "creation_method": "hierarchy_engine"
                        }
                    )
                    
                    if success:
                        hierarchy_results["hierarchy_edges_created"] += 1
                        hierarchy_results["authority_relationships"] += 1
        
        # Create temporal precedence relationships
        for conflict in hierarchy_analysis["hierarchy_conflicts"]:
            if conflict["conflict_type"] == "temporal_hierarchy_conflict":
                # Later document overrides earlier at same level
                success = self.graph_db.add_edge(
                    conflict["entity2_id"],  # Later document
                    conflict["entity1_id"],  # Earlier document
                    "OVERRIDES",
                    {
                        "override_type": "temporal_precedence",
                        "later_date": conflict["entity2_date"],
                        "earlier_date": conflict["entity1_date"],
                        "hierarchy_level": conflict["hierarchy_level"],
                        "creation_method": "hierarchy_engine"
                    }
                )
                
                if success:
                    hierarchy_results["hierarchy_edges_created"] += 1
                    hierarchy_results["temporal_relationships"] += 1
        
        # Create subordination relationships (rules under acts, etc.)
        self._create_subordination_relationships(hierarchy_analysis["document_levels"], hierarchy_results)
        
        logger.info(f"✅ Hierarchy graph building complete - {hierarchy_results['hierarchy_edges_created']} edges created")
        
        return hierarchy_results
    
    def _create_subordination_relationships(self, document_levels: Dict, results: Dict):
        """Create subordination relationships between related legal documents"""
        
        # Find acts and their related rules
        acts = {eid: data for eid, data in document_levels.items() 
                if data['document_type'] == 'ACT_NODE'}
        
        rules = {eid: data for eid, data in document_levels.items() 
                 if data['document_type'] == 'RULE_NODE'}
        
        # Link rules to their parent acts
        for rule_id, rule_data in rules.items():
            rule_text = rule_data['title'].lower()
            
            # Find matching act
            for act_id, act_data in acts.items():
                act_text = act_data['title'].lower()
                
                # Check for common keywords (income tax, vat, etc.)
                act_keywords = self._extract_keywords(act_text)
                rule_keywords = self._extract_keywords(rule_text)
                
                common_keywords = set(act_keywords) & set(rule_keywords)
                
                if len(common_keywords) > 0:  # Found matching act
                    success = self.graph_db.add_edge(
                        act_id,  # Parent act
                        rule_id,  # Subordinate rule
                        "HIERARCHY",
                        {
                            "hierarchy_type": "subordination",
                            "parent_type": "act",
                            "child_type": "rule",
                            "common_subject": list(common_keywords),
                            "creation_method": "hierarchy_engine"
                        }
                    )
                    
                    if success:
                        results["hierarchy_edges_created"] += 1
                        results["subordination_relationships"] += 1
                        break  # One rule can belong to one primary act
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key legal subject keywords from text"""
        
        keywords = []
        
        # Common legal subjects
        subjects = [
            'income tax', 'আয়কর',
            'value added tax', 'vat', 'মূল্য সংযোজন কর',
            'customs', 'শুল্ক',
            'excise', 'আবগারি',
            'sales tax', 'বিক্রয় কর'
        ]
        
        for subject in subjects:
            if subject in text:
                keywords.append(subject.replace(' ', '_'))
        
        return keywords
    
    def validate_hierarchy_integrity(self) -> Dict[str, Any]:
        """Validate the integrity of the hierarchy graph"""
        
        logger.info("🔍 Validating hierarchy integrity...")
        
        validation_results = {
            "validation_date": datetime.now().isoformat(),
            "total_hierarchy_edges": 0,
            "circular_dependencies": [],
            "disconnected_components": [],
            "authority_consistency": {},
            "integrity_score": 0.0
        }
        
        # Count hierarchy edges
        hierarchy_edges = []
        for u, v, data in self.graph_db.graph.edges(data=True):
            edge_type = data.get('edge_type')
            if edge_type in ['HIERARCHY', 'OVERRIDES']:
                hierarchy_edges.append((u, v, data))
        
        validation_results["total_hierarchy_edges"] = len(hierarchy_edges)
        
        # Check for circular dependencies using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            # Check successors in hierarchy
            for successor in self.graph_db.graph.successors(node):
                edge_data = self.graph_db.graph.get_edge_data(node, successor)
                if any(d.get('edge_type') in ['HIERARCHY', 'OVERRIDES'] 
                       for d in edge_data.values()):
                    if has_cycle(successor):
                        validation_results["circular_dependencies"].append((node, successor))
                        rec_stack.remove(node)
                        return True
            
            rec_stack.remove(node)
            return False
        
        # Check all nodes for cycles
        for node in self.graph_db.graph.nodes():
            if node not in visited:
                has_cycle(node)
        
        # Calculate integrity score
        score = 100.0
        
        # Deduct for circular dependencies
        if validation_results["circular_dependencies"]:
            score -= len(validation_results["circular_dependencies"]) * 10
        
        # Deduct for missing hierarchy information
        total_nodes = self.graph_db.graph.number_of_nodes()
        nodes_with_hierarchy = len([n for n in self.graph_db.graph.nodes() 
                                   if self.graph_db.graph.in_degree(n) > 0 or 
                                   self.graph_db.graph.out_degree(n) > 0])
        hierarchy_coverage = nodes_with_hierarchy / max(1, total_nodes)
        
        if hierarchy_coverage < 0.8:
            score -= (0.8 - hierarchy_coverage) * 50
        
        validation_results["integrity_score"] = max(0.0, score)
        
        logger.info(f"✅ Hierarchy integrity validation complete - Score: {validation_results['integrity_score']:.1f}/100")
        
        return validation_results
    
    def generate_hierarchy_report(self) -> Dict[str, Any]:
        """Generate comprehensive hierarchy analysis report"""
        
        logger.info("📋 Generating hierarchy analysis report...")
        
        # Run all analyses
        hierarchy_analysis = self.analyze_document_hierarchy()
        hierarchy_build = self.build_hierarchy_graph()
        integrity_validation = self.validate_hierarchy_integrity()
        
        # Generate comprehensive report
        hierarchy_report = {
            "report_metadata": {
                "generation_date": datetime.now().isoformat(),
                "phase": "Phase 2.3 - Legal Hierarchy Engine",
                "engine_version": "legal_hierarchy_engine_v1.0"
            },
            
            "hierarchy_framework": self.hierarchy_rules["constitutional_hierarchy"],
            
            "analysis_results": hierarchy_analysis,
            "build_results": hierarchy_build,
            "validation_results": integrity_validation,
            
            "system_performance": {
                "total_entities": len(hierarchy_analysis["document_levels"]),
                "entities_classified": sum(1 for d in hierarchy_analysis["document_levels"].values() 
                                         if d["hierarchy_level"] > 0),
                "classification_rate": hierarchy_analysis["hierarchy_completeness"],
                "hierarchy_edges": hierarchy_build["hierarchy_edges_created"],
                "authority_chains": len(hierarchy_analysis["authority_chains"]),
                "conflicts_identified": len(hierarchy_analysis["hierarchy_conflicts"])
            },
            
            "recommendations": [
                "Review orphaned documents and classify them properly",
                "Resolve identified hierarchy conflicts",
                "Add more explicit authority information to documents",
                "Validate hierarchy relationships with legal experts"
            ]
        }
        
        # Save report
        with open("hierarchy_analysis_report.json", 'w', encoding='utf-8') as f:
            json.dump(hierarchy_report, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ Hierarchy analysis report generated")
        
        return hierarchy_report

def main():
    """Main execution function"""
    logger.info("🚀 Phase 2.3: Legal Hierarchy Engine")
    logger.info("=" * 60)
    
    try:
        # Initialize hierarchy engine
        engine = LegalHierarchyEngine()
        
        # Generate comprehensive hierarchy report
        final_report = engine.generate_hierarchy_report()
        
        logger.info("=" * 60)
        logger.info("✅ Phase 2.3: Legal Hierarchy Engine COMPLETE")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   📋 Entities classified: {final_report['system_performance']['entities_classified']}")
        logger.info(f"   📈 Classification rate: {final_report['system_performance']['classification_rate']:.1%}")
        logger.info(f"   🔗 Hierarchy edges: {final_report['system_performance']['hierarchy_edges']}")
        logger.info(f"   ⛓️ Authority chains: {final_report['system_performance']['authority_chains']}")
        logger.info(f"   ⚠️ Conflicts found: {final_report['system_performance']['conflicts_identified']}")
        logger.info(f"   🏥 Integrity score: {final_report['validation_results']['integrity_score']:.1f}/100")
        
        # Close database
        engine.graph_db.close_database()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Hierarchy engine failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())