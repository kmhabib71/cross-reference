#!/usr/bin/env python3
"""
Relationship Engine for Phase 2.2
Advanced relationship building for Bengali Legal Knowledge Graph
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
from graph_database_setup import LegalKnowledgeGraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedRelationshipEngine:
    """
    Advanced relationship building engine for Bengali Legal Knowledge Graph
    """
    
    def __init__(self, db_path: str = "bengali_legal_knowledge_graph.db"):
        self.graph_db = LegalKnowledgeGraphDatabase(db_path)
        self.relationship_patterns = self._load_relationship_patterns()
        self.created_relationships = []
        
        # Load existing graph data if available
        self._load_existing_graph_data()
        
        logger.info("🔧 Initialized Advanced Relationship Engine")
    
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
            
            logger.info(f"✅ Loaded existing graph: {len(graph_data.get('nodes', []))} nodes, {len(graph_data.get('edges', []))} edges")
            
        except FileNotFoundError:
            logger.info("ℹ️ No existing graph data found, starting fresh")
        except Exception as e:
            logger.warning(f"⚠️ Error loading existing graph data: {str(e)}")
    
    def _load_relationship_patterns(self) -> Dict[str, Any]:
        """Load advanced relationship detection patterns"""
        return {
            "REFERENCES": {
                "bengali_keywords": [
                    "উক্ত", "সংশ্লিষ্ট", "উল্লেখিত", "বর্ণিত", "নির্দেশিত", 
                    "অনুসারে", "মতে", "ভিত্তিতে", "অনুযায়ী"
                ],
                "english_keywords": [
                    "according to", "as per", "mentioned", "referred", "specified", 
                    "pursuant to", "in accordance", "said", "aforesaid"
                ],
                "proximity_window": 100,  # characters
                "strength_indicators": ["উক্ত", "said", "aforesaid"]
            },
            
            "OVERRIDES": {
                "bengali_keywords": [
                    "রহিত", "বাতিল", "প্রতিস্থাপন", "পরিবর্তন", "সংশোধন", 
                    "নতুন", "পরিবর্তে", "স্থলে", "রদ"
                ],
                "english_keywords": [
                    "override", "supersede", "replace", "substitute", "amend", 
                    "repeal", "cancel", "modify", "revoke"
                ],
                "proximity_window": 150,
                "strength_indicators": ["রহিত", "বাতিল", "override", "supersede"]
            },
            
            "IMPLEMENTS": {
                "bengali_keywords": [
                    "বাস্তবায়ন", "কার্যকর", "প্রয়োগ", "পালন", "অনুসরণ", 
                    "বাস্তবায়িত", "কার্যকরী", "প্রয়োগকারী"
                ],
                "english_keywords": [
                    "implement", "execute", "enforce", "apply", "carry out", 
                    "put into effect", "operationalize", "enact"
                ],
                "proximity_window": 120,
                "strength_indicators": ["বাস্তবায়ন", "implement", "execute"]
            },
            
            "MODIFIES": {
                "bengali_keywords": [
                    "সংশোধন", "পরিবর্তন", "সংযোজন", "বিয়োজন", "সংস্কার", 
                    "হালনাগাদ", "সংশোধিত", "পরিবর্তিত"
                ],
                "english_keywords": [
                    "modify", "amend", "alter", "change", "revise", 
                    "update", "adjust", "reform"
                ],
                "proximity_window": 130,
                "strength_indicators": ["সংশোধন", "modify", "amend"]
            },
            
            "CONDITIONS": {
                "bengali_keywords": [
                    "শর্ত", "যদি", "তাহলে", "কিন্তু", "তবে", "শর্তসাপেক্ষে", 
                    "ব্যতিক্রম", "ক্ষেত্রে", "সাপেক্ষে"
                ],
                "english_keywords": [
                    "condition", "if", "then", "provided that", "subject to", 
                    "except", "unless", "in case of", "where"
                ],
                "proximity_window": 80,
                "strength_indicators": ["যদি", "তাহলে", "if", "then"]
            },
            
            "HIERARCHY": {
                "bengali_keywords": [
                    "আইন", "বিধিমালা", "নীতিমালা", "নির্দেশনা", "প্রধান", 
                    "গৌণ", "উপ", "অধীন", "কর্তৃক", "প্রণীত"
                ],
                "english_keywords": [
                    "act", "rules", "policy", "guidelines", "primary", 
                    "secondary", "subordinate", "under", "made by", "framed"
                ],
                "proximity_window": 200,
                "strength_indicators": ["অধীন", "under", "made by"]
            }
        }
    
    def analyze_existing_graph(self) -> Dict[str, Any]:
        """Analyze current graph structure for relationship opportunities"""
        
        logger.info("🔍 Analyzing existing graph for relationship opportunities...")
        
        analysis = {
            "analysis_date": datetime.now().isoformat(),
            "total_nodes": self.graph_db.graph.number_of_nodes(),
            "total_edges": self.graph_db.graph.number_of_edges(),
            "node_analysis": {},
            "relationship_opportunities": [],
            "missing_relationships": []
        }
        
        # Analyze nodes by type
        for node_id, data in self.graph_db.graph.nodes(data=True):
            node_type = data.get('node_type', 'UNKNOWN')
            if node_type not in analysis["node_analysis"]:
                analysis["node_analysis"][node_type] = []
            
            analysis["node_analysis"][node_type].append({
                "node_id": node_id,
                "properties": {k: v for k, v in data.items() if k != 'node_type'}
            })
        
        # Find relationship opportunities
        analysis["relationship_opportunities"] = self._find_relationship_opportunities()
        
        logger.info(f"✅ Graph analysis complete - found {len(analysis['relationship_opportunities'])} opportunities")
        
        return analysis
    
    def _find_relationship_opportunities(self) -> List[Dict[str, Any]]:
        """Find potential relationships between existing nodes"""
        
        opportunities = []
        
        # Get all nodes with text content
        text_nodes = []
        for node_id, data in self.graph_db.graph.nodes(data=True):
            if 'text' in data and 'document_id' in data:
                text_nodes.append({
                    "node_id": node_id,
                    "text": data['text'],
                    "document_id": data['document_id'],
                    "node_type": data.get('node_type', 'UNKNOWN'),
                    "start_position": data.get('start_position', 0),
                    "end_position": data.get('end_position', 0)
                })
        
        # Group nodes by document for context analysis
        document_groups = {}
        for node in text_nodes:
            doc_id = node['document_id']
            if doc_id not in document_groups:
                document_groups[doc_id] = []
            document_groups[doc_id].append(node)
        
        # Analyze relationships within each document
        for doc_id, nodes in document_groups.items():
            # Sort nodes by position
            nodes.sort(key=lambda x: x['start_position'])
            
            # Look for relationship patterns between nodes
            for i, source_node in enumerate(nodes):
                for j, target_node in enumerate(nodes):
                    if i != j:
                        opportunity = self._analyze_node_pair(source_node, target_node, nodes)
                        if opportunity:
                            opportunities.append(opportunity)
        
        return opportunities
    
    def _analyze_node_pair(self, 
                          source_node: Dict[str, Any], 
                          target_node: Dict[str, Any],
                          context_nodes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze a pair of nodes for potential relationships"""
        
        # Skip if nodes are too close (likely same entity)
        pos_diff = abs(source_node['start_position'] - target_node['start_position'])
        if pos_diff < 10:
            return None
        
        # Look for relationship keywords between nodes
        start_pos = min(source_node['end_position'], target_node['end_position'])
        end_pos = max(source_node['start_position'], target_node['start_position'])
        
        # Find intervening text (would need document text for full implementation)
        # For now, we'll use a simplified approach based on node content
        
        for rel_type, patterns in self.relationship_patterns.items():
            # Check for relationship keywords in node text
            source_text = source_node['text'].lower()
            target_text = target_node['text'].lower()
            
            # Check Bengali keywords
            for keyword in patterns['bengali_keywords']:
                if keyword in source_text or keyword in target_text:
                    confidence = 0.6
                    if keyword in patterns.get('strength_indicators', []):
                        confidence = 0.8
                    
                    return {
                        "source_node": source_node['node_id'],
                        "target_node": target_node['node_id'],
                        "relationship_type": rel_type,
                        "confidence": confidence,
                        "evidence": f"Found '{keyword}' in node text",
                        "context": f"Document: {source_node['document_id']}"
                    }
            
            # Check English keywords
            for keyword in patterns['english_keywords']:
                if keyword in source_text or keyword in target_text:
                    confidence = 0.6
                    if keyword in patterns.get('strength_indicators', []):
                        confidence = 0.8
                    
                    return {
                        "source_node": source_node['node_id'],
                        "target_node": target_node['node_id'],
                        "relationship_type": rel_type,
                        "confidence": confidence,
                        "evidence": f"Found '{keyword}' in node text",
                        "context": f"Document: {source_node['document_id']}"
                    }
        
        return None
    
    def create_relationships_from_opportunities(self, 
                                              opportunities: List[Dict[str, Any]], 
                                              min_confidence: float = 0.7) -> Dict[str, Any]:
        """Create relationships from identified opportunities"""
        
        logger.info(f"🔄 Creating relationships from {len(opportunities)} opportunities...")
        
        creation_results = {
            "creation_date": datetime.now().isoformat(),
            "total_opportunities": len(opportunities),
            "created_relationships": [],
            "skipped_relationships": [],
            "creation_stats": {}
        }
        
        for opportunity in opportunities:
            if opportunity['confidence'] >= min_confidence:
                # Create relationship
                success = self.graph_db.add_edge(
                    opportunity['source_node'],
                    opportunity['target_node'],
                    opportunity['relationship_type'],
                    {
                        "confidence": opportunity['confidence'],
                        "evidence": opportunity['evidence'],
                        "context": opportunity['context'],
                        "creation_method": "advanced_relationship_engine",
                        "creation_date": datetime.now().isoformat()
                    }
                )
                
                if success:
                    creation_results["created_relationships"].append(opportunity)
                    self.created_relationships.append(opportunity)
                    
                    # Update stats
                    rel_type = opportunity['relationship_type']
                    creation_results["creation_stats"][rel_type] = \
                        creation_results["creation_stats"].get(rel_type, 0) + 1
                else:
                    creation_results["skipped_relationships"].append({
                        **opportunity,
                        "reason": "Failed to create edge"
                    })
            else:
                creation_results["skipped_relationships"].append({
                    **opportunity,
                    "reason": f"Low confidence ({opportunity['confidence']} < {min_confidence})"
                })
        
        logger.info("✅ Relationship creation complete")
        for rel_type, count in creation_results["creation_stats"].items():
            logger.info(f"   🔗 {rel_type}: {count} relationships created")
        
        return creation_results
    
    def enhance_document_structure_relationships(self) -> Dict[str, Any]:
        """Create structural relationships within documents"""
        
        logger.info("🔄 Creating document structure relationships...")
        
        enhancement_results = {
            "enhancement_date": datetime.now().isoformat(),
            "structural_relationships": [],
            "document_hierarchies": {}
        }
        
        # Get document nodes
        document_nodes = self.graph_db.query_nodes_by_type("DOCUMENT_NODE")
        
        for doc_id, doc_data in document_nodes:
            logger.info(f"   📄 Processing document: {doc_id}")
            
            # Find all nodes belonging to this document
            doc_nodes = []
            for node_id, data in self.graph_db.graph.nodes(data=True):
                if data.get('document_id') == doc_id:
                    doc_nodes.append((node_id, data))
            
            # Create CONTAINS relationships from document to its entities
            contains_count = 0
            for node_id, data in doc_nodes:
                if node_id != doc_id:  # Don't self-reference
                    # Check if CONTAINS relationship already exists
                    if not self.graph_db.graph.has_edge(doc_id, node_id):
                        success = self.graph_db.add_edge(doc_id, node_id, "CONTAINS", {
                            "position": data.get('start_position', 0),
                            "entity_type": data.get('entity_type', 'unknown'),
                            "creation_method": "document_structure_enhancement"
                        })
                        if success:
                            contains_count += 1
            
            # Create hierarchical relationships between sections and subsections
            sections = [node for node in doc_nodes if node[1].get('node_type') == 'SECTION_NODE']
            hierarchy_count = 0
            
            for i, (section_id, section_data) in enumerate(sections):
                for j, (other_section_id, other_section_data) in enumerate(sections):
                    if i != j:
                        # Simple hierarchy: if section numbers are sequential or hierarchical
                        section_num = section_data.get('section_number', '0')
                        other_section_num = other_section_data.get('section_number', '0')
                        
                        if self._is_hierarchical_relationship(section_num, other_section_num):
                            success = self.graph_db.add_edge(section_id, other_section_id, "HIERARCHY", {
                                "hierarchy_type": "section_subsection",
                                "parent_section": section_num,
                                "child_section": other_section_num,
                                "creation_method": "document_structure_enhancement"
                            })
                            if success:
                                hierarchy_count += 1
            
            enhancement_results["document_hierarchies"][doc_id] = {
                "contains_relationships": contains_count,
                "hierarchy_relationships": hierarchy_count,
                "total_entities": len(doc_nodes)
            }
        
        logger.info("✅ Document structure enhancement complete")
        
        return enhancement_results
    
    def _is_hierarchical_relationship(self, parent_num: str, child_num: str) -> bool:
        """Determine if two section numbers have a hierarchical relationship"""
        try:
            # Simple numeric comparison (can be enhanced for complex numbering)
            parent_int = int(re.search(r'(\d+)', parent_num).group(1)) if re.search(r'(\d+)', parent_num) else 0
            child_int = int(re.search(r'(\d+)', child_num).group(1)) if re.search(r'(\d+)', child_num) else 0
            
            # Child sections typically have higher numbers
            return child_int == parent_int + 1
            
        except (AttributeError, ValueError):
            return False
    
    def create_semantic_relationships(self) -> Dict[str, Any]:
        """Create semantic relationships based on legal concepts"""
        
        logger.info("🔄 Creating semantic relationships...")
        
        semantic_results = {
            "semantic_date": datetime.now().isoformat(),
            "concept_relationships": [],
            "semantic_stats": {}
        }
        
        # Get concept nodes (AMOUNT, PERCENTAGE, etc.)
        concept_nodes = self.graph_db.query_nodes_by_type("CONCEPT_NODE")
        legal_nodes = (self.graph_db.query_nodes_by_type("SECTION_NODE") + 
                      self.graph_db.query_nodes_by_type("ACT_NODE") + 
                      self.graph_db.query_nodes_by_type("RULE_NODE"))
        
        # Create APPLIES_TO relationships between legal provisions and concepts
        for legal_id, legal_data in legal_nodes:
            legal_doc = legal_data.get('document_id', '')
            
            for concept_id, concept_data in concept_nodes:
                concept_doc = concept_data.get('document_id', '')
                
                # If they're from the same document and close in position
                if legal_doc == concept_doc:
                    legal_pos = legal_data.get('start_position', 0)
                    concept_pos = concept_data.get('start_position', 0)
                    
                    # If concept is within reasonable distance (same sentence/paragraph)
                    if abs(legal_pos - concept_pos) < 200:
                        concept_type = concept_data.get('entity_type', 'unknown')
                        
                        # Create APPLIES_TO relationship
                        success = self.graph_db.add_edge(legal_id, concept_id, "APPLIES_TO", {
                            "concept_type": concept_type,
                            "proximity": abs(legal_pos - concept_pos),
                            "creation_method": "semantic_relationship_engine"
                        })
                        
                        if success:
                            semantic_results["concept_relationships"].append({
                                "legal_provision": legal_id,
                                "concept": concept_id,
                                "concept_type": concept_type
                            })
                            
                            # Update stats
                            semantic_results["semantic_stats"][concept_type] = \
                                semantic_results["semantic_stats"].get(concept_type, 0) + 1
        
        logger.info("✅ Semantic relationship creation complete")
        for concept_type, count in semantic_results["semantic_stats"].items():
            logger.info(f"   🔗 {concept_type} relationships: {count}")
        
        return semantic_results
    
    def validate_relationship_quality(self) -> Dict[str, Any]:
        """Validate the quality of created relationships"""
        
        logger.info("🔍 Validating relationship quality...")
        
        validation_results = {
            "validation_date": datetime.now().isoformat(),
            "total_relationships": self.graph_db.graph.number_of_edges(),
            "relationship_quality": {},
            "quality_issues": [],
            "overall_quality_score": 0.0
        }
        
        # Analyze each relationship type
        for u, v, data in self.graph_db.graph.edges(data=True):
            edge_type = data.get('edge_type', 'UNKNOWN')
            confidence = data.get('confidence', 0.5)
            
            if edge_type not in validation_results["relationship_quality"]:
                validation_results["relationship_quality"][edge_type] = {
                    "count": 0,
                    "avg_confidence": 0.0,
                    "high_quality": 0,
                    "low_quality": 0
                }
            
            stats = validation_results["relationship_quality"][edge_type]
            stats["count"] += 1
            stats["avg_confidence"] += confidence
            
            if confidence >= 0.8:
                stats["high_quality"] += 1
            elif confidence < 0.6:
                stats["low_quality"] += 1
                validation_results["quality_issues"].append({
                    "source": u,
                    "target": v,
                    "type": edge_type,
                    "confidence": confidence,
                    "issue": "Low confidence relationship"
                })
        
        # Calculate averages
        total_confidence = 0
        total_relationships = 0
        
        for rel_type, stats in validation_results["relationship_quality"].items():
            if stats["count"] > 0:
                stats["avg_confidence"] /= stats["count"]
                total_confidence += stats["avg_confidence"] * stats["count"]
                total_relationships += stats["count"]
        
        if total_relationships > 0:
            validation_results["overall_quality_score"] = total_confidence / total_relationships
        
        logger.info("✅ Relationship quality validation complete")
        logger.info(f"   📊 Overall quality score: {validation_results['overall_quality_score']:.3f}")
        
        return validation_results
    
    def generate_relationship_report(self) -> Dict[str, Any]:
        """Generate comprehensive relationship analysis report"""
        
        logger.info("📋 Generating relationship analysis report...")
        
        # Gather all analysis data
        graph_analysis = self.analyze_existing_graph()
        quality_validation = self.validate_relationship_quality()
        graph_stats = self.graph_db.get_graph_statistics()
        
        report = {
            "report_metadata": {
                "generation_date": datetime.now().isoformat(),
                "phase": "Phase 2.2 - Advanced Relationship Building",
                "engine_version": "advanced_relationship_engine_v1.0"
            },
            
            "graph_overview": {
                "total_nodes": graph_stats["total_nodes"],
                "total_edges": graph_stats["total_edges"],
                "density": graph_stats["connectivity_metrics"].get("density", 0),
                "connected": graph_stats["connectivity_metrics"].get("is_connected", False),
                "components": graph_stats["connectivity_metrics"].get("number_of_components", 0)
            },
            
            "node_distribution": graph_stats["node_type_distribution"],
            "edge_distribution": graph_stats["edge_type_distribution"],
            
            "relationship_opportunities": {
                "total_opportunities": len(graph_analysis["relationship_opportunities"]),
                "created_relationships": len(self.created_relationships),
                "success_rate": (len(self.created_relationships) / 
                               max(1, len(graph_analysis["relationship_opportunities"]))) * 100
            },
            
            "relationship_quality": quality_validation["relationship_quality"],
            "quality_score": quality_validation["overall_quality_score"],
            "quality_issues": len(quality_validation["quality_issues"]),
            
            "recommendations": self._generate_recommendations(graph_stats, quality_validation)
        }
        
        # Save report
        with open("relationship_analysis_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ Relationship analysis report generated")
        
        return report
    
    def _generate_recommendations(self, 
                                graph_stats: Dict[str, Any], 
                                quality_validation: Dict[str, Any]) -> List[str]:
        """Generate recommendations for graph improvement"""
        
        recommendations = []
        
        # Connectivity recommendations
        if not graph_stats["connectivity_metrics"].get("is_connected", False):
            recommendations.append("Graph is not fully connected - consider adding more cross-references")
        
        # Density recommendations
        density = graph_stats["connectivity_metrics"].get("density", 0)
        if density < 0.01:
            recommendations.append("Graph density is very low - add more relationships between entities")
        
        # Quality recommendations
        if quality_validation["overall_quality_score"] < 0.7:
            recommendations.append("Overall relationship quality is low - review confidence thresholds")
        
        if len(quality_validation["quality_issues"]) > 0:
            recommendations.append(f"Found {len(quality_validation['quality_issues'])} low-quality relationships - manual review recommended")
        
        # Node distribution recommendations
        isolated_nodes = graph_stats["connectivity_metrics"].get("number_of_components", 0) - 1
        if isolated_nodes > 5:
            recommendations.append(f"Too many isolated nodes ({isolated_nodes}) - enhance entity linking")
        
        return recommendations

