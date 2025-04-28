# lib/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, log_folder: str = "logs", log_name: str = "agent.log"):
        os.makedirs(log_folder, exist_ok=True)
        log_path = os.path.join(log_folder, log_name)

        self.logger = logging.getLogger("ERPUpdateAgent")
        self.logger.setLevel(logging.DEBUG)

        handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger
