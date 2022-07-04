from src.core.logger import LOGGING
from src.core.config import config as app_config


bind = "0.0.0.0:5000"
worker_class = "uvicorn.workers.UvicornWorker"
workers = app_config.GUNICORN_WORKERS
logconfig_dict = LOGGING
reload = app_config.GUNICORN_RELOAD