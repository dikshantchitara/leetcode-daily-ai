import json
import logging
import time
from typing import Any

import requests

from .models import Problem, Solution

LOGGER = logging.getLogger(__name__)


class ProviderError(RuntimeError):
    pass


class OpenAICompatibleProvider:
    def __init__(self, settings: Any) -> None:
        if not settings.ai_api_key:
            raise ProviderError("AI_API_KEY is not configured")
        self.settings = settings

    def generate(self, problem: Problem) -> Solution:
        prompt = {
            "title": problem.title,
            "url": problem.url,
            "statement": problem.statement,
            "examples": problem.examples,
        }
        system = (
            "You are a careful Python 3.12 algorithm engineer. Return only valid JSON with keys "
            "title, url, explanation, time_complexity, space_complexity, implementation, tests. "
            "The implementation must be complete Python source. Tests must be a self-contained "
            "Python unittest script importing solution.py; use only safe deterministic examples."
        )
        body = {"model": self.settings.ai_model, "temperature": 0.1, "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(prompt)},
        ]}
        headers = {"Authorization": "Bearer " + self.settings.ai_api_key, "Content-Type": "application/json"}
        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries + 1):
            try:
                response = requests.post(
                    self.settings.ai_api_url,
                    headers=headers,
                    json=body,
                    timeout=self.settings.request_timeout,
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                return _parse_solution(content, problem)
            except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
                last_error = error
                if attempt < self.settings.max_retries:
                    delay = 2**attempt
                    LOGGER.warning("AI request failed (attempt %d); retrying in %ds", attempt + 1, delay)
                    time.sleep(delay)
        raise ProviderError(f"AI generation failed after retries: {last_error}") from last_error


def _parse_solution(content: str, problem: Problem) -> Solution:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    data: dict[str, Any] = json.loads(cleaned)
    values = {key: str(data.get(key, "")).strip() for key in (
        "title", "url", "explanation", "time_complexity", "space_complexity", "implementation", "tests"
    )}
    if any(not values[key] for key in ("title", "url", "explanation", "time_complexity", "space_complexity", "implementation")):
        raise ProviderError("AI response omitted a required solution field")
    return Solution(**values)