from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional

from src.domain.ports import PredictionRepository


@dataclass(frozen=True)
class StatsResult:
    distribution: Dict[str, int]
    trend: List[Dict[str, object]]


def compute_stats(
    repo: PredictionRepository,
    start_date: Optional[date],
    end_date: Optional[date],
) -> StatsResult:
    data = repo.get_stats(start_date=start_date, end_date=end_date)
    distribution = data.get("distribution", {})
    trend = data.get("trend", [])
    return StatsResult(distribution=distribution, trend=trend)
