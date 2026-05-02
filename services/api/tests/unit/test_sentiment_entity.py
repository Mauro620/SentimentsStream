from datetime import datetime

import pytest

from src.domain.entities.sentiment_prediction import SentimentPrediction


def _make(**kwargs):
    defaults = dict(
        comment_id=1,
        text_original="original",
        text_clean="clean",
        prediction="positivo",
        confidence=0.9,
        probabilities={"positivo": 0.9, "negativo": 0.1},
        ingested_at=datetime(2026, 1, 1, 0, 0),
        model_version="v1.0.0",
    )
    defaults.update(kwargs)
    return SentimentPrediction(**defaults)


def test_id_defaults_none():
    assert _make().id is None


def test_id_can_be_set():
    sp = _make(id="abc123")
    assert sp.id == "abc123"


def test_frozen_rejects_mutation():
    sp = _make()
    with pytest.raises(Exception):
        sp.prediction = "negativo"  # type: ignore


def test_probabilities_stored_correctly():
    probs = {"positivo": 0.7, "negativo": 0.2, "neutral": 0.1}
    sp = _make(probabilities=probs)
    assert sp.probabilities == probs
