from __future__ import annotations

from datetime import date
from typing import Optional

from flask import Blueprint, jsonify, request

from src.application.list_sentiments import list_sentiments
from src.domain.ports import PredictionRepository


def create_sentiments_controller(repo: PredictionRepository) -> Blueprint:
    bp = Blueprint("sentiments", __name__)

    @bp.get("/sentiments")
    def get_sentiments():
        sentiment: Optional[str] = request.args.get("sentiment")
        start_date_str: Optional[str] = request.args.get("from")
        end_date_str: Optional[str] = request.args.get("to")
        limit: int = min(int(request.args.get("limit", 100)), 1000)
        cursor: Optional[str] = request.args.get("cursor")

        start_date = date.fromisoformat(start_date_str) if start_date_str else None
        end_date = date.fromisoformat(end_date_str) if end_date_str else None

        result = list_sentiments(
            repo=repo,
            sentiment=sentiment,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            cursor=cursor,
        )

        payload = {
            "items": [item.__dict__ for item in result.items],
            "next_cursor": result.next_cursor,
        }
        return jsonify(payload), 200

    return bp
