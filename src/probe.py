#!/usr/bin/env python3
"""
probe.py — OmniHeal deterministic directory scanner

Usage:
    python probe.py <target_dir>              # Summary stats to stdout
    python probe.py <target_dir> --list-files # One line per text file

Output (--list-files): 5 pipe-separated fields per line:
    path | type | size | complexity | depth

Complexity thresholds:
    > 50KB  → high   → deep
    > 5KB   → medium → standard
    <= 5KB  → low    → fast
"""
import sys
from pathlib import Path

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp",
    ".mp4", ".mp3", ".wav", ".avi", ".mov", ".mkv",
    ".zip", ".gz", ".tar", ".rar", ".7z", ".bz2",
    ".pdf", ".docx", ".xlsx", ".pptx", ".odt",
    ".exe", ".dll", ".so", ".dylib", ".bin",
    ".pyc", ".class", ".jar", ".wasm",
    ".db", ".sqlite", ".sqlite3",
    ".svg",
}

MAX_FILE_SIZE = 1024 * 1024  # 1MB


def _is_text_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return False
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return False
    except OSError:
        return False
    try:
        path.read_text(encoding="utf-8", errors="strict")
        return True
    except (UnicodeDecodeError, PermissionError, OSError):
        return False


def _estimate_complexity(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError:
        return "low"
    if size > 50_000:
        return "high"
    if size > 5_000:
        return "medium"
    return "low"


_DEPTH = {"high": "deep", "medium": "standard", "low": "fast"}


def _is_hidden(rel: Path) -> bool:
    return any(
        part.startswith(".") or part == "__pycache__"
        for part in rel.parts
    )


def _iter_files(target: Path):
    for p in sorted(target.rglob("*")):
        if p.is_dir():
            continue
        if _is_hidden(p.relative_to(target)):
            continue
        yield p


def _list_files(target: Path) -> None:
    for p in _iter_files(target):
        if not _is_text_file(p):
            continue
        rel = p.relative_to(target)
        size_kb = p.stat().st_size / 1024
        file_type = p.suffix.lstrip(".") or "text"
        complexity = _estimate_complexity(p)
        print(f"{rel} | {file_type} | {size_kb:.1f}KB | {complexity} | {_DEPTH[complexity]}")


def _summary(target: Path) -> None:
    text_count = 0
    binary_count = 0
    skip_count = 0

    for p in sorted(target.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(target)
        if _is_hidden(rel):
            skip_count += 1
            continue
        if _is_text_file(p):
            text_count += 1
        else:
            binary_count += 1

    print(f"目標目錄：{target}")
    print(f"純文字檔：{text_count} 個")
    print(f"二進位/過大：{binary_count} 個")
    print(f"跳過（隱藏/快取）：{skip_count} 個")
    print(f"總計：{text_count + binary_count + skip_count} 個")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python probe.py <target_dir> [--list-files]", file=sys.stderr)
        sys.exit(1)
    target = Path(sys.argv[1])
    if not target.exists():
        print(f"Error: does not exist: {target}", file=sys.stderr)
        sys.exit(1)
    if not target.is_dir():
        print(f"Error: not a directory: {target}", file=sys.stderr)
        sys.exit(1)
    if "--list-files" in sys.argv:
        _list_files(target)
    else:
        _summary(target)


if __name__ == "__main__":
    try:
        main()
    except (BrokenPipeError, OSError):
        sys.exit(0)
