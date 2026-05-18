#!/usr/bin/env python3
"""
probe.py — OmniHeal deterministic directory scanner

Usage:
    python probe.py <target_dir>              # Summary stats to stdout
    python probe.py <target_dir> --list-files # One line per text file
    python probe.py <target_dir> --git-log    # All git commits (full history)

Output (--list-files): 5 pipe-separated fields per line:
    path | type | size | complexity | depth

Output (--git-log): one record per commit
    First line:  git_total_commits: N
    Per commit:  hash8 | YYYY-MM-DD | author_email | subject
    If body:     [body] first 300 chars (space-collapsed)

Complexity thresholds:
    > 50KB  → high   → deep
    > 5KB   → medium → standard
    <= 5KB  → low    → fast
"""
import subprocess
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


def _git_log(target: Path) -> None:
    _FS = "OMNI_FS"   # field separator — safe on all platforms
    _RS = "OMNI_RS"   # record separator
    fmt = f"%H{_FS}%ae{_FS}%as{_FS}%s{_FS}%b{_FS}{_RS}"
    try:
        result = subprocess.run(
            ["git", "log", "--all", f"--format={fmt}"],
            capture_output=True,
            text=True,
            cwd=target,
            timeout=120,
        )
    except FileNotFoundError:
        print("Warning: git not found in PATH", file=sys.stderr)
        return
    except subprocess.TimeoutExpired:
        print("Warning: git log timed out after 120s", file=sys.stderr)
        return

    if result.returncode != 0:
        err = result.stderr.strip()[:200]
        print(f"Warning: git error (not a git repo?): {err}", file=sys.stderr)
        return

    records = [r.strip() for r in result.stdout.split(_RS) if r.strip()]
    print(f"git_total_commits: {len(records)}")

    for block in records:
        fields = block.split(_FS)
        if len(fields) < 4:
            continue
        commit_hash = fields[0].strip()[:8]
        author = fields[1].strip()
        date = fields[2].strip()
        subject = fields[3].strip()
        body = fields[4].strip() if len(fields) > 4 else ""

        print(f"{commit_hash} | {date} | {author} | {subject}")
        if body:
            body_preview = " ".join(body.split())[:300]
            if body_preview:
                print(f"  [body] {body_preview}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python probe.py <target_dir> [--list-files|--git-log]", file=sys.stderr)
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
    elif "--git-log" in sys.argv:
        _git_log(target)
    else:
        _summary(target)


if __name__ == "__main__":
    try:
        main()
    except (BrokenPipeError, OSError):
        sys.exit(0)
