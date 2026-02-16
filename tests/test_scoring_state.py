from src.models.scoring_state import ScoringState


def test_mark_awarded_only_once() -> None:
    ss = ScoringState()
    assert ss.is_awarded(1) is False
    assert ss.mark_awarded(1) is True
    assert ss.is_awarded(1) is True
    assert ss.mark_awarded(1) is False


def test_reset() -> None:
    ss = ScoringState()
    ss.mark_awarded(1)
    ss.reset(1)
    assert ss.is_awarded(1) is False

