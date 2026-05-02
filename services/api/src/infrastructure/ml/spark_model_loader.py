from __future__ import annotations

from typing import Dict

from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession


class SparkModelLoader:
    def __init__(self, model_path: str = "/app/data/models/v1.0.0") -> None:
        self._model_path = model_path
        self._spark = (
            SparkSession.builder.master("local[1]")
            .appName("SentimentStream-API")
            .getOrCreate()
        )
        self._model = PipelineModel.load(self._model_path)
        self._labels = self._labels_from_model(self._model)

    def predict(self, text: str) -> Dict[str, object]:
        df = self._spark.createDataFrame([(text,)], ["text"])
        cleaned = df.selectExpr(
            "lower(regexp_replace(text, '[^\\\\w\\\\s]', '')) as text_clean"
        )
        predictions = self._model.transform(cleaned)
        label_col = "predicted_label" if "predicted_label" in predictions.columns else "prediction"
        row = predictions.select(label_col, "probability").collect()[0]
        prob = row["probability"]
        probabilities = {
            self._labels[i]: float(prob[i]) for i in range(min(len(self._labels), len(prob)))
        }
        return {
            "prediction": str(row[label_col]),
            "confidence": float(max(prob)),
            "probabilities": probabilities,
        }

    @staticmethod
    def _labels_from_model(model: PipelineModel) -> list[str]:
        for stage in model.stages:
            labels = getattr(stage, "labels", None)
            if isinstance(labels, list) and labels:
                return [str(label) for label in labels]
        return ["negativo", "neutral", "positivo"]
