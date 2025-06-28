import logging
import os
import sys
from logging.handlers import RotatingFileHandler

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler("logs/app_logs.log", maxBytes=10**6, backupCount=3)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)