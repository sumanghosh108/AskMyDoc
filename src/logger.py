"""
Structured logging module.
Configures structlog to output colorful text to console and JSON to a rotating log file.
"""

import sys
import logging
import logging.handlers
from pathlib import Path

import structlog

# Ensure logs directory exists
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "app.log"


def configure_logging():
    """Configures the standard logging library and structlog."""
    if structlog.is_configured():
        return

    # 1. Configure standard Python logging
    # Use a rotating file handler to prevent massive log files
    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
        format="%(message)s",
    )

    # 2. Add structlog formatting before sending to standard logging
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
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

    structlog.configure(
        processors=shared_processors + [
            # Prepare event dict for stdlib
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 3. Formatters: JSON for file, visually pleasing text for console
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


# Initialize configuration immediately upon import
configure_logging()


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a structlog logger bound to the given name."""
    return structlog.get_logger(name)
