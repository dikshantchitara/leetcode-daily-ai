import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    problem_source_url: str | None
    problem_url: str | None
    problem_json_path: str | None
    ai_api_url: str
    ai_api_key: str
    ai_model: str
    output_root: str
    request_timeout: int
    max_retries: int

    @classmethod
    def from_env(cls) -> "Settings":
        api_url = os.getenv("AI_API_URL") or "https://api.openai.com/v1/chat/completions"
        model = os.getenv("AI_MODEL") or "gpt-4o-mini"
        return cls(
            problem_source_url=os.getenv("DAILY_PROBLEM_SOURCE_URL"),
            problem_url=os.getenv("DAILY_PROBLEM_URL"),
            problem_json_path=os.getenv("DAILY_PROBLEM_JSON_PATH"),
            ai_api_url=api_url,
            ai_api_key=os.getenv("AI_API_KEY", ""),
            ai_model=model,
            output_root=os.getenv("OUTPUT_ROOT", "solutions"),
            request_timeout=max(1, int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))),
            max_retries=max(0, min(5, int(os.getenv("MAX_RETRIES", "2")))),
        )