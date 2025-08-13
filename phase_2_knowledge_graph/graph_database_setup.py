#!/usr/bin/env python3
"""
Graph Database Setup for Phase 2.2
Setup and configure graph database infrastructure for Bengali Legal Knowledge Graph
"""

import json
import networkx as nx
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LegalKnowledgeGraphDatabase:
    """
    Graph Database Infrastructure for Bengali Legal Knowledge Graph
    Using NetworkX for graph operations and SQLite for persistence
    """
    
    def __init__(self, db_path: str = "bengali_legal_knowledge_graph.db"):
        self.db_path = db_path
        self.graph = nx.MultiDiGraph()  # Directed graph supporting multiple edges
        self.node_types = self._define_node_types()
        self.edge_types = self._define_edge_types()
        self.setup_database()
        
        logger.info(f"🔧 Initialized Legal Knowledge Graph Database")
        logger.info(f"📁 Database path: {self.db_path}")
        
    def _define_node_types(self) -> Dict[str, Dict[str, Any]]:
        """Define the types of nodes in the knowledge graph"""
        return {
            "DOCUMENT_NODE": {
                "description": "Root document nodes representing legal documents",
                "properties": ["document_id", "title", "type", "date", "authority", "language"],
                "examples": ["Income Tax Act 2023", "VAT Law 2012"]
            },
            
            "SECTION_NODE": {
                "description": "Legal section nodes from documents",
                "properties": ["section_id", "document_id", "text", "section_number", "title"],
                "examples": ["Section 163 of Income Tax Act", "ধারা ১৬৩"]
            },
            
            "SCHEDULE_NODE": {
                "description": "Schedule and appendix nodes",
                "properties": ["schedule_id", "document_id", "schedule_number", "title", "content"],
                "examples": ["6th Schedule", "তৃতীয় তফসিল"]
            },
            
            "RULE_NODE": {
                "description": "Rules and regulation nodes",
                "properties": ["rule_id", "document_id", "rule_number", "title", "content"],
                "examples": ["Income Tax Rules", "আয়কর বিধিমালা"]
            },
            
            "ACT_NODE": {
                "description": "Act and law nodes",
                "properties": ["act_id", "title", "year", "authority", "status"],
                "examples": ["Income Tax Act", "মূল্য সংযোজন কর আইন"]
            },
            
            "CONCEPT_NODE": {
                "description": "Legal concept nodes (amounts, dates, authorities, etc.)",
                "properties": ["concept_id", "type", "value", "context", "document_id"],
                "examples": ["50,000 Taka", "15 percent", "National Board of Revenue"]
            }
        }
    
    def _define_edge_types(self) -> Dict[str, Dict[str, Any]]:
        """Define the types of relationships in the knowledge graph"""
        return {
            "REFERENCES": {
                "description": "One legal provision references another",
                "properties": ["reference_type", "context", "confidence"],
                "examples": ["Section A references Schedule B", "উক্ত ধারার অনুসারে"]
            },
            
            "OVERRIDES": {
                "description": "One provision overrides/supersedes another",
                "properties": ["override_type", "effective_date", "authority"],
                "examples": ["New section overrides old section", "সংশোধিত ধারা পূর্বের রহিত করে"]
            },
            
            "IMPLEMENTS": {
                "description": "One provision implements/executes another",
                "properties": ["implementation_method", "scope", "requirements"],
                "examples": ["Rule implements Act provision", "বিধি আইনের বাস্তবায়ন"]
            },
            
            "MODIFIES": {
                "description": "One provision modifies another",
                "properties": ["modification_type", "changes", "version"],
                "examples": ["Amendment modifies original", "সংশোধনী মূল পরিবর্তন করে"]
            },
            
            "CONDITIONS": {
                "description": "Conditional relationships between provisions",
                "properties": ["condition_type", "requirements", "exceptions"],
                "examples": ["If taxpayer income > 50K then Section X applies", "শর্তসাপেক্ষে প্রযোজ্য"]
            },
            
            "HIERARCHY": {
                "description": "Hierarchical relationships (parent-child)",
                "properties": ["hierarchy_level", "authority", "precedence"],
                "examples": ["Act > Rules > Guidelines", "আইন > বিধিমালা > নির্দেশনা"]
            },
            
            "CONTAINS": {
                "description": "Document contains sections/schedules",
                "properties": ["container_type", "position", "sequence"],
                "examples": ["Act contains Section", "আইন ধারা ধারণ করে"]
            },
            
            "APPLIES_TO": {
                "description": "Provision applies to specific concepts/entities",
                "properties": ["application_scope", "conditions", "exceptions"],
                "examples": ["Tax rate applies to income range", "কর হার আয়ের পরিসরে প্রযোজ্য"]
            }
        }
    
    def setup_database(self):
        """Setup SQLite database for graph persistence"""
        try:
            # Create database connection
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create nodes table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT NOT NULL,
                    properties TEXT,
                    created_date TEXT,
                    updated_date TEXT
                )
            """)
            
            # Create edges table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    edge_id TEXT PRIMARY KEY,
                    source_node TEXT,
                    target_node TEXT,
                    edge_type TEXT NOT NULL,
                    properties TEXT,
                    weight REAL DEFAULT 1.0,
                    created_date TEXT,
                    FOREIGN KEY (source_node) REFERENCES nodes (node_id),
                    FOREIGN KEY (target_node) REFERENCES nodes (node_id)
                )
            """)
            
            # Create metadata table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS graph_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_date TEXT
                )
            """)
            
            self.conn.commit()
            logger.info("✅ Database tables created successfully")
            
            # Initialize metadata
            self._initialize_metadata()
            
        except sqlite3.Error as e:
            logger.error(f"❌ Database setup error: {str(e)}")
            raise
    
    def _initialize_metadata(self):
        """Initialize graph metadata"""
        metadata = {
            "graph_version": "2.0",
            "phase": "Phase 2.2 - Graph Database Construction",
            "creation_date": datetime.now().isoformat(),
            "total_nodes": "0",
            "total_edges": "0",
            "node_types": json.dumps(list(self.node_types.keys())),
            "edge_types": json.dumps(list(self.edge_types.keys()))
        }
        
        for key, value in metadata.items():
            self.cursor.execute(
                "INSERT OR REPLACE INTO graph_metadata (key, value, updated_date) VALUES (?, ?, ?)",
                (key, value, datetime.now().isoformat())
            )
        
        self.conn.commit()
        logger.info("✅ Graph metadata initialized")
        
        # Load existing data from database into graph
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing nodes and edges from database into NetworkX graph"""
        try:
            # Load nodes
            self.cursor.execute("SELECT node_id, node_type, properties FROM nodes")
            nodes_data = self.cursor.fetchall()
            
            for node_id, node_type, properties_json in nodes_data:
                try:
                    properties = json.loads(properties_json) if properties_json else {}
                    properties['node_type'] = node_type
                    self.graph.add_node(node_id, **properties)
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Invalid JSON for node {node_id}")
            
            # Load edges
            self.cursor.execute("SELECT source_node, target_node, edge_type, properties, weight FROM edges")
            edges_data = self.cursor.fetchall()
            
            for source, target, edge_type, properties_json, weight in edges_data:
                try:
                    properties = json.loads(properties_json) if properties_json else {}
                    properties['edge_type'] = edge_type
                    properties['weight'] = weight
                    self.graph.add_edge(source, target, **properties)
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Invalid JSON for edge {source}->{target}")
            
            nodes_loaded = self.graph.number_of_nodes()
            edges_loaded = self.graph.number_of_edges()
            logger.info(f"✅ Loaded existing graph: {nodes_loaded} nodes, {edges_loaded} edges")
            
        except sqlite3.Error as e:
            logger.warning(f"⚠️ Could not load existing data: {str(e)}")
    
    def add_node(self, 
                 node_id: str, 
                 node_type: str, 
                 properties: Dict[str, Any]) -> bool:
        """Add a node to the knowledge graph"""
        try:
            # Validate node type
            if node_type not in self.node_types:
                logger.error(f"❌ Invalid node type: {node_type}")
                return False
            
            # Add to NetworkX graph (avoid 'type' conflict with NetworkX)
            node_attrs = properties.copy()
            node_attrs['node_type'] = node_type
            self.graph.add_node(node_id, **node_attrs)
            
            # Add to SQLite database
            self.cursor.execute("""
                INSERT OR REPLACE INTO nodes 
                (node_id, node_type, properties, created_date, updated_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                node_id,
                node_type,
                json.dumps(properties),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            logger.debug(f"✅ Added node: {node_id} ({node_type})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding node {node_id}: {str(e)}")
            return False
    
    def add_edge(self, 
                 source_node: str, 
                 target_node: str, 
                 edge_type: str, 
                 properties: Optional[Dict[str, Any]] = None,
                 weight: float = 1.0) -> bool:
        """Add an edge to the knowledge graph"""
        try:
            # Validate edge type
            if edge_type not in self.edge_types:
                logger.error(f"❌ Invalid edge type: {edge_type}")
                return False
            
            # Validate nodes exist
            if source_node not in self.graph.nodes or target_node not in self.graph.nodes:
                logger.error(f"❌ Source or target node not found: {source_node} -> {target_node}")
                return False
            
            if properties is None:
                properties = {}
            
            # Add to NetworkX graph (avoid 'type' conflict with NetworkX)
            edge_attrs = properties.copy() if properties else {}
            edge_attrs['edge_type'] = edge_type
            edge_attrs['weight'] = weight
            self.graph.add_edge(source_node, target_node, **edge_attrs)
            
            # Generate edge ID
            edge_id = f"{source_node}_{edge_type}_{target_node}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Add to SQLite database
            self.cursor.execute("""
                INSERT INTO edges 
                (edge_id, source_node, target_node, edge_type, properties, weight, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                edge_id,
                source_node,
                target_node,
                edge_type,
                json.dumps(properties),
                weight,
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            logger.debug(f"✅ Added edge: {source_node} --[{edge_type}]--> {target_node}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding edge: {str(e)}")
            return False
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics"""
        stats = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_type_distribution": {},
            "edge_type_distribution": {},
            "connectivity_metrics": {}
        }
        
        # Node type distribution
        for node_id, data in self.graph.nodes(data=True):
            node_type = data.get('node_type', 'UNKNOWN')
            stats["node_type_distribution"][node_type] = \
                stats["node_type_distribution"].get(node_type, 0) + 1
        
        # Edge type distribution
        for u, v, data in self.graph.edges(data=True):
            edge_type = data.get('edge_type', 'UNKNOWN')
            stats["edge_type_distribution"][edge_type] = \
                stats["edge_type_distribution"].get(edge_type, 0) + 1
        
        # Connectivity metrics
        if stats["total_nodes"] > 0:
            stats["connectivity_metrics"] = {
                "density": nx.density(self.graph),
                "is_connected": nx.is_weakly_connected(self.graph) if stats["total_edges"] > 0 else False,
                "number_of_components": nx.number_weakly_connected_components(self.graph)
            }
        
        return stats
    
    def save_graph_to_file(self, filename: str = "bengali_legal_knowledge_graph.json"):
        """Save graph to JSON file for backup/analysis"""
        try:
            graph_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "graph_version": "2.0",
                    "phase": "Phase 2.2"
                },
                "statistics": self.get_graph_statistics(),
                "nodes": [],
                "edges": []
            }
            
            # Export nodes
            for node_id, data in self.graph.nodes(data=True):
                graph_data["nodes"].append({
                    "id": node_id,
                    "type": data.get('node_type'),
                    "properties": {k: v for k, v in data.items() if k != 'node_type'}
                })
            
            # Export edges
            for u, v, data in self.graph.edges(data=True):
                graph_data["edges"].append({
                    "source": u,
                    "target": v,
                    "type": data.get('edge_type'),
                    "weight": data.get('weight', 1.0),
                    "properties": {k: v for k, v in data.items() if k not in ['edge_type', 'weight']}
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Graph saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving graph: {str(e)}")
            return False
    
    def query_nodes_by_type(self, node_type: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Query nodes by type"""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get('type') == node_type:
                nodes.append((node_id, data))
        return nodes
    
    def find_relationships(self, node_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Find all relationships for a given node"""
        relationships = {
            "outgoing": [],
            "incoming": []
        }
        
        # Outgoing relationships
        for target in self.graph.successors(node_id):
            edge_data = self.graph.get_edge_data(node_id, target)
            for key, data in edge_data.items():
                relationships["outgoing"].append({
                    "target": target,
                    "type": data.get('edge_type'),
                    "weight": data.get('weight', 1.0),
                    "properties": {k: v for k, v in data.items() if k not in ['edge_type', 'weight']}
                })
        
        # Incoming relationships
        for source in self.graph.predecessors(node_id):
            edge_data = self.graph.get_edge_data(source, node_id)
            for key, data in edge_data.items():
                relationships["incoming"].append({
                    "source": source,
                    "type": data.get('edge_type'),
                    "weight": data.get('weight', 1.0),
                    "properties": {k: v for k, v in data.items() if k not in ['edge_type', 'weight']}
                })
        
        return relationships
    
    def validate_graph_integrity(self) -> Dict[str, Any]:
        """Validate graph structure and integrity"""
        validation_report = {
            "validation_date": datetime.now().isoformat(),
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "issues": [],
            "recommendations": [],
            "overall_status": "UNKNOWN"
        }
        
        issues_count = 0
        
        # Check for isolated nodes
        isolated_nodes = list(nx.isolates(self.graph))
        if isolated_nodes:
            validation_report["issues"].append(f"Found {len(isolated_nodes)} isolated nodes")
            issues_count += len(isolated_nodes)
        
        # Check for invalid node types
        invalid_node_types = []
        for node_id, data in self.graph.nodes(data=True):
            node_type = data.get('node_type')
            if node_type not in self.node_types:
                invalid_node_types.append((node_id, node_type))
        
        if invalid_node_types:
            validation_report["issues"].append(f"Found {len(invalid_node_types)} nodes with invalid types")
            issues_count += len(invalid_node_types)
        
        # Check for invalid edge types
        invalid_edge_types = []
        for u, v, data in self.graph.edges(data=True):
            edge_type = data.get('edge_type')
            if edge_type not in self.edge_types:
                invalid_edge_types.append((u, v, edge_type))
        
        if invalid_edge_types:
            validation_report["issues"].append(f"Found {len(invalid_edge_types)} edges with invalid types")
            issues_count += len(invalid_edge_types)
        
        # Determine overall status
        if issues_count == 0:
            validation_report["overall_status"] = "HEALTHY"
        elif issues_count < 10:
            validation_report["overall_status"] = "WARNING"
        else:
            validation_report["overall_status"] = "CRITICAL"
        
        # Add recommendations
        if isolated_nodes:
            validation_report["recommendations"].append("Review isolated nodes - they may need connections")
        
        if validation_report["total_nodes"] > 0 and validation_report["total_edges"] == 0:
            validation_report["recommendations"].append("Graph has nodes but no edges - consider adding relationships")
        
        return validation_report
    
    def export_graph_to_json(self, filename: str = "bengali_legal_knowledge_graph.json") -> bool:
        """Export graph to JSON format"""
        try:
            graph_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "graph_version": "2.0",
                    "phase": "Phase 2.2 - Graph Database Export"
                },
                "statistics": {
                    "total_nodes": self.graph.number_of_nodes(),
                    "total_edges": self.graph.number_of_edges(),
                    "node_type_distribution": {}
                },
                "nodes": [],
                "edges": []
            }
            
            # Count node types
            for node_id, node_data in self.graph.nodes(data=True):
                node_type = node_data.get('node_type', 'UNKNOWN')
                graph_data["statistics"]["node_type_distribution"][node_type] = \
                    graph_data["statistics"]["node_type_distribution"].get(node_type, 0) + 1
                
                # Add node to export
                node_export = {
                    "id": node_id,
                    "type": node_type,
                    "properties": {k: v for k, v in node_data.items() if k != 'node_type'}
                }
                graph_data["nodes"].append(node_export)
            
            # Export edges
            for u, v, edge_data in self.graph.edges(data=True):
                edge_export = {
                    "source": u,
                    "target": v,
                    "type": edge_data.get('edge_type', 'UNKNOWN'),
                    "weight": edge_data.get('weight', 1.0),
                    "properties": {k: v for k, v in edge_data.items() 
                                 if k not in ['edge_type', 'weight']}
                }
                graph_data["edges"].append(edge_export)
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Graph exported to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Export failed: {str(e)}")
            return False
    
    def close_database(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
            logger.info("📁 Database connection closed")

def main():
    """Main execution function"""
    logger.info("🚀 Phase 2.2: Graph Database Setup")
    logger.info("=" * 60)
    
    try:
        # Initialize graph database
        graph_db = LegalKnowledgeGraphDatabase()
        
        # Display configuration
        logger.info("📋 Graph Database Configuration:")
        logger.info(f"   🏷️ Node types: {len(graph_db.node_types)}")
        logger.info(f"   🔗 Edge types: {len(graph_db.edge_types)}")
        
        for node_type, config in graph_db.node_types.items():
            logger.info(f"     📝 {node_type}: {config['description']}")
        
        for edge_type, config in graph_db.edge_types.items():
            logger.info(f"     ⚡ {edge_type}: {config['description']}")
        
        # Test basic functionality
        logger.info("\n🧪 Testing basic functionality...")
        
        # Add test nodes
        test_success = True
        test_success &= graph_db.add_node("test_act_1", "ACT_NODE", {
            "title": "আয়কর আইন ২০২৩",
            "year": "2023",
            "authority": "জাতীয় রাজস্ব বোর্ড"
        })
        
        test_success &= graph_db.add_node("test_section_1", "SECTION_NODE", {
            "section_number": "163",
            "title": "কর নির্ধারণ",
            "document_id": "test_act_1"
        })
        
        # Add test edge
        test_success &= graph_db.add_edge("test_act_1", "test_section_1", "CONTAINS", {
            "position": 163,
            "sequence": 1
        })
        
        if test_success:
            logger.info("✅ Basic functionality test passed")
        else:
            logger.error("❌ Basic functionality test failed")
        
        # Get statistics
        stats = graph_db.get_graph_statistics()
        logger.info("\n📊 Graph Statistics:")
        logger.info(f"   📝 Total nodes: {stats['total_nodes']}")
        logger.info(f"   🔗 Total edges: {stats['total_edges']}")
        
        # Validate graph
        validation = graph_db.validate_graph_integrity()
        logger.info(f"\n🔍 Graph Validation: {validation['overall_status']}")
        
        # Save graph
        graph_db.save_graph_to_file()
        
        # Create configuration file
        config_data = {
            "database_config": {
                "type": "hybrid",
                "graph_engine": "NetworkX",
                "persistence": "SQLite",
                "database_path": graph_db.db_path
            },
            "node_types": graph_db.node_types,
            "edge_types": graph_db.edge_types,
            "setup_date": datetime.now().isoformat(),
            "status": "READY"
        }
        
        with open("graph_database_config.json", 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        logger.info("\n✅ Phase 2.2: Graph Database Setup COMPLETE")
        logger.info("📁 Files created:")
        logger.info("   - bengali_legal_knowledge_graph.db (SQLite database)")
        logger.info("   - bengali_legal_knowledge_graph.json (Graph export)")
        logger.info("   - graph_database_config.json (Configuration)")
        
        # Close database
        graph_db.close_database()
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())