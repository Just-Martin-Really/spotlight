from src.models.reveal_state import RevealState


def test_toggle_and_is_revealed() -> None:
    rs = RevealState()

    assert rs.is_revealed(1) is False
    assert rs.toggle(1) is True
    assert rs.is_revealed(1) is True

    assert rs.toggle(1) is False
    assert rs.is_revealed(1) is False


def test_reset_and_clear() -> None:
    rs = RevealState()
    rs.toggle(1)
    rs.toggle(2)

    rs.reset(1)
    assert rs.is_revealed(1) is False
    assert rs.is_revealed(2) is True

    rs.clear_all()
    assert rs.is_revealed(2) is False

