import pytest

from src.models.game_state import BuzzState, GameState


def test_scoring_add_and_subtract() -> None:
    gs = GameState.with_teams(["A", "B"])

    gs.add_points(0, 3)
    gs.add_points(1, 1)
    gs.add_points(0, -2)

    assert gs.teams[0].score == 1
    assert gs.teams[1].score == 1


def test_scoring_invalid_team_ignored() -> None:
    gs = GameState.with_teams(["A"])

    gs.add_points(123, 5)
    assert gs.teams[0].score == 0


def test_buzz_open_lock_reset() -> None:
    gs = GameState.with_teams(["A", "B", "C"])

    assert gs.buzz_state == BuzzState.CLOSED

    gs.open_buzz()
    assert gs.buzz_state == BuzzState.OPEN

    assert gs.buzz(1) is True
    assert gs.buzz_state == BuzzState.LOCKED
    assert gs.buzz_locked_team == 1

    # second buzz shouldn't change anything
    assert gs.buzz(2) is False
    assert gs.buzz_locked_team == 1

    gs.reset_buzz()
    assert gs.buzz_state == BuzzState.CLOSED
    assert gs.buzz_locked_team is None


def test_timer_toggle_and_tick_stopwatch() -> None:
    gs = GameState.with_teams(["A"])

    now = 1000
    gs.timer_start_pause_toggle(now)
    assert gs.timer.running is True

    gs.tick(now + 500)
    assert gs.timer.elapsed_ms == 500

    gs.timer_start_pause_toggle(now + 500)
    assert gs.timer.running is False

    # ticking while paused shouldn't change
    gs.tick(now + 1000)
    assert gs.timer.elapsed_ms == 500


def test_timer_reset() -> None:
    gs = GameState.with_teams(["A"])

    gs.timer_start_pause_toggle(0)
    gs.tick(200)

    gs.timer_reset(200)
    assert gs.timer.elapsed_ms == 0
    assert gs.timer.running is False


def test_persistence_roundtrip() -> None:
    gs = GameState.with_teams(["Alpha", "Beta"])
    gs.add_points(0, 5)
    gs.open_buzz()
    gs.buzz(0)

    data = gs.to_dict()
    restored = GameState.from_dict(data)

    assert [t.name for t in restored.teams] == ["Alpha", "Beta"]
    assert [t.score for t in restored.teams] == [5, 0]
    assert restored.buzz_state == BuzzState.LOCKED
    assert restored.buzz_locked_team == 0


def test_from_dict_sanitizes_locked_team_out_of_range() -> None:
    data = {
        "version": 1,
        "teams": [{"name": "A", "score": 0}],
        "buzz": {"state": "locked", "locked_team": 9},
        "timer": {"mode": "stopwatch", "running": False, "elapsed_ms": 0, "target_ms": None},
    }

    restored = GameState.from_dict(data)
    assert restored.buzz_locked_team is None
    assert restored.buzz_state in (BuzzState.CLOSED, BuzzState.OPEN)


def test_with_teams_requires_at_least_one_name() -> None:
    with pytest.raises(ValueError):
        GameState.with_teams(["  ", ""])

