"""Fungsi pembantu kecil yang dipakai di banyak tempat."""
import re
import unicodedata
from datetime import datetime, timezone

MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def utcnow() -> datetime:
    """Waktu UTC tanpa tzinfo (konsisten dengan kolom DateTime di database)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:90] or "artikel"


def strip_tags(html_text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html_text or "")).strip()


def timeago(moment: datetime) -> str:
    seconds = (utcnow() - moment).total_seconds()
    if seconds < 3600:
        return f"{max(int(seconds // 60), 1)} mnt lalu"
    if seconds < 86400:
        return f"{int(seconds // 3600)} jam lalu"
    if seconds < 30 * 86400:
        return f"{int(seconds // 86400)} hari lalu"
    return datefmt(moment)


def datefmt(moment: datetime) -> str:
    return f"{moment.day} {MONTHS[moment.month - 1]} {moment.year}"
