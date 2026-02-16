from src.models.game_show import award_points_for_current_task
from src.models.game_state import GameState
from src.models.scoring_state import ScoringState
from src.models.session import Session
from src.models.task import QuizTask


def test_award_lock_persists_across_circular_navigation() -> None:
    tasks = [
        QuizTask(type="quiz", id=0, difficulty=1, question="Q0"),
        QuizTask(type="quiz", id=1, difficulty=1, question="Q1"),
    ]
    session = Session(tasks)
    gs = GameState.with_teams(["A"])
    scoring = ScoringState()

    # Award task 0
    assert scoring.is_awarded(0) is False
    assert award_points_for_current_task(session, gs, selected_team_index=0, now_ms=0) == 0
    assert scoring.mark_awarded(0) is True

    # Move forward twice to loop back to task 0
    session.next_task()  # task 1
    session.next_task()  # back to task 0

    # Still considered awarded
    assert scoring.is_awarded(0) is True

