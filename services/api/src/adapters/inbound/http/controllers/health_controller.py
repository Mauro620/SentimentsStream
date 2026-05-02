from __future__ import annotations

from flask import Blueprint


def create_health_controller() -> Blueprint:
    bp = Blueprint("health", __name__)

    @bp.get("/health")
    def health():
        return "OK", 200

    return bp
