from src.models.game_show import award_points_for_current_task
from src.models.game_state import GameState
from src.models.scoring_state import ScoringState
from src.models.session import Session
from src.models.task import QuizTask


def test_award_blocked_team_does_not_consume_award() -> None:
    session = Session([QuizTask(type="quiz", id=0, difficulty=2, question="Q")])
    gs = GameState.with_teams(["A", "B"])
    scoring = ScoringState()

    # Block team 0
    gs.buzz_blocked_teams.add(0)

    # Attempt to award to blocked team should not mark awarded
    assert scoring.is_awarded(0) is False
    before = gs.teams[0].score
    award_points_for_current_task(session, gs, selected_team_index=0, now_ms=0)
    assert gs.teams[0].score == before
    assert scoring.is_awarded(0) is False

    # Award to non-blocked team should work and then can be marked awarded
    assert award_points_for_current_task(session, gs, selected_team_index=1, now_ms=0) == 1
    assert scoring.mark_awarded(0) is True

