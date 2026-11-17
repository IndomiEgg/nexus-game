"""Halaman publik."""
from flask import Blueprint, abort, current_app, redirect, render_template, request, Response
from sqlalchemy import update

from ..extensions import db
from ..models import Article, Category, News
from ..services import feed

bp = Blueprint("public", __name__)


def _per_page() -> int:
    return current_app.config["PER_PAGE"]


@bp.route("/")
def index():
    latest, has_more = feed.query_cards(per_page=_per_page())
    return render_template(
        "index.html", hero=feed.hero_cards(), originals=feed.original_cards(), latest=latest,
        has_more=has_more, sections=feed.category_sections(current_app.config["HOME_SECTIONS"]),
        trending=feed.trending_cards(),
    )


@bp.route("/kategori/<slug>")
def category(slug):
    cat = Category.query.filter_by(slug=slug).first_or_404()
    cards, has_more = feed.query_cards(category=slug, per_page=_per_page())
    return render_template("listing.html", heading=cat.name, cat=cat.slug, q="", cards=cards,
                           has_more=has_more, trending=feed.trending_cards())


@bp.route("/cari")
def search():
    q = request.args.get("q", "").strip()[:80]
    cards, has_more = feed.query_cards(text=q, per_page=_per_page()) if q else ([], False)
    return render_template("listing.html", heading=f"Hasil untuk “{q}”" if q else "Pencarian", cat="",
                           q=q, cards=cards, has_more=has_more, trending=feed.trending_cards())


@bp.route("/feed")
def feed_partial():
    """Potongan HTML untuk tombol 'Muat lebih banyak'."""
    page = max(request.args.get("page", 1, type=int), 1)
    cards, has_more = feed.query_cards(category=request.args.get("cat") or None,
                                       text=request.args.get("q") or None, page=page, per_page=_per_page())
    return render_template("_cards.html", cards=cards), 200, {"X-Has-More": "1" if has_more else "0"}


@bp.route("/artikel/<slug>")
def article(slug):
    item = Article.query.filter_by(slug=slug, status="published").first_or_404()
    db.session.execute(update(Article).where(Article.id == item.id).values(views=Article.views + 1))
    db.session.commit()
    return render_template("article.html", a=item, related=feed.related_articles(item))


@bp.route("/go/<int:news_id>")
def go(news_id):
    """Hitung klik (untuk Trending) lalu arahkan ke artikel di sumber asli."""
    item = db.session.get(News, news_id) or abort(404)
    db.session.execute(update(News).where(News.id == news_id).values(views=News.views + 1))
    db.session.commit()
    return redirect(item.url)


@bp.route("/tentang")
def about():
    return render_template("page.html", page="tentang")


@bp.route("/disclaimer")
def disclaimer():
    return render_template("page.html", page="disclaimer")


@bp.route("/robots.txt")
def robots():
    base = current_app.config["SITE_URL"] or request.url_root.rstrip("/")
    return Response(f"User-agent: *\nDisallow: /admin\nSitemap: {base}/sitemap.xml\n", mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap():
    base = current_app.config["SITE_URL"] or request.url_root.rstrip("/")
    paths = ["/", "/tentang", "/disclaimer"] + [f"/kategori/{c.slug}" for c in Category.query]
    paths += [f"/artikel/{a.slug}" for a in Article.query.filter_by(status="published")]
    urls = "".join(f"<url><loc>{base}{p}</loc></url>" for p in paths)
    return Response(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
                    mimetype="application/xml")
