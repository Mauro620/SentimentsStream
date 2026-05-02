from __future__ import annotations

import os

from flask import Blueprint, jsonify, request

from src.application.predict_sentiment import predict_sentiment
from src.domain.ports import SentimentClassifier


def create_predict_controller(classifier: SentimentClassifier) -> Blueprint:
    bp = Blueprint("predict", __name__)
    api_key = os.getenv("API_KEY")

    @bp.post("/predict")
    def post_predict():
        if api_key:
            header_key = request.headers.get("X-API-Key")
            if header_key != api_key:
                return jsonify({"error": "unauthorized"}), 401
        body = request.get_json(silent=True) or {}
        text = str(body.get("text", "")).strip()
        if not text:
            return jsonify({"error": "text required"}), 400

        result = predict_sentiment(classifier=classifier, text=text)
        return jsonify(result.__dict__), 200

    return bp
