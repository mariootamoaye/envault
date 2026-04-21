"""Value masking utilities for envault.

Provides helpers to mask sensitive values when displaying them,
with configurable reveal length and mask character.
"""

from __future__ import annotations

DEFAULT_MASK_CHAR = "*"
DEFAULT_REVEAL_CHARS = 4
MIN_LENGTH_FOR_PARTIAL = 8


def mask_value(
    value: str,
    reveal_chars: int = DEFAULT_REVEAL_CHARS,
    mask_char: str = DEFAULT_MASK_CHAR,
    full: bool = False,
) -> str:
    """Return a masked version of *value*.

    If *full* is True the entire value is masked regardless of length.
    For short values (< MIN_LENGTH_FOR_PARTIAL) the full value is masked
    to avoid leaking information through the revealed suffix.

    Examples::

        mask_value("supersecret")       -> "*******cret"
        mask_value("hi")                -> "**"
        mask_value("supersecret", full=True) -> "***********"
    """
    if not value:
        return ""
    if full or len(value) < MIN_LENGTH_FOR_PARTIAL:
        return mask_char * len(value)
    visible = value[-reveal_chars:]
    hidden_len = len(value) - reveal_chars
    return mask_char * hidden_len + visible


def mask_dict(
    data: dict[str, str],
    reveal_chars: int = DEFAULT_REVEAL_CHARS,
    mask_char: str = DEFAULT_MASK_CHAR,
    full: bool = False,
) -> dict[str, str]:
    """Return a copy of *data* with all values masked."""
    return {
        k: mask_value(v, reveal_chars=reveal_chars, mask_char=mask_char, full=full)
        for k, v in data.items()
    }


def format_masked_table(data: dict[str, str], reveal_chars: int = DEFAULT_REVEAL_CHARS) -> str:
    """Format a key/masked-value table suitable for terminal output."""
    if not data:
        return "(empty)"
    width = max(len(k) for k in data)
    lines: list[str] = []
    for key in sorted(data):
        masked = mask_value(data[key], reveal_chars=reveal_chars)
        lines.append(f"{key:<{width}}  {masked}")
    return "\n".join(lines)
