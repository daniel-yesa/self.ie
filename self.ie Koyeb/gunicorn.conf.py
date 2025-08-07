import os

workers = int(os.getenv("WEB_CONCURRENCY", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "1"))
keepalive = 30
graceful_timeout = 30
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"
