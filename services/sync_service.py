"""
Sync Service - Offline-First Strategy with Sync Queue
Emerging Technology: Offline-First Data Strategy
"""
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from database import db


class SyncService:
    """
    Service for handling offline-first data synchronization.
    
    This implements the offline-first enhancement requirement through:
    - Queue-based operation tracking
    - Retry logic for failed operations
    - Conflict resolution strategies
    - Delta updates for efficiency
    """
    
    # Sync status constants
    STATUS_PENDING = 'pending'
    STATUS_SYNCING = 'syncing'
    STATUS_SYNCED = 'synced'
    STATUS_FAILED = 'failed'
    
    @staticmethod
    def queue_operation(operation: str, table_name: str,
                        record_id: int = None, data: Dict = None) -> int:
        """
        Add an operation to the sync queue.
        Returns the queue entry ID.
        """
        db.add_to_sync_queue(operation, table_name, record_id, data)
        return db.conn.cursor().lastrowid
    
    @staticmethod
    def get_pending_operations() -> List[Dict]:
        """Get all pending sync operations"""
        return db.get_pending_sync()
    
    @staticmethod
    def get_pending_count() -> int:
        """Get count of pending operations"""
        return len(db.get_pending_sync())
    
    @staticmethod
    def mark_synced(sync_id: int) -> bool:
        """Mark an operation as synced"""
        try:
            db.mark_synced(sync_id)
            return True
        except Exception:
            return False
    
    @staticmethod
    def process_sync_queue() -> Tuple[int, int]:
        """
        Process all pending sync operations.
        Returns: (successful_count, failed_count)
        
        This simulates syncing with a remote server.
        In a real implementation, this would make API calls.
        """
        pending = db.get_pending_sync()
        successful = 0
        failed = 0
        
        for operation in pending:
            try:
                # Simulate network sync (in production, make API call here)
                # For now, we just mark as synced since we're offline-first
                SyncService._simulate_sync(operation)
                db.mark_synced(operation['id'])
                successful += 1
            except Exception as e:
                print(f"Sync failed for operation {operation['id']}: {e}")
                failed += 1
        
        return successful, failed
    
    @staticmethod
    def _simulate_sync(operation: Dict) -> bool:
        """
        Simulate syncing an operation to a remote server.
        In production, this would make actual API calls.
        """
        # Simulate network delay and potential failures
        import random
        
        # 95% success rate simulation
        if random.random() < 0.95:
            return True
        else:
            raise Exception("Simulated network error")
    
    @staticmethod
    def resolve_conflict(local_data: Dict, remote_data: Dict,
                         strategy: str = 'local_wins') -> Dict:
        """
        Resolve conflicts between local and remote data.
        
        Strategies:
        - local_wins: Local changes take precedence
        - remote_wins: Remote changes take precedence
        - newest_wins: Most recently updated version wins
        - merge: Attempt to merge both versions
        """
        if strategy == 'local_wins':
            return local_data
        elif strategy == 'remote_wins':
            return remote_data
        elif strategy == 'newest_wins':
            local_time = local_data.get('updated_at', '')
            remote_time = remote_data.get('updated_at', '')
            return local_data if local_time > remote_time else remote_data
        elif strategy == 'merge':
            # Merge strategy: combine both, local takes precedence for conflicts
            merged = {**remote_data, **local_data}
            return merged
        else:
            return local_data
    
    @staticmethod
    def is_online() -> bool:
        """
        Check if the application has network connectivity.
        In production, this would check actual network status.
        """
        # Simulate online status - always return True for demo
        return True
    
    @staticmethod
    def get_sync_status() -> Dict:
        """Get current sync status"""
        pending = SyncService.get_pending_count()
        
        return {
            'is_online': SyncService.is_online(),
            'pending_operations': pending,
            'last_sync': datetime.now().isoformat() if pending == 0 else None,
            'status': 'synced' if pending == 0 else 'pending'
        }
    
    @staticmethod
    def queue_attendance_mark(session_id: int, student_id: int, status: str):
        """Queue an attendance mark operation for sync"""
        SyncService.queue_operation(
            operation='INSERT',
            table_name='attendance_records',
            data={
                'session_id': session_id,
                'student_id': student_id,
                'status': status,
                'marked_at': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def queue_class_update(class_id: int, updates: Dict):
        """Queue a class update operation for sync"""
        SyncService.queue_operation(
            operation='UPDATE',
            table_name='classes',
            record_id=class_id,
            data=updates
        )
    
    @staticmethod
    def clear_sync_queue() -> int:
        """Clear all synced operations from queue"""
        cursor = db.conn.cursor()
        cursor.execute('DELETE FROM sync_queue WHERE synced = 1')
        db.conn.commit()
        return cursor.rowcount







