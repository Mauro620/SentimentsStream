from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
from typing import Optional

from flask import Blueprint, jsonify, request

from src.application.list_sentiments import list_sentiments
from src.domain.entities import SentimentPrediction
from src.domain.ports import PredictionRepository


def _serialize(item: SentimentPrediction) -> dict:
    d = asdict(item)
    if isinstance(d.get("ingested_at"), datetime):
        d["ingested_at"] = d["ingested_at"].isoformat()
    return d


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
            "items": [_serialize(item) for item in result.items],
            "next_cursor": result.next_cursor,
        }
        return jsonify(payload), 200

    return bp
