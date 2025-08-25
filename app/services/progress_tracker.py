"""
Simple Progress Tracker for Real-time Updates
SIMPLE! GA OVER-ENGINEER!
"""
from typing import Dict, List
import time
import uuid

class ProgressTracker:
    """Simple in-memory progress tracker"""
    
    def __init__(self):
        self.progress_data: Dict[str, Dict] = {}
    
    def create_session(self) -> str:
        """Create new progress session"""
        session_id = str(uuid.uuid4())
        self.progress_data[session_id] = {
            'messages': [],
            'current_step': 0,
            'total_steps': 8,  # 8 progress messages dari pipeline
            'status': 'started',
            'created_at': time.time()
        }
        return session_id
    
    def add_message(self, session_id: str, message: str):
        """Add progress message to session"""
        if session_id in self.progress_data:
            self.progress_data[session_id]['messages'].append({
                'message': message,
                'timestamp': time.time()
            })
            self.progress_data[session_id]['current_step'] += 1
    
    def set_completed(self, session_id: str, result_data: Dict = None):
        """Mark session as completed"""
        if session_id in self.progress_data:
            self.progress_data[session_id]['status'] = 'completed'
            if result_data:
                self.progress_data[session_id]['result'] = result_data
    
    def set_error(self, session_id: str, error_message: str):
        """Mark session as error"""
        if session_id in self.progress_data:
            self.progress_data[session_id]['status'] = 'error'
            self.progress_data[session_id]['error'] = error_message
    
    def get_progress(self, session_id: str) -> Dict:
        """Get current progress for session"""
        return self.progress_data.get(session_id, {})
    
    def cleanup_old_sessions(self, max_age_seconds: int = 3600):
        """Clean up old sessions"""
        current_time = time.time()
        to_remove = []
        
        for session_id, data in self.progress_data.items():
            if current_time - data['created_at'] > max_age_seconds:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.progress_data[session_id]

# Global instance
progress_tracker = ProgressTracker()
