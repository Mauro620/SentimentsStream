from unittest.mock import MagicMock

import pytest

from src.application.predict_sentiment import PredictResult, predict_sentiment


def _mock_classifier(prediction="positivo", confidence=0.92, probs=None):
    if probs is None:
        probs = {"positivo": 0.92, "negativo": 0.05, "neutral": 0.03}
    c = MagicMock()
    c.predict.return_value = {
        "prediction": prediction,
        "confidence": confidence,
        "probabilities": probs,
    }
    return c


def test_returns_predict_result():
    result = predict_sentiment(_mock_classifier(), "excelente producto")
    assert isinstance(result, PredictResult)


def test_prediction_label_forwarded():
    result = predict_sentiment(_mock_classifier(prediction="negativo"), "horrible")
    assert result.prediction == "negativo"


def test_confidence_cast_to_float():
    result = predict_sentiment(_mock_classifier(confidence="0.88"), "ok")
    assert isinstance(result.confidence, float)
    assert result.confidence == pytest.approx(0.88)


def test_classifier_called_with_input_text():
    c = _mock_classifier()
    predict_sentiment(c, "muy bueno")
    c.predict.assert_called_once_with("muy bueno")


def test_empty_probs_handled():
    result = predict_sentiment(_mock_classifier(probs={}), "texto")
    assert result.probabilities == {}
