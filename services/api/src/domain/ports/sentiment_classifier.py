from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict


class SentimentClassifier(ABC):
    @abstractmethod
    def predict(self, text: str) -> Dict[str, object]:
        raise NotImplementedError
