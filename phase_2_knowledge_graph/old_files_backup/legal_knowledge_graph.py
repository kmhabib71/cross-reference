#!/usr/bin/env python3
"""
Legal Knowledge Graph Constructor for Phase 2 - Task 2.2
========================================================

Build comprehensive relationship graph for Bangladesh tax laws using NetworkX.
Future: Can be migrated to Neo4j for production scalability.

Graph Structure:
- Document nodes (Act, Schedule, Rule, Circular)  
- Section nodes (individual provisions)
- Concept nodes (tax rates, exemptions, procedures)

Relationship Types:
- REFERENCES (ধারা ১৬ৃ references তফসিল ৪)
- OVERRIDES (Finance Ordinance overrides Income Tax Act)  
- IMPLEMENTS (Rules implement Act provisions)
- MODIFIES (Circulars modify interpretation)

Author: Phase 2 Implementation
Date: August 10, 2025  
"""

import json
import logging
import networkx as nx
try:
    import matplotlib.pyplot as plt
    PLOT_AVAILABLE = True
except (ImportError, AttributeError) as e:
    PLOT_AVAILABLE = False
    plt = None
    print(f"⚠️ Plotting disabled in legal_knowledge_graph due to: {e}")
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
import re

from legal_entity_extractor import LegalEntityExtractor, LegalEntity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GraphNode:
    """Structured graph node with metadata"""
    node_id: str
    node_type: str  # document, section, concept
    title: str
    content: Optional[str]
    metadata: Dict[str, Any]
    authority_level: int = 50  # 1-100, higher = more authoritative

@dataclass
class GraphRelationship:
    """Structured graph relationship with metadata"""
    source_id: str
    target_id: str
    relationship_type: str  # REFERENCES, OVERRIDES, IMPLEMENTS, MODIFIES
    strength: float = 1.0  # 0.0-1.0, confidence of relationship
    context: Optional[str] = None
    metadata: Dict[str, Any] = None

