"""Query gabungan berita agregasi + artikel orisinal, dalam bentuk Card seragam."""
from dataclasses import dataclass
from datetime import datetime

from flask import url_for
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from ..models import Article, Category, News


@dataclass
class Card:
    title: str
    summary: str
    image: str | None
    category: Category
    source: str
    href: str
    original: bool
    published_at: datetime
    views: int

    @property
    def external(self) -> bool:
        return not self.original


def _from_news(n: News) -> Card:
    return Card(n.title, n.summary, n.image_url, n.category, n.source.name,
                url_for("public.go", news_id=n.id), False, n.published_at, n.views)


def _from_article(a: Article) -> Card:
    return Card(a.title, a.excerpt, a.cover_url, a.category, "Original",
                url_for("public.article", slug=a.slug), True, a.published_at, a.views)


def _like(text: str) -> str:
    return "%" + text.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_") + "%"


def _news_query(category=None, text=None):
    query = News.query.options(joinedload(News.source), joinedload(News.category))
    if category:
        query = query.filter(News.category.has(slug=category))
    if text:
        like = _like(text)
        query = query.filter(or_(News.title.ilike(like, escape="\\"), News.summary.ilike(like, escape="\\")))
    return query


def _article_query(category=None, text=None):
    query = Article.query.options(joinedload(Article.category)).filter_by(status="published")
    if category:
        query = query.filter(Article.category.has(slug=category))
    if text:
        like = _like(text)
        query = query.filter(or_(Article.title.ilike(like, escape="\\"), Article.excerpt.ilike(like, escape="\\")))
    return query


def query_cards(category=None, text=None, page=1, per_page=12):
    """Satu halaman campuran berita + artikel, terbaru dulu. Return (cards, has_more)."""
    limit = page * per_page + 1
    news = _news_query(category, text).order_by(News.published_at.desc()).limit(limit).all()
    articles = _article_query(category, text).order_by(Article.published_at.desc()).limit(limit).all()
    cards = sorted([_from_news(n) for n in news] + [_from_article(a) for a in articles],
                   key=lambda c: c.published_at, reverse=True)
    start = (page - 1) * per_page
    return cards[start:start + per_page], len(cards) > start + per_page


def hero_cards(count=4):
    featured = _article_query().filter_by(is_featured=True).order_by(Article.published_at.desc()).limit(count)
    latest, _ = query_cards(per_page=count)
    unique = {}
    for card in [_from_article(a) for a in featured] + latest:
        unique.setdefault(card.href, card)
    return list(unique.values())[:count]


def original_cards(count=4):
    return [_from_article(a) for a in _article_query().order_by(Article.published_at.desc()).limit(count)]


def ticker_cards(count=10):
    return [_from_news(n) for n in _news_query().order_by(News.published_at.desc()).limit(count)]


def trending_cards(count=5):
    news = _news_query().order_by(News.views.desc(), News.published_at.desc()).limit(count).all()
    articles = _article_query().order_by(Article.views.desc(), Article.published_at.desc()).limit(count).all()
    cards = [_from_news(n) for n in news] + [_from_article(a) for a in articles]
    return sorted(cards, key=lambda c: (c.views, c.published_at), reverse=True)[:count]


def category_sections(slugs, per_section=4):
    categories = {c.slug: c for c in Category.query.filter(Category.slug.in_(slugs))}
    sections = [(categories[s], query_cards(category=s, per_page=per_section)[0]) for s in slugs if s in categories]
    return [(cat, cards) for cat, cards in sections if cards]


def related_articles(article: Article, count=3):
    query = _article_query().filter(Article.category_id == article.category_id, Article.id != article.id)
    return [_from_article(a) for a in query.order_by(Article.published_at.desc()).limit(count)]
