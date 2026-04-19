# envault

> CLI tool to securely manage and sync environment variables across dev environments

---

## Installation

```bash
pip install envault
```

Or with pipx:

```bash
pipx install envault
```

---

## Usage

Initialize a new vault in your project:

```bash
envault init
```

Add and retrieve environment variables:

```bash
envault set DATABASE_URL "postgres://localhost:5432/mydb"
envault get DATABASE_URL
```

Push and pull variables across environments:

```bash
envault push --env production
envault pull --env staging
```

Export variables to a `.env` file:

```bash
envault export > .env
```

Run a command with your vaulted variables injected:

```bash
envault run -- python app.py
```

---

## Why envault?

- 🔒 Variables are encrypted at rest
- 🔄 Sync seamlessly across dev, staging, and production
- ⚡ Simple CLI interface with no overhead
- 🤝 Team-friendly sharing with access controls

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Contributions welcome — open an issue or submit a PR.*