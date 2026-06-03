"""
ContentPilot scheduler service.

Entry point for the scheduler Docker service.  Initialises the DB,
loads schedules, starts APScheduler, and runs a heartbeat loop.
"""

import logging
import signal
import sys
import time

from apscheduler.schedulers.background import BackgroundScheduler

from shared.scheduler.models import init_scheduler_db, seed_default_schedule

logger = logging.getLogger(__name__)

_running = True


def _handle_signal(signum: int, _frame) -> None:
    global _running
    logger.info("Received signal %d — shutting down scheduler", signum)
    _running = False


def run_scheduler() -> None:
    """Initialise the DB, seed defaults, start APScheduler, and loop."""
    init_scheduler_db()
    seed_default_schedule()

    scheduler = BackgroundScheduler()
    # TODO: Load schedules from DB and register APScheduler jobs here
    scheduler.start()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    logger.info("Scheduler started — entering heartbeat loop")
    try:
        while _running:
            time.sleep(60)  # Heartbeat / polling loop
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler exiting")
    finally:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")


if __name__ == "__main__":
    run_scheduler()