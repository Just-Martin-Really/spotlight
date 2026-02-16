from src.models.game_show import award_points_for_current_task
from src.models.game_state import GameState
from src.models.scoring_state import ScoringState
from src.models.session import Session
from src.models.task import QuizTask


def test_award_only_once_per_task() -> None:
    session = Session([QuizTask(type="quiz", id=0, difficulty=3, question="Q")])
    gs = GameState.with_teams(["A"])
    scoring = ScoringState()

    # first award allowed
    assert scoring.mark_awarded(0) is True
    assert award_points_for_current_task(session, gs, selected_team_index=0, now_ms=0) == 0
    assert gs.teams[0].score == 3

    # second award blocked
    assert scoring.mark_awarded(0) is False

