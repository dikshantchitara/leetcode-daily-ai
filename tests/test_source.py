from types import SimpleNamespace

import pytest

from daily_solver.source import ConfiguredProblemSource, ProblemSourceError


def settings(**values):
    defaults = dict(problem_source_url=None, problem_url=None, problem_json_path=None, request_timeout=2)
    defaults.update(values)
    return SimpleNamespace(**defaults)


def test_manual_url_fallback():
    problem = ConfiguredProblemSource(settings(problem_url="https://leetcode.com/problems/two-sum/")).get_problem()
    assert problem.source == "manual-url"
    assert problem.url.endswith("two-sum/")


def test_source_requires_configuration():
    with pytest.raises(ProblemSourceError, match="Configure"):
        ConfiguredProblemSource(settings()).get_problem()