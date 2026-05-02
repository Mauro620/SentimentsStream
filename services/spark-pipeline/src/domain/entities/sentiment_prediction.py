from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SentimentPrediction:
    comment_id: int
    text_original: str
    text_clean: str
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    ingested_at: str
    model_version: str
