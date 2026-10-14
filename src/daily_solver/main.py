import logging
import random
import sys
from datetime import date

from .catalog import load_catalog, load_completed

from .config import Settings
from .provider import OpenAICompatibleProvider
from .source import ConfiguredProblemSource
from .validator import validate_solution
from .writer import write_solution


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        settings = Settings.from_env()
        completed = load_completed(settings.completed_path)
        catalog = [
            entry for entry in load_catalog(settings.catalog_path)
            if entry[0].url.rstrip("/").lower() not in completed
        ]
        randomizer = random.Random(date.today().isoformat())
        randomizer.shuffle(catalog)
        selected = catalog[:settings.problem_count]

        if len(selected) < settings.problem_count:
            if not settings.ai_api_key:
                raise RuntimeError(
                    f"Catalog contains {len(selected)} problem(s), but "
                    f"{settings.problem_count} requested; configure AI_API_KEY or add catalog entries"
                )
            source = ConfiguredProblemSource(settings)
            for _ in range(settings.problem_count - len(selected)):
                problem = source.get_problem()
                selected.append((problem, OpenAICompatibleProvider(settings).generate(problem)))

        for problem, solution in selected:
            validate_solution(solution)
            destination = write_solution(settings.output_root, problem, solution)
            logging.info("Validated solution written to %s", destination)
        return 0
    except Exception as error:
        logging.error("Daily solver failed: %s", error)
        return 1


if __name__ == "__main__":
    sys.exit(main())