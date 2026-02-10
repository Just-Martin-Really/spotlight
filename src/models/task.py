"""
Task data models for Spotlight.

Defines typed data structures for different task types using Python dataclasses.
Provides factory method for deserializing JSON data into appropriate task objects.

Design principle: Pure data classes with no business logic.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class BaseTask:
    """
    Base class for all task types.
    
    Attributes:
        type: Task category identifier (quiz, tabu, discussion)
        id: Unique identifier (auto-generated from index)
    """
    type: str
    id: Optional[int] = None


@dataclass
class QuizTask(BaseTask):
    """
    Quiz question task.
    
    Displays a question prominently. Optional note provides context
    for discussion or hints for the moderator.
    
    Attributes:
        question: Main quiz question text (required)
        note: Additional context or moderation hint (optional)
    """
    question: str = None
    note: Optional[str] = None


@dataclass
class TabuTask(BaseTask):
    """
    Tabu/Explain task.
    
    Participant must explain a topic without using forbidden words.
    Similar to the Taboo board game format.
    
    Attributes:
        topic: Subject to be explained
        forbidden_words: List of words that must not be used
    """
    topic: str = None
    forbidden_words: List[str] = None


@dataclass
class DiscussionTask(BaseTask):
    """
    Open discussion/Spotlight task.
    
    A participant comes to the front to discuss a topic.
    The audience can ask questions.
    
    Attributes:
        prompt: Discussion topic or question
        spotlight_duration: Suggested time allocation (e.g., "5 minutes")
    """
    prompt: str = None
    spotlight_duration: Optional[str] = None


class TaskFactory:
    """
    Factory for creating task objects from dictionaries.
    
    Handles deserialization from JSON data and type-based dispatch
    to appropriate task subclasses.
    """
    
    # Mapping of type strings to task classes
    _TASK_CLASSES = {
        "quiz": QuizTask,
        "tabu": TabuTask,
        "discussion": DiscussionTask,
    }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], task_id: int) -> BaseTask:
        """
        Create a task object from dictionary data.
        
        Args:
            data: Dictionary containing task data (typically from JSON)
            task_id: Unique identifier to assign to the task
            
        Returns:
            Appropriate task subclass instance
            
        Raises:
            ValueError: If task type is unknown or required fields are missing
        """
        task_type = data.get("type")
        
        if task_type not in cls._TASK_CLASSES:
            raise ValueError(
                f"Unknown task type: {task_type}. "
                f"Valid types: {', '.join(cls._TASK_CLASSES.keys())}"
            )
        
        # Get the appropriate task class
        task_class = cls._TASK_CLASSES[task_type]
        
        # Create copy of data and add ID
        task_data = data.copy()
        task_data["id"] = task_id
        
        try:
            # Instantiate the task (dataclass will validate required fields)
            return task_class(**task_data)
        except TypeError as e:
            raise ValueError(
                f"Invalid data for {task_type} task: {e}"
            ) from e
