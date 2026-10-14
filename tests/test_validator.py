import pytest

from daily_solver.models import Solution
from daily_solver.validator import ValidationError, validate_solution


def solution(implementation: str, tests: str = "import unittest\nunittest.main()") -> Solution:
    return Solution("Title", "https://example.com", "Explanation", "O(n)", "O(1)", implementation, tests)


def test_valid_solution_and_tests_run():
    validate_solution(solution("def add(a, b):\n    return a + b", """import unittest\nfrom solution import add\nclass TestAdd(unittest.TestCase):\n    def test_example(self):\n        self.assertEqual(add(2, 3), 5)\nunittest.main()"""))


def test_invalid_syntax_is_rejected():
    with pytest.raises(ValidationError, match="syntax"):
        validate_solution(solution("def broken(:\n    pass"))


def test_failing_generated_test_is_rejected():
    with pytest.raises(ValidationError, match="tests failed"):
        validate_solution(solution("def add(a, b):\n    return a + b", """import unittest\nfrom solution import add\nclass TestAdd(unittest.TestCase):\n    def test_example(self):\n        self.assertEqual(add(2, 2), 5)\nunittest.main()"""))