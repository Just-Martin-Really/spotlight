import json
from pathlib import Path

import pytest

from src.cli import main as cli_main
from src.models.session import Session
from src.services.task_loader import TaskLoader, TaskLoadError


def _write_json(tmp_path: Path, payload) -> str:
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return str(path)


def test_task_loader_happy_path(tmp_path: Path) -> None:
    task_file = _write_json(
        tmp_path,
        [
            {"type": "quiz", "question": "What is Big-O?", "difficulty": 3},
            {"type": "tabu", "topic": "Databases", "forbidden_words": ["SQL", "table"], "difficulty": 2},
            {"type": "discussion", "prompt": "Explain stacks vs queues", "difficulty": 1},
            {"type": "code", "code": "print('hi')", "question": "What prints?", "difficulty": 4},
            {"type": "explain_to", "topic": "Recursion", "audience": "a child", "difficulty": 5},
        ],
    )

    tasks = TaskLoader.load_tasks(task_file)

    assert len(tasks) == 5
    assert [t.type for t in tasks] == ["quiz", "tabu", "discussion", "code", "explain_to"]
    assert [t.id for t in tasks] == [0, 1, 2, 3, 4]
    assert [t.difficulty for t in tasks] == [3, 2, 1, 4, 5]


def test_task_loader_unknown_type(tmp_path: Path) -> None:
    task_file = _write_json(tmp_path, [{"type": "nope", "question": "x", "difficulty": 1}])

    with pytest.raises(TaskLoadError, match=r"Invalid task at index 0: Unknown task type"):
        TaskLoader.load_tasks(task_file)


def test_task_loader_missing_required_field(tmp_path: Path) -> None:
    task_file = _write_json(tmp_path, [{"type": "quiz", "difficulty": 1}])

    with pytest.raises(TaskLoadError, match=r"Field 'question' must be a non-empty string"):
        TaskLoader.load_tasks(task_file)


def test_task_loader_wrong_type_field(tmp_path: Path) -> None:
    task_file = _write_json(tmp_path, [{"type": "tabu", "topic": "X", "forbidden_words": "SQL", "difficulty": 1}])

    with pytest.raises(TaskLoadError, match=r"Field 'forbidden_words' must be a non-empty array of strings"):
        TaskLoader.load_tasks(task_file)


def test_task_loader_missing_difficulty(tmp_path: Path) -> None:
    task_file = _write_json(tmp_path, [{"type": "quiz", "question": "Q"}])

    with pytest.raises(TaskLoadError, match=r"difficulty.*required"):
        TaskLoader.load_tasks(task_file)


def test_task_loader_invalid_difficulty(tmp_path: Path) -> None:
    task_file = _write_json(tmp_path, [{"type": "quiz", "question": "Q", "difficulty": 6}])

    with pytest.raises(TaskLoadError, match=r"difficulty.*between 1 and 5"):
        TaskLoader.load_tasks(task_file)


def test_session_wraparound_next_prev() -> None:
    tasks = TaskLoader.load_tasks("data/tasks.json")
    session = Session(tasks)

    assert session.get_position_info().startswith("1 /")

    # prev from first wraps to last
    session.prev_task()
    assert session.is_last_task()

    # next from last wraps back to first
    session.next_task()
    assert session.is_first_task()


def test_cli_validate_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    task_file = _write_json(tmp_path, [{"type": "quiz", "question": "Ok", "difficulty": 1}])

    code = cli_main(["validate", "--task-file", task_file])

    assert code == 0
    captured = capsys.readouterr()
    assert "OK:" in captured.out


def test_cli_validate_invalid(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    task_file = _write_json(tmp_path, [{"type": "quiz", "question": "Ok"}])

    code = cli_main(["validate", "--task-file", task_file])

    assert code == 2
    captured = capsys.readouterr()
    assert "INVALID:" in captured.err