def main():
    """Main execution function"""
    logger.info("🚀 Phase 2.2: Advanced Relationship Building")
    logger.info("=" * 60)
    
    try:
        # Initialize relationship engine
        engine = AdvancedRelationshipEngine()
        
        # Step 1: Analyze existing graph
        analysis = engine.analyze_existing_graph()
        logger.info(f"📊 Found {len(analysis['relationship_opportunities'])} relationship opportunities")
        
        # Step 2: Create relationships from opportunities
        creation_results = engine.create_relationships_from_opportunities(
            analysis['relationship_opportunities'], 
            min_confidence=0.6
        )
        
        # Step 3: Enhance document structure
        structure_results = engine.enhance_document_structure_relationships()
        
        # Step 4: Create semantic relationships
        semantic_results = engine.create_semantic_relationships()
        
        # Step 5: Generate comprehensive report
        final_report = engine.generate_relationship_report()
        
        logger.info("=" * 60)
        logger.info("✅ Phase 2.2: Advanced Relationship Building COMPLETE")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   📝 Total nodes: {final_report['graph_overview']['total_nodes']}")
        logger.info(f"   🔗 Total edges: {final_report['graph_overview']['total_edges']}")
        logger.info(f"   🎯 Quality score: {final_report['quality_score']:.3f}")
        logger.info(f"   🔄 Success rate: {final_report['relationship_opportunities']['success_rate']:.1f}%")
        
        # Close database
        engine.graph_db.close_database()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Advanced relationship building failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())