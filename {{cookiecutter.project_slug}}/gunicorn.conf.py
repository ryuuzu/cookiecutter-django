import os

bind = "0.0.0.0:8000"

workers = int(os.environ.get("GUNICORN_WORKERS", "8"))
worker_class = "gthread"
threads = int(os.environ.get("GUNICORN_THREADS", "4"))
proc_name = os.environ.get("GUNICORN_PROCESS_NAME", "{{ cookiecutter.project_slug }}")

# Allow Reload for local development
reload = os.environ.get("GUNICORN_RELOAD", "False") == "True"