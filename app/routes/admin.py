"""Panel admin: login, daftar artikel, editor, refresh RSS."""
import hmac
import os

import nh3
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import Article, Category
from ..security import verify_csrf
from ..services.rss import refresh_feeds
from ..services.scheduler import refresh_in_background
from ..utils import slugify, utcnow

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.before_request
def guard():
    verify_csrf()
    if request.endpoint != "admin.login" and not session.get("admin"):
        return redirect(url_for("admin.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cfg = current_app.config
        user_ok = hmac.compare_digest(request.form.get("username", ""), cfg["ADMIN_USER"])
        pass_ok = hmac.compare_digest(request.form.get("password", ""), cfg["ADMIN_PASSWORD"])
        if user_ok and pass_ok:
            session.clear()
            session["admin"] = True
            return redirect(url_for("admin.dashboard"))
        flash("Username atau password salah.")
    return render_template("admin/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("public.index"))


@bp.route("/")
def dashboard():
    articles = Article.query.order_by(Article.updated_at.desc()).all()
    return render_template("admin/dashboard.html", articles=articles)


@bp.route("/refresh", methods=["POST"])
def refresh():
    if os.getenv("VERCEL"):  # thread latar belakang dimatikan setelah response di serverless
        flash(f"RSS selesai diambil: {refresh_feeds()} berita baru.")
    else:
        refresh_in_background(current_app._get_current_object())
        flash("Refresh RSS dimulai di latar belakang. Muat ulang beranda beberapa saat lagi.")
    return redirect(url_for("admin.dashboard"))


def _unique_slug(base: str, exclude_id=None) -> str:
    slug, n = base, 2
    while (found := Article.query.filter_by(slug=slug).first()) and found.id != exclude_id:
        slug, n = f"{base}-{n}", n + 1
    return slug


def _apply_form(article: Article) -> None:
    form = request.form
    article.title = form["title"].strip()[:200]
    article.slug = _unique_slug(slugify(form.get("slug") or article.title), article.id)
    article.category_id = int(form["category_id"])
    article.tags = form.get("tags", "").strip()[:200]
    article.cover_url = form.get("cover_url", "").strip() or None
    article.excerpt = form.get("excerpt", "").strip()[:300]
    article.body = nh3.clean(form.get("body", ""))  # bersihkan HTML dari editor
    article.is_featured = "is_featured" in form
    new_status = "published" if form.get("status") == "published" else "draft"
    if new_status == "published" and not article.published_at:
        article.published_at = utcnow()
    article.status = new_status


@bp.route("/artikel/baru", methods=["GET", "POST"], defaults={"article_id": None})
@bp.route("/artikel/<int:article_id>/edit", methods=["GET", "POST"])
def editor(article_id):
    article = db.get_or_404(Article, article_id) if article_id else None
    if request.method == "POST":
        if not request.form.get("title", "").strip():
            flash("Judul wajib diisi.")
        else:
            article = article or Article()
            _apply_form(article)
            db.session.add(article)
            db.session.commit()
            flash("Artikel disimpan.")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/editor.html", article=article, categories=Category.query.order_by(Category.sort_order))


@bp.route("/artikel/<int:article_id>/toggle", methods=["POST"])
def toggle(article_id):
    article = db.get_or_404(Article, article_id)
    article.status = "draft" if article.status == "published" else "published"
    if article.status == "published" and not article.published_at:
        article.published_at = utcnow()
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@bp.route("/artikel/<int:article_id>/hapus", methods=["POST"])
def delete(article_id):
    db.session.delete(db.get_or_404(Article, article_id))
    db.session.commit()
    flash("Artikel dihapus.")
    return redirect(url_for("admin.dashboard"))
