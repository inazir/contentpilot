#!/usr/bin/env python3
"""Regression test for structured logging timestamp formatting."""

import io
import logging
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from shared.logging import configure_logging, get_logger


def _timestamp_ok(line: str) -> bool:
    return bool(line and len(line) > 20 and line[0:20].count('-') >= 2 and line[10] == 'T' and line[19] == 'Z')


def test_structured_logging_format() -> None:
    """Ensure INFO and ERROR logs produce full ISO8601 timestamps."""
    logging.root.handlers[:] = []

    capture = io.StringIO()
    original_stdout = sys.stdout
    try:
        sys.stdout = capture
        configure_logging()
        logger = get_logger('test_logging_format')
        logger.info('job_start | module=%s | run_id=%s', 'test', 'abc123')
        try:
            raise RuntimeError('simulated failure')
        except RuntimeError as exc:
            logger.exception('job_error | module=%s | run_id=%s | error=%s', 'test', 'abc123', exc)
    finally:
        sys.stdout = original_stdout

    output = capture.getvalue().splitlines()
    assert any('[INFO] test_logging_format: job_start | module=test | run_id=abc123' in line for line in output), \
        'INFO log line must be present and formatted correctly.'
    assert any('[ERROR] test_logging_format: job_error | module=test | run_id=abc123 | error=simulated failure' in line for line in output), \
        'ERROR log line must be present and formatted correctly.'
    log_lines = [line for line in output if line.startswith('202') and '[INFO]' in line or line.startswith('202') and '[ERROR]' in line]
    assert log_lines, f'No structured log lines found. Output:\n{output}'
    assert all(_timestamp_ok(line) for line in log_lines), \
        f'Only structured log entries should start with full ISO8601 timestamps. Got:\n{log_lines}'


if __name__ == '__main__':
    test_structured_logging_format()
    print('All logging format assertions passed.')
