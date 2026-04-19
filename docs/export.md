# Exporting Secrets

The `export` command decrypts your vault and prints all secrets in a
shell-friendly format so you can source them into your current session.

## Usage

```bash
envault export [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-f, --format` | `dotenv` | Output format: `dotenv`, `bash`, or `fish` |
| `--vault` | `.envault` | Path to the vault file |
| `-o, --output` | *(stdout)* | Write output to a file instead of stdout |

## Formats

### dotenv

Compatible with tools like `dotenv`, `direnv`, and Docker Compose.

```
API_KEY='s3cr3t'
DB_URL='postgres://localhost/mydb'
```

### bash

Source directly in bash/zsh:

```bash
export API_KEY='s3cr3t'
export DB_URL='postgres://localhost/mydb'
```

```bash
# Load into current shell
source <(envault export --format bash)
```

### fish

For [Fish shell](https://fishshell.com/) users:

```fish
set -x API_KEY 's3cr3t'
set -x DB_URL 'postgres://localhost/mydb'
```

```fish
# Load into current shell
envault export --format fish | source
```

## Writing to a file

```bash
envault export --format dotenv --output .env
```

> **Warning:** The output file will contain plaintext secrets.
> Add it to `.gitignore` and handle it with care.
