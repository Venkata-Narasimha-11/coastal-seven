"""Automated tests asserting code quality tools (Black, isort, Flake8, mypy) pass."""

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_black_code_formatting() -> None:
    """Ensure all app code adheres strictly to Black formatting standard."""
    result = subprocess.run(
        [sys.executable, "-m", "black", "--check", "app"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
    )
    assert (
        result.returncode == 0
    ), f"Black formatting violations:\n{result.stdout}\n{result.stderr}"


def test_isort_import_sorting() -> None:
    """Ensure all imports in app adhere to isort ordering standard."""
    result = subprocess.run(
        [sys.executable, "-m", "isort", "--check-only", "app"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
    )
    assert (
        result.returncode == 0
    ), f"isort violations:\n{result.stdout}\n{result.stderr}"


def test_flake8_linter_compliance() -> None:
    """Ensure app code has 0 Flake8 linting or complexity violations."""
    result = subprocess.run(
        [sys.executable, "-m", "flake8", "app"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
    )
    assert (
        result.returncode == 0
    ), f"Flake8 violations:\n{result.stdout}\n{result.stderr}"


def test_mypy_static_type_safety() -> None:
    """Ensure app code passes static type checking with Mypy."""
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "app"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
    )
    assert (
        result.returncode == 0
    ), f"Mypy type errors:\n{result.stdout}\n{result.stderr}"
