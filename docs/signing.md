# Vault Signing

envault can attach an **HMAC-SHA256 signature** to a vault so you can detect
unauthorised or accidental modifications between sessions.

## How it works

When you sign a vault, envault:

1. Serialises the vault data to a canonical, deterministic JSON string
   (keys sorted, no extra whitespace).
2. Computes `HMAC-SHA256(canonical_json, secret)` using your chosen secret.
3. Writes the hex digest to `.vault.sig` in the same directory as the vault
   file.

Verification re-derives the expected signature and performs a
constant-time comparison to prevent timing attacks.

## API

```python
from envault.signing import sign, verify, save_signature, verify_vault, clear_signature

data = {"API_KEY": "abc", "DB_URL": "postgres://localhost/dev"}
secret = "my-shared-secret"

# Compute a signature without persisting it
sig = sign(data, secret)

# Check a raw signature
ok = verify(data, secret, sig)  # True

# Persist next to the vault file
from pathlib import Path
vault_path = Path("/home/user/.envault/default.json")
save_signature(vault_path, data, secret)

# Verify the persisted signature
if not verify_vault(vault_path, data, secret):
    raise RuntimeError("Vault integrity check failed!")

# Remove the signature file
clear_signature(vault_path)
```

## Security notes

- The secret is **not** the vault password; use a separate value (e.g. a
  team-shared token or a CI secret).
- Signatures do **not** encrypt data — use `envault.crypto` for encryption.
- `.vault.sig` should be committed alongside the vault file when sharing
  signed vaults in version control.

## Functions

| Function | Description |
|---|---|
| `sign(data, secret)` | Return hex HMAC-SHA256 signature |
| `verify(data, secret, signature)` | Return `True` if signature matches |
| `save_signature(vault_path, data, secret)` | Persist signature to `.vault.sig` |
| `load_signature(vault_path)` | Load persisted signature or `None` |
| `verify_vault(vault_path, data, secret)` | Verify persisted signature |
| `clear_signature(vault_path)` | Delete the `.vault.sig` file |
