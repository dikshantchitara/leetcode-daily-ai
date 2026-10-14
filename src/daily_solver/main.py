import logging
import sys

from .config import Settings
from .provider import OpenAICompatibleProvider
from .source import ConfiguredProblemSource
from .validator import validate_solution
from .writer import write_solution


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        settings = Settings.from_env()
        problem = ConfiguredProblemSource(settings).get_problem()
        solution = OpenAICompatibleProvider(settings).generate(problem)
        validate_solution(solution)
        destination = write_solution(settings.output_root, problem, solution)
        logging.info("Validated solution written to %s", destination)
        return 0
    except Exception as error:
        logging.error("Daily solver failed: %s", error)
        return 1


if __name__ == "__main__":
    sys.exit(main())