class LegalKnowledgeGraph:
    """
    Comprehensive legal knowledge graph for Bangladesh tax laws.
    
    Features:
    - Multi-layered graph structure (documents, sections, concepts)
    - Cross-reference relationship mapping
    - Authority hierarchy enforcement  
    - Semantic relationship scoring
    - Query processing and path finding
    - Export/import capabilities
    """
    
    def __init__(self):
        """Initialize knowledge graph with NetworkX backend"""
        self.graph = nx.MultiDiGraph()  # Allow multiple edges between nodes
        self.entity_extractor = LegalEntityExtractor()
        self.nodes: Dict[str, GraphNode] = {}
        self.relationships: List[GraphRelationship] = []
        
        # Authority levels for document types
        self.authority_hierarchy = {
            'finance_ordinance': 100,
            'income_tax_act': 95,
            'schedules': 90,
            'tds_rules': 85,
            'circulars': 70,
            'sro_orders': 80
        }
        
        logger.info("Legal Knowledge Graph initialized")
    
    def build_graph_from_documents(self, document_paths: List[str]) -> None:
        """
        Build knowledge graph from list of legal document JSON files
        
        Args:
            document_paths: List of paths to legal document JSON files
        """
        logger.info(f"Building graph from {len(document_paths)} documents")
        
        # Phase 1: Extract entities from all documents
        all_entities = []
        for doc_path in document_paths:
            entities = self._extract_entities_from_document(doc_path)
            all_entities.extend(entities)
        
        # Phase 2: Create document and section nodes
        self._create_document_nodes(document_paths)
        self._create_entity_nodes(all_entities)
        
        # Phase 3: Detect and create relationships
        self._detect_relationships(all_entities)
        
        # Phase 4: Build NetworkX graph
        self._build_networkx_graph()
        
        logger.info(f"Graph construction complete: {len(self.nodes)} nodes, {len(self.relationships)} relationships")
    
    def _extract_entities_from_document(self, doc_path: str) -> List[LegalEntity]:
        """Extract entities from single document JSON file"""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
            
            # Extract text content from JSON structure
            text_content = self._extract_text_from_json(doc_data)
            document_name = Path(doc_path).stem
            
            # Use entity extractor
            entities = self.entity_extractor.extract_entities(text_content, document_name)
            
            logger.info(f"Extracted {len(entities)} entities from {document_name}")
            return entities
            
        except Exception as e:
            logger.error(f"Failed to extract entities from {doc_path}: {e}")
            return []
    
    def _extract_text_from_json(self, json_data: Dict) -> str:
        """Recursively extract text content from JSON structure"""
        text_parts = []
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['content', 'text', 'description', 'title', 'provision']:
                        if isinstance(value, str):
                            text_parts.append(value)
                    else:
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
            elif isinstance(obj, str) and len(obj) > 20:  # Only meaningful text
                text_parts.append(obj)
        
        extract_recursive(json_data)
        return ' '.join(text_parts)
    
    def _create_document_nodes(self, document_paths: List[str]) -> None:
        """Create document-level nodes"""
        for doc_path in document_paths:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)
                
                document_name = Path(doc_path).stem
                doc_type = self._classify_document_type(document_name)
                
                # Create document node
                doc_node = GraphNode(
                    node_id=f"doc_{document_name}",
                    node_type="document", 
                    title=doc_data.get('title', document_name),
                    content=self._extract_text_from_json(doc_data),
                    authority_level=self.authority_hierarchy.get(doc_type, 50),
                    metadata={
                        'document_type': doc_type,
                        'file_path': doc_path,
                        'sections_count': self._count_sections(doc_data)
                    }
                )
                
                self.nodes[doc_node.node_id] = doc_node
                
            except Exception as e:
                logger.error(f"Failed to create document node for {doc_path}: {e}")
    
    def _classify_document_type(self, document_name: str) -> str:
        """Classify document type based on filename"""
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
        elif 'sro' in name_lower or 'এসআরও' in name_lower:
            return 'sro_orders'
        else:
            return 'other'
    
    def _count_sections(self, doc_data: Dict) -> int:
        """Count sections in document"""
        section_count = 0
        
        def count_recursive(obj):
            nonlocal section_count
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if 'section' in key.lower() or 'ধারা' in key:
                        section_count += 1
                    elif isinstance(value, (dict, list)):
                        count_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_recursive(item)
        
        count_recursive(doc_data)
        return section_count
    
    def _create_entity_nodes(self, entities: List[LegalEntity]) -> None:
        """Create nodes for extracted legal entities"""
        for entity in entities:
            node_id = self._generate_node_id(entity)
            
            # Determine node type
            if entity.entity_type in ['sections', 'SECTION_DIRECT', 'SECTION_INDIRECT']:
                node_type = 'section'
            elif entity.entity_type in ['schedules', 'SCHEDULE_REF']:
                node_type = 'schedule'
            elif entity.entity_type in ['rules']:
                node_type = 'rule'
            else:
                node_type = 'concept'  # amounts, rates, years, etc.
            
            entity_node = GraphNode(
                node_id=node_id,
                node_type=node_type,
                title=entity.text,
                content=entity.context,
                authority_level=self._calculate_entity_authority(entity),
                metadata={
                    'entity_type': entity.entity_type,
                    'normalized_form': entity.normalized_form,
                    'confidence': entity.confidence,
                    'document_source': entity.document_source,
                    'numerical_value': entity.numerical_value
                }
            )
            
            self.nodes[node_id] = entity_node
    
    def _generate_node_id(self, entity: LegalEntity) -> str:
        """Generate unique node ID for entity"""
        # Create consistent ID based on normalized form and type
        clean_text = re.sub(r'[^\w\s]', '', entity.normalized_form.lower())
        clean_text = re.sub(r'\s+', '_', clean_text)
        return f"{entity.entity_type}_{clean_text}_{entity.document_source}"
    
    def _calculate_entity_authority(self, entity: LegalEntity) -> int:
        """Calculate authority level for entity based on source and type"""
        base_authority = 50
        
        # Boost based on document source
        doc_source = entity.document_source.lower()
        for doc_type, authority in self.authority_hierarchy.items():
            if doc_type.replace('_', '-') in doc_source:
                base_authority = authority
                break
        
        # Adjust based on entity type
        if entity.entity_type in ['SECTION_DIRECT', 'sections']:
            base_authority += 5  # Sections are more authoritative
        elif entity.entity_type in ['amounts', 'tax_rates']:
            base_authority += 3  # Specific values are important
        
        return min(100, base_authority)
    
    def _detect_relationships(self, entities: List[LegalEntity]) -> None:
        """Detect relationships between entities"""
        logger.info("Detecting relationships between entities...")
        
        # Group entities by document for intra-document relationships
        entities_by_doc = defaultdict(list)
        for entity in entities:
            entities_by_doc[entity.document_source].append(entity)
        
        # Detect various relationship types
        self._detect_reference_relationships(entities)
        self._detect_override_relationships(entities_by_doc)
        self._detect_implementation_relationships(entities_by_doc)
        self._detect_modification_relationships(entities)
        
        logger.info(f"Detected {len(self.relationships)} relationships")
    
    def _detect_reference_relationships(self, entities: List[LegalEntity]) -> None:
        """Detect REFERENCES relationships (ধারা X references তফসিল Y)"""
        # Look for explicit references in entity contexts
        for entity in entities:
            if entity.entity_type in ['sections', 'SECTION_DIRECT']:
                # Look for schedule references in section context
                schedule_refs = re.findall(r'তফসিল\s*(\d+)', entity.context)
                schedule_refs.extend(re.findall(r'Schedule\s*(\d+)', entity.context))
                
                for schedule_num in schedule_refs:
                    target_id = self._find_schedule_node_id(schedule_num)
                    if target_id:
                        relationship = GraphRelationship(
                            source_id=self._generate_node_id(entity),
                            target_id=target_id,
                            relationship_type="REFERENCES",
                            strength=0.8,
                            context=f"Section references Schedule {schedule_num}",
                            metadata={'reference_type': 'schedule_reference'}
                        )
                        self.relationships.append(relationship)
        
    def _detect_override_relationships(self, entities_by_doc: Dict[str, List[LegalEntity]]) -> None:
        """Detect OVERRIDES relationships (Finance Ordinance overrides Income Tax Act)"""
        # Find documents with override relationships
        finance_docs = []
        income_tax_docs = []
        
        for doc_name, entities in entities_by_doc.items():
            if 'finance' in doc_name.lower() or 'অর্থ' in doc_name:
                finance_docs.extend(entities)
            elif 'income-tax-act' in doc_name.lower():
                income_tax_docs.extend(entities)
        
        # Create override relationships
        for finance_entity in finance_docs:
            for tax_entity in income_tax_docs:
                # Look for similar section numbers or topics
                if self._entities_cover_same_topic(finance_entity, tax_entity):
                    relationship = GraphRelationship(
                        source_id=self._generate_node_id(finance_entity),
                        target_id=self._generate_node_id(tax_entity),
                        relationship_type="OVERRIDES",
                        strength=0.9,
                        context="Finance Ordinance overrides Income Tax Act provision",
                        metadata={'override_type': 'legal_hierarchy'}
                    )
                    self.relationships.append(relationship)
    
    def _detect_implementation_relationships(self, entities_by_doc: Dict[str, List[LegalEntity]]) -> None:
        """Detect IMPLEMENTS relationships (Rules implement Act provisions)"""
        # Find rules and act entities
        rules_entities = []
        act_entities = []
        
        for doc_name, entities in entities_by_doc.items():
            if 'rules' in doc_name.lower() or 'বিধি' in doc_name:
                rules_entities.extend(entities)
            elif 'act' in doc_name.lower() or 'আইন' in doc_name:
                act_entities.extend(entities)
        
        # Create implementation relationships
        for rule_entity in rules_entities:
            for act_entity in act_entities:
                if self._rule_implements_section(rule_entity, act_entity):
                    relationship = GraphRelationship(
                        source_id=self._generate_node_id(rule_entity),
                        target_id=self._generate_node_id(act_entity),
                        relationship_type="IMPLEMENTS",
                        strength=0.7,
                        context="Rule implements Act section",
                        metadata={'implementation_type': 'procedural'}
                    )
                    self.relationships.append(relationship)
    
    def _detect_modification_relationships(self, entities: List[LegalEntity]) -> None:
        """Detect MODIFIES relationships (Circulars modify interpretation)"""
        circular_entities = [e for e in entities if 'circular' in e.document_source.lower()]
        other_entities = [e for e in entities if 'circular' not in e.document_source.lower()]
        
        for circular_entity in circular_entities:
            for other_entity in other_entities:
                if self._circular_modifies_provision(circular_entity, other_entity):
                    relationship = GraphRelationship(
                        source_id=self._generate_node_id(circular_entity),
                        target_id=self._generate_node_id(other_entity),
                        relationship_type="MODIFIES",
                        strength=0.6,
                        context="Circular modifies provision interpretation",
                        metadata={'modification_type': 'interpretive'}
                    )
                    self.relationships.append(relationship)
    
    def _build_networkx_graph(self) -> None:
        """Build NetworkX graph from nodes and relationships"""
        # Add nodes
        for node_id, node in self.nodes.items():
            self.graph.add_node(
                node_id, 
                **asdict(node)
            )
        
        # Add edges (relationships)
        for rel in self.relationships:
            self.graph.add_edge(
                rel.source_id,
                rel.target_id,
                relationship_type=rel.relationship_type,
                strength=rel.strength,
                context=rel.context,
                metadata=rel.metadata
            )
        
        logger.info(f"NetworkX graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
    
    # Utility methods for relationship detection
    def _find_schedule_node_id(self, schedule_num: str) -> Optional[str]:
        """Find node ID for schedule by number"""
        for node_id, node in self.nodes.items():
            if (node.node_type == 'schedule' and 
                (schedule_num in node.title or schedule_num in node.normalized_form)):
                return node_id
        return None
    
    def _entities_cover_same_topic(self, entity1: LegalEntity, entity2: LegalEntity) -> bool:
        """Check if two entities cover the same legal topic"""
        # Simple keyword-based matching
        keywords1 = set(re.findall(r'\w+', entity1.context.lower()))
        keywords2 = set(re.findall(r'\w+', entity2.context.lower()))
        
        overlap = len(keywords1.intersection(keywords2))
        return overlap > 3  # Arbitrary threshold
    
    def _rule_implements_section(self, rule_entity: LegalEntity, act_entity: LegalEntity) -> bool:
        """Check if rule implements act section"""
        # Look for section references in rule context
        section_refs = re.findall(r'ধারা\s*(\d+)|Section\s*(\d+)', rule_entity.context)
        act_sections = re.findall(r'ধারা\s*(\d+)|Section\s*(\d+)', act_entity.text)
        
        # Check for matching section numbers
        rule_sections = {num for match in section_refs for num in match if num}
        entity_sections = {num for match in act_sections for num in match if num}
        
        return bool(rule_sections.intersection(entity_sections))
    
    def _circular_modifies_provision(self, circular_entity: LegalEntity, other_entity: LegalEntity) -> bool:
        """Check if circular modifies other provision"""
        # Look for references to other provisions in circular
        return ('ধারা' in circular_entity.context and 
                'আইন' in circular_entity.context and
                len(circular_entity.context.split()) > 10)
    
    # Query and analysis methods
    def find_related_entities(self, entity_id: str, relationship_types: List[str] = None, max_depth: int = 2) -> List[Dict]:
        """Find entities related to given entity"""
        if entity_id not in self.graph:
            return []
        
        related = []
        
        # BFS to find related entities
        for target in nx.single_source_shortest_path_length(self.graph, entity_id, cutoff=max_depth):
            if target != entity_id:
                # Get relationship info
                try:
                    edge_data = self.graph[entity_id][target]
                    if relationship_types is None or edge_data.get('relationship_type') in relationship_types:
                        related.append({
                            'entity_id': target,
                            'entity_data': self.nodes.get(target),
                            'relationship': edge_data
                        })
                except:
                    pass
        
        return related
    
    def get_authority_chain(self, topic_keywords: List[str]) -> List[GraphNode]:
        """Get authoritative chain for given topic"""
        relevant_nodes = []
        
        for node_id, node in self.nodes.items():
            # Check if node is relevant to topic
            node_text = (node.title + ' ' + (node.content or '')).lower()
            if any(keyword.lower() in node_text for keyword in topic_keywords):
                relevant_nodes.append(node)
        
        # Sort by authority level
        return sorted(relevant_nodes, key=lambda x: x.authority_level, reverse=True)
    
    def export_graph(self, output_path: str, format: str = 'json') -> None:
        """Export graph in various formats"""
        if format == 'json':
            graph_data = {
                'nodes': {node_id: asdict(node) for node_id, node in self.nodes.items()},
                'relationships': [asdict(rel) for rel in self.relationships],
                'metadata': {
                    'total_nodes': len(self.nodes),
                    'total_relationships': len(self.relationships),
                    'node_types': self._get_node_type_distribution(),
                    'relationship_types': self._get_relationship_type_distribution(),
                    'authority_levels': self._get_authority_distribution()
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
        
        elif format == 'graphml':
            nx.write_graphml(self.graph, output_path)
        
        elif format == 'visualization':
            self._create_graph_visualization(output_path)
        
        logger.info(f"Graph exported to {output_path} in {format} format")
    
    def _get_node_type_distribution(self) -> Dict[str, int]:
        """Get distribution of node types"""
        distribution = defaultdict(int)
        for node in self.nodes.values():
            distribution[node.node_type] += 1
        return dict(distribution)
    
    def _get_relationship_type_distribution(self) -> Dict[str, int]:
        """Get distribution of relationship types"""
        distribution = defaultdict(int)
        for rel in self.relationships:
            distribution[rel.relationship_type] += 1
        return dict(distribution)
    
    def _get_authority_distribution(self) -> Dict[str, int]:
        """Get authority level distribution"""
        ranges = {'high (80-100)': 0, 'medium (60-79)': 0, 'low (0-59)': 0}
        
        for node in self.nodes.values():
            if node.authority_level >= 80:
                ranges['high (80-100)'] += 1
            elif node.authority_level >= 60:
                ranges['medium (60-79)'] += 1
            else:
                ranges['low (0-59)'] += 1
        
        return ranges
    
    def _create_graph_visualization(self, output_path: str) -> None:
        """Create graph visualization using matplotlib"""
        if not PLOT_AVAILABLE:
            logger.warning("⚠️ Visualization skipped - matplotlib not available")
            return
        
        plt.figure(figsize=(15, 10))
        
        # Use spring layout for better visualization
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # Draw nodes with different colors for different types
        node_colors = []
        for node_id in self.graph.nodes():
            node = self.nodes.get(node_id)
            if node:
                if node.node_type == 'document':
                    node_colors.append('red')
                elif node.node_type == 'section':
                    node_colors.append('blue')
                elif node.node_type == 'schedule':
                    node_colors.append('green')
                elif node.node_type == 'rule':
                    node_colors.append('orange')
                else:
                    node_colors.append('gray')
            else:
                node_colors.append('gray')
        
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, node_size=100, alpha=0.7)
        nx.draw_networkx_edges(self.graph, pos, alpha=0.5, width=0.5)
        
        plt.title("Bangladesh Legal Knowledge Graph")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

def main():
    """Test the Legal Knowledge Graph system"""
    # Test with sample documents
    graph = LegalKnowledgeGraph()
    
    # For testing, we'll create some mock entities
    test_entities = [
        LegalEntity(
            entity_type="sections",
            text="ধারা ১৬৩",
            normalized_form="ধারা 163",
            confidence=0.9,
            context="আয়কর আইন ২০২৩ এর ধারা ১৬৩ অনুযায়ী ন্যূনতম কর প্রযোজ্য। তফসিল ৪ দেখুন।",
            document_source="income-tax-act-2023"
        ),
        LegalEntity(
            entity_type="schedules", 
            text="তফসিল ৪",
            normalized_form="তফসিল 4",
            confidence=0.85,
            context="চতুর্থ তফসিলে কর হার নির্ধারিত রয়েছে।",
            document_source="income-tax-schedule-4"
        )
    ]
    
    # Create nodes manually for testing
    for entity in test_entities:
        node_id = graph._generate_node_id(entity)
        graph.nodes[node_id] = GraphNode(
            node_id=node_id,
            node_type="section" if "section" in entity.entity_type else "schedule",
            title=entity.text,
            content=entity.context,
            authority_level=95,
            metadata={'test': True}
        )
    
    # Create a test relationship
    if len(graph.nodes) >= 2:
        nodes_list = list(graph.nodes.keys())
        test_relationship = GraphRelationship(
            source_id=nodes_list[0],
            target_id=nodes_list[1], 
            relationship_type="REFERENCES",
            strength=0.8,
            context="Test relationship"
        )
        graph.relationships.append(test_relationship)
    
    # Build graph
    graph._build_networkx_graph()
    
    # Export results
    output_dir = Path(__file__).parent
    graph.export_graph(str(output_dir / "test_knowledge_graph.json"))
    graph.export_graph(str(output_dir / "test_knowledge_graph.png"), format="visualization")
    
    print(f"\n🎯 Knowledge Graph Statistics:")
    print(f"📊 Total Nodes: {len(graph.nodes)}")
    print(f"🔗 Total Relationships: {len(graph.relationships)}")
    print(f"📈 NetworkX Graph: {graph.graph.number_of_nodes()} nodes, {graph.graph.number_of_edges()} edges")
    
    # Test query functionality
    if graph.nodes:
        first_node = list(graph.nodes.keys())[0]
        related = graph.find_related_entities(first_node)
        print(f"🔍 Related entities to {first_node}: {len(related)}")

if __name__ == "__main__":
    main()