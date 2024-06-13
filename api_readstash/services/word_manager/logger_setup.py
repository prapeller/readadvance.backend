from pathlib import Path

from core.logger_config import setup_logger

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)
