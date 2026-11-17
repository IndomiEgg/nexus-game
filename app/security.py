"""CSRF sederhana untuk form admin."""
import secrets

from flask import abort, request, session
from markupsafe import Markup


def csrf_token() -> str:
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


def csrf_field() -> Markup:
    return Markup(f'<input type="hidden" name="csrf" value="{csrf_token()}">')


def verify_csrf() -> None:
    if request.method == "POST" and request.form.get("csrf") != session.get("csrf"):
        abort(400, "Token CSRF tidak valid")
