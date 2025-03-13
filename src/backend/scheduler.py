"""
Scheduler for periodic tasks in the ESG & Finance AI Research Assistant.
"""

import sys
import time
import threading
import schedule
from pathlib import Path
from datetime import datetime
import json
import os

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import SCHEDULE, DATA_DIR
from src.backend.data_collectors import collect_new_papers
from src.backend.ai_processing import process_new_papers
from src.backend.database import init_db

# File to store the scheduler's status
SCHEDULER_STATUS_FILE = DATA_DIR / "scheduler_status.json"

class TaskScheduler:
    """Scheduler for periodic tasks."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.stop_event = threading.Event()
        self.threads = []
        self.status = {
            'running': False,
            'last_collection': None,
            'last_processing': None,
            'collection_stats': {},
            'processing_stats': {}
        }
        
        # Load status if it exists
        self._load_status()
        
        # Initialize database if needed
        init_db()
    
    def start(self):
        """Start the scheduler."""
        if self.status['running']:
            print("Scheduler is already running")
            return False
            
        print("Starting scheduler")
        
        # Schedule data collection
        schedule.every(SCHEDULE['data_collection']).minutes.do(self._run_data_collection)
        
        # Schedule data processing
        schedule.every(SCHEDULE['data_processing']).minutes.do(self._run_data_processing)
        
        # Set status to running
        self.status['running'] = True
        self._save_status()
        
        # Start the scheduler thread
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        self.threads.append(scheduler_thread)
        
        return True
    
    def stop(self):
        """Stop the scheduler."""
        if not self.status['running']:
            print("Scheduler is not running")
            return False
            
        print("Stopping scheduler")
        
        # Signal threads to stop
        self.stop_event.set()
        
        # Clear all scheduled jobs
        schedule.clear()
        
        # Wait for threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
        
        # Clear threads list
        self.threads = []
        
        # Set status to not running
        self.status['running'] = False
        self._save_status()
        
        return True
    
    def get_status(self):
        """Get the current status of the scheduler.
        
        Returns:
            dict: Status information
        """
        return self.status
    
    def run_collection_now(self):
        """Run data collection immediately.
        
        Returns:
            dict: Collection statistics
        """
        stats = self._run_data_collection()
        return stats
    
    def run_processing_now(self, limit=10):
        """Run data processing immediately.
        
        Args:
            limit (int): Maximum number of papers to process
            
        Returns:
            dict: Processing statistics
        """
        stats = self._run_data_processing(limit=limit)
        return stats
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)
    
    def _run_data_collection(self):
        """Run data collection task.
        
        Returns:
            dict: Collection statistics
        """
        print(f"Running data collection at {datetime.now().isoformat()}")
        
        try:
            # Collect new papers
            stats = collect_new_papers()
            
            # Update status
            self.status['last_collection'] = datetime.now().isoformat()
            self.status['collection_stats'] = stats
            self._save_status()
            
            print(f"Data collection completed: {stats}")
            return stats
        except Exception as e:
            print(f"Error in data collection: {e}")
            return {'error': str(e)}
    
    def _run_data_processing(self, limit=10):
        """Run data processing task.
        
        Args:
            limit (int): Maximum number of papers to process
            
        Returns:
            dict: Processing statistics
        """
        print(f"Running data processing at {datetime.now().isoformat()}")
        
        try:
            # Process new papers
            stats = process_new_papers(limit=limit)
            
            # Update status
            self.status['last_processing'] = datetime.now().isoformat()
            self.status['processing_stats'] = stats
            self._save_status()
            
            print(f"Data processing completed: {stats}")
            return stats
        except Exception as e:
            print(f"Error in data processing: {e}")
            return {'error': str(e)}
    
    def _save_status(self):
        """Save status to file."""
        try:
            with open(SCHEDULER_STATUS_FILE, 'w') as f:
                json.dump(self.status, f)
        except Exception as e:
            print(f"Error saving scheduler status: {e}")
    
    def _load_status(self):
        """Load status from file."""
        try:
            if os.path.exists(SCHEDULER_STATUS_FILE):
                with open(SCHEDULER_STATUS_FILE, 'r') as f:
                    self.status.update(json.load(f))
        except Exception as e:
            print(f"Error loading scheduler status: {e}")


# Singleton instance
_scheduler = None

def get_scheduler():
    """Get the scheduler instance.
    
    Returns:
        TaskScheduler: Scheduler instance
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


if __name__ == "__main__":
    # Test the scheduler
    scheduler = get_scheduler()
    scheduler.start()
    
    # Run collection and processing immediately
    print("Running collection...")
    collection_stats = scheduler.run_collection_now()
    print(f"Collection stats: {collection_stats}")
    
    print("Running processing...")
    processing_stats = scheduler.run_processing_now(limit=5)
    print(f"Processing stats: {processing_stats}")
    
    # Let the scheduler run for a while
    try:
        print("Scheduler running. Press Ctrl+C to stop.")
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped.")