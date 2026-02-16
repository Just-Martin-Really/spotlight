from src.models.game_show import award_points_for_current_task
from src.models.game_state import GameState
from src.models.session import Session
from src.models.task import QuizTask


def test_award_uses_selected_team_when_no_buzz_lock() -> None:
    session = Session([QuizTask(type="quiz", id=0, difficulty=4, question="Q")])
    gs = GameState.with_teams(["A", "B"])

    awarded = award_points_for_current_task(session, gs, selected_team_index=1, now_ms=0)

    assert awarded == 1
    assert gs.teams[1].score == 4


def test_award_prefers_buzz_locked_team_over_selected() -> None:
    session = Session([QuizTask(type="quiz", id=0, difficulty=2, question="Q")])
    gs = GameState.with_teams(["A", "B"])

    gs.open_buzz()
    assert gs.buzz(0) is True

    awarded = award_points_for_current_task(session, gs, selected_team_index=1, now_ms=0)

    assert awarded == 0
    assert gs.teams[0].score == 2
    assert gs.teams[1].score == 0


def test_award_without_team_sets_status_and_does_nothing() -> None:
    session = Session([QuizTask(type="quiz", id=0, difficulty=1, question="Q")])
    gs = GameState.with_teams(["A"])

    awarded = award_points_for_current_task(session, gs, selected_team_index=None, now_ms=100)

    assert awarded is None
    assert gs.teams[0].score == 0
    assert gs.status_message == "No team selected"

