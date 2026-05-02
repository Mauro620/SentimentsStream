"""
Flask integration tests — no real Mongo or Spark required.
Both SparkModelLoader and MongoPredictionRepository are patched.
"""
import os
from unittest.mock import MagicMock, patch

import pytest

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("MODEL_PATH", "/tmp/no_model")

_SPARK_PATCH = "src.infrastructure.ml.spark_model_loader.SparkModelLoader.__init__"
_MONGO_PATCH = "src.infrastructure.mongo.prediction_repository.MongoPredictionRepository"


@pytest.fixture(scope="module")
def client():
    mock_repo = MagicMock()
    mock_repo.list_predictions.return_value = ([], None)
    mock_repo.get_stats.return_value = {"positivo": 0, "negativo": 0, "neutral": 0}

    with patch(_SPARK_PATCH, side_effect=RuntimeError("spark not available in CI")):
        with patch(_MONGO_PATCH, return_value=mock_repo):
            from src.main.app_factory import create_app

            app = create_app()
            app.config["TESTING"] = True
            with app.test_client() as c:
                yield c


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert b"OK" in resp.data


def test_unknown_route_returns_404(client):
    resp = client.get("/nonexistent")
    assert resp.status_code == 404


def test_sentiments_returns_200(client):
    resp = client.get("/sentiments")
    assert resp.status_code == 200


def test_predict_disabled_when_classifier_unavailable(client):
    resp = client.post("/predict", json={"text": "test"})
    assert resp.status_code == 404
