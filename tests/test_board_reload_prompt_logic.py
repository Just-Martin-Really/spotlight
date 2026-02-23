from src.views.board_reload_prompt_testable import update_reload_prompt


def test_prompt_toggle_and_confirm() -> None:
    # default choice True
    upd = update_reload_prompt(True, "DOWN")
    assert upd.choice is False
    assert upd.result is None

    upd2 = update_reload_prompt(upd.choice, "ENTER")
    assert upd2.result is False


def test_prompt_abort() -> None:
    upd = update_reload_prompt(True, "ESC")
    assert upd.result == "abort"

