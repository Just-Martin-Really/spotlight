from src.models.game_state import BuzzState, GameState


def test_fail_blocks_team_and_reopens_buzz() -> None:
    gs = GameState.with_teams(["A", "B"])

    gs.open_buzz()
    assert gs.buzz_state == BuzzState.OPEN

    assert gs.buzz(0) is True
    assert gs.buzz_state == BuzzState.LOCKED
    assert gs.buzz_locked_team == 0

    gs.fail_locked_team_and_reopen()
    assert gs.buzz_state == BuzzState.OPEN
    assert gs.buzz_locked_team is None
    assert 0 in gs.buzz_blocked_teams

    # blocked team can't re-buzz
    assert gs.buzz(0) is False
    # other team can
    assert gs.buzz(1) is True
    assert gs.buzz_locked_team == 1


def test_reset_buzz_clears_blocks() -> None:
    gs = GameState.with_teams(["A", "B"])
    gs.open_buzz()
    gs.buzz(0)
    gs.fail_locked_team_and_reopen()
    assert gs.buzz_blocked_teams

    gs.reset_buzz()
    assert gs.buzz_blocked_teams == set()

