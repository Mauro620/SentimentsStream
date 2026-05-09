from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


class TimestampGenerator(ABC):
    """Port: deterministic temporal dispersion for bronze ingestion."""

    @abstractmethod
    def generate_batch(self, n: int) -> List[datetime]:
        """Return n datetimes. Must be deterministic for same (n, seed)."""
        pass
