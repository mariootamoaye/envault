# Watch

The `watch` feature monitors a vault for changes and automatically re-runs a
command whenever the stored variables are updated.

## How it works

`envault.watch.watch()` polls the vault file at a configurable interval.  On
each tick it reloads the vault and compares a SHA-256 hash of the decrypted
contents against the previous hash.  When the hash differs the optional
`on_change` callback is invoked with the new env dict, and the supplied command
is executed via `subprocess.run`.

## API

```python
from envault.watch import watch

watch(
    store,          # VaultStore instance
    password,       # vault password
    command,        # list[str] — command to run on change
    interval=2.0,   # poll interval in seconds
    on_change=None, # optional callback(dict) -> None
)
```

## Example

```python
from pathlib import Path
from envault.store import VaultStore
from envault.watch import watch

store = VaultStore(Path(".envault"))
watch(store, "my-password", command=["make", "reload"], interval=5.0)
```

The process will block, sleeping for `interval` seconds between polls.  Send
`SIGINT` (Ctrl-C) to stop it.

## Notes

- The vault is **decrypted on every poll**, so a wrong password will raise
  immediately on the first iteration.
- Only the *decrypted values* are compared; metadata such as file timestamps
  are ignored.
- For CI or scripting use `max_iterations` to limit the number of polls.
