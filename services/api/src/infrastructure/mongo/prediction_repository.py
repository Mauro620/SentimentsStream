from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from bson import ObjectId
from pymongo import DESCENDING, MongoClient

from src.domain.entities import SentimentPrediction
from src.domain.ports import PredictionRepository


class MongoPredictionRepository(PredictionRepository):
    def __init__(self, mongo_uri: str = "mongodb://mongo:27017") -> None:
        self._client = MongoClient(mongo_uri)
        self._db = self._client["sentimentstream"]
        self._collection = self._db["predictions"]

    def list_predictions(
        self,
        sentiment: Optional[str],
        start_date: Optional[date],
        end_date: Optional[date],
        limit: int,
        cursor: Optional[str],
    ) -> Tuple[List[SentimentPrediction], Optional[str]]:
        query: Dict[str, object] = {}
        if sentiment:
            query["prediction"] = sentiment
        if start_date or end_date:
            date_query: Dict[str, object] = {}
            if start_date:
                date_query["$gte"] = datetime.combine(start_date, datetime.min.time())
            if end_date:
                date_query["$lte"] = datetime.combine(end_date, datetime.max.time())
            query["ingested_at"] = date_query
        if cursor:
            query["_id"] = {"$lt": ObjectId(cursor)}

        docs = list(self._collection.find(query).sort("_id", DESCENDING).limit(limit))

        items = [self._to_entity(doc) for doc in docs]
        next_cursor = str(docs[-1]["_id"]) if docs else None
        return items, next_cursor

    def get_stats(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
    ) -> Dict[str, object]:
        match: Dict[str, object] = {}
        if start_date or end_date:
            date_query: Dict[str, object] = {}
            if start_date:
                date_query["$gte"] = datetime.combine(start_date, datetime.min.time())
            if end_date:
                date_query["$lte"] = datetime.combine(end_date, datetime.max.time())
            match["ingested_at"] = date_query

        distribution_pipeline = [
            {"$match": match} if match else {"$match": {}},
            {"$group": {"_id": "$prediction", "count": {"$sum": 1}}},
        ]

        trend_pipeline = [
            {"$match": match} if match else {"$match": {}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$ingested_at"}
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        distribution_docs = list(self._collection.aggregate(distribution_pipeline))
        trend_docs = list(self._collection.aggregate(trend_pipeline))

        distribution = {doc["_id"]: int(doc["count"]) for doc in distribution_docs}
        trend = [{"date": doc["_id"], "count": int(doc["count"])} for doc in trend_docs]

        return {"distribution": distribution, "trend": trend}

    def wordcloud(self, sentiment: str, top_n: int) -> List[Dict[str, object]]:
        pipeline = [
            {"$match": {"prediction": sentiment}},
            {"$project": {"tokens": {"$split": ["$text_clean", " "]}}},
            {"$unwind": "$tokens"},
            {
                "$group": {
                    "_id": "$tokens",
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": int(top_n)},
        ]
        docs = list(self._collection.aggregate(pipeline))
        return [{"word": doc["_id"], "count": int(doc["count"])} for doc in docs]

    def _to_entity(self, doc: Dict[str, object]) -> SentimentPrediction:
        ingested_at = doc.get("ingested_at")
        if isinstance(ingested_at, str):
            ingested_at = datetime.fromisoformat(ingested_at)
        return SentimentPrediction(
            id=str(doc.get("_id")),
            comment_id=int(doc.get("comment_id", 0)),
            text_original=str(doc.get("text_original", "")),
            text_clean=str(doc.get("text_clean", "")),
            prediction=str(doc.get("prediction", "")),
            confidence=float(doc.get("confidence", 0.0)),
            probabilities=dict(doc.get("probabilities", {})),
            ingested_at=ingested_at,
            model_version=str(doc.get("model_version", "")),
        )
