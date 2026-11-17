"""Pengaturan aplikasi. Semua nilai sensitif dibaca dari environment variable."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env.local")  # hasil `neon env pull`
load_dotenv(ROOT / ".env")


def _normalize(url: str) -> str:
    return url.replace("postgres://", "postgresql://", 1)


def _database_url() -> str:
    """Koneksi aplikasi: pakai URL pooled (-pooler) milik Neon untuk web app."""
    return _normalize(os.getenv("DATABASE_URL") or "sqlite:///nexus.db")


def _engine_options() -> dict:
    options = {"pool_pre_ping": True}
    if os.getenv("VERCEL"):  # serverless: jangan menahan koneksi antar-request
        from sqlalchemy.pool import NullPool
        options["poolclass"] = NullPool
    else:
        options["pool_recycle"] = 300  # Neon menidurkan compute saat sepi
    return options


class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "ganti-di-production")
    SQLALCHEMY_DATABASE_URI = _database_url()
    # Direct (non-pooled) URL dipakai hanya untuk membuat tabel / migrasi.
    DATABASE_URL_UNPOOLED = _normalize(os.getenv("DATABASE_URL_UNPOOLED", ""))
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options()

    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    SITE_NAME = "NEXUS.GAME"
    SITE_URL = os.getenv("SITE_URL", "").rstrip("/")

    RSS_INTERVAL_MINUTES = 30
    RSS_MAX_ITEMS = 500
    PER_PAGE = 12
    HOME_SECTIONS = ["pc", "console", "mobile", "esports", "review"]
