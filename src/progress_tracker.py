"""Progress tracking for AI summary generation."""

import queue
import threading
from typing import Dict


class ProgressTracker:
    """Thread-safe progress tracker for AI generation."""

    def __init__(self):
        self._trackers: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def create_tracker(self, tracker_id: str) -> None:
        """Create a new progress tracker.

        Args:
            tracker_id: Unique ID for this tracker
        """
        with self._lock:
            self._trackers[tracker_id] = {
                'completed': 0,
                'total': 0,
                'current': '',
                'done': False,
                'queue': queue.Queue()
            }

    def update(self, tracker_id: str, completed: int, total: int, current: str) -> None:
        """Update progress.

        Args:
            tracker_id: Tracker ID
            completed: Number completed
            total: Total number
            current: Current item being processed
        """
        with self._lock:
            if tracker_id in self._trackers:
                tracker = self._trackers[tracker_id]
                tracker['completed'] = completed
                tracker['total'] = total
                tracker['current'] = current
                tracker['queue'].put({
                    'completed': completed,
                    'total': total,
                    'current': current,
                    'done': False
                })

    def mark_done(self, tracker_id: str) -> None:
        """Mark tracker as done.

        Args:
            tracker_id: Tracker ID
        """
        with self._lock:
            if tracker_id in self._trackers:
                tracker = self._trackers[tracker_id]
                tracker['done'] = True
                tracker['queue'].put({'done': True})

    def get_updates(self, tracker_id: str):
        """Generator that yields progress updates.

        Args:
            tracker_id: Tracker ID

        Yields:
            Progress update dicts
        """
        if tracker_id not in self._trackers:
            return

        tracker = self._trackers[tracker_id]
        q = tracker['queue']

        while True:
            try:
                update = q.get(timeout=60)  # 60 second timeout
                yield update
                if update.get('done'):
                    break
            except queue.Empty:
                break

        # Cleanup
        with self._lock:
            if tracker_id in self._trackers:
                del self._trackers[tracker_id]


# Global progress tracker instance
progress_tracker = ProgressTracker()
