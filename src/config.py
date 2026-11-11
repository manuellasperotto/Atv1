from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
MYSQL_URL = os.getenv("MYSQL_URL", "").strip()
SQLITE_FILE = DATA_DIR / "festa_ifc.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE}"


def get_database_url() -> str:
    if APP_ENV == "production" and MYSQL_URL:
        return MYSQL_URL
    return SQLITE_URL


DATABASE_URL = get_database_url()
