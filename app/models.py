"""Model database. Index sengaja dibuat untuk query yang paling sering dipakai."""
from sqlalchemy import Index

from .extensions import db
from .utils import strip_tags, utcnow


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(60), nullable=False)
    hue = db.Column(db.Integer, nullable=False, server_default="240")  # warna gradient badge
    sort_order = db.Column(db.Integer, nullable=False, server_default="0")


class Source(db.Model):
    __tablename__ = "sources"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    feed_url = db.Column(db.String(500), nullable=False)
    lang = db.Column(db.String(5), nullable=False, server_default="en")
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.true())


class News(db.Model):
    """Berita agregasi dari RSS (hanya ringkasan + tautan ke sumber asli)."""

    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    summary = db.Column(db.String(300), nullable=False, server_default="")
    image_url = db.Column(db.String(1000))
    url = db.Column(db.String(1000), unique=True, nullable=False)  # anti-duplikat
    published_at = db.Column(db.DateTime, nullable=False)
    views = db.Column(db.Integer, nullable=False, server_default="0")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow, server_default=db.func.now())

    source = db.relationship(Source)
    category = db.relationship(Category)

    __table_args__ = (
        Index("ix_news_published_at", "published_at"),
        Index("ix_news_category_published", "category_id", "published_at"),
        Index("ix_news_source", "source_id"),
        Index("ix_news_views", "views"),
    )


class Article(db.Model):
    """Artikel orisinal yang ditulis lewat panel admin."""

    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    excerpt = db.Column(db.String(300), nullable=False, server_default="")
    body = db.Column(db.Text, nullable=False, server_default="")
    cover_url = db.Column(db.String(1000))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    tags = db.Column(db.String(200), nullable=False, server_default="")
    author = db.Column(db.String(80), nullable=False, server_default="Redaksi")
    is_featured = db.Column(db.Boolean, nullable=False, server_default=db.false())
    status = db.Column(db.String(10), nullable=False, server_default="draft")  # draft | published
    views = db.Column(db.Integer, nullable=False, server_default="0")
    published_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow, server_default=db.func.now())

    category = db.relationship(Category)

    __table_args__ = (
        Index("ix_articles_status_published", "status", "published_at"),
        Index("ix_articles_category_status", "category_id", "status"),
        Index("ix_articles_featured", "is_featured"),
        Index("ix_articles_views", "views"),
    )

    @property
    def reading_time(self) -> int:
        return max(1, len(strip_tags(self.body).split()) // 200)

    @property
    def tag_list(self) -> list[str]:
        return [t.strip() for t in self.tags.split(",") if t.strip()]
