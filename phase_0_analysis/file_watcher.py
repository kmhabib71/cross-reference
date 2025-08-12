#!/usr/bin/env python3
"""
Real-time File Watcher for Legal Documents
Automatically detects new files and triggers integration
Ensures system always has latest legal documents for advice
"""

import time
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from dynamic_file_integrator import DynamicFileIntegrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDocumentHandler(FileSystemEventHandler):
    def __init__(self, integrator: DynamicFileIntegrator):
        self.integrator = integrator
        self.pending_files = set()
        self.last_integration = 0
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        if event.src_path.endswith('.json'):
            logger.info(f"📂 New legal document detected: {event.src_path}")
            self.pending_files.add(Path(event.src_path))
            self.schedule_integration()
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        if event.src_path.endswith('.json'):
            logger.info(f"📝 Legal document modified: {event.src_path}")
            self.pending_files.add(Path(event.src_path))
            self.schedule_integration()
    
    def schedule_integration(self):
        """Schedule integration with debouncing (wait for file operations to complete)"""
        current_time = time.time()
        
        # Debounce: wait 5 seconds after last file change
        if current_time - self.last_integration > 5:
            self.integrate_pending_files()
            self.last_integration = current_time
    
    def integrate_pending_files(self):
        """Integrate all pending files"""
        if not self.pending_files:
            return
            
        logger.info(f"🔄 Integrating {len(self.pending_files)} legal documents...")
        
        try:
            result = self.integrator.integrate_new_files()
            
            if result["status"] == "success":
                logger.info(f"✅ Successfully integrated legal documents")
                logger.info(f"   New files: {result['new_files']}")
                logger.info("   System is now ready for precise legal advice!")
            else:
                logger.error(f"❌ Integration failed: {result}")
                
        except Exception as e:
            logger.error(f"❌ Integration error: {e}")
        finally:
            self.pending_files.clear()

class LegalDocumentWatcher:
    def __init__(self, data_dir: str, phase_dir: str):
        self.data_dir = Path(data_dir)
        self.integrator = DynamicFileIntegrator(data_dir, phase_dir)
        self.handler = LegalDocumentHandler(self.integrator)
        self.observer = Observer()
        
    def start_watching(self):
        """Start watching for new legal documents"""
        logger.info(f"👀 Starting legal document watcher on: {self.data_dir}")
        
        # Recursive watching of all subdirectories
        self.observer.schedule(self.handler, str(self.data_dir), recursive=True)
        self.observer.start()
        
        logger.info("🚀 Legal document watcher is running!")
        logger.info("   Add new SRO/Circular/Act files to data/ folder")
        logger.info("   System will automatically integrate them for precise advice")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping legal document watcher...")
            self.observer.stop()
        
        self.observer.join()
        logger.info("✅ Legal document watcher stopped")

def main():
    """Start the legal document watcher service"""
    data_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/data"
    phase_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/precision_crossref_system_2025/phase_0_analysis"
    
    watcher = LegalDocumentWatcher(data_dir, phase_dir)
    watcher.start_watching()

if __name__ == "__main__":
    main()