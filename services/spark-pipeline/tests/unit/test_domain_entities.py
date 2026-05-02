import pytest
from src.domain.entities.comment import Comment
from src.domain.entities.sentiment_prediction import SentimentPrediction


def test_comment_creation():
    c = Comment(id=1, texto="Great!", sentimiento="positivo", fecha="2026-05-01")
    assert c.id == 1
    assert c.texto == "Great!"
    assert c.sentimiento == "positivo"
    assert c.text_clean is None


def test_comment_with_text_clean():
    c = Comment(id=2, texto="Bad!", sentimiento="negativo", fecha="2026-05-01", text_clean="bad")
    assert c.text_clean == "bad"


def test_comment_frozen():
    c = Comment(id=1, texto="Great!", sentimiento="positivo", fecha="2026-05-01")
    with pytest.raises(AttributeError):
        c.texto = "changed"


def test_sentiment_prediction_creation():
    p = SentimentPrediction(
        comment_id=1,
        text_original="Great!",
        text_clean="great",
        prediction="positivo",
        confidence=0.95,
        probabilities={"positivo": 0.95, "negativo": 0.03, "neutral": 0.02},
        ingested_at="2026-05-01T12:00:00",
        model_version="v1.0.0",
    )
    assert p.prediction == "positivo"
    assert p.confidence == 0.95
    assert len(p.probabilities) == 3


def test_sentiment_prediction_frozen():
    p = SentimentPrediction(
        comment_id=1,
        text_original="Great!",
        text_clean="great",
        prediction="positivo",
        confidence=0.95,
        probabilities={"positivo": 0.95},
        ingested_at="2026-05-01T12:00:00",
        model_version="v1.0.0",
    )
    with pytest.raises(AttributeError):
        p.prediction = "negativo"
