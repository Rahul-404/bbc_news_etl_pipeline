import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory
os.makedirs("logs", exist_ok=True)
log_path = os.path.join("logs", "app.json")

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "service": getattr(record, 'service', None),
            "host": getattr(record, 'host', None),
            "stack_trace": getattr(record, 'stack_trace', None),
            "duration_ms": getattr(record, 'duration_ms', None)
        }
        return json.dumps(log_entry)

def get_logger(name="MyService"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = JSONFormatter()

        # Console Handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # Rotating File Handler
        fh = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,  # 5 MB per log file
            backupCount=5              # Keep last 5 log files
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
