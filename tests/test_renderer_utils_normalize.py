from src.services.renderer_utils import wrap_text


def test_wrap_text_normalizes_unicode_dashes() -> None:
    class _FakeFont:
        def size(self, text: str):
            # pretend everything fits
            return (0, 0)

    lines = wrap_text("a—b a–b a−b a‑b", _FakeFont(), 999)
    assert lines == ["a-b a-b a-b a-b"]

