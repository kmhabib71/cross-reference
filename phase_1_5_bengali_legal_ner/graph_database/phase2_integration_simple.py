#!/usr/bin/env python3
"""
Phase 2 Simple Integration Test - Verify All Components Work
Quick verification that all Phase 2 components can be imported and have generated their outputs
"""

import json
import sys
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Simple integration test for Phase 2 components"""
    logger.info("🚀 Phase 2: Simple Integration Test")
    logger.info("=" * 60)
    
    integration_results = {
        "test_date": datetime.now().isoformat(),
        "phase": "Phase 2: Legal Knowledge Graph Construction", 
        "components_verified": [],
        "files_present": [],
        "components_functional": 0,
        "total_components": 6,
        "integration_status": "UNKNOWN"
    }
    
    try:
        # Test 1: Verify core components can be imported
        logger.info("🔧 Testing component imports...")
        
        import_success = 0
        components = [
            "graph_database_setup",
            "knowledge_graph_builder", 
            "relationship_engine",
            "graph_validator",
            "precedence_engine",
            "hierarchy_engine"
        ]
        
        for component in components:
            try:
                __import__(component)
                import_success += 1
                integration_results["components_verified"].append(component)
                logger.info(f"   ✅ {component}")
            except Exception as e:
                logger.error(f"   ❌ {component}: {str(e)}")
        
        # Test 2: Verify output files exist
        logger.info("📁 Testing output files...")
        
        expected_files = [
            "bengali_legal_knowledge_graph.json",
            "bengali_legal_knowledge_graph.db",
            "relationship_analysis_report.json", 
            "comprehensive_graph_validation_report.json",
            "precedence_analysis_report.json",
            "hierarchy_analysis_report.json"
        ]
        
        files_found = 0
        for filename in expected_files:
            if os.path.exists(filename):
                files_found += 1
                integration_results["files_present"].append(filename)
                logger.info(f"   ✅ {filename}")
            else:
                logger.info(f"   ⚠️ {filename} (not found)")
        
        # Test 3: Verify data integrity
        logger.info("📊 Testing data integrity...")
        
        data_integrity_score = 0.0
        
        # Check graph data
        if os.path.exists("bengali_legal_knowledge_graph.json"):
            try:
                with open("bengali_legal_knowledge_graph.json", 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
                
                nodes = len(graph_data.get("nodes", []))
                edges = len(graph_data.get("edges", []))
                
                if nodes > 0 and edges > 0:
                    data_integrity_score += 0.2
                    logger.info(f"   ✅ Graph data: {nodes} nodes, {edges} edges")
                else:
                    logger.info(f"   ⚠️ Graph data: {nodes} nodes, {edges} edges")
                    
            except Exception as e:
                logger.error(f"   ❌ Graph data validation failed: {str(e)}")
        
        # Check relationship report
        if os.path.exists("relationship_analysis_report.json"):
            try:
                with open("relationship_analysis_report.json", 'r', encoding='utf-8') as f:
                    rel_data = json.load(f)
                
                relationships = rel_data.get("relationship_results", {}).get("total_relationships", 0)
                if relationships > 0:
                    data_integrity_score += 0.2
                    logger.info(f"   ✅ Relationships: {relationships}")
                else:
                    logger.info(f"   ⚠️ Relationships: {relationships}")
                    
            except Exception as e:
                logger.error(f"   ❌ Relationship data validation failed: {str(e)}")
        
        # Check validation report
        if os.path.exists("comprehensive_graph_validation_report.json"):
            try:
                with open("comprehensive_graph_validation_report.json", 'r', encoding='utf-8') as f:
                    val_data = json.load(f)
                
                score = val_data.get("overall_score", 0)
                if score >= 60:
                    data_integrity_score += 0.2
                    logger.info(f"   ✅ Validation score: {score}/100")
                else:
                    logger.info(f"   ⚠️ Validation score: {score}/100")
                    
            except Exception as e:
                logger.error(f"   ❌ Validation data validation failed: {str(e)}")
        
        # Check precedence report
        if os.path.exists("precedence_analysis_report.json"):
            try:
                with open("precedence_analysis_report.json", 'r', encoding='utf-8') as f:
                    prec_data = json.load(f)
                
                conflicts = prec_data.get("system_performance", {}).get("conflicts_detected", 0)
                resolution_rate = prec_data.get("system_performance", {}).get("resolution_rate", 0.0)
                
                if conflicts > 0 and resolution_rate >= 0.8:
                    data_integrity_score += 0.2
                    logger.info(f"   ✅ Precedence: {conflicts} conflicts, {resolution_rate:.1%} resolved")
                else:
                    logger.info(f"   ⚠️ Precedence: {conflicts} conflicts, {resolution_rate:.1%} resolved")
                    
            except Exception as e:
                logger.error(f"   ❌ Precedence data validation failed: {str(e)}")
        
        # Check hierarchy report
        if os.path.exists("hierarchy_analysis_report.json"):
            try:
                with open("hierarchy_analysis_report.json", 'r', encoding='utf-8') as f:
                    hier_data = json.load(f)
                
                entities = hier_data.get("system_performance", {}).get("entities_classified", 0)
                integrity = hier_data.get("validation_results", {}).get("integrity_score", 0.0)
                
                if entities > 0 and integrity >= 80:
                    data_integrity_score += 0.2
                    logger.info(f"   ✅ Hierarchy: {entities} entities, {integrity:.1f}% integrity")
                else:
                    logger.info(f"   ⚠️ Hierarchy: {entities} entities, {integrity:.1f}% integrity")
                    
            except Exception as e:
                logger.error(f"   ❌ Hierarchy data validation failed: {str(e)}")
        
        # Calculate final results
        import_score = (import_success / len(components)) * 0.4  # 40% weight
        files_score = (files_found / len(expected_files)) * 0.3  # 30% weight
        data_score = data_integrity_score * 0.3  # 30% weight (already normalized)
        
        overall_score = (import_score + files_score + data_score) * 100
        
        integration_results["components_functional"] = import_success
        integration_results["files_found"] = files_found
        integration_results["data_integrity_score"] = data_integrity_score
        integration_results["overall_score"] = overall_score
        
        # Determine status
        if overall_score >= 80:
            integration_results["integration_status"] = "EXCELLENT"
        elif overall_score >= 70:
            integration_results["integration_status"] = "GOOD"
        elif overall_score >= 60:
            integration_results["integration_status"] = "ACCEPTABLE"
        else:
            integration_results["integration_status"] = "NEEDS_IMPROVEMENT"
        
        # Save integration report
        with open("phase2_integration_simple_report.json", 'w', encoding='utf-8') as f:
            json.dump(integration_results, f, ensure_ascii=False, indent=2)
        
        logger.info("=" * 60)
        logger.info("✅ Phase 2: Simple Integration Test COMPLETE")
        logger.info(f"📊 Final Results:")
        logger.info(f"   🔧 Components functional: {import_success}/{len(components)}")
        logger.info(f"   📁 Files present: {files_found}/{len(expected_files)}")
        logger.info(f"   📊 Data integrity: {data_integrity_score:.1%}")
        logger.info(f"   🏁 Overall score: {overall_score:.1f}/100")
        logger.info(f"   🎯 Status: {integration_results['integration_status']}")
        
        return 0 if integration_results["integration_status"] in ['EXCELLENT', 'GOOD', 'ACCEPTABLE'] else 1
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())