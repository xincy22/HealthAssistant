import logging
import os
from datetime import datetime

class LoggerManager:
    _instance = None
    _initialized = False
    _loggers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LoggerManager._initialized:
            os.makedirs('logs', exist_ok=True)
            LoggerManager._initialized = True

    @classmethod
    def get_logger(cls, name : str) -> logging.Logger:
        if '.' in name:
            name = name.split('.')[-1]
        
        if name not in cls._loggers:
            logger = logging.getLogger(f"HealthAssistant.{name}")
            logger.setLevel(logging.DEBUG)

            if not logger.handlers:
                file_handler, console_handler = cls._create_handlers(name)
                logger.addHandler(file_handler)
                logger.addHandler(console_handler)

            cls._loggers[name] = logger

        return cls._loggers[name]
    
    @staticmethod
    def _create_handlers(name : str) -> tuple[logging.Handler, logging.Handler]:
        log_file = os.path.join(
            'logs', 
            f'HealthAssistant_{name}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        return file_handler, console_handler
