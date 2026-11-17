"""Mengambil berita dari RSS, mengkategorikan, lalu menyimpannya ke database."""
import html
import logging
import re
from datetime import datetime

import feedparser
import requests
from flask import current_app

from config.feeds import CATEGORY_RULES, DEFAULT_CATEGORY

from ..extensions import db
from ..models import Category, News, Source
from ..utils import strip_tags, utcnow

log = logging.getLogger(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NexusGameBot/1.0)"}
IMG_RE = re.compile(r"""<img[^>]+src=["']([^"']+)["']""", re.I)


def categorize(text: str) -> str:
    text = text.lower()
    for slug, pattern in CATEGORY_RULES:
        if re.search(pattern, text):
            return slug
    return DEFAULT_CATEGORY


def extract_image(entry) -> str | None:
    for key in ("media_content", "media_thumbnail"):
        for media in entry.get(key) or []:
            if media.get("url"):
                return media["url"][:1000]
    for link in entry.get("links", []):
        if link.get("type", "").startswith("image"):
            return link["href"][:1000]
    content = (entry.get("content") or [{}])[0].get("value", "") + entry.get("summary", "")
    match = IMG_RE.search(content)
    return match.group(1)[:1000] if match else None


def parse_date(entry) -> datetime:
    stamp = entry.get("published_parsed") or entry.get("updated_parsed")
    return min(datetime(*stamp[:6]), utcnow()) if stamp else utcnow()


def shorten(text: str, limit: int = 200) -> str:
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


def fetch_source(source: Source, category_ids: dict, known_urls: set) -> list[News]:
    response = requests.get(source.feed_url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    items = []
    for entry in feedparser.parse(response.content).entries[:30]:
        url = entry.get("link", "")
        if not url.startswith("http") or url in known_urls:
            continue
        known_urls.add(url)
        title = html.unescape(strip_tags(entry.get("title", "")))
        summary = html.unescape(strip_tags(entry.get("summary", "")))
        slug = categorize(f"{title} {summary}")
        items.append(News(
            source_id=source.id, category_id=category_ids[slug], title=title[:300],
            summary=shorten(summary), image_url=extract_image(entry), url=url[:1000],
            published_at=parse_date(entry),
        ))
    return items


def refresh_feeds() -> int:
    """Ambil semua feed aktif. Error satu feed tidak menghentikan feed lain."""
    category_ids = {c.slug: c.id for c in Category.query}
    known_urls = {url for (url,) in db.session.query(News.url)}
    added = 0
    for source in Source.query.filter_by(is_active=True).all():
        try:
            items = fetch_source(source, category_ids, known_urls)
            db.session.add_all(items)
            db.session.commit()
            added += len(items)
        except Exception as exc:  # noqa: BLE001 - satu feed rusak tidak boleh mematikan job
            db.session.rollback()
            log.warning("Feed %s dilewati: %s", source.name, exc)
    prune_old()
    return added


def prune_old() -> None:
    """Simpan hanya RSS_MAX_ITEMS berita terbaru."""
    cutoff = (db.session.query(News.published_at)
              .order_by(News.published_at.desc()).offset(current_app.config["RSS_MAX_ITEMS"]).limit(1).scalar())
    if cutoff:
        News.query.filter(News.published_at <= cutoff).delete()
        db.session.commit()
