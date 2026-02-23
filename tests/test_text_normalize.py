from src.services.text_normalize import normalize_text


def test_normalize_text_dashes_and_quotes() -> None:
    assert normalize_text("a—b") == "a-b"
    assert normalize_text("a–b") == "a-b"
    assert normalize_text("a−b") == "a-b"
    assert normalize_text("a‑b") == "a-b"
    assert normalize_text("“hi”") == '"hi"'

