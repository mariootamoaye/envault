"""Profile support: named vaults (e.g. dev, staging, prod)."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_PROFILE = "default"
_ENV_VAR = "ENVAULT_PROFILE"


def get_profile_name(override: str | None = None) -> str:
    """Return active profile name (CLI flag > env var > default)."""
    if override:
        return override
    return os.environ.get(_ENV_VAR, DEFAULT_PROFILE)


def vault_path_for_profile(base_dir: Path, profile: str) -> Path:
    """Return the vault file path for a given profile."""
    base_dir.mkdir(parents=True, exist_ok=True)
    if profile == DEFAULT_PROFILE:
        return base_dir / "vault.enc"
    return base_dir / f"vault.{profile}.enc"


def list_profiles(base_dir: Path) -> list[str]:
    """List all profiles that have a vault file in *base_dir*."""
    if not base_dir.exists():
        return []
    profiles: list[str] = []
    for p in sorted(base_dir.iterdir()):
        if p.suffix == ".enc" and p.stem.startswith("vault"):
            stem = p.stem  # vault  or  vault.<profile>
            parts = stem.split(".", 1)
            profiles.append(parts[1] if len(parts) == 2 else DEFAULT_PROFILE)
    return profiles
