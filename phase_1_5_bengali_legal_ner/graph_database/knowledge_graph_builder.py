#!/usr/bin/env python3
"""
Knowledge Graph Builder for Phase 2.2
Build legal document nodes and relationships using NER outputs from Phase 2.1
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import logging
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph_database.graph_database_setup import LegalKnowledgeGraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeGraphBuilder:
    """
    Build Bengali Legal Knowledge Graph from NER-extracted entities and relationships
    """
    
    def __init__(self, db_path: str = "bengali_legal_knowledge_graph.db"):
        self.graph_db = LegalKnowledgeGraphDatabase(db_path)
        self.entity_counter = {"nodes": 0, "edges": 0}
        self.ner_model_config = self._load_ner_config()
        
        logger.info("🔧 Initialized Knowledge Graph Builder")
        
    def _load_ner_config(self) -> Dict[str, Any]:
        """Load NER model configuration and entity mappings"""
        try:
            config_path = "../training/expanded_model_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info("✅ Loaded NER model configuration")
            return config
            
        except FileNotFoundError:
            logger.warning("⚠️ NER config not found, using default mappings")
            return self._get_default_entity_mapping()
    
    def _get_default_entity_mapping(self) -> Dict[str, Any]:
        """Default entity to node type mapping"""
        return {
            "entity_to_node_mapping": {
                "ACT": "ACT_NODE",
                "SECTION": "SECTION_NODE", 
                "SCHEDULE": "SCHEDULE_NODE",
                "RULE": "RULE_NODE",
                "AMOUNT": "CONCEPT_NODE",
                "PERCENTAGE": "CONCEPT_NODE",
                "DATE": "CONCEPT_NODE",
                "AUTHORITY": "CONCEPT_NODE",
                "TAXPAYER": "CONCEPT_NODE",
                "FORM": "CONCEPT_NODE"
            },
            "relationship_to_edge_mapping": {
                "REFERENCE": "REFERENCES",
                "OVERRIDE": "OVERRIDES", 
                "IMPLEMENT": "IMPLEMENTS",
                "MODIFY": "MODIFIES",
                "CONDITION": "CONDITIONS",
                "HIERARCHY": "HIERARCHY"
            }
        }
    
    def create_document_node(self, document_data: Dict[str, Any]) -> str:
        """Create a document root node"""
        
        document_id = f"doc_{document_data.get('id', self.entity_counter['nodes'])}"
        self.entity_counter['nodes'] += 1
        
        node_properties = {
            "title": document_data.get("title", "Unknown Document"),
            "type": document_data.get("type", "legal_document"),
            "date": document_data.get("date", datetime.now().isoformat()),
            "authority": document_data.get("authority", "Unknown Authority"),
            "language": document_data.get("language", "bengali"),
            "source": document_data.get("source", "ner_extraction")
        }
        
        success = self.graph_db.add_node(document_id, "DOCUMENT_NODE", node_properties)
        
        if success:
            logger.info(f"✅ Created document node: {document_id}")
            return document_id
        else:
            logger.error(f"❌ Failed to create document node: {document_id}")
            return None
    
    def create_nodes_from_ner_entities(self, 
                                     ner_output: Dict[str, Any], 
                                     document_id: str) -> Dict[str, List[str]]:
        """Create graph nodes from NER-extracted entities"""
        
        created_nodes = {
            "SECTION_NODE": [],
            "SCHEDULE_NODE": [],
            "RULE_NODE": [],
            "ACT_NODE": [],
            "CONCEPT_NODE": []
        }
        
        entity_mapping = self.ner_model_config.get("entity_to_node_mapping", 
                                                  self._get_default_entity_mapping()["entity_to_node_mapping"])
        
        # Process each entity from NER output
        entities = ner_output.get("entities", [])
        text = ner_output.get("text", "")
        
        logger.info(f"🔄 Processing {len(entities)} entities from NER output...")
        
        for entity in entities:
            try:
                start, end, entity_type = entity
                entity_text = text[start:end]
                
                # Map entity type to node type
                node_type = entity_mapping.get(entity_type, "CONCEPT_NODE")
                
                # Create unique node ID
                node_id = self._generate_node_id(entity_text, entity_type, document_id)
                
                # Create node properties based on entity type
                node_properties = self._create_node_properties(
                    entity_text, entity_type, document_id, start, end
                )
                
                # Add node to graph
                success = self.graph_db.add_node(node_id, node_type, node_properties)
                
                if success:
                    created_nodes[node_type].append(node_id)
                    self.entity_counter['nodes'] += 1
                    
                    # Create CONTAINS relationship from document to entity
                    self.graph_db.add_edge(document_id, node_id, "CONTAINS", {
                        "position": start,
                        "length": end - start,
                        "extraction_confidence": 0.9
                    })
                    self.entity_counter['edges'] += 1
                    
                else:
                    logger.warning(f"⚠️ Failed to create node for entity: {entity_text}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing entity {entity}: {str(e)}")
                continue
        
        logger.info("✅ Node creation from NER entities complete")
        for node_type, nodes in created_nodes.items():
            if nodes:
                logger.info(f"   📝 {node_type}: {len(nodes)} nodes")
        
        return created_nodes
    
    def _generate_node_id(self, entity_text: str, entity_type: str, document_id: str) -> str:
        """Generate unique node ID"""
        # Clean text for ID
        clean_text = re.sub(r'[^\w\s-]', '', entity_text).strip()
        clean_text = re.sub(r'\s+', '_', clean_text)[:50]  # Limit length
        
        return f"{document_id}_{entity_type.lower()}_{clean_text}_{self.entity_counter['nodes']}"
    
    def _create_node_properties(self, 
                              entity_text: str, 
                              entity_type: str, 
                              document_id: str,
                              start_pos: int,
                              end_pos: int) -> Dict[str, Any]:
        """Create appropriate properties for different node types"""
        
        base_properties = {
            "text": entity_text,
            "entity_type": entity_type,
            "document_id": document_id,
            "start_position": start_pos,
            "end_position": end_pos,
            "extraction_method": "phase_2_1_ner"
        }
        
        # Add type-specific properties
        if entity_type == "SECTION":
            # Extract section number if possible
            section_match = re.search(r'(\d+)', entity_text)
            base_properties.update({
                "section_number": section_match.group(1) if section_match else "unknown",
                "title": entity_text
            })
            
        elif entity_type == "ACT":
            base_properties.update({
                "title": entity_text,
                "year": self._extract_year(entity_text),
                "status": "active"
            })
            
        elif entity_type == "SCHEDULE":
            schedule_match = re.search(r'(\d+)', entity_text)
            base_properties.update({
                "schedule_number": schedule_match.group(1) if schedule_match else "unknown",
                "title": entity_text
            })
            
        elif entity_type == "RULE":
            rule_match = re.search(r'(\d+)', entity_text)
            base_properties.update({
                "rule_number": rule_match.group(1) if rule_match else "unknown",
                "title": entity_text
            })
            
        elif entity_type in ["AMOUNT", "PERCENTAGE", "DATE", "AUTHORITY", "TAXPAYER", "FORM"]:
            base_properties.update({
                "concept_type": entity_type.lower(),
                "value": entity_text,
                "context": f"extracted from {document_id}"
            })
        
        return base_properties
    
    def _extract_year(self, text: str) -> Optional[str]:
        """Extract year from text"""
        year_match = re.search(r'(\d{4})', text)
        return year_match.group(1) if year_match else None
    
    def create_relationships_from_ner(self, 
                                    ner_output: Dict[str, Any], 
                                    created_nodes: Dict[str, List[str]]) -> Dict[str, int]:
        """Create relationships from NER relationship entities"""
        
        relationship_stats = {
            "REFERENCES": 0,
            "OVERRIDES": 0, 
            "IMPLEMENTS": 0,
            "MODIFIES": 0,
            "CONDITIONS": 0,
            "HIERARCHY": 0
        }
        
        relationship_mapping = self.ner_model_config.get("relationship_to_edge_mapping",
                                                        self._get_default_entity_mapping()["relationship_to_edge_mapping"])
        
        # Extract relationship entities from NER output
        entities = ner_output.get("entities", [])
        text = ner_output.get("text", "")
        
        logger.info("🔄 Creating relationships from NER relationship entities...")
        
        # Group entities by type
        entity_groups = {}
        for entity in entities:
            if len(entity) >= 3:
                start, end, entity_type = entity[:3]
                if entity_type not in entity_groups:
                    entity_groups[entity_type] = []
                entity_groups[entity_type].append((start, end, text[start:end]))
        
        # Create relationships based on proximity and context
        for relationship_type in relationship_mapping.keys():
            if relationship_type in entity_groups:
                edge_type = relationship_mapping[relationship_type]
                
                # Find nearby entities to connect
                relationship_entities = entity_groups[relationship_type]
                
                for rel_start, rel_end, rel_text in relationship_entities:
                    # Find closest legal entities before and after the relationship
                    source_entities = self._find_nearby_entities(
                        rel_start, entities, text, direction="before"
                    )
                    target_entities = self._find_nearby_entities(
                        rel_end, entities, text, direction="after"  
                    )
                    
                    # Create relationships
                    for source in source_entities:
                        for target in target_entities:
                            source_node = self._find_matching_node(source, created_nodes)
                            target_node = self._find_matching_node(target, created_nodes)
                            
                            if source_node and target_node and source_node != target_node:
                                success = self.graph_db.add_edge(
                                    source_node, target_node, edge_type,
                                    {
                                        "relationship_text": rel_text,
                                        "context": text[max(0, rel_start-50):rel_end+50],
                                        "confidence": 0.8,
                                        "extraction_method": "phase_2_1_ner"
                                    }
                                )
                                
                                if success:
                                    relationship_stats[relationship_type] += 1
                                    self.entity_counter['edges'] += 1
        
        logger.info("✅ Relationship creation complete")
        for rel_type, count in relationship_stats.items():
            if count > 0:
                logger.info(f"   🔗 {rel_type}: {count} relationships")
        
        return relationship_stats
    
    def _find_nearby_entities(self, 
                            position: int, 
                            all_entities: List, 
                            text: str, 
                            direction: str = "before",
                            max_distance: int = 200) -> List[Tuple]:
        """Find entities near a given position"""
        nearby_entities = []
        legal_entity_types = ["SECTION", "ACT", "SCHEDULE", "RULE"]
        
        for entity in all_entities:
            if len(entity) >= 3:
                start, end, entity_type = entity[:3]
                
                if entity_type in legal_entity_types:
                    if direction == "before" and start < position and position - end <= max_distance:
                        nearby_entities.append((start, end, entity_type, text[start:end]))
                    elif direction == "after" and start > position and start - position <= max_distance:
                        nearby_entities.append((start, end, entity_type, text[start:end]))
        
        # Sort by distance
        if direction == "before":
            nearby_entities.sort(key=lambda x: position - x[1], reverse=False)
        else:
            nearby_entities.sort(key=lambda x: x[0] - position, reverse=False)
        
        return nearby_entities[:3]  # Return top 3 closest
    
    def _find_matching_node(self, 
                          entity_info: Tuple, 
                          created_nodes: Dict[str, List[str]]) -> Optional[str]:
        """Find the node ID that matches an entity"""
        start, end, entity_type, entity_text = entity_info
        
        # Get entity to node mapping
        entity_mapping = self.ner_model_config.get("entity_to_node_mapping",
                                                  self._get_default_entity_mapping()["entity_to_node_mapping"])
        
        node_type = entity_mapping.get(entity_type, "CONCEPT_NODE")
        
        # Search in created nodes
        for node_id in created_nodes.get(node_type, []):
            # Simple text matching - in production would use more sophisticated matching
            if entity_text.lower() in node_id.lower() or any(word in node_id.lower() for word in entity_text.lower().split()):
                return node_id
        
        return None
    
    def process_document_with_ner(self, 
                                document_data: Dict[str, Any],
                                ner_output: Dict[str, Any]) -> Dict[str, Any]:
        """Process a complete document with NER output to build knowledge graph"""
        
        logger.info(f"🔄 Processing document: {document_data.get('title', 'Unknown')}")
        
        processing_results = {
            "document_id": None,
            "created_nodes": {},
            "relationship_stats": {},
            "processing_time": datetime.now().isoformat(),
            "success": False
        }
        
        try:
            # Step 1: Create document node
            document_id = self.create_document_node(document_data)
            if not document_id:
                raise Exception("Failed to create document node")
            
            processing_results["document_id"] = document_id
            
            # Step 2: Create nodes from NER entities
            created_nodes = self.create_nodes_from_ner_entities(ner_output, document_id)
            processing_results["created_nodes"] = created_nodes
            
            # Step 3: Create relationships from NER relationship entities
            relationship_stats = self.create_relationships_from_ner(ner_output, created_nodes)
            processing_results["relationship_stats"] = relationship_stats
            
            processing_results["success"] = True
            logger.info(f"✅ Document processing complete: {document_id}")
            
        except Exception as e:
            logger.error(f"❌ Document processing failed: {str(e)}")
            processing_results["error"] = str(e)
        
        return processing_results
    
    def batch_process_documents(self, documents_and_ner: List[Tuple[Dict, Dict]]) -> Dict[str, Any]:
        """Process multiple documents in batch"""
        
        logger.info(f"🚀 Starting batch processing of {len(documents_and_ner)} documents")
        
        batch_results = {
            "batch_start": datetime.now().isoformat(),
            "total_documents": len(documents_and_ner),
            "processed_documents": [],
            "batch_stats": {
                "successful": 0,
                "failed": 0,
                "total_nodes": 0,
                "total_edges": 0
            }
        }
        
        for i, (document_data, ner_output) in enumerate(documents_and_ner, 1):
            logger.info(f"📋 Processing document {i}/{len(documents_and_ner)}")
            
            result = self.process_document_with_ner(document_data, ner_output)
            batch_results["processed_documents"].append(result)
            
            if result["success"]:
                batch_results["batch_stats"]["successful"] += 1
                # Count nodes and edges
                for node_type, nodes in result["created_nodes"].items():
                    batch_results["batch_stats"]["total_nodes"] += len(nodes)
                for rel_type, count in result["relationship_stats"].items():
                    batch_results["batch_stats"]["total_edges"] += count
            else:
                batch_results["batch_stats"]["failed"] += 1
        
        batch_results["batch_end"] = datetime.now().isoformat()
        
        logger.info("✅ Batch processing complete")
        logger.info(f"   📊 Successful: {batch_results['batch_stats']['successful']}")
        logger.info(f"   ❌ Failed: {batch_results['batch_stats']['failed']}")
        logger.info(f"   📝 Total nodes: {batch_results['batch_stats']['total_nodes']}")
        logger.info(f"   🔗 Total edges: {batch_results['batch_stats']['total_edges']}")
        
        return batch_results
    
    def get_graph_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of the built knowledge graph"""
        
        graph_stats = self.graph_db.get_graph_statistics()
        validation = self.graph_db.validate_graph_integrity()
        
        summary = {
            "generation_date": datetime.now().isoformat(),
            "phase": "Phase 2.2 - Knowledge Graph Construction",
            "graph_statistics": graph_stats,
            "validation_status": validation["overall_status"],
            "graph_health": validation,
            "builder_stats": {
                "total_nodes_created": self.entity_counter["nodes"],
                "total_edges_created": self.entity_counter["edges"]
            }
        }
        
        return summary
    
    def save_results(self, filename: str = "knowledge_graph_construction_results.json"):
        """Save graph construction results"""
        
        results = self.get_graph_summary()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Results saved to {filename}")
        
        # Also save graph export
        self.graph_db.save_graph_to_file()
        
        return results
    
    def build_knowledge_graph_from_ner(self, ner_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build knowledge graph from NER outputs"""
        
        logger.info(f"🏗️ Building knowledge graph from {len(ner_outputs)} NER outputs...")
        
        build_results = {
            "build_status": "SUCCESS",
            "nodes_created": 0,
            "edges_created": 0,
            "documents_processed": len(ner_outputs),
            "errors": []
        }
        
        try:
            for ner_output in ner_outputs:
                # Process each NER output
                document_metadata = {
                    "id": ner_output.get("document_id", f"doc_{len(ner_outputs)}"),
                    "type": "legal_document",
                    "source": "ner_processing",
                    "language": "bengali"
                }
                
                # Create mock NER result in expected format
                ner_result = {
                    "document_id": document_metadata["id"],
                    "text": ner_output.get("text", ""),
                    "entities": ner_output.get("entities", []),
                    "relationships": []  # Add empty relationships for now
                }
                
                # Process the document
                result = self.process_document_with_ner(document_metadata, ner_result)
                
                if result.get("status") == "SUCCESS":
                    build_results["nodes_created"] += result.get("nodes_created", 0)
                    build_results["edges_created"] += result.get("edges_created", 0)
                else:
                    build_results["errors"].append(f"Failed to process {document_metadata['id']}")
            
            logger.info(f"✅ Knowledge graph built: {build_results['nodes_created']} nodes, {build_results['edges_created']} edges")
            
        except Exception as e:
            build_results["build_status"] = "FAILED"
            build_results["errors"].append(str(e))
            logger.error(f"❌ Knowledge graph building failed: {str(e)}")
        
        return build_results

def create_sample_test_data() -> List[Tuple[Dict, Dict]]:
    """Create sample test data for demonstration"""
    
    sample_documents = [
        {
            "id": "sample_1",
            "title": "আয়কর আইন ২০২৩",
            "type": "act",
            "date": "2023-07-01",
            "authority": "জাতীয় রাজস্ব বোর্ড",
            "language": "bengali"
        },
        {
            "id": "sample_2", 
            "title": "Income Tax Rules 2024",
            "type": "rules",
            "date": "2024-01-01",
            "authority": "National Board of Revenue",
            "language": "english"
        }
    ]
    
    sample_ner_outputs = [
        {
            "text": "আয়কর আইন ২০২৩ এর ধারা ১৬৩ অনুসারে করদাতার আয় ৫০ হাজার টাকার বেশি হলে ১৫ শতাংশ কর প্রযোজ্য। উক্ত ধারার বিধান জাতীয় রাজস্ব বোর্ড কর্তৃক বাস্তবায়িত হবে।",
            "entities": [
                [0, 16, "ACT"],
                [20, 28, "SECTION"],
                [29, 37, "REFERENCE"],
                [38, 46, "TAXPAYER"],
                [49, 60, "AMOUNT"],
                [67, 77, "PERCENTAGE"],
                [86, 89, "REFERENCE"],
                [90, 95, "SECTION"],
                [99, 104, "IMPLEMENT"],
                [105, 124, "AUTHORITY"]
            ]
        },
        {
            "text": "According to section 163 of Income Tax Act 2023, if taxpayer income exceeds 50,000 taka then 15 percent tax applies. The said section shall be implemented by National Board of Revenue.",
            "entities": [
                [13, 23, "SECTION"],
                [27, 44, "ACT"],
                [52, 60, "TAXPAYER"],
                [77, 88, "AMOUNT"],
                [94, 104, "PERCENTAGE"],
                [122, 135, "REFERENCE"],
                [147, 158, "IMPLEMENT"],
                [162, 187, "AUTHORITY"]
            ]
        }
    ]
    
    return list(zip(sample_documents, sample_ner_outputs))

def main():
    """Main execution function"""
    logger.info("🚀 Phase 2.2: Knowledge Graph Construction")
    logger.info("=" * 60)
    
    try:
        # Initialize graph builder
        builder = KnowledgeGraphBuilder()
        
        # Create sample test data
        test_data = create_sample_test_data()
        logger.info(f"📋 Created {len(test_data)} sample documents for testing")
        
        # Process documents
        batch_results = builder.batch_process_documents(test_data)
        
        # Get final summary
        summary = builder.get_graph_summary()
        
        # Save results
        builder.save_results()
        
        logger.info("=" * 60)
        logger.info("✅ Phase 2.2: Knowledge Graph Construction COMPLETE")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   📝 Total nodes: {summary['graph_statistics']['total_nodes']}")
        logger.info(f"   🔗 Total edges: {summary['graph_statistics']['total_edges']}")
        logger.info(f"   🏥 Graph health: {summary['validation_status']}")
        
        # Close database
        builder.graph_db.close_database()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Knowledge graph construction failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())