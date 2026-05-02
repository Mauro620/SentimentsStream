from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, Optional, Tuple

from src.domain.entities import SentimentPrediction


class PredictionRepository(ABC):
    @abstractmethod
    def list_predictions(
        self,
        sentiment: Optional[str],
        start_date: Optional[date],
        end_date: Optional[date],
        limit: int,
        cursor: Optional[str],
    ) -> Tuple[List[SentimentPrediction], Optional[str]]:
        raise NotImplementedError

    @abstractmethod
    def get_stats(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
    ) -> Dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def wordcloud(self, sentiment: str, top_n: int) -> List[Dict[str, object]]:
        raise NotImplementedError
