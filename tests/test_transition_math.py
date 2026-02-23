import pytest

from src.services.transition_math import transition_progress


def test_transition_progress_bounds() -> None:
    assert transition_progress(0, 300) == 0.0
    assert transition_progress(-5, 300) == 0.0
    assert transition_progress(300, 300) == 1.0
    assert transition_progress(999, 300) == 1.0


def test_transition_progress_middle() -> None:
    assert transition_progress(150, 300) == 0.5


def test_transition_progress_invalid_duration() -> None:
    with pytest.raises(ValueError):
        transition_progress(10, 0)

