import ast
import os
import resource
import subprocess
import sys
import tempfile
from pathlib import Path

from .models import Solution


class ValidationError(RuntimeError):
    pass


def _limit_child_resources() -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))


def validate_solution(solution: Solution, timeout_seconds: int = 10) -> None:
    try:
        ast.parse(solution.implementation)
        ast.parse(solution.tests or "import unittest\nunittest.main()")
    except SyntaxError as error:
        raise ValidationError(f"Generated Python has a syntax error: {error}") from error

    with tempfile.TemporaryDirectory(prefix="daily-solver-") as directory:
        root = Path(directory)
        (root / "solution.py").write_text(solution.implementation, encoding="utf-8")
        tests = solution.tests or "import unittest\nunittest.main()\n"
        (root / "test_solution.py").write_text(tests, encoding="utf-8")
        environment = {"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"}
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-S",
                    "-c",
                    "import os, runpy, sys; script = sys.argv[1]; sys.argv = [script]; sys.path.insert(0, os.path.dirname(script)); runpy.run_path(script, run_name='__main__')",
                    str(root / "test_solution.py"),
                ],
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                preexec_fn=_limit_child_resources,
            )
        except subprocess.TimeoutExpired as error:
            raise ValidationError("Generated tests exceeded the time limit") from error
        if result.returncode:
            output = (result.stdout + "\n" + result.stderr).strip()[-4000:]
            raise ValidationError(f"Generated tests failed:\n{output}")