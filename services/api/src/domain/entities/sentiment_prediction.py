from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass(frozen=True)
class SentimentPrediction:
    comment_id: int
    text_original: str
    text_clean: str
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    ingested_at: datetime
    model_version: str
    id: Optional[str] = None
