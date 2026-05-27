#!/usr/bin/env python3
"""
Standardized module entrypoint for ContentPilot.

All modules expose main.py. `scripts/run_job.sh` calls:
    docker compose run --rm <module> python main.py [args]

This wrapper wires shared runtime lifecycle behavior around the existing runner.
"""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, "/app")

from shared.logging import configure_logging, get_logger
from shared.runtime import managed_run
from shared.notify import notify_failure

configure_logging()
logger = get_logger("daily_news.main")


def run(args: list[str]) -> int:
    """Run the existing runner module and return an exit code."""
    sys.argv = ["runner.py"] + args
    import runner
    runner.main()
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]

    try:
        with managed_run("daily_news") as ctx:
            run(args)
    except SystemExit as exc:
        code = int(exc.code) if exc.code is not None else 1
        if code != 0:
            notify_failure("daily_news", f"exit code {code}")
        sys.exit(code)
