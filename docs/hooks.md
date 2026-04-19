# Hooks

envault supports shell hooks that fire automatically around vault operations.

## Supported Events

| Event | Fires |
|---|---|
| `pre-set` | Before a variable is written |
| `post-set` | After a variable is written |
| `pre-unset` | Before a variable is removed |
| `post-unset` | After a variable is removed |
| `post-import` | After a batch import completes |

## Hook Storage

Hooks are stored in `.envault-hooks.json` inside the vault directory. The file is plain JSON and can be committed to version control to share hooks with your team.

## Adding a Hook

```python
from pathlib import Path
from envault.hooks import add_hook

add_hook(Path(".vault"), "post-set", "make reload-env")
```

## Removing a Hook

```python
from envault.hooks import remove_hook

removed = remove_hook(Path(".vault"), "post-set", "make reload-env")
```

Returns `True` if the hook existed and was removed, `False` otherwise.

## Firing Hooks Manually

```python
from envault.hooks import fire

codes = fire(Path(".vault"), "post-set", env={"ENVAULT_KEY": "MY_VAR"})
```

Extra `env` keys are merged into the subprocess environment, letting hooks inspect which key triggered them.

## Example `.envault-hooks.json`

```json
{
  "post-set": ["make reload-env"],
  "post-import": ["./scripts/notify-team.sh"]
}
```

## Notes

- Commands run via the system shell (`sh -c`).
- All registered commands for an event run in order.
- Non-zero exit codes are collected and returned but do **not** abort the vault operation.
