"""Template rendering: substitute vault variables into template strings."""
import re
from typing import Dict, List, Tuple

_VAR_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


class RenderError(Exception):
    pass


def find_variables(template: str) -> List[str]:
    """Return list of variable names referenced in template."""
    return _VAR_RE.findall(template)


def render_template(template: str, variables: Dict[str, str], strict: bool = True) -> str:
    """Replace ${VAR} placeholders with values from variables dict.

    Args:
        template: Template string with ${VAR} placeholders.
        variables: Mapping of variable name to value.
        strict: If True, raise RenderError for missing variables.

    Returns:
        Rendered string.
    """
    missing: List[str] = []

    def replacer(m: re.Match) -> str:
        name = m.group(1)
        if name in variables:
            return variables[name]
        missing.append(name)
        return m.group(0)

    result = _VAR_RE.sub(replacer, template)
    if strict and missing:
        raise RenderError(f"Missing variables: {', '.join(sorted(missing))}")
    return result


def render_file(path: str, variables: Dict[str, str], strict: bool = True) -> str:
    """Read a template file and render it."""
    with open(path) as fh:
        template = fh.read()
    return render_template(template, variables, strict=strict)


def check_template(template: str, variables: Dict[str, str]) -> List[Tuple[str, str]]:
    """Return list of (name, 'missing'|'ok') for each referenced variable."""
    results = []
    for name in find_variables(template):
        status = "ok" if name in variables else "missing"
        results.append((name, status))
    return results
