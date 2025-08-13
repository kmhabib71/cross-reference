#!/usr/bin/env python3
"""
Enhanced Graph Builder - Create Rich Legal Knowledge Graph
Build a comprehensive legal knowledge graph with meaningful relationships
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Set
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph_database.graph_database_setup import LegalKnowledgeGraphDatabase
from graph_database.knowledge_graph_builder import KnowledgeGraphBuilder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_comprehensive_legal_dataset() -> List[Dict[str, Any]]:
    """Create comprehensive legal dataset with diverse entities"""
    
    return [
        # Document 1: Income Tax Act 2023
        {
            "document_id": "income_tax_act_2023",
            "text": "আয়কর আইন ২০২৩ এর ধারা ১৬৩ অনুসারে ব্যক্তি করদাতার আয় ৫০,০০০ টাকার বেশি হলে ১৫ শতাংশ কর প্রযোজ্য হবে। এই আইনটি জাতীয় রাজস্ব বোর্ড কর্তৃক প্রয়োগ করা হয়।",
            "entities": [
                (0, 15, "ACT"),
                (19, 27, "SECTION"),
                (36, 49, "TAXPAYER"),
                (56, 66, "AMOUNT"),
                (79, 87, "PERCENTAGE"),
                (110, 126, "AUTHORITY")
            ]
        },
        
        # Document 2: Income Tax Rules 2024
        {
            "document_id": "income_tax_rules_2024", 
            "text": "আয়কর বিধিমালা ২০২৪ এর বিধি ২৫ অনুযায়ী আয়কর আইন ২০২৩ এর বাস্তবায়নের জন্য ব্যক্তি করদাতার আয়ের ২০ শতাংশ কর প্রযোজ্য হবে। তবে এই হার আইনের বিপরীত নয়।",
            "entities": [
                (0, 18, "RULE"),
                (22, 29, "SECTION"),
                (38, 53, "ACT"),
                (57, 66, "IMPLEMENTS"),
                (75, 88, "TAXPAYER"),
                (96, 104, "PERCENTAGE"),
                (132, 138, "OVERRIDE")
            ]
        },
        
        # Document 3: VAT Act 2012
        {
            "document_id": "vat_act_2012",
            "text": "মূল্য সংযোজন কর আইন ২০১২ এর ধারা ৫০ অনুসারে বিক্রয়ের উপর ১৫ শতাংশ ভ্যাট প্রযোজ্য। এই আইন আয়কর আইনের সাথে সংযুক্ত কিন্তু আলাদা প্রয়োগক্ষেত্র রয়েছে।",
            "entities": [
                (0, 24, "ACT"),
                (28, 35, "SECTION"),
                (44, 49, "CONCEPT"),
                (57, 65, "PERCENTAGE"),
                (66, 70, "CONCEPT"),
                (88, 97, "ACT"),
                (105, 111, "REFERENCE")
            ]
        },
        
        # Document 4: Customs Act 1969 
        {
            "document_id": "customs_act_1969",
            "text": "শুল্ক আইন ১৯৬৯ এর তফসিল ১ অনুযায়ী আমদানি শুল্ক নির্ধারণ করা হয়। এই আইন মূল্য সংযোজন কর আইনের সাথে সামঞ্জস্যপূর্ণ এবং জাতীয় রাজস্ব বোর্ড কর্তৃক নিয়ন্ত্রিত।",
            "entities": [
                (0, 14, "ACT"),
                (18, 25, "SCHEDULE"),
                (34, 46, "CONCEPT"),
                (63, 82, "ACT"),
                (90, 102, "REFERENCE"),
                (107, 123, "AUTHORITY")
            ]
        },
        
        # Document 5: Tax Tribunal Rules
        {
            "document_id": "tax_tribunal_rules_2020",
            "text": "কর ট্রাইব্যুনাল বিধিমালা ২০২০ এর বিধি ১২ অনুযায়ী আয়কর, ভ্যাট ও শুল্ক সংক্রান্ত বিরোধ নিষ্পত্তি করা হয়। এই বিধি সংবিধানের ১০৭ অনুচ্ছেদের অধীনে প্রণীত।",
            "entities": [
                (0, 27, "RULE"),
                (31, 38, "SECTION"),
                (47, 52, "CONCEPT"),
                (54, 58, "CONCEPT"),
                (61, 65, "CONCEPT"),
                (75, 87, "CONCEPT"),
                (101, 108, "ACT"),
                (112, 123, "SECTION")
            ]
        }
    ]

def main():
    """Main execution function"""
    logger.info("🚀 Enhanced Graph Builder - Creating Rich Legal Knowledge Graph")
    logger.info("=" * 70)
    
    try:
        # Initialize knowledge graph builder
        builder = KnowledgeGraphBuilder()
        
        # Create comprehensive dataset
        comprehensive_dataset = create_comprehensive_legal_dataset()
        logger.info(f"📋 Created {len(comprehensive_dataset)} comprehensive legal documents")
        
        # Build knowledge graph from comprehensive NER data
        build_result = builder.build_knowledge_graph_from_ner(comprehensive_dataset)
        
        # Get final statistics
        summary = builder.get_graph_summary()
        
        # Save enhanced results
        enhanced_results = {
            "enhancement_date": datetime.now().isoformat(),
            "phase": "Phase 2 Enhancement - Rich Legal Knowledge Graph",
            "build_result": build_result,
            "final_summary": summary,
            "dataset_characteristics": {
                "documents_processed": len(comprehensive_dataset),
                "entity_types_covered": ["ACT", "RULE", "SECTION", "SCHEDULE", "CONCEPT", "TAXPAYER", "AMOUNT", "PERCENTAGE", "AUTHORITY"],
                "relationship_types": ["IMPLEMENTS", "OVERRIDE", "REFERENCE"],
                "legal_domains": ["Income Tax", "VAT", "Customs", "Tax Tribunals", "Constitutional Law"]
            }
        }
        
        with open("enhanced_graph_results.json", 'w', encoding='utf-8') as f:
            json.dump(enhanced_results, f, ensure_ascii=False, indent=2)
        
        logger.info("=" * 70)
        logger.info("✅ Enhanced Graph Builder COMPLETE")
        logger.info(f"📊 Enhanced Statistics:")
        logger.info(f"   📝 Total nodes: {summary['graph_statistics']['total_nodes']}")
        logger.info(f"   🔗 Total edges: {summary['graph_statistics']['total_edges']}")
        logger.info(f"   📋 Documents processed: {build_result['documents_processed']}")
        logger.info(f"   🏥 Build status: {build_result['build_status']}")
        
        # Export enhanced graph
        builder.graph_db.export_graph_to_json("enhanced_bengali_legal_knowledge_graph.json")
        
        # Close database
        builder.graph_db.close_database()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Enhanced graph building failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())