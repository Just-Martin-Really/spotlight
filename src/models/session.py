"""
Session state management for TIA25 Spotlight.

Manages the current position in the task sequence and navigation history.
Implements circular navigation (wrapping at start/end).

Design principle: State object with no rendering or input logic.
"""

from typing import List
from src.models.task import BaseTask


class Session:
    """
    Manages the active session state.
    
    Tracks which task is currently displayed and provides navigation methods.
    Implements circular navigation - advancing past the last task wraps to first.
    
    Attributes:
        tasks: Complete list of loaded tasks
        current_index: Index of currently displayed task (0-based)
    """
    
    def __init__(self, tasks: List[BaseTask]):
        """
        Initialize a new session.
        
        Args:
            tasks: List of task objects to display
            
        Raises:
            ValueError: If tasks list is empty
        """
        if not tasks:
            raise ValueError("Cannot create session with empty task list")
        
        self.tasks = tasks
        self.current_index = 0
    
    def next_task(self) -> None:
        """
        Navigate to the next task.
        
        Wraps around to first task if currently at the end.
        """
        self.current_index = (self.current_index + 1) % len(self.tasks)
    
    def prev_task(self) -> None:
        """
        Navigate to the previous task.
        
        Wraps around to last task if currently at the start.
        """
        self.current_index = (self.current_index - 1) % len(self.tasks)
    
    def current_task(self) -> BaseTask:
        """
        Get the currently active task.
        
        Returns:
            The task object at current_index
        """
        return self.tasks[self.current_index]
    
    def get_position_info(self) -> str:
        """
        Get human-readable position information.
        
        Returns:
            String like "3 / 12" indicating current position and total
        """
        return f"{self.current_index + 1} / {len(self.tasks)}"
    
    def is_first_task(self) -> bool:
        """Check if currently at first task."""
        return self.current_index == 0
    
    def is_last_task(self) -> bool:
        """Check if currently at last task."""
        return self.current_index == len(self.tasks) - 1
