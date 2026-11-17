"""Menyiapkan database saat aplikasi pertama kali jalan."""
from pathlib import Path

from flask import current_app
from sqlalchemy import create_engine

from config.feeds import FEEDS

from ..extensions import db
from ..models import Category, Source

SEED_FILE = Path(__file__).resolve().parents[2] / "database" / "seed.sql"


def init_database() -> None:
    """Buat tabel + seed lewat koneksi direct (non-pooled) bila tersedia, sesuai praktik Neon."""
    direct_url = current_app.config.get("DATABASE_URL_UNPOOLED")
    engine = create_engine(direct_url, pool_pre_ping=True) if direct_url else db.engine
    try:
        db.metadata.create_all(engine)
        if not Category.query.first():
            run_sql_file(SEED_FILE, engine)
    finally:
        if direct_url:
            engine.dispose()
    sync_sources()


def run_sql_file(path: Path, engine) -> None:
    with engine.begin() as connection:
        for statement in path.read_text(encoding="utf-8").split(";\n"):
            if statement.strip():
                connection.exec_driver_sql(statement)


def sync_sources() -> None:
    """Samakan tabel sources dengan config/feeds.py (sumber di luar config dinonaktifkan)."""
    existing = {s.name: s for s in Source.query}
    configured = {feed["name"] for feed in FEEDS}
    for feed in FEEDS:
        source = existing.get(feed["name"]) or Source(name=feed["name"])
        source.feed_url, source.lang, source.is_active = feed["url"], feed["lang"], True
        db.session.add(source)
    for name, source in existing.items():
        if name not in configured:
            source.is_active = False
    db.session.commit()
