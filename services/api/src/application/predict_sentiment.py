from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from src.domain.ports import SentimentClassifier


@dataclass(frozen=True)
class PredictResult:
    prediction: str
    confidence: float
    probabilities: Dict[str, float]


def predict_sentiment(classifier: SentimentClassifier, text: str) -> PredictResult:
    result = classifier.predict(text)
    return PredictResult(
        prediction=str(result.get("prediction")),
        confidence=float(result.get("confidence")),
        probabilities={
            str(k): float(v) for k, v in dict(result.get("probabilities", {})).items()
        },
    )
