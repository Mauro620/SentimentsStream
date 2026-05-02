from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from src.domain.entities import SentimentPrediction
from src.domain.ports import PredictionRepository


@dataclass(frozen=True)
class ListSentimentsResult:
    items: List[SentimentPrediction]
    next_cursor: Optional[str]


def list_sentiments(
    repo: PredictionRepository,
    sentiment: Optional[str],
    start_date: Optional[date],
    end_date: Optional[date],
    limit: int,
    cursor: Optional[str],
) -> ListSentimentsResult:
    items, next_cursor = repo.list_predictions(
        sentiment=sentiment,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        cursor=cursor,
    )
    return ListSentimentsResult(items=items, next_cursor=next_cursor)
