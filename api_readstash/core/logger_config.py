import logging

from core.config import BASE_DIR


def setup_logger(log_name: str):
    logger = logging.getLogger(name=log_name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s ')

        file_handler = logging.FileHandler(BASE_DIR / 'logs' / f'{log_name}.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
