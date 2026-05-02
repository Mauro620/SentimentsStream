from __future__ import annotations

from datetime import date
from typing import Optional

from flask import Blueprint, jsonify, request

from src.application.compute_stats import compute_stats
from src.domain.ports import PredictionRepository


def create_stats_controller(repo: PredictionRepository) -> Blueprint:
    bp = Blueprint("stats", __name__)

    @bp.get("/stats")
    def get_stats():
        start_date_str: Optional[str] = request.args.get("from")
        end_date_str: Optional[str] = request.args.get("to")

        start_date = date.fromisoformat(start_date_str) if start_date_str else None
        end_date = date.fromisoformat(end_date_str) if end_date_str else None

        result = compute_stats(repo=repo, start_date=start_date, end_date=end_date)
        payload = {"distribution": result.distribution, "trend": result.trend}
        return jsonify(payload), 200

    return bp
