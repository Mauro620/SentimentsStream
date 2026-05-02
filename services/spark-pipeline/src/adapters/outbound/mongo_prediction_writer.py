from typing import List, Any
from pyspark.sql import DataFrame
from src.domain.ports.prediction_sink import PredictionSink
from src.domain.entities.sentiment_prediction import SentimentPrediction


class MongoPredictionWriter(PredictionSink):
    """Implements PredictionSink port for batch use cases."""

    def __init__(self, mongo_uri: str = "mongodb://mongo:27017/sentimentstream.predictions"):
        self._mongo_uri = mongo_uri

    def write(self, prediction: SentimentPrediction) -> None:
        from pymongo import MongoClient
        client = MongoClient(self._mongo_uri)
        db = client.get_database()
        collection = db["predictions"]
        collection.insert_one({
            "comment_id": prediction.comment_id,
            "text_original": prediction.text_original,
            "text_clean": prediction.text_clean,
            "prediction": prediction.prediction,
            "confidence": prediction.confidence,
            "probabilities": prediction.probabilities,
            "ingested_at": prediction.ingested_at,
            "model_version": prediction.model_version,
        })
        client.close()

    def write_batch(self, predictions: List[SentimentPrediction]) -> None:
        from pymongo import MongoClient
        client = MongoClient(self._mongo_uri)
        db = client.get_database()
        collection = db["predictions"]
        docs = [
            {
                "comment_id": p.comment_id,
                "text_original": p.text_original,
                "text_clean": p.text_clean,
                "prediction": p.prediction,
                "confidence": p.confidence,
                "probabilities": p.probabilities,
                "ingested_at": p.ingested_at,
                "model_version": p.model_version,
            }
            for p in predictions
        ]
        collection.insert_many(docs, ordered=False)
        client.close()


def write_mongo_batch(batch_df: DataFrame, batch_id: Any) -> None:
    """ForeachBatch function to write Spark DataFrame to Mongo via PyMongo."""
    if batch_df.rdd.isEmpty():
        return

    import os
    from pymongo import MongoClient

    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://mongo:27017/sentimentstream?authSource=admin")
    client = MongoClient(mongo_uri)
    collection = client["sentimentstream"]["predictions"]

    rows = batch_df.collect()
    docs = [row.asDict() for row in rows]
    if docs:
        collection.insert_many(docs, ordered=False)
    client.close()
