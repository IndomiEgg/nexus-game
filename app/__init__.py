"""Application factory."""
import os

from flask import Flask

from config.settings import Settings

from .extensions import db
from .models import Source
from .security import csrf_field
from .services import feed
from .services.bootstrap import init_database
from .services.scheduler import start_scheduler
from .utils import datefmt, timeago


def create_app(overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Settings)
    app.config.update(overrides or {})
    db.init_app(app)

    from .routes import admin, public
    app.register_blueprint(public.bp)
    app.register_blueprint(admin.bp)

    app.add_template_filter(timeago)
    app.add_template_filter(datefmt)
    app.jinja_env.globals["csrf_field"] = csrf_field

    @app.context_processor
    def inject_globals():
        from .models import Category
        return {
            "site_name": app.config["SITE_NAME"],
            "nav_categories": Category.query.order_by(Category.sort_order).all(),
            "footer_sources": Source.query.filter_by(is_active=True).order_by(Source.name).all(),
            "ticker": feed.ticker_cards(),
        }

    with app.app_context():
        init_database()
    serverless = bool(os.getenv("VERCEL"))  # di serverless, RSS diambil GitHub Actions
    if not (app.config.get("TESTING") or serverless or os.getenv("DISABLE_SCHEDULER")):
        start_scheduler(app)
    return app
