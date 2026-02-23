import pygame

from src.models.reveal_state import RevealState
from src.models.task import QuizTask
from src.views.quiz_renderer import QuizRenderer


def test_reveal_state_toggle() -> None:
    rs = RevealState()
    assert rs.is_revealed(1) is False
    assert rs.toggle(1) is True
    assert rs.is_revealed(1) is True
    assert rs.toggle(1) is False
    assert rs.is_revealed(1) is False


def test_quiz_renderer_note_hidden_when_not_revealed() -> None:
    """Low-level regression test: render_content must be callable with show_note flag."""
    pygame.init()
    try:
        screen = pygame.Surface((800, 600))
        r = QuizRenderer(screen)
        task = QuizTask(type="quiz", id=0, points=100, question="Q", note="SECRET")

        # Should not throw either way.
        r.render_content(task, show_note=False)
        r.render_content(task, show_note=True)
    finally:
        pygame.quit()

