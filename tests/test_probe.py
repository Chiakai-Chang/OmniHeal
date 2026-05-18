"""Tests for src/probe.py — run from OmniHeal root: python -m pytest tests/"""
import subprocess
import sys
import tempfile
from pathlib import Path


def run_probe(target_dir: str, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "src/probe.py", target_dir, *extra_args],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,  # OmniHeal root
    )


def test_list_files_excludes_known_binary_extensions():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "script.py").write_text("print('hello')")
        Path(tmpdir, "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        Path(tmpdir, "archive.zip").write_bytes(b"PK\x03\x04")

        result = run_probe(tmpdir, "--list-files")

        assert result.returncode == 0
        assert "script.py" in result.stdout
        assert "image.png" not in result.stdout
        assert "archive.zip" not in result.stdout


def test_list_files_output_has_five_pipe_separated_fields():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "small.py").write_text("x = 1\n")

        result = run_probe(tmpdir, "--list-files")

        assert result.returncode == 0
        lines = [ln for ln in result.stdout.strip().split("\n") if ln]
        assert len(lines) == 1
        fields = lines[0].split(" | ")
        assert len(fields) == 5, f"Expected 5 fields, got: {lines[0]!r}"
        _path, file_type, size, complexity, depth = fields
        assert "small.py" in _path
        assert file_type == "py"
        assert "KB" in size
        assert complexity in ("low", "medium", "high")
        assert depth in ("fast", "standard", "deep")


def test_complexity_low_maps_to_fast_depth():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "tiny.py").write_text("x = 1\n")  # tiny → low complexity

        result = run_probe(tmpdir, "--list-files")

        assert result.returncode == 0
        line = result.stdout.strip().split("\n")[0]
        assert line.endswith("fast")


def test_summary_mode_counts_text_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "a.py").write_text("x = 1")
        Path(tmpdir, "b.md").write_text("# doc")
        Path(tmpdir, "c.png").write_bytes(b"\x89PNG\r\n")

        result = run_probe(tmpdir)

        assert result.returncode == 0
        assert "純文字檔" in result.stdout
        assert "2" in result.stdout  # 2 text files


def test_hidden_directories_excluded():
    with tempfile.TemporaryDirectory() as tmpdir:
        hidden_dir = Path(tmpdir, ".git")
        hidden_dir.mkdir()
        (hidden_dir / "config").write_text("repositoryformatversion = 0")
        Path(tmpdir, "visible.py").write_text("x = 1")

        result = run_probe(tmpdir, "--list-files")

        assert result.returncode == 0
        assert "config" not in result.stdout
        assert "visible.py" in result.stdout


def test_error_on_nonexistent_directory():
    result = run_probe("/nonexistent/path/that/does/not/exist/xyz123")

    assert result.returncode != 0
    assert result.stderr


def test_list_files_excludes_files_larger_than_1mb():
    with tempfile.TemporaryDirectory() as tmpdir:
        big_file = Path(tmpdir, "huge.txt")
        big_file.write_bytes(b"x" * (1024 * 1024 + 1))  # 1MB + 1 byte
        small_file = Path(tmpdir, "small.txt")
        small_file.write_text("hello")

        result = run_probe(tmpdir, "--list-files")

        assert result.returncode == 0
        assert "small.txt" in result.stdout
        assert "huge.txt" not in result.stdout
