# Backup & Restore

envault can create compressed backups of your vault file and restore from them at any time.

## Commands

### Create a backup

```bash
envault backup create
```

Creates a gzipped snapshot of the current vault and saves it to `~/.envault/backups/` by default.

Options:
- `--profile NAME` — target a specific profile
- `--backup-dir PATH` — override the backup storage directory

Output example:
```
Backup created: /home/user/.envault/backups/vault_backup_20240601T120000Z.json.gz
```

---

### List backups

```bash
envault backup list
```

Lists all available backups, newest first.

Options:
- `--profile NAME`
- `--backup-dir PATH`

---

### Restore a backup

```bash
envault backup restore <backup_file>
```

Restores the vault from the given backup file. **This overwrites the current vault.** You will be prompted to confirm.

Options:
- `--profile NAME`

Example:
```bash
envault backup restore ~/.envault/backups/vault_backup_20240601T120000Z.json.gz
```

---

### Delete a backup

```bash
envault backup delete <backup_file>
```

Permanently removes a single backup file.

---

## Notes

- Backups are stored as gzipped JSON and remain encrypted — the vault password is required to read the values.
- Backup filenames include a UTC timestamp for easy identification.
- Use `envault snapshot` for in-app named snapshots; use `backup` for portable off-site copies.
