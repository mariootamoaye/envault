# Template Rendering

envault can render template files by substituting `${VAR}` placeholders with values stored in your vault.

## Syntax

Use `${VARIABLE_NAME}` in any text file. Variable names must match the pattern `[A-Z_][A-Z0-9_]*`.

```
# config.tpl
DATABASE_URL=${DB_URL}
SECRET_KEY=${SECRET_KEY}
DEBUG=false
```

## Commands

### `envault template render <file>`

Render a template file, printing the result to stdout.

```bash
envault template render config.tpl
```

Write output to a file:

```bash
envault template render config.tpl -o .env
```

By default, rendering fails if any referenced variable is missing from the vault. Use `--non-strict` to leave missing placeholders unchanged:

```bash
envault template render config.tpl --non-strict
```

### `envault template check <file>`

Check which variables referenced in a template are present in the vault without rendering.

```bash
envault template check config.tpl
```

Example output:

```
  ✓ DB_URL (ok)
  ✓ SECRET_KEY (ok)
  ✗ MISSING_VAR (missing)
Error: 1 variable(s) missing from vault.
```

## Profiles

Both commands accept `--profile` to select a named vault profile:

```bash
envault template render config.tpl --profile production
```
