# Profiles

envault supports **named profiles** so you can maintain separate vaults for different environments (e.g. `dev`, `staging`, `prod`) side-by-side.

## Active profile

The active profile is resolved in this order:

1. `--profile` CLI flag (where supported)
2. `ENVAULT_PROFILE` environment variable
3. Falls back to `default`

```bash
# Use the staging profile for a single command
ENVAULT_PROFILE=staging envault list
```

## Vault files

| Profile   | File                    |
|-----------|-------------------------|
| `default` | `~/.envault/vault.enc`  |
| `dev`     | `~/.envault/vault.dev.enc` |
| `staging` | `~/.envault/vault.staging.enc` |

## Commands

### List profiles

```bash
envault profile list
```

Prints all profiles that have a vault file, marking the currently active one.

### Copy a profile

```bash
envault profile copy dev staging
```

Copies all variables from the `dev` vault into `staging`. Both vaults must share the same master password.

## Tips

- Keep production secrets in a dedicated `prod` profile with a stronger password.
- Use `ENVAULT_PROFILE=dev` in your shell's rc file to set a per-shell default.
- Combine with `envault export` to inject variables into your shell session:

```bash
eval "$(ENVAULT_PROFILE=staging envault export bash)"
```
