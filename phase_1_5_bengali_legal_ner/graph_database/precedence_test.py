#!/usr/bin/env python3
"""
Precedence Engine Test with Real Legal Conflicts
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Set
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph_database.precedence_engine import LegalPrecedenceEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_legal_graph():
    """Create a test legal graph with potential conflicts"""
    
    logger.info("📋 Creating test legal graph with conflicts...")
    
    test_graph_data = {
        "metadata": {
            "export_date": datetime.now().isoformat(),
            "graph_version": "2.0",
            "phase": "Phase 2.3 Test"
        },
        "statistics": {
            "total_nodes": 8,
            "total_edges": 2,
            "node_type_distribution": {
                "DOCUMENT_NODE": 2,
                "ACT_NODE": 2,
                "SECTION_NODE": 2,
                "RULE_NODE": 2
            }
        },
        "nodes": [
            # Document 1: Income Tax Act 2023
            {
                "id": "income_tax_act_2023",
                "type": "DOCUMENT_NODE", 
                "properties": {
                    "title": "আয়কর আইন ২০২৩",
                    "type": "act",
                    "date": "2023-07-01",
                    "authority": "জাতীয় রাজস্ব বোর্ড",
                    "language": "bengali"
                }
            },
            
            # Act Node 1
            {
                "id": "act_income_tax_2023",
                "type": "ACT_NODE",
                "properties": {
                    "text": "আয়কর আইন ২০২৩ অনুসারে ব্যক্তি করদাতার আয় ৫০,০০০ টাকার বেশি হলে ১৫ শতাংশ কর প্রযোজ্য",
                    "title": "আয়কর আইন ২০২৩",
                    "year": "2023",
                    "document_id": "income_tax_act_2023",
                    "entity_type": "ACT",
                    "date": "2023-07-01"
                }
            },
            
            # Section under Act 1
            {
                "id": "section_163_income_tax",
                "type": "SECTION_NODE",
                "properties": {
                    "text": "ধারা ১৬৩: ব্যক্তি করদাতার আয় ৫০,০০০ টাকার বেশি হলে ১৫ শতাংশ কর প্রযোজ্য হবে",
                    "section_number": "163",
                    "title": "কর নির্ধারণ",
                    "document_id": "income_tax_act_2023",
                    "entity_type": "SECTION"
                }
            },
            
            # Document 2: Income Tax Rules 2024
            {
                "id": "income_tax_rules_2024",
                "type": "DOCUMENT_NODE",
                "properties": {
                    "title": "আয়কর বিধিমালা ২০২৪", 
                    "type": "rules",
                    "date": "2024-01-01",
                    "authority": "জাতীয় রাজস্ব বোর্ড",
                    "language": "bengali"
                }
            },
            
            # Rule Node 1 - CONFLICTING with Act
            {
                "id": "rule_25_income_tax",
                "type": "RULE_NODE",
                "properties": {
                    "text": "বিধি ২৫: ব্যক্তি করদাতার আয় ৫০,০০০ টাকার বেশি হলে ২০ শতাংশ কর প্রযোজ্য হবে। তবে এই বিধি আইনের বিপরীত নয়।",
                    "rule_number": "25", 
                    "title": "কর হার নির্ধারণ",
                    "document_id": "income_tax_rules_2024",
                    "entity_type": "RULE",
                    "date": "2024-01-01"
                }
            },
            
            # Section with temporal conflict
            {
                "id": "section_164_amended",
                "type": "SECTION_NODE", 
                "properties": {
                    "text": "ধারা ১৬৪ (সংশোধিত): ব্যক্তি করদাতার আয় ৫০,০০০ টাকার বেশি হলে ১৮ শতাংশ কর প্রযোজ্য। এই ধারা পূর্বের বিধান রহিত করে।",
                    "section_number": "164",
                    "title": "সংশোধিত কর নির্ধারণ",
                    "document_id": "income_tax_act_2023",
                    "entity_type": "SECTION",
                    "date": "2024-06-01"  # Later date
                }
            },
            
            # Act Node 2 - Different Act with overlapping provision
            {
                "id": "act_vat_2012",
                "type": "ACT_NODE",
                "properties": {
                    "text": "মূল্য সংযোজন কর আইন ২০১২: ব্যক্তি করদাতার বিক্রয় আয় ৫০,০০০ টাকার বেশি হলে ১৫ শতাংশ ভ্যাট প্রযোজ্য",
                    "title": "মূল্য সংযোজন কর আইন ২০১২",
                    "year": "2012", 
                    "document_id": "vat_act_2012",
                    "entity_type": "ACT",
                    "date": "2012-07-01"
                }
            },
            
            # Rule with scope differentiation
            {
                "id": "rule_special_case",
                "type": "RULE_NODE",
                "properties": {
                    "text": "বিশেষ বিধি: যদি করদাতা রপ্তানিকারক হয় তাহলে আয়ের উপর মাত্র ১০ শতাংশ কর প্রযোজ্য। শর্ত সাপেক্ষে এই হার কার্যকর।",
                    "rule_number": "special",
                    "title": "রপ্তানিকারক বিশেষ সুবিধা",
                    "document_id": "income_tax_rules_2024", 
                    "entity_type": "RULE"
                }
            }
        ],
        "edges": [
            {
                "source": "income_tax_act_2023",
                "target": "act_income_tax_2023",
                "type": "CONTAINS",
                "weight": 1.0,
                "properties": {"containment_type": "act"}
            },
            {
                "source": "income_tax_rules_2024", 
                "target": "rule_25_income_tax",
                "type": "CONTAINS",
                "weight": 1.0,
                "properties": {"containment_type": "rule"}
            }
        ]
    }
    
    # Save test graph
    with open("bengali_legal_knowledge_graph.json", 'w', encoding='utf-8') as f:
        json.dump(test_graph_data, f, ensure_ascii=False, indent=2)
    
    logger.info("✅ Test legal graph created with potential conflicts")
    
    return test_graph_data

def main():
    """Main test execution"""
    logger.info("🚀 Phase 2.3: Precedence Engine Test")
    logger.info("=" * 60)
    
    try:
        # Create test graph with conflicts
        test_data = create_test_legal_graph()
        
        # Initialize precedence engine with test data
        engine = LegalPrecedenceEngine()
        
        # Generate comprehensive precedence report
        final_report = engine.generate_precedence_report()
        
        logger.info("=" * 60)
        logger.info("✅ Phase 2.3: Precedence Engine Test COMPLETE")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   🔍 Conflicts detected: {final_report['system_performance']['conflicts_detected']}")
        logger.info(f"   ✅ Conflicts resolved: {final_report['system_performance']['conflicts_resolved']}")
        logger.info(f"   📈 Resolution rate: {final_report['system_performance']['resolution_rate']:.1%}")
        logger.info(f"   🔗 Precedence edges: {final_report['system_performance']['precedence_edges_created']}")
        
        # Display detailed conflict analysis
        if final_report['conflict_analysis']['detected_conflicts']:
            logger.info("\n🔍 Detected Conflicts:")
            for i, conflict in enumerate(final_report['conflict_analysis']['detected_conflicts'][:3], 1):
                logger.info(f"   {i}. {conflict['entity1_id']} vs {conflict['entity2_id']}")
                logger.info(f"      Type: {conflict['conflict_type']}")
                logger.info(f"      Indicators: {conflict['conflict_indicators'][:2]}")
        
        # Display resolution results
        if final_report['resolution_results']['resolved_conflicts']:
            logger.info("\n✅ Conflict Resolutions:")
            for i, resolution in enumerate(final_report['resolution_results']['resolved_conflicts'][:3], 1):
                if resolution.get('winning_entity'):
                    logger.info(f"   {i}. Winner: {resolution['winning_entity']}")
                    logger.info(f"      Method: {resolution['resolution_method']}")
                    logger.info(f"      Reasoning: {resolution['reasoning'][:60]}...")
        
        # Close database
        engine.graph_db.close_database()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Precedence engine test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())