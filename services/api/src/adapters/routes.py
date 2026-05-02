from __future__ import annotations

from typing import Optional

from flask import Flask

from src.adapters.inbound.http.controllers.health_controller import (
    create_health_controller,
)
from src.adapters.inbound.http.controllers.predict_controller import (
    create_predict_controller,
)
from src.adapters.inbound.http.controllers.sentiments_controller import (
    create_sentiments_controller,
)
from src.adapters.inbound.http.controllers.stats_controller import (
    create_stats_controller,
)
from src.domain.ports import PredictionRepository, SentimentClassifier


def register_routes(
    app: Flask,
    repo: PredictionRepository,
    classifier: Optional[SentimentClassifier],
) -> None:
    app.register_blueprint(create_health_controller())
    app.register_blueprint(create_sentiments_controller(repo))
    app.register_blueprint(create_stats_controller(repo))
    if classifier is not None:
        app.register_blueprint(create_predict_controller(classifier))
