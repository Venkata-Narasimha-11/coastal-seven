"""Tutorial 4: Code Quality & Formatting Pipeline Deep Dive.

Topics covered:
1. The 5 Pillars of Python Code Quality:
   - Black: Uncompromising, deterministic code formatter (PEP 8).
   - isort: Automatic sorting, grouping, and styling of imports.
   - Flake8: Linter checking PEP 8 violations, complexity, and syntax hazards.
   - Mypy: Static type checking for robust runtime prevention of TypeError.
   - Pre-commit: Git hook automation ensuring clean code before commits.
2. Configuration standards in pyproject.toml, .flake8, and .pre-commit-config.yaml.
3. Verification commands and automated CI/CD quality gates.
"""

import subprocess
import sys
from pathlib import Path

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure module importability
ROOT_DIR = Path(__file__).resolve().parent.parent


def run_tool_check(name: str, command: list[str]) -> bool:
    print(f"[*] Running {name}: {' '.join(command)}")
    res = subprocess.run(command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if res.returncode == 0:
        print(f"    -> [PASS] {name} passed with 0 errors!")
        return True
    else:
        print(f"    -> [FAIL] {name} reported issues:")
        output = (res.stdout + res.stderr).strip()
        for line in output.splitlines()[:10]:
            print(f"       {line}")
        return False


def main() -> None:
    print("=" * 70)
    print("AUTOMATED CODE QUALITY VERIFICATION PIPELINE")
    print("=" * 70)

    # 1. Black formatting verification
    black_ok = run_tool_check(
        "Black Formatter", [sys.executable, "-m", "black", "--check", "app"]
    )

    # 2. isort import sorting check
    isort_ok = run_tool_check(
        "isort Import Sorter", [sys.executable, "-m", "isort", "--check-only", "app"]
    )

    # 3. Flake8 linter check
    flake8_ok = run_tool_check("Flake8 Linter", [sys.executable, "-m", "flake8", "app"])

    # 4. Mypy static type checker
    mypy_ok = run_tool_check("Mypy Type Checker", [sys.executable, "-m", "mypy", "app"])

    print("\n" + "=" * 70)
    print("QUALITY PIPELINE SUMMARY:")
    print(f"  - Black (Formatting):    {'PASSED' if black_ok else 'FAILED'}")
    print(f"  - isort (Import Sort):   {'PASSED' if isort_ok else 'FAILED'}")
    print(f"  - Flake8 (Linting):      {'PASSED' if flake8_ok else 'FAILED'}")
    print(f"  - Mypy (Type Safety):    {'PASSED' if mypy_ok else 'FAILED'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
