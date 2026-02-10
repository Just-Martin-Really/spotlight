"""
Task loading service for Spotlight.

Handles loading and parsing task data from JSON files.
Provides error handling for common file and data issues.

Design principle: Service layer - no UI, no state, just data transformation.
"""

import json
from pathlib import Path
from typing import List

from src.models.task import BaseTask, TaskFactory


class TaskLoadError(Exception):
    """Custom exception for task loading errors."""
    pass


class TaskLoader:
    """
    Service for loading tasks from JSON files.
    
    Handles file I/O, JSON parsing, validation, and conversion
    to typed task objects.
    """
    
    @staticmethod
    def load_tasks(filepath: str) -> List[BaseTask]:
        """
        Load tasks from a JSON file.
        
        Args:
            filepath: Path to JSON file containing task array
            
        Returns:
            List of task objects (QuizTask, TabuTask, DiscussionTask)
            
        Raises:
            TaskLoadError: If file cannot be read, JSON is invalid,
                          or task data is malformed
        """
        # Convert to Path object for better path handling
        path = Path(filepath)
        
        # Check if file exists
        if not path.exists():
            raise TaskLoadError(
                f"Task file not found: {filepath}\n"
                f"Make sure the file exists at the specified path."
            )
        
        # Read and parse JSON
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise TaskLoadError(
                f"Invalid JSON in task file: {filepath}\n"
                f"Error: {e}"
            ) from e
        except Exception as e:
            raise TaskLoadError(
                f"Failed to read task file: {filepath}\n"
                f"Error: {e}"
            ) from e
        
        # Validate that data is a list
        if not isinstance(data, list):
            raise TaskLoadError(
                f"Task file must contain a JSON array, got: {type(data).__name__}"
            )
        
        if not data:
            raise TaskLoadError(
                "Task file contains an empty array - at least one task required"
            )
        
        # Convert dictionaries to task objects
        tasks = []
        for index, task_data in enumerate(data):
            try:
                task = TaskFactory.from_dict(task_data, task_id=index)
                tasks.append(task)
            except ValueError as e:
                raise TaskLoadError(
                    f"Invalid task at index {index}: {e}"
                ) from e
        
        return tasks
    
    @staticmethod
    def validate_task_file(filepath: str) -> bool:
        """
        Validate a task file without loading it.
        
        Useful for pre-flight checks before starting the application.
        
        Args:
            filepath: Path to JSON file to validate
            
        Returns:
            True if file is valid, False otherwise
        """
        try:
            TaskLoader.load_tasks(filepath)
            return True
        except TaskLoadError:
            return False
