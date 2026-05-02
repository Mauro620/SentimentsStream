from abc import ABC, abstractmethod
from typing import List
from ..entities.sentiment_prediction import SentimentPrediction


class PredictionSink(ABC):
    @abstractmethod
    def write(self, prediction: SentimentPrediction) -> None:
        pass

    @abstractmethod
    def write_batch(self, predictions: List[SentimentPrediction]) -> None:
        pass
