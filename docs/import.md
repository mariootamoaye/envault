# Importing Environment Variables

`envault` can bulk-import variables from an existing `.env` file or directly
from the current shell environment.

## From a `.env` file

```bash
envault import file path/to/.env
```

By default, existing keys in the vault are **not** overwritten. Pass
`--overwrite` to replace them:

```bash
envault import file path/to/.env --overwrite
```

The command prints a summary:

```
Imported 5 variable(s), skipped 2.
```

## From the current environment

Import specific variables that are already set in your shell:

```bash
envault import env DATABASE_URL REDIS_URL SECRET_KEY
```

Only variables that actually exist in the environment are imported; missing
keys are silently skipped.

## Supported `.env` syntax

| Syntax | Supported |
|--------|-----------|
| `KEY=value` | ✅ |
| `export KEY=value` | ✅ |
| `KEY="quoted value"` | ✅ |
| `KEY='single quoted'` | ✅ |
| `# comment lines` | ✅ (ignored) |
| Blank lines | ✅ (ignored) |

## Vault path

All import commands accept `--vault <path>` (default: `.envault`) to target a
non-default vault file.
