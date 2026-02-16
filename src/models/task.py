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


@dataclass
class CodeTask(BaseTask):
    """
    Code analysis task.

    Displays code snippet with a question like "Find the bug" or
    "Which programming language is this?". Code is displayed in
    monospace font without syntax highlighting.

    Attributes:
        code: Code snippet (can include newlines with \n)
        question: Question about the code (e.g., "Erkenne den Fehler")
        note: Optional hint or additional context
    """
    code: str = None
    question: str = None
    note: Optional[str] = None


@dataclass
class ExplainToTask(BaseTask):
    """
    Explain-to-audience task.

    Challenge participant to explain a technical topic to a specific
    audience (e.g., "your grandmother", "a 5-year-old").

    Attributes:
        topic: Technical concept to explain
        audience: Target audience (e.g., "deiner Oma", "einem 5-Jährigen")
        note: Optional hint about what to focus on
    """
    topic: str = None
    audience: str = None
    note: Optional[str] = None


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
        "code": CodeTask,
        "explain_to": ExplainToTask,
    }

    _REQUIRED_FIELDS: Dict[str, List[str]] = {
        "quiz": ["question"],
        "tabu": ["topic", "forbidden_words"],
        "discussion": ["prompt"],
        "code": ["code", "question"],
        "explain_to": ["topic", "audience"],
    }

    @staticmethod
    def _require_non_empty_str(data: Dict[str, Any], field: str) -> None:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Field '{field}' must be a non-empty string")

    @staticmethod
    def _require_str_list(data: Dict[str, Any], field: str) -> None:
        value = data.get(field)
        if not isinstance(value, list) or not value:
            raise ValueError(f"Field '{field}' must be a non-empty array of strings")
        if not all(isinstance(item, str) and item.strip() for item in value):
            raise ValueError(f"Field '{field}' must contain only non-empty strings")

    @staticmethod
    def _optional_str(data: Dict[str, Any], field: str) -> None:
        if field in data and data[field] is not None and not isinstance(data[field], str):
            raise ValueError(f"Optional field '{field}' must be a string when provided")

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

        if not isinstance(data, dict):
            raise ValueError(f"Task must be an object, got: {type(data).__name__}")

        task_type = data.get("type")
        if not isinstance(task_type, str) or not task_type.strip():
            raise ValueError("Field 'type' must be a non-empty string")

        if task_type not in cls._TASK_CLASSES:
            raise ValueError(
                f"Unknown task type: {task_type}. "
                f"Valid types: {', '.join(cls._TASK_CLASSES.keys())}"
            )

        # Per-type validation for required fields
        if task_type == "quiz":
            cls._require_non_empty_str(data, "question")
            cls._optional_str(data, "note")
        elif task_type == "tabu":
            cls._require_non_empty_str(data, "topic")
            cls._require_str_list(data, "forbidden_words")
        elif task_type == "discussion":
            cls._require_non_empty_str(data, "prompt")
            cls._optional_str(data, "spotlight_duration")
        elif task_type == "code":
            cls._require_non_empty_str(data, "code")
            cls._require_non_empty_str(data, "question")
            cls._optional_str(data, "note")
        elif task_type == "explain_to":
            cls._require_non_empty_str(data, "topic")
            cls._require_non_empty_str(data, "audience")
            cls._optional_str(data, "note")

        # Get the appropriate task class
        task_class = cls._TASK_CLASSES[task_type]

        # Create copy of data and add ID
        task_data = data.copy()
        task_data["id"] = task_id

        try:
            return task_class(**task_data)
        except TypeError as e:
            raise ValueError(f"Invalid data for {task_type} task: {e}") from e

