"""Shared logger factory for CLI batch scripts.

Most scripts under instagram_dm_mcp/scripts/ used to `print()` their
progress — which disappears when a batch runs unattended (cron,
launchd, `/loop`). This helper gives every script a logger that
writes to stdout AND, when `log_dir` is passed, to a timestamped
file under that directory.

Usage:

    from infra.common.logging_utils import get_logger
    log = get_logger("campaign", log_dir=Path("data/logs"))
    log.info("starting batch for %d accounts", len(accounts))
    log.exception("failed for %s", username)  # grabs stack trace
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path


_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def get_logger(
    name: str,
    log_dir: Path | None = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """Return a logger that writes to stdout plus an optional file.

    If `log_dir` is provided, a new file is created at
    `log_dir/{name}_{YYYY-MM-DD_HH-MM-SS}.log` (one per invocation, no
    collision between parallel runs).

    Idempotent: calling twice with the same name reuses the logger and
    doesn't duplicate handlers (useful when called from tests or
    repeated imports).
    """
    logger = logging.getLogger(name)
    if getattr(logger, "_configured_by_infra", False):
        return logger

    logger.setLevel(level)
    logger.propagate = False
    formatter = logging.Formatter(_FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_dir is not None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger._configured_by_infra = True  # type: ignore[attr-defined]
    return logger
