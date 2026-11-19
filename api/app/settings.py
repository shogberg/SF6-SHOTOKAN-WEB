"""Runtime settings, all from environment variables (no secrets in code or images)."""
import os

DB_PATH = os.environ.get("SHOTOKAN_DB", "/data/current.db")
STATIC_DIR = os.environ.get("SHOTOKAN_STATIC", "")            # built frontend; empty = API only (nginx serves it)
BASE_URL = os.environ.get("SHOTOKAN_BASE_URL", "/")
# optional shared login inside the app, for running without nginx: "user:sha256-hex-of-password"
AUTH = os.environ.get("SHOTOKAN_AUTH", "")
SUPPORTED_MAJOR = "1"
