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
        from pyspark.ml.feature import StringIndexerModel

        df = self._spark.createDataFrame([(text,)], ["text"])
        result_df = df.selectExpr(
            "lower(regexp_replace(text, '[^\\\\w\\\\s]', '')) as text_clean"
        )

        for stage in self._model.stages:
            if not isinstance(stage, StringIndexerModel):
                result_df = stage.transform(result_df)

        row = result_df.select("prediction", "probability").collect()[0]
        prob = row["probability"]
        pred_idx = int(row["prediction"])
        label = (
            self._labels[pred_idx] if pred_idx < len(self._labels) else str(pred_idx)
        )
        probabilities = {
            self._labels[i]: float(prob[i])
            for i in range(min(len(self._labels), len(prob)))
        }
        return {
            "prediction": label,
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
