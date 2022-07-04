from src.core.config import config as app_config
from src.core.logger import LOGGING

bind = "0.0.0.0:5000"
worker_class = "uvicorn.workers.UvicornWorker"
workers = app_config.GUNICORN_WORKERS
logconfig_dict = LOGGING

# doesn't work yet
# https://github.com/benoitc/gunicorn/issues/2339
reload = app_config.GUNICORN_RELOAD
