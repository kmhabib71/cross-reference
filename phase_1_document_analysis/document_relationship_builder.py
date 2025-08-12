#!/usr/bin/env python3
"""
Document Relationship Database Builder
Phase 1: Document Structure Analysis & Mapping

Creates comprehensive relationship mappings between legal documents
for precision cross-reference system.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentRelationshipBuilder:
    """Build comprehensive relationship mappings between legal documents"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.relationships = {
            'hierarchical': {},  # Authority-based relationships
            'temporal': {},      # Time-based relationships  
            'referential': {},   # Cross-reference relationships
            'semantic': {}       # Content-based relationships
        }
        
        # Load Phase 0 analysis results
        self.phase_0_hierarchy = self._load_phase_0_data()
        
        # Document authority mapping
        self.authority_levels = {
            'finance_ordinance_2025': 100,
            'income_tax_act_2023': 100,
            'schedules': 95,
            'tds_rules': 85,
            'circulars': 70,
            'sro_orders': 80
        }
    
    def _load_phase_0_data(self) -> Dict:
        """Load Phase 0 hierarchy analysis"""
        hierarchy_path = self.base_path / "precision_crossref_system_2025/phase_0_analysis/legal_hierarchy.json"
        try:
            with open(hierarchy_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load Phase 0 data: {e}")
            return {}
    
    def _load_citation_analysis(self) -> Dict:
        """Load citation pattern analysis results"""
        citation_path = self.base_path / "precision_crossref_system_2025/phase_1_structures/citation_patterns_analysis.json"
        try:
            with open(citation_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load citation analysis: {e}")
            return {}
    
    def build_hierarchical_relationships(self) -> Dict:
        """Build authority-based hierarchical relationships"""
        
        hierarchical = {
            'authority_chain': [
                {
                    'level': 1,
                    'authority': 100,
                    'documents': ['finance_ordinance_2025'],
                    'overrides': ['income_tax_act_2023', 'schedules', 'tds_rules', 'circulars'],
                    'effective_period': '2025-07-01 to 2026-06-30'
                },
                {
                    'level': 2, 
                    'authority': 100,
                    'documents': ['income_tax_act_2023'],
                    'overridden_by': ['finance_ordinance_2025'],
                    'contains': ['schedules'],
                    'implemented_by': ['tds_rules'],
                    'interpreted_by': ['circulars']
                },
                {
                    'level': 3,
                    'authority': 95,
                    'documents': ['schedules_1st_8th'],
                    'parent': 'income_tax_act_2023',
                    'referenced_by': ['section_163', 'tds_rules']
                },
                {
                    'level': 4,
                    'authority': 85,
                    'documents': ['tds_rules_2025', 'tds_rules_2024'],
                    'implements': ['income_tax_act_2023'],
                    'temporal_versions': True
                },
                {
                    'level': 5,
                    'authority': 80,
                    'documents': ['sro_orders'],
                    'grants': 'specific_exemptions',
                    'references': ['income_tax_act_2023', 'schedules']
                },
                {
                    'level': 6,
                    'authority': 70,
                    'documents': ['income_tax_circulars'],
                    'interprets': ['income_tax_act_2023'],
                    'guidance_type': 'administrative'
                }
            ],
            'conflict_resolution': {
                'precedence_order': [
                    'finance_ordinance_2025',
                    'income_tax_act_2023', 
                    'schedules',
                    'sro_orders',
                    'tds_rules',
                    'circulars'
                ],
                'resolution_rules': {
                    'same_level_conflict': 'later_date_prevails',
                    'cross_level_conflict': 'higher_authority_prevails',
                    'temporal_conflict': 'current_financial_year_prevails'
                }
            }
        }
        
        return hierarchical
    
    def build_temporal_relationships(self) -> Dict:
        """Build time-based relationships between document versions"""
        
        temporal = {
            'financial_year_versions': {
                '2025-26': {
                    'current': True,
                    'primary_law': 'finance_ordinance_2025',
                    'tax_free_limit': 400000,
                    'active_documents': [
                        'finance_ordinance_2025',
                        'income_tax_act_2023',
                        'tds_rules_2025',
                        'schedules_2025'
                    ]
                },
                '2024-25': {
                    'current': False,
                    'primary_law': 'finance_act_2024',
                    'tax_free_limit': 350000,
                    'superseded_by': '2025-26',
                    'active_documents': [
                        'finance_act_2024',
                        'income_tax_act_2023',
                        'tds_rules_2024'
                    ]
                },
                '2023-24': {
                    'current': False,
                    'primary_law': 'income_tax_act_2023',
                    'tax_free_limit': 350000,
                    'historical': True,
                    'active_documents': [
                        'income_tax_act_2023',
                        'tds_rules_2023'
                    ]
                }
            },
            'version_changes': {
                'section_163_changes': {
                    '2024_to_2025': {
                        'changed_provisions': [
                            'minimum_tax_rates',
                            'exemption_categories',
                            'gross_receipt_thresholds'
                        ],
                        'impact': 'rate_structure_modified'
                    }
                },
                'tds_rule_changes': {
                    '2024_to_2025': {
                        'new_rules': ['rule_6a', 'enhanced_rule_3'],
                        'modified_rates': ['contractors', 'services'],
                        'impact': 'compliance_requirements_updated'
                    }
                }
            },
            'effective_date_mapping': {
                'finance_ordinance_2025': '2025-07-01',
                'tds_rules_2025': '2025-07-01',
                'income_tax_act_2023': '2023-07-01',
                'schedule_updates_2025': '2025-07-01'
            }
        }
        
        return temporal
    
    def build_referential_relationships(self) -> Dict:
        """Build cross-reference relationships using citation analysis"""
        
        citation_data = self._load_citation_analysis()
        
        referential = {
            'cross_references': {},
            'section_networks': {},
            'schedule_dependencies': {},
            'indirect_references': []
        }
        
        # Process citation registry if available
        if 'citation_registry' in citation_data:
            registry = citation_data['citation_registry']
            
            # Build section networks
            for section_key, section_data in registry.get('sections', {}).items():
                referenced_docs = [ref['document'] for ref in section_data.get('referenced_in', [])]
                
                referential['section_networks'][section_key] = {
                    'section_number': section_data.get('section_number'),
                    'primary_act': section_data.get('act_name'),
                    'year': section_data.get('year'),
                    'referenced_in_documents': referenced_docs,
                    'reference_count': len(referenced_docs),
                    'importance_score': len(referenced_docs) * 0.2  # Basic scoring
                }
            
            # Build schedule dependencies
            for schedule_key, schedule_data in registry.get('schedules', {}).items():
                referenced_docs = [ref['document'] for ref in schedule_data.get('referenced_in', [])]
                
                referential['schedule_dependencies'][schedule_key] = {
                    'schedule_number': schedule_data.get('schedule_number'),
                    'referenced_in_documents': referenced_docs,
                    'dependency_strength': len(referenced_docs)
                }
            
            # Store indirect references for resolution
            referential['indirect_references'] = registry.get('indirect_references', [])
        
        # Add specific high-importance relationships
        referential['critical_relationships'] = {
            'section_163_network': {
                'primary_section': 'income_tax_act_2023_s163',
                'related_sections': ['88', '89', '90', '91', '92', '94', '95', '100-102', '105', '106', '108', '110-118', '120-129', '132-139'],
                'related_schedules': ['4th'],
                'implementing_rules': ['tds_rules'],
                'modifying_ordinances': ['finance_ordinance_2025'],
                'relationship_type': 'minimum_tax_calculation'
            },
            'schedule_4_network': {
                'primary_schedule': '4th_schedule',
                'related_sections': ['163', '76', '77', '78'],
                'document_type': 'tax_exemptions',
                'dependency_type': 'bidirectional'
            }
        }
        
        return referential
    
    def build_semantic_relationships(self) -> Dict:
        """Build content-based semantic relationships"""
        
        semantic = {
            'topic_clusters': {
                'minimum_tax': {
                    'primary_documents': ['section_163_minimum_tax', 'finance_ordinance_2025'],
                    'supporting_documents': ['schedules_bangla', 'tds_rules_2025'],
                    'key_concepts': ['ন্যূনতম কর', 'minimum tax', 'gross receipt', 'গ্রস প্রাপ্তি'],
                    'related_topics': ['tax_calculation', 'exemptions', 'tds']
                },
                'tax_deduction_source': {
                    'primary_documents': ['tds_rules_2025', 'income_tax_act_bangla'],
                    'supporting_documents': ['section_163_minimum_tax'],
                    'key_concepts': ['উৎসে কর কর্তন', 'tax deduction at source', 'withholding tax'],
                    'related_topics': ['minimum_tax', 'contractors', 'services']
                },
                'tax_exemptions': {
                    'primary_documents': ['schedules_bangla', 'schedules_english'],
                    'supporting_documents': ['finance_ordinance_2025'],
                    'key_concepts': ['কর অব্যাহতি', 'tax exemption', 'tax holiday'],
                    'related_topics': ['minimum_tax', 'investment_incentives']
                }
            },
            'concept_relationships': {
                'minimum_tax_concepts': {
                    'core_concept': 'ন্যূনতম কর (minimum tax)',
                    'related_concepts': [
                        'গ্রস প্রাপ্তি (gross receipt)',
                        'কর অব্যাহতি (tax exemption)', 
                        'উৎসে কর কর্তন (tax deduction at source)',
                        'তফসিল (schedule)',
                        'অর্থবছর (financial year)'
                    ],
                    'calculation_dependencies': ['section_163', 'schedule_4', 'tds_rules']
                }
            },
            'language_mappings': {
                'section_references': {
                    'bengali': ['ধারা', 'অনুচ্ছেদ'],
                    'english': ['section', 'sec', 'clause'],
                    'numerical': ['163', '১৬৩', 'একশত তেষট্টি']
                },
                'schedule_references': {
                    'bengali': ['তফসিল', 'তফসিল'],
                    'english': ['schedule', 'sch'],
                    'numerical': ['4', '৪', 'চতুর্থ', '4th', 'fourth']
                }
            }
        }
        
        return semantic
    
    def generate_relationship_database(self) -> Dict:
        """Generate comprehensive relationship database"""
        
        logger.info("Building hierarchical relationships...")
        hierarchical = self.build_hierarchical_relationships()
        
        logger.info("Building temporal relationships...")
        temporal = self.build_temporal_relationships()
        
        logger.info("Building referential relationships...")
        referential = self.build_referential_relationships()
        
        logger.info("Building semantic relationships...")
        semantic = self.build_semantic_relationships()
        
        # Compile comprehensive database
        relationship_db = {
            'metadata': {
                'created_date': '2025-01-15',
                'phase': 'Phase_1_Document_Structure_Analysis',
                'version': '1.0',
                'total_documents_analyzed': 7,
                'relationship_types': 4
            },
            'hierarchical_relationships': hierarchical,
            'temporal_relationships': temporal, 
            'referential_relationships': referential,
            'semantic_relationships': semantic,
            'integration_points': self._build_integration_points(hierarchical, temporal, referential, semantic),
            'validation_rules': self._generate_validation_rules()
        }
        
        return relationship_db
    
    def _build_integration_points(self, hierarchical: Dict, temporal: Dict, referential: Dict, semantic: Dict) -> Dict:
        """Build integration points between different relationship types"""
        
        return {
            'section_163_integration': {
                'hierarchical_context': 'income_tax_act_2023_section',
                'temporal_context': 'modified_by_finance_ordinance_2025',
                'referential_context': 'references_multiple_sections_and_schedules',
                'semantic_context': 'minimum_tax_calculation_cluster',
                'integration_complexity': 'high'
            },
            'schedule_4_integration': {
                'hierarchical_context': 'part_of_income_tax_act_2023',
                'temporal_context': 'updated_annually',
                'referential_context': 'referenced_by_section_163',
                'semantic_context': 'tax_exemptions_cluster',
                'integration_complexity': 'medium'
            },
            'tds_rules_integration': {
                'hierarchical_context': 'implements_income_tax_act',
                'temporal_context': 'financial_year_specific',
                'referential_context': 'implements_sections_88_to_139',
                'semantic_context': 'tax_deduction_source_cluster',
                'integration_complexity': 'high'
            }
        }
    
    def _generate_validation_rules(self) -> Dict:
        """Generate validation rules for relationship consistency"""
        
        return {
            'hierarchical_validation': {
                'authority_consistency': 'higher_authority_must_override_lower',
                'circular_dependency_check': 'no_document_can_override_itself',
                'temporal_authority_check': 'current_law_takes_precedence'
            },
            'temporal_validation': {
                'date_consistency': 'effective_dates_must_be_sequential',
                'version_completeness': 'all_current_versions_must_exist',
                'supersession_logic': 'superseded_documents_marked_inactive'
            },
            'referential_validation': {
                'reference_resolution': 'all_references_must_resolve_to_valid_targets',
                'circular_reference_check': 'detect_and_flag_circular_references',
                'broken_link_detection': 'identify_references_to_non_existent_sections'
            },
            'semantic_validation': {
                'concept_consistency': 'related_concepts_must_be_coherent',
                'language_mapping_accuracy': 'bengali_english_mappings_verified',
                'topic_cluster_integrity': 'topic_clusters_must_have_coherent_boundaries'
            }
        }
    
    def run_analysis(self) -> Dict:
        """Run complete document relationship analysis"""
        logger.info("Starting document relationship database construction...")
        
        relationship_db = self.generate_relationship_database()
        
        logger.info("Document relationship database construction complete!")
        return relationship_db

def main():
    """Main execution function"""
    base_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap"
    
    builder = DocumentRelationshipBuilder(base_path)
    results = builder.run_analysis()
    
    # Save results
    output_path = Path(base_path) / "precision_crossref_system_2025/phase_1_structures/document_relationships.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ Document relationship database complete!")
    print(f"📊 Results saved to: {output_path}")
    print(f"🔗 Built {len(results['integration_points'])} integration points")
    print(f"📈 Analyzed {results['metadata']['total_documents_analyzed']} documents with {results['metadata']['relationship_types']} relationship types")

if __name__ == "__main__":
    main()