import json
from datetime import date
from pathlib import Path

from .models import Problem, Solution


def write_solution(root: str, problem: Problem, solution: Solution, run_date: date | None = None) -> Path:
    destination = Path(root) / (run_date or date.today()).isoformat()
    destination.mkdir(parents=True, exist_ok=True)
    markdown = f"""# {solution.title}

URL: {solution.url}

## Explanation
{solution.explanation}

## Complexity
- Time: {solution.time_complexity}
- Space: {solution.space_complexity}

## Python implementation
```python
{solution.implementation}
```

## Example tests
```python
{solution.tests or '# No tests were supplied.'}
```
"""
    (destination / "solution.md").write_text(markdown, encoding="utf-8")
    metadata = {"title": problem.title, "url": problem.url, "source": problem.source, "examples": problem.examples}
    (destination / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return destination