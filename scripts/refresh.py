"""Ambil RSS satu kali (dipakai GitHub Actions): python -m scripts.refresh"""
import os
import sys

os.environ.setdefault("DISABLE_SCHEDULER", "1")

if not os.getenv("DATABASE_URL"):
    sys.exit("DATABASE_URL belum diatur (isi sebagai secret di GitHub).")

from app import create_app  # noqa: E402
from app.services.rss import refresh_feeds  # noqa: E402

app = create_app()
with app.app_context():
    print(f"Berita baru: {refresh_feeds()}")
