"""Value formatting helpers for envault.

Provides utilities to format vault values for display, including
truncation, type inference, and table rendering.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}


def infer_type(value: str) -> str:
    """Return a human-readable type label for a string value."""
    if value.lower() in _BOOL_TRUE | _BOOL_FALSE:
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    if value.startswith(("http://", "https://")):
        return "url"
    if len(value) >= 20 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=-_" for c in value):
        return "secret"
    return "str"


def truncate(value: str, max_len: int = 40, placeholder: str = "...") -> str:
    """Truncate a string to *max_len* characters, appending *placeholder* if cut."""
    if len(value) <= max_len:
        return value
    keep = max_len - len(placeholder)
    return value[:keep] + placeholder


def format_row(key: str, value: str, show_type: bool = False, max_val: int = 40) -> str:
    """Format a single key/value pair as a padded row string."""
    display = truncate(value, max_val)
    if show_type:
        return f"{key:<30}  {display:<42}  {infer_type(value)}"
    return f"{key:<30}  {display}"


def format_table(
    data: Dict[str, str],
    show_type: bool = False,
    max_val: int = 40,
) -> str:
    """Render a dict of key/value pairs as an aligned table string."""
    if not data:
        return "(empty)"
    rows: List[str] = []
    if show_type:
        header = f"{'KEY':<30}  {'VALUE':<42}  TYPE"
        rows.append(header)
        rows.append("-" * len(header))
    for key in sorted(data):
        rows.append(format_row(key, data[key], show_type=show_type, max_val=max_val))
    return "\n".join(rows)


def format_pairs(data: Dict[str, str]) -> List[Tuple[str, str, str]]:
    """Return list of (key, truncated_value, type) tuples sorted by key."""
    return [
        (k, truncate(data[k]), infer_type(data[k]))
        for k in sorted(data)
    ]
