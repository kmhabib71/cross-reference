#!/usr/bin/env python3
"""
Graph Validator for Phase 2.2
Comprehensive validation of Bengali Legal Knowledge Graph construction
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Set
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph_database_setup import LegalKnowledgeGraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveGraphValidator:
    """
    Comprehensive validator for Bengali Legal Knowledge Graph
    """
    
    def __init__(self, db_path: str = "bengali_legal_knowledge_graph.db"):
        self.graph_db = LegalKnowledgeGraphDatabase(db_path)
        self._load_existing_graph_data()
        self.validation_results = {}
        
        logger.info("🔧 Initialized Comprehensive Graph Validator")
    
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
            logger.warning("⚠️ No existing graph data found")
        except Exception as e:
            logger.error(f"❌ Error loading existing graph data: {str(e)}")
    
    def validate_graph_structure(self) -> Dict[str, Any]:
        """Validate overall graph structure and integrity"""
        
        logger.info("🔍 Validating graph structure...")
        
        structure_validation = {
            "validation_date": datetime.now().isoformat(),
            "basic_metrics": {},
            "node_validation": {},
            "edge_validation": {},
            "connectivity_validation": {},
            "structure_issues": [],
            "structure_score": 0.0
        }
        
        # Basic metrics
        total_nodes = self.graph_db.graph.number_of_nodes()
        total_edges = self.graph_db.graph.number_of_edges()
        
        structure_validation["basic_metrics"] = {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "nodes_per_edge_ratio": total_nodes / max(1, total_edges),
            "density": self.graph_db.get_graph_statistics()["connectivity_metrics"].get("density", 0)
        }
        
        # Node validation
        node_types = {}
        nodes_with_properties = 0
        nodes_missing_critical_props = 0
        
        for node_id, data in self.graph_db.graph.nodes(data=True):
            node_type = data.get('node_type', 'UNKNOWN')
            node_types[node_type] = node_types.get(node_type, 0) + 1
            
            if len(data) > 1:  # More than just node_type
                nodes_with_properties += 1
            
            # Check for critical properties
            if node_type in ['DOCUMENT_NODE', 'SECTION_NODE', 'ACT_NODE']:
                if 'title' not in data and 'text' not in data:
                    nodes_missing_critical_props += 1
                    structure_validation["structure_issues"].append(
                        f"Node {node_id} missing critical properties (title/text)"
                    )
        
        structure_validation["node_validation"] = {
            "node_type_distribution": node_types,
            "nodes_with_properties": nodes_with_properties,
            "nodes_missing_critical_props": nodes_missing_critical_props,
            "property_coverage": nodes_with_properties / max(1, total_nodes)
        }
        
        # Edge validation
        edge_types = {}
        edges_with_properties = 0
        bidirectional_edges = 0
        
        for u, v, data in self.graph_db.graph.edges(data=True):
            edge_type = data.get('edge_type', 'UNKNOWN')
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
            
            if len(data) > 2:  # More than just edge_type and weight
                edges_with_properties += 1
            
            # Check for bidirectional relationships
            if self.graph_db.graph.has_edge(v, u):
                bidirectional_edges += 1
        
        structure_validation["edge_validation"] = {
            "edge_type_distribution": edge_types,
            "edges_with_properties": edges_with_properties,
            "bidirectional_edges": bidirectional_edges // 2,  # Divide by 2 to avoid double counting
            "property_coverage": edges_with_properties / max(1, total_edges)
        }
        
        # Connectivity validation
        import networkx as nx
        connectivity_metrics = {
            "is_weakly_connected": nx.is_weakly_connected(self.graph_db.graph),
            "number_of_components": nx.number_weakly_connected_components(self.graph_db.graph),
            "isolated_nodes": len(list(nx.isolates(self.graph_db.graph))),
            "average_degree": sum(dict(self.graph_db.graph.degree()).values()) / max(1, total_nodes)
        }
        
        structure_validation["connectivity_validation"] = connectivity_metrics
        
        # Calculate structure score
        score = 0.0
        
        # Node completeness (25%)
        if structure_validation["node_validation"]["property_coverage"] > 0.8:
            score += 25
        elif structure_validation["node_validation"]["property_coverage"] > 0.6:
            score += 15
        elif structure_validation["node_validation"]["property_coverage"] > 0.4:
            score += 10
        
        # Edge completeness (25%)
        if structure_validation["edge_validation"]["property_coverage"] > 0.8:
            score += 25
        elif structure_validation["edge_validation"]["property_coverage"] > 0.6:
            score += 15
        elif structure_validation["edge_validation"]["property_coverage"] > 0.4:
            score += 10
        
        # Connectivity (30%)
        isolated_ratio = connectivity_metrics["isolated_nodes"] / max(1, total_nodes)
        if isolated_ratio < 0.1:
            score += 30
        elif isolated_ratio < 0.3:
            score += 20
        elif isolated_ratio < 0.5:
            score += 10
        
        # Relationship diversity (20%)
        edge_type_count = len(edge_types)
        if edge_type_count >= 5:
            score += 20
        elif edge_type_count >= 3:
            score += 15
        elif edge_type_count >= 2:
            score += 10
        elif edge_type_count >= 1:
            score += 5
        
        structure_validation["structure_score"] = score
        
        logger.info(f"✅ Structure validation complete - Score: {score}/100")
        
        return structure_validation
    
    def validate_legal_semantics(self) -> Dict[str, Any]:
        """Validate legal document semantics and relationships"""
        
        logger.info("🔍 Validating legal semantics...")
        
        semantic_validation = {
            "validation_date": datetime.now().isoformat(),
            "document_coverage": {},
            "legal_entity_validation": {},
            "relationship_semantics": {},
            "semantic_issues": [],
            "semantic_score": 0.0
        }
        
        # Document coverage analysis
        document_nodes = self.graph_db.query_nodes_by_type("DOCUMENT_NODE")
        total_documents = len(document_nodes)
        
        document_analysis = {}
        for doc_id, doc_data in document_nodes:
            # Count entities per document
            doc_entities = 0
            entity_types = set()
            
            for node_id, data in self.graph_db.graph.nodes(data=True):
                if data.get('document_id') == doc_id:
                    doc_entities += 1
                    entity_types.add(data.get('entity_type', 'unknown'))
            
            document_analysis[doc_id] = {
                "total_entities": doc_entities,
                "entity_types": list(entity_types),
                "entity_diversity": len(entity_types)
            }
        
        semantic_validation["document_coverage"] = {
            "total_documents": total_documents,
            "document_analysis": document_analysis,
            "avg_entities_per_doc": sum(d["total_entities"] for d in document_analysis.values()) / max(1, total_documents),
            "avg_entity_diversity": sum(d["entity_diversity"] for d in document_analysis.values()) / max(1, total_documents)
        }
        
        # Legal entity validation
        legal_entities = {
            "SECTION_NODE": self.graph_db.query_nodes_by_type("SECTION_NODE"),
            "ACT_NODE": self.graph_db.query_nodes_by_type("ACT_NODE"),
            "RULE_NODE": self.graph_db.query_nodes_by_type("RULE_NODE"),
            "SCHEDULE_NODE": self.graph_db.query_nodes_by_type("SCHEDULE_NODE")
        }
        
        entity_validation = {}
        for entity_type, entities in legal_entities.items():
            validation_data = {
                "count": len(entities),
                "with_numbers": 0,
                "with_titles": 0,
                "connected": 0
            }
            
            for entity_id, entity_data in entities:
                # Check for section/rule numbers
                if entity_type in ["SECTION_NODE", "RULE_NODE"]:
                    if "section_number" in entity_data or "rule_number" in entity_data:
                        validation_data["with_numbers"] += 1
                
                # Check for titles
                if "title" in entity_data or "text" in entity_data:
                    validation_data["with_titles"] += 1
                
                # Check connectivity
                if (self.graph_db.graph.in_degree(entity_id) + 
                    self.graph_db.graph.out_degree(entity_id)) > 0:
                    validation_data["connected"] += 1
            
            entity_validation[entity_type] = validation_data
        
        semantic_validation["legal_entity_validation"] = entity_validation
        
        # Relationship semantics
        relationship_analysis = {}
        for u, v, data in self.graph_db.graph.edges(data=True):
            edge_type = data.get('edge_type', 'UNKNOWN')
            
            if edge_type not in relationship_analysis:
                relationship_analysis[edge_type] = {
                    "count": 0,
                    "source_types": set(),
                    "target_types": set(),
                    "avg_confidence": 0.0,
                    "with_context": 0
                }
            
            rel_data = relationship_analysis[edge_type]
            rel_data["count"] += 1
            
            # Get node types
            source_type = self.graph_db.graph.nodes[u].get('node_type', 'UNKNOWN')
            target_type = self.graph_db.graph.nodes[v].get('node_type', 'UNKNOWN')
            
            rel_data["source_types"].add(source_type)
            rel_data["target_types"].add(target_type)
            
            # Check confidence and context
            if 'confidence' in data:
                rel_data["avg_confidence"] += data['confidence']
            
            if 'context' in data or 'evidence' in data:
                rel_data["with_context"] += 1
        
        # Calculate averages
        for edge_type, rel_data in relationship_analysis.items():
            if rel_data["count"] > 0:
                rel_data["avg_confidence"] /= rel_data["count"]
                rel_data["source_types"] = list(rel_data["source_types"])
                rel_data["target_types"] = list(rel_data["target_types"])
        
        semantic_validation["relationship_semantics"] = relationship_analysis
        
        # Calculate semantic score
        score = 0.0
        
        # Document coverage (25%)
        if semantic_validation["document_coverage"]["avg_entity_diversity"] >= 5:
            score += 25
        elif semantic_validation["document_coverage"]["avg_entity_diversity"] >= 3:
            score += 15
        elif semantic_validation["document_coverage"]["avg_entity_diversity"] >= 2:
            score += 10
        
        # Entity completeness (35%)
        total_legal_entities = sum(data["count"] for data in entity_validation.values())
        connected_entities = sum(data["connected"] for data in entity_validation.values())
        connectivity_ratio = connected_entities / max(1, total_legal_entities)
        
        if connectivity_ratio >= 0.8:
            score += 35
        elif connectivity_ratio >= 0.6:
            score += 25
        elif connectivity_ratio >= 0.4:
            score += 15
        elif connectivity_ratio >= 0.2:
            score += 5
        
        # Relationship quality (40%)
        total_relationships = sum(data["count"] for data in relationship_analysis.values())
        relationships_with_context = sum(data["with_context"] for data in relationship_analysis.values())
        context_ratio = relationships_with_context / max(1, total_relationships)
        
        if context_ratio >= 0.8:
            score += 40
        elif context_ratio >= 0.6:
            score += 30
        elif context_ratio >= 0.4:
            score += 20
        elif context_ratio >= 0.2:
            score += 10
        
        semantic_validation["semantic_score"] = score
        
        logger.info(f"✅ Semantic validation complete - Score: {score}/100")
        
        return semantic_validation
    
    def validate_performance_metrics(self) -> Dict[str, Any]:
        """Validate graph performance and efficiency metrics"""
        
        logger.info("🔍 Validating performance metrics...")
        
        performance_validation = {
            "validation_date": datetime.now().isoformat(),
            "query_performance": {},
            "memory_usage": {},
            "scalability_metrics": {},
            "performance_score": 0.0
        }
        
        import time
        import sys
        
        # Query performance tests
        start_time = time.time()
        
        # Test 1: Node retrieval by type
        document_nodes = self.graph_db.query_nodes_by_type("DOCUMENT_NODE")
        node_query_time = time.time() - start_time
        
        # Test 2: Relationship traversal
        start_time = time.time()
        if document_nodes:
            relationships = self.graph_db.find_relationships(document_nodes[0][0])
        else:
            relationships = {"outgoing": [], "incoming": []}
        relationship_query_time = time.time() - start_time
        
        # Test 3: Graph statistics
        start_time = time.time()
        stats = self.graph_db.get_graph_statistics()
        stats_query_time = time.time() - start_time
        
        performance_validation["query_performance"] = {
            "node_query_time_ms": round(node_query_time * 1000, 2),
            "relationship_query_time_ms": round(relationship_query_time * 1000, 2),
            "stats_query_time_ms": round(stats_query_time * 1000, 2),
            "total_query_time_ms": round((node_query_time + relationship_query_time + stats_query_time) * 1000, 2)
        }
        
        # Memory usage estimation
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            performance_validation["memory_usage"] = {
                "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                "vms_mb": round(memory_info.vms / 1024 / 1024, 2)
            }
        except ImportError:
            performance_validation["memory_usage"] = {
                "rss_mb": "unavailable (psutil not installed)",
                "vms_mb": "unavailable (psutil not installed)"
            }
        
        # Scalability metrics
        total_nodes = self.graph_db.graph.number_of_nodes()
        total_edges = self.graph_db.graph.number_of_edges()
        
        performance_validation["scalability_metrics"] = {
            "nodes_per_second_estimate": round(total_nodes / max(0.001, stats_query_time), 0),
            "edges_per_second_estimate": round(total_edges / max(0.001, stats_query_time), 0),
            "graph_complexity": total_nodes * total_edges,
            "projected_10x_performance": {
                "estimated_nodes": total_nodes * 10,
                "estimated_edges": total_edges * 10,
                "estimated_query_time_ms": round(stats_query_time * 10 * 1000, 2)
            }
        }
        
        # Calculate performance score
        score = 0.0
        
        # Query speed (40%)
        total_query_time = performance_validation["query_performance"]["total_query_time_ms"]
        if total_query_time < 50:  # < 50ms
            score += 40
        elif total_query_time < 100:
            score += 30
        elif total_query_time < 200:
            score += 20
        elif total_query_time < 500:
            score += 10
        
        # Memory efficiency (30%)
        if isinstance(performance_validation["memory_usage"]["rss_mb"], (int, float)):
            memory_mb = performance_validation["memory_usage"]["rss_mb"]
            if memory_mb < 100:
                score += 30
            elif memory_mb < 250:
                score += 20
            elif memory_mb < 500:
                score += 10
        else:
            score += 15  # Default score if memory info unavailable
        
        # Scalability (30%)
        complexity = performance_validation["scalability_metrics"]["graph_complexity"]
        if complexity < 1000:
            score += 30
        elif complexity < 5000:
            score += 20
        elif complexity < 10000:
            score += 10
        
        performance_validation["performance_score"] = score
        
        logger.info(f"✅ Performance validation complete - Score: {score}/100")
        
        return performance_validation
    
    def generate_comprehensive_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        logger.info("📋 Generating comprehensive validation report...")
        
        # Run all validations
        structure_results = self.validate_graph_structure()
        semantic_results = self.validate_legal_semantics()
        performance_results = self.validate_performance_metrics()
        
        # Generate comprehensive report
        comprehensive_report = {
            "report_metadata": {
                "generation_date": datetime.now().isoformat(),
                "phase": "Phase 2.2 - Graph Validation",
                "validator_version": "comprehensive_graph_validator_v1.0",
                "validation_scope": "structure + semantics + performance"
            },
            
            "overall_assessment": {
                "structure_score": structure_results["structure_score"],
                "semantic_score": semantic_results["semantic_score"],
                "performance_score": performance_results["performance_score"],
                "overall_score": (structure_results["structure_score"] + 
                                semantic_results["semantic_score"] + 
                                performance_results["performance_score"]) / 3,
                "validation_status": "PENDING"
            },
            
            "detailed_results": {
                "structure_validation": structure_results,
                "semantic_validation": semantic_results,
                "performance_validation": performance_results
            },
            
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            
            "production_readiness": {
                "ready_for_phase_2_3": False,
                "blocking_issues": [],
                "improvement_suggestions": []
            }
        }
        
        # Determine overall status
        overall_score = comprehensive_report["overall_assessment"]["overall_score"]
        
        if overall_score >= 80:
            comprehensive_report["overall_assessment"]["validation_status"] = "EXCELLENT"
            comprehensive_report["production_readiness"]["ready_for_phase_2_3"] = True
        elif overall_score >= 65:
            comprehensive_report["overall_assessment"]["validation_status"] = "GOOD"
            comprehensive_report["production_readiness"]["ready_for_phase_2_3"] = True
        elif overall_score >= 50:
            comprehensive_report["overall_assessment"]["validation_status"] = "ACCEPTABLE"
            comprehensive_report["production_readiness"]["ready_for_phase_2_3"] = True
        elif overall_score >= 35:
            comprehensive_report["overall_assessment"]["validation_status"] = "NEEDS_IMPROVEMENT"
        else:
            comprehensive_report["overall_assessment"]["validation_status"] = "CRITICAL"
        
        # Generate recommendations
        if structure_results["structure_score"] < 60:
            comprehensive_report["recommendations"].append("Improve graph structure - add more node properties and relationships")
        
        if semantic_results["semantic_score"] < 60:
            comprehensive_report["recommendations"].append("Enhance legal semantics - improve entity relationships and context")
        
        if performance_results["performance_score"] < 60:
            comprehensive_report["recommendations"].append("Optimize performance - consider indexing and caching strategies")
        
        # Add critical issues
        structure_issues = structure_results.get("structure_issues", [])
        semantic_issues = semantic_results.get("semantic_issues", [])
        
        comprehensive_report["critical_issues"] = structure_issues + semantic_issues
        
        if not comprehensive_report["production_readiness"]["ready_for_phase_2_3"]:
            comprehensive_report["production_readiness"]["blocking_issues"] = [
                f"Overall score ({overall_score:.1f}) below minimum threshold (50)",
                "Graph requires improvement before proceeding to Phase 2.3"
            ]
        
        # Save report
        with open("comprehensive_graph_validation_report.json", 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ Comprehensive validation report generated")
        
        return comprehensive_report

def main():
    """Main execution function"""
    logger.info("🚀 Phase 2.2: Comprehensive Graph Validation")
    logger.info("=" * 60)
    
    try:
        # Initialize validator
        validator = ComprehensiveGraphValidator()
        
        # Generate comprehensive validation report
        final_report = validator.generate_comprehensive_validation_report()
        
        logger.info("=" * 60)
        logger.info("✅ Phase 2.2: Graph Validation COMPLETE")
        logger.info(f"📊 Final Assessment:")
        logger.info(f"   📈 Overall Score: {final_report['overall_assessment']['overall_score']:.1f}/100")
        logger.info(f"   🏥 Status: {final_report['overall_assessment']['validation_status']}")
        logger.info(f"   ✅ Ready for Phase 2.3: {final_report['production_readiness']['ready_for_phase_2_3']}")
        
        if final_report['recommendations']:
            logger.info("💡 Recommendations:")
            for rec in final_report['recommendations']:
                logger.info(f"   - {rec}")
        
        # Close database
        validator.graph_db.close_database()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Graph validation failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())