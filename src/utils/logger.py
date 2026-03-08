"""
Production-ready structured logging module for Ask My Doc.
Implements a reusable custom logger class using structlog that
automatically outputs to console (text) and a unique run-specific file (JSON).
"""

import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
import structlog
from typing import Any, Dict


class AppLogger:
    """
    Custom Logger class that initializes localized logging.
    Generates a unique log file per run in the logs/ directory.
    Uses structlog for structured JSON logging.
    """
    _instance = None
    _configured = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._configured:
            return

        self._configure_structlog()
        self._configured = True

    def _configure_structlog(self):
        """Configures standard logging library and structlog pipeline."""
        if structlog.is_configured():
            return

        # 1. Ensure logs directory exists (logger is in src/utils/ now so we need 3 parents up)
        project_root = Path(__file__).resolve().parent.parent.parent
        logs_dir = project_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        # 2. Generate unique log file name: run_YYYY-MM-DD_HH-MM-SS.log
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._run_id = timestamp
        log_file_path = logs_dir / f"run_{timestamp}.log"

        # 3. Configure standard Python logging handlers
        file_handler = logging.FileHandler(filename=log_file_path, encoding="utf-8")
        console_handler = logging.StreamHandler(sys.stdout)

        # Initialize python basic logging
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler],
            format="%(message)s",
        )

        # 4. Define shared structlog processors
        shared_processors = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            # Add strict ISO 8601 UTC timestamps
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
        ]

        # 5. Configure structlog wrapper
        structlog.configure(
            processors=shared_processors + [
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # 6. Set formatters per handler (JSON for file, colored text for console)
        json_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(sort_keys=True),
            foreign_pre_chain=shared_processors,
        )
        
        console_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True),
            foreign_pre_chain=shared_processors,
        )

        file_handler.setFormatter(json_formatter)
        console_handler.setFormatter(console_formatter)

    @staticmethod
    def get_logger(name: str) -> structlog.BoundLogger:
        """
        Return a structlog logger bound to the given name.
        Supports adding dynamic contextual fields (e.g., logger.bind(user_id=123)).
        """
        # Ensure the singleton is initialized before returning a logger
        AppLogger()
        logger = structlog.get_logger(name)
        
        # Add a run tracker detail for this specific execution to all logs
        logger = logger.bind(
            run_id=AppLogger._instance._run_id
        )
        return logger


# Create a global instance backward-compatibility hook so that existing imports work easily
def get_logger(name: str) -> structlog.BoundLogger:
    """Wrapper function to return a configured structlog logger."""
    return AppLogger.get_logger(name)
