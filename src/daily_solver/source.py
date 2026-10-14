import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from .models import Problem

LOGGER = logging.getLogger(__name__)


class ProblemSourceError(RuntimeError):
    pass


def _problem_from_payload(payload: dict[str, Any], source: str) -> Problem:
    required = ("title", "url", "statement")
    missing = [key for key in required if not str(payload.get(key, "")).strip()]
    if missing:
        raise ProblemSourceError(f"Problem source is missing: {', '.join(missing)}")
    examples = payload.get("examples", [])
    if not isinstance(examples, list):
        raise ProblemSourceError("Problem source field 'examples' must be a list")
    return Problem(
        title=str(payload["title"]).strip(),
        url=str(payload["url"]).strip(),
        statement=str(payload["statement"]).strip(),
        examples=examples,
        source=source,
    )


class ConfiguredProblemSource:
    """Load a user-authorized JSON feed, local JSON, or manually supplied URL."""

    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def get_problem(self) -> Problem:
        if self.settings.problem_source_url:
            parsed = urlparse(self.settings.problem_source_url)
            if parsed.scheme != "https":
                raise ProblemSourceError("DAILY_PROBLEM_SOURCE_URL must use HTTPS")
            LOGGER.info("Loading daily problem from configured HTTPS JSON source")
            response = requests.get(self.settings.problem_source_url, timeout=self.settings.request_timeout)
            response.raise_for_status()
            return _problem_from_payload(response.json(), self.settings.problem_source_url)

        if self.settings.problem_json_path:
            LOGGER.info("Loading daily problem from local JSON configuration")
            with Path(self.settings.problem_json_path).open(encoding="utf-8") as file:
                return _problem_from_payload(json.load(file), self.settings.problem_json_path)

        if self.settings.problem_url:
            LOGGER.info("Using manually configured problem URL")
            return Problem(
                title="LeetCode Daily Challenge",
                url=self.settings.problem_url,
                statement="Problem statement supplied by the configured AI provider or reviewer.",
                source="manual-url",
            )

        raise ProblemSourceError(
            "Configure DAILY_PROBLEM_SOURCE_URL, DAILY_PROBLEM_JSON_PATH, or DAILY_PROBLEM_URL"
        )