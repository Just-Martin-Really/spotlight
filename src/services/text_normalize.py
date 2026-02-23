"""Text normalization helpers.

Projector/venue machines often have limited font coverage. Even with better
fallback fonts, some Unicode punctuation (e.g., various dash/minus characters)
can render as squares.

We normalize a small set of common characters to safer ASCII equivalents at
render time.

Contract
- Input: arbitrary string
- Output: string safe for typical fonts
- Side effects: none
"""

from __future__ import annotations


_TRANSLATION_TABLE = str.maketrans(
    {
        # Dashes / minus-like
        "−": "-",  # U+2212 minus
        "–": "-",  # en dash
        "—": "-",  # em dash
        "‑": "-",  # non-breaking hyphen
        "‒": "-",  # figure dash
        "―": "-",  # horizontal bar
        # Common quote variants (optional but tends to help)
        "“": '"',
        "”": '"',
        "„": '"',
        "’": "'",
        "‘": "'",
        "‚": "'",
    }
)


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    return text.translate(_TRANSLATION_TABLE)

