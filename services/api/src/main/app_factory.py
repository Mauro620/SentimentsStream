from __future__ import annotations

import logging
import os

from flask import Flask, jsonify
from flask_caching import Cache
from flask_cors import CORS

from src.adapters.routes import register_routes
from src.infrastructure.ml.spark_model_loader import SparkModelLoader
from src.infrastructure.mongo.prediction_repository import MongoPredictionRepository

logger = logging.getLogger(__name__)

cache = Cache()


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 30

    CORS(app)
    cache.init_app(app)

    mongo_uri = os.getenv("MONGO_URI") or "mongodb://mongo:27017"
    model_path = os.getenv("MODEL_PATH") or "/app/data/models/v1.0.0"

    repo = MongoPredictionRepository(mongo_uri=mongo_uri)

    classifier = None
    try:
        classifier = SparkModelLoader(model_path=model_path)
    except Exception as exc:
        logger.warning("SparkModelLoader unavailable: %s — /predict disabled", exc)

    register_routes(app, repo, classifier)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "internal server error"}), 500

    return app
