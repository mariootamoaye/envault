# Password Rotation

envault supports rotating the master password used to encrypt your vault without losing any stored secrets.

## Usage

```bash
envault rotate
```

You will be prompted for:
1. The **current** master password (to decrypt existing secrets).
2. The **new** master password (entered twice for confirmation).

All secrets are re-encrypted under the new password atomically.

## Profile-specific rotation

```bash
envault rotate --profile staging
```

This rotates only the `staging` profile vault.

## Security notes

- The old password is never stored; it is used in-memory only during rotation.
- The new password must differ from the current one.
- A fresh derived key (via Argon2/PBKDF2) is generated for the new password.
- If the process is interrupted the original vault file remains intact until the new file is fully written.

## Audit log

A `rotate` event is recorded in the audit log after a successful rotation:

```
2024-06-01T12:00:00Z  rotate  (all keys)
```
