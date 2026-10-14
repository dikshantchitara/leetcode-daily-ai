import json
from pathlib import Path
from typing import Any

from .models import Problem, Solution


class CatalogError(RuntimeError):
    pass


def load_completed(path: str) -> set[str]:
    completed_path = Path(path)
    if not completed_path.exists():
        return set()
    try:
        values = json.loads(completed_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CatalogError(f"Could not read completed-problems file {path}: {error}") from error
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise CatalogError("Completed-problems file must contain a JSON list of URLs")
    return {value.rstrip("/").lower() for value in values}


def load_catalog(path: str) -> list[tuple[Problem, Solution]]:
    catalog_path = Path(path)
    if not catalog_path.exists():
        return []
    try:
        entries = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CatalogError(f"Could not read solution catalog {path}: {error}") from error
    if not isinstance(entries, list):
        raise CatalogError("Solution catalog must contain a JSON list")

    result: list[tuple[Problem, Solution]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise CatalogError(f"Catalog entry {index} must be an object")
        try:
            problem = Problem(
                title=str(entry["title"]).strip(),
                url=str(entry["url"]).strip(),
                statement=str(entry.get("statement", "")).strip(),
                examples=entry.get("examples", []),
                source="catalog",
            )
            solution = Solution(
                title=problem.title,
                url=problem.url,
                explanation=str(entry["explanation"]).strip(),
                time_complexity=str(entry["time_complexity"]).strip(),
                space_complexity=str(entry["space_complexity"]).strip(),
                implementation=str(entry["implementation"]).strip(),
                tests=str(entry.get("tests", "")).strip(),
            )
        except (KeyError, TypeError) as error:
            raise CatalogError(f"Catalog entry {index} is missing a required field") from error
        if not all((problem.title, problem.url, solution.explanation, solution.time_complexity,
                    solution.space_complexity, solution.implementation)):
            raise CatalogError(f"Catalog entry {index} contains an empty required field")
        result.append((problem, solution))
    return result
