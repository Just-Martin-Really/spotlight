import pygame
import pytest

from src.services.renderer_utils import wrap_text
from src.services.transitions import crossfade


@pytest.fixture(scope="module", autouse=True)
def _pygame_init():
    pygame.init()
    # Use a tiny dummy display; some pygame Surface ops require a display
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def test_wrap_text_hard_wrap_splits_long_token() -> None:
    font = pygame.font.Font(None, 24)

    token = "A" * 200
    lines = wrap_text(token, font, max_width=50, hard_wrap=True)

    assert len(lines) > 1
    assert all(font.size(line)[0] <= 50 for line in lines)


def test_crossfade_progress_validation() -> None:
    s1 = pygame.Surface((10, 10)).convert_alpha()
    s2 = pygame.Surface((10, 10)).convert_alpha()

    with pytest.raises(ValueError):
        crossfade(s1, s2, -0.1)

    with pytest.raises(ValueError):
        crossfade(s1, s2, 1.1)


def test_crossfade_size_mismatch() -> None:
    s1 = pygame.Surface((10, 10)).convert_alpha()
    s2 = pygame.Surface((11, 10)).convert_alpha()

    with pytest.raises(ValueError, match="same size"):
        crossfade(s1, s2, 0.5)
