from datetime import datetime, timedelta
from random import Random
from typing import List, Optional

from src.domain.ports.timestamp_generator import TimestampGenerator


class DeterministicTimestampGenerator(TimestampGenerator):
    """Infra adapter: reproducible random dates across last N days."""

    def __init__(
        self,
        seed: int,
        days_back: int = 90,
        now: Optional[datetime] = None,
    ) -> None:
        self._seed = seed
        self._days_back = days_back
        self._now = now

    def generate_batch(self, n: int) -> List[datetime]:
        rng = Random(self._seed)
        now = self._now if self._now is not None else datetime.now()
        base = now - timedelta(days=self._days_back)
        total_seconds = self._days_back * 24 * 3600
        return [
            base + timedelta(seconds=rng.randint(0, total_seconds)) for _ in range(n)
        ]
