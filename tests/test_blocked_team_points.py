from src.models.game_state import GameState


def test_blocked_team_cannot_receive_points() -> None:
    gs = GameState.with_teams(["A", "B"])

    gs.open_buzz()
    assert gs.buzz(0) is True
    gs.fail_locked_team_and_reopen()

    # Team 0 is now blocked
    assert gs.teams[0].score == 0
    gs.add_points(0, 5)
    assert gs.teams[0].score == 0

    # Team 1 is not blocked
    gs.add_points(1, 3)
    assert gs.teams[1].score == 3

