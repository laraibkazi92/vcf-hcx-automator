import logging
import sys
import json
from typing import Any, Dict, Optional
from datetime import datetime
from rich.logging import RichHandler
from vcf_hcx_automator.config.constants import LOG_FORMAT, DEFAULT_LOG_LEVEL

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if hasattr(record, "correlation_id"):
            log_record["correlation_id"] = record.correlation_id # type: ignore

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)

def setup_logging(level: str = DEFAULT_LOG_LEVEL, json_format: bool = False) -> None:
    """
    Setup logging configuration.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    if json_format:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
    else:
        handler = RichHandler(rich_tracebacks=True, show_time=False, show_path=False)
        # RichHandler handles formatting, so we don't need to set a formatter for it
        # unless we want to customize it further. The default is usually good.
        # But let's set a simple one if needed.
        # Actually RichHandler ignores most of the formatter.

    root_logger.addHandler(handler)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    """
    return logging.getLogger(name)
