#!/usr/bin/env python3
"""
Fail fast on invalid text encodings (e.g. UTF-16/null-byte files).
"""

from __future__ import annotations

import sys
from pathlib import Path


CHECK_SUFFIXES = {
    ".py",
    ".txt",
    ".md",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".ini",
    ".sh",
}

CHECK_FILENAMES = {
    "requirements.txt",
    ".env.example",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".next",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}


def should_check(path: Path) -> bool:
    return path.name in CHECK_FILENAMES or path.suffix.lower() in CHECK_SUFFIXES


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    data = path.read_bytes()

    if b"\x00" in data:
        errors.append("contains null bytes (likely UTF-16/binary)")
        return errors

    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        errors.append("contains UTF-16 BOM; expected UTF-8")
        return errors

    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"not valid UTF-8: {exc}")

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    violations: list[tuple[Path, str]] = []

    for path in repo_root.rglob("*"):
        if not path.is_file() or is_skipped(path):
            continue
        if not should_check(path):
            continue
        for issue in validate_file(path):
            violations.append((path.relative_to(repo_root), issue))

    if violations:
        print("ERROR: Text encoding validation failed.")
        for rel_path, issue in violations:
            print(f" - {rel_path}: {issue}")
        return 1

    print("OK: Text encoding validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
