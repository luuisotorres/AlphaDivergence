import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger with the given name.
    Logs to both console (stdout) and a rotating file.
    """
    logger = logging.getLogger(name)
    
    # If the logger has no handlers, configure it
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        # Determine log file path relative to the backend directory
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "app.log"
        
        # RotatingFileHandler: max 10MB per file, keep 5 backup files
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Prevent propagation to root logger to avoid double logging
        logger.propagate = False

    return logger
