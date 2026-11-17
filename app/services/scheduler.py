"""Penjadwal pengambilan RSS (berjalan di thread latar belakang)."""
import threading
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from .rss import refresh_feeds


def _job(app) -> None:
    with app.app_context():
        refresh_feeds()


def start_scheduler(app) -> None:
    """Jalankan sekali saat start (agar situs tidak kosong), lalu tiap N menit."""
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(_job, "interval", args=[app], minutes=app.config["RSS_INTERVAL_MINUTES"],
                      next_run_time=datetime.now(), max_instances=1, coalesce=True)
    scheduler.start()


def refresh_in_background(app) -> None:
    threading.Thread(target=_job, args=[app], daemon=True).start()
