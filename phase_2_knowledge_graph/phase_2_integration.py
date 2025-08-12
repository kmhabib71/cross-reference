#!/usr/bin/env python3
"""
Phase 2 Integration Module - Legal Knowledge Graph System
=========================================================

Complete integration of Phase 2 components:
- Entity Recognition System (Task 2.1)
- Knowledge Graph Construction (Task 2.2)  
- Precedence Engine (Task 2.3)

This module provides unified interface for Phase 2 functionality
and prepares for Phase 2.5 (Temporal Law Version Control).

Author: Phase 2 Implementation
Date: August 10, 2025
"""

import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import sys

# Import Phase 2 components
from legal_entity_extractor import LegalEntityExtractor, LegalEntity
from legal_knowledge_graph import LegalKnowledgeGraph, GraphNode, GraphRelationship
from precedence_engine import LegalPrecedenceEngine, LegalProvision, ConflictResolution

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase2IntegratedSystem:
    """
    Unified interface for Phase 2 Legal Knowledge Graph System.
    
    Features:
    - Complete entity extraction from legal documents
    - Knowledge graph construction and relationship mapping
    - Precedence-based conflict resolution
    - Query processing with authority hierarchy
    - Export/import capabilities for all components
    """
    
    def __init__(self):
        """Initialize integrated Phase 2 system"""
        self.entity_extractor = LegalEntityExtractor()
        self.knowledge_graph = LegalKnowledgeGraph()
        self.precedence_engine = LegalPrecedenceEngine(self.knowledge_graph)
        
        self.processed_documents = {}
        self.system_metadata = {
            'version': '2.1.0',
            'phase': 'Phase 2 - Legal Knowledge Graph',
            'components': [
                'Entity Recognition System',
                'Knowledge Graph Constructor', 
                'Legal Precedence Engine'
            ],
            'capabilities': [
                'Bengali/English Entity Extraction',
                'Cross-reference Relationship Mapping',
                'Authority Hierarchy Enforcement',
                'Conflict Resolution with Evidence',
                'Query Processing with Precedence'
            ]
        }
        
        logger.info("Phase 2 Integrated System initialized")
    
    def process_legal_document(self, document_path: str) -> Dict[str, Any]:
        """
        Process single legal document through complete Phase 2 pipeline
        
        Args:
            document_path: Path to legal document JSON file
            
        Returns:
            Processing results with entities, graph nodes, and provisions
        """
        logger.info(f"Processing legal document: {document_path}")
        
        try:
            # Load document
            with open(document_path, 'r', encoding='utf-8') as f:
                document_data = json.load(f)
            
            document_name = Path(document_path).stem
            
            # Step 1: Extract entities
            text_content = self._extract_text_content(document_data)
            entities = self.entity_extractor.extract_entities(text_content, document_name)
            
            # Step 2: Create graph nodes
            graph_nodes = self._entities_to_graph_nodes(entities, document_data)
            
            # Step 3: Create legal provisions
            provisions = self._entities_to_legal_provisions(entities, document_name)
            
            # Step 4: Update knowledge graph
            self._update_knowledge_graph(graph_nodes, document_name)
            
            # Store processing results
            processing_result = {
                'document_path': document_path,
                'document_name': document_name,
                'entities_count': len(entities),
                'graph_nodes_count': len(graph_nodes),
                'provisions_count': len(provisions),
                'entities': entities,
                'graph_nodes': graph_nodes,
                'provisions': provisions,
                'processing_metadata': {
                    'extraction_version': '2.1.0',
                    'success': True,
                    'timestamp': self._get_timestamp()
                }
            }
            
            self.processed_documents[document_name] = processing_result
            
            logger.info(f"Document processed: {len(entities)} entities, {len(graph_nodes)} nodes, {len(provisions)} provisions")
            return processing_result
            
        except Exception as e:
            logger.error(f"Failed to process document {document_path}: {e}")
            return {
                'document_path': document_path,
                'success': False,
                'error': str(e),
                'processing_metadata': {
                    'extraction_version': '2.1.0',
                    'success': False,
                    'timestamp': self._get_timestamp()
                }
            }
    
    def process_document_collection(self, document_paths: List[str]) -> Dict[str, Any]:
        """
        Process collection of legal documents and build unified knowledge graph
        
        Args:
            document_paths: List of paths to legal document JSON files
            
        Returns:
            Collection processing results with unified graph
        """
        logger.info(f"Processing document collection: {len(document_paths)} documents")
        
        collection_results = []
        all_entities = []
        all_provisions = []
        
        # Process each document
        for doc_path in document_paths:
            result = self.process_legal_document(doc_path)
            collection_results.append(result)
            
            if result.get('success', True):
                all_entities.extend(result['entities'])
                all_provisions.extend(result['provisions'])
        
        # Build unified knowledge graph
        logger.info("Building unified knowledge graph...")
        self.knowledge_graph.build_graph_from_documents(document_paths)
        
        # Detect and resolve conflicts
        logger.info("Detecting and resolving conflicts...")
        conflicts = self._detect_provision_conflicts(all_provisions)
        conflict_resolutions = []
        
        for conflict in conflicts:
            resolution = self.precedence_engine.resolve_conflict(conflict)
            conflict_resolutions.append(resolution)
        
        # Build collection summary
        collection_summary = {
            'total_documents': len(document_paths),
            'processed_documents': len([r for r in collection_results if r.get('success', True)]),
            'failed_documents': len([r for r in collection_results if not r.get('success', True)]),
            'total_entities': len(all_entities),
            'total_provisions': len(all_provisions),
            'total_conflicts': len(conflicts),
            'resolved_conflicts': len(conflict_resolutions),
            'graph_stats': {
                'nodes': len(self.knowledge_graph.nodes),
                'relationships': len(self.knowledge_graph.relationships),
                'authority_levels': self.knowledge_graph._get_authority_distribution()
            },
            'entity_distribution': self._get_entity_distribution(all_entities),
            'document_results': collection_results,
            'conflict_resolutions': conflict_resolutions,
            'processing_metadata': {
                'version': '2.1.0',
                'timestamp': self._get_timestamp(),
                'success': True
            }
        }
        
        logger.info(f"Collection processing complete: {collection_summary['processed_documents']}/{collection_summary['total_documents']} documents")
        return collection_summary
    
    def query_legal_provision(self, query_text: str, resolve_conflicts: bool = True) -> Dict[str, Any]:
        """
        Query legal provisions with precedence-based resolution
        
        Args:
            query_text: Legal query in Bengali/English
            resolve_conflicts: Whether to resolve conflicts using precedence engine
            
        Returns:
            Query results with relevant provisions and conflict resolutions
        """
        logger.info(f"Processing legal query: {query_text[:50]}...")
        
        # Extract entities from query
        query_entities = self.entity_extractor.extract_entities(query_text, "user_query")
        
        # Find relevant provisions
        relevant_provisions = self._find_relevant_provisions(query_entities, query_text)
        
        # Detect conflicts if multiple provisions found
        conflicts = []
        resolutions = []
        
        if len(relevant_provisions) > 1 and resolve_conflicts:
            # Group by topic for conflict detection
            provision_groups = self._group_provisions_by_topic(relevant_provisions)
            
            for topic, provisions in provision_groups.items():
                if len(provisions) > 1:
                    conflicts.append(provisions)
                    resolution = self.precedence_engine.resolve_conflict(provisions)
                    resolutions.append(resolution)
        
        # Build query result
        query_result = {
            'query_text': query_text,
            'extracted_entities': query_entities,
            'relevant_provisions': relevant_provisions,
            'conflicts_detected': len(conflicts),
            'conflict_resolutions': resolutions,
            'primary_answer': resolutions[0].winning_provision if resolutions else (relevant_provisions[0] if relevant_provisions else None),
            'authority_analysis': [self.precedence_engine.get_precedence_analysis(p) for p in relevant_provisions],
            'query_metadata': {
                'processing_time': 'real-time',
                'confidence_score': self._calculate_query_confidence(relevant_provisions, resolutions),
                'resolution_method': 'precedence_hierarchy' if resolutions else 'direct_match'
            }
        }
        
        logger.info(f"Query processed: {len(relevant_provisions)} provisions, {len(resolutions)} resolutions")
        return query_result
    
    def export_complete_system(self, output_directory: str) -> None:
        """Export complete Phase 2 system data"""
        output_path = Path(output_directory)
        output_path.mkdir(exist_ok=True)
        
        # Export entities
        all_entities = []
        for doc_result in self.processed_documents.values():
            if 'entities' in doc_result:
                all_entities.extend(doc_result['entities'])
        
        entities_data = [entity.__dict__ if hasattr(entity, '__dict__') else entity for entity in all_entities]
        with open(output_path / "extracted_entities.json", 'w', encoding='utf-8') as f:
            json.dump({
                'entities': entities_data,
                'total_count': len(entities_data),
                'extraction_metadata': self.entity_extractor._get_entity_type_distribution(all_entities)
            }, f, ensure_ascii=False, indent=2)
        
        # Export knowledge graph
        self.knowledge_graph.export_graph(str(output_path / "knowledge_graph.json"))
        
        # Export precedence rules
        self.precedence_engine.export_precedence_rules(str(output_path / "precedence_rules.json"))
        
        # Export system metadata
        with open(output_path / "phase_2_metadata.json", 'w', encoding='utf-8') as f:
            json.dump({
                'system_metadata': self.system_metadata,
                'processed_documents': list(self.processed_documents.keys()),
                'statistics': {
                    'total_documents': len(self.processed_documents),
                    'total_entities': len(all_entities),
                    'graph_nodes': len(self.knowledge_graph.nodes),
                    'graph_relationships': len(self.knowledge_graph.relationships)
                },
                'export_timestamp': self._get_timestamp()
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Complete system exported to {output_directory}")
    
    # Internal utility methods
    def _extract_text_content(self, document_data: Dict) -> str:
        """Extract text content from document JSON"""
        text_parts = []
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['content', 'text', 'description', 'title', 'provision']:
                        if isinstance(value, str) and len(value) > 20:
                            text_parts.append(value)
                    else:
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
            elif isinstance(obj, str) and len(obj) > 20:
                text_parts.append(obj)
        
        extract_recursive(document_data)
        return ' '.join(text_parts)
    
    def _entities_to_graph_nodes(self, entities: List[LegalEntity], document_data: Dict) -> List[GraphNode]:
        """Convert entities to graph nodes"""
        graph_nodes = []
        
        for entity in entities:
            node = GraphNode(
                node_id=f"entity_{hash(entity.text + entity.document_source) % 10000}",
                node_type=self._classify_entity_node_type(entity),
                title=entity.text,
                content=entity.context,
                authority_level=self._calculate_node_authority(entity),
                metadata={
                    'entity_type': entity.entity_type,
                    'confidence': entity.confidence,
                    'normalized_form': entity.normalized_form
                }
            )
            graph_nodes.append(node)
        
        return graph_nodes
    
    def _entities_to_legal_provisions(self, entities: List[LegalEntity], document_name: str) -> List[LegalProvision]:
        """Convert entities to legal provisions"""
        provisions = []
        
        for entity in entities:
            if entity.entity_type in ['sections', 'SECTION_DIRECT', 'schedules', 'rules']:
                provision = self.precedence_engine.classify_provision(
                    text=entity.context or entity.text,
                    document_type=self._classify_document_type(document_name)
                )
                provisions.append(provision)
        
        return provisions
    
    def _classify_entity_node_type(self, entity: LegalEntity) -> str:
        """Classify entity as graph node type"""
        if entity.entity_type in ['sections', 'SECTION_DIRECT']:
            return 'section'
        elif entity.entity_type in ['schedules', 'SCHEDULE_REF']:
            return 'schedule'
        elif entity.entity_type in ['rules']:
            return 'rule'
        else:
            return 'concept'
    
    def _classify_document_type(self, document_name: str) -> str:
        """Classify document type for precedence engine"""
        name_lower = document_name.lower()
        
        if 'finance-ordinance' in name_lower or 'অর্থ_অধ্যাদেশ' in name_lower:
            return 'finance_ordinance'
        elif 'income-tax-act' in name_lower or 'আয়কর-আইন' in name_lower:
            return 'income_tax_act'
        elif 'schedule' in name_lower or 'তফসিল' in name_lower:
            return 'schedules'
        elif 'tds-rules' in name_lower or 'টিডিএস-বিধি' in name_lower:
            return 'tds_rules'
        elif 'circular' in name_lower or 'সার্কুলার' in name_lower:
            return 'circulars'
        else:
            return 'other'
    
    def _calculate_node_authority(self, entity: LegalEntity) -> int:
        """Calculate authority level for graph node"""
        base_authority = 50
        
        if entity.entity_type in ['sections', 'SECTION_DIRECT']:
            base_authority = 80
        elif entity.entity_type in ['schedules']:
            base_authority = 75
        elif entity.confidence > 0.8:
            base_authority += 10
        
        return min(100, base_authority)
    
    def _update_knowledge_graph(self, graph_nodes: List[GraphNode], document_name: str) -> None:
        """Update knowledge graph with new nodes"""
        for node in graph_nodes:
            self.knowledge_graph.nodes[node.node_id] = node
    
    def _detect_provision_conflicts(self, provisions: List[LegalProvision]) -> List[List[LegalProvision]]:
        """Detect conflicting provisions"""
        # Simple conflict detection based on overlapping topics
        conflicts = []
        
        # Group provisions by section number
        section_groups = {}
        for provision in provisions:
            if provision.section_number:
                key = provision.section_number
                if key not in section_groups:
                    section_groups[key] = []
                section_groups[key].append(provision)
        
        # Find groups with multiple provisions (potential conflicts)
        for section, group_provisions in section_groups.items():
            if len(group_provisions) > 1:
                # Check if they have different document types (likely conflict)
                doc_types = set(p.document_type for p in group_provisions)
                if len(doc_types) > 1:
                    conflicts.append(group_provisions)
        
        return conflicts
    
    def _find_relevant_provisions(self, query_entities: List[LegalEntity], query_text: str) -> List[LegalProvision]:
        """Find provisions relevant to query"""
        relevant_provisions = []
        
        # Simple keyword matching for now
        query_lower = query_text.lower()
        
        for doc_result in self.processed_documents.values():
            if 'provisions' in doc_result:
                for provision in doc_result['provisions']:
                    provision_text = provision.text.lower()
                    
                    # Check for keyword overlap
                    query_words = set(query_lower.split())
                    provision_words = set(provision_text.split())
                    overlap = len(query_words.intersection(provision_words))
                    
                    if overlap > 2:  # Arbitrary threshold
                        relevant_provisions.append(provision)
        
        return relevant_provisions
    
    def _group_provisions_by_topic(self, provisions: List[LegalProvision]) -> Dict[str, List[LegalProvision]]:
        """Group provisions by topic for conflict detection"""
        # Simple grouping by section number
        groups = {}
        
        for provision in provisions:
            key = provision.section_number or 'general'
            if key not in groups:
                groups[key] = []
            groups[key].append(provision)
        
        return groups
    
    def _calculate_query_confidence(self, provisions: List[LegalProvision], resolutions: List[ConflictResolution]) -> float:
        """Calculate confidence score for query result"""
        if not provisions:
            return 0.0
        
        if resolutions:
            return max(r.confidence_score for r in resolutions)
        
        return 0.7  # Default confidence for direct match
    
    def _get_entity_distribution(self, entities: List[LegalEntity]) -> Dict[str, int]:
        """Get distribution of entity types"""
        distribution = {}
        for entity in entities:
            entity_type = entity.entity_type if hasattr(entity, 'entity_type') else 'unknown'
            distribution[entity_type] = distribution.get(entity_type, 0) + 1
        return distribution
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    """Test Phase 2 Integrated System"""
    system = Phase2IntegratedSystem()
    
    print("🎯 Phase 2 Integrated System Test")
    print("=" * 50)
    
    # Test query processing
    test_query = "আয়কর আইন ২০২৩ এর ধারা ১৬৩ অনুযায়ী ন্যূনতম কর কত?"
    
    # For testing, add some mock processed documents
    system.processed_documents['test_doc'] = {
        'entities': [
            LegalEntity(
                entity_type="sections",
                text="ধারা ১৬৩", 
                normalized_form="ধারা 163",
                confidence=0.9,
                context="আয়কর আইন ২০২৩ এর ধারা ১৬৩ অনুযায়ী ন্যূনতম কর প্রযোজ্য।",
                document_source="income-tax-act-2023"
            )
        ],
        'provisions': [
            LegalProvision(
                provision_id="ita_2023_163",
                text="আয়কর আইন ২০২৩ এর ধারা ১৬৩ অনুযায়ী ন্যূনতম কর প্রযোজ্য।",
                document_type="income_tax_act",
                authority_level=95,
                section_number="163"
            )
        ]
    }
    
    result = system.query_legal_provision(test_query)
    
    print(f"Query: {result['query_text']}")
    print(f"Extracted Entities: {len(result['extracted_entities'])}")
    print(f"Relevant Provisions: {len(result['relevant_provisions'])}")
    print(f"Conflicts Detected: {result['conflicts_detected']}")
    print(f"Query Confidence: {result['query_metadata']['confidence_score']:.2f}")
    
    if result['primary_answer']:
        print(f"Primary Answer: {result['primary_answer'].text}")
    
    # Test export functionality
    output_dir = Path(__file__).parent / "phase_2_export"
    system.export_complete_system(str(output_dir))
    
    print(f"\nSystem exported to: {output_dir}")
    print("\n✅ Phase 2 Integration Test Complete")

if __name__ == "__main__":
    main()