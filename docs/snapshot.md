# Snapshots

Snapshots let you capture the current state of a vault and restore it later.
This is useful before bulk edits, rotations, or risky imports.

## Commands

### Create a snapshot

```bash
envault snapshot create --label "before-deploy"
```

You will be prompted for your vault password. The snapshot is stored in
`.snapshots/` next to your vault file.

### List snapshots

```bash
envault snapshot list
```

Output example:

```
1718000000.json (before-deploy)  [5 keys]
1717990000.json                  [3 keys]
```

### Restore a snapshot

```bash
envault snapshot restore 1718000000.json
```

All keys stored in the snapshot will be written into the current vault,
encrypted with the password you provide at the prompt.

### Delete a snapshot

```bash
envault snapshot delete 1718000000.json
```

## Notes

- Snapshots store **decrypted** values in plain JSON. Protect the `.snapshots/`
  directory accordingly (it is recommended to add it to `.gitignore`).
- Restoring does **not** remove keys that exist in the vault but not in the
  snapshot; it only sets the keys present in the snapshot.
- Use `--profile` on any command to target a non-default profile.
