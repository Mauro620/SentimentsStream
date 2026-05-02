from typing import Dict, List, Optional

from pyspark.ml import PipelineModel
from pyspark.ml.linalg import Vector
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    current_timestamp,
    lit,
    lower,
    monotonically_increasing_id,
    regexp_replace,
)
from pyspark.sql.types import FloatType, MapType, StringType


def _confidence_udf():
    from pyspark.sql.functions import udf

    def extract_max(prob: Vector) -> float:
        return float(max(prob))

    return udf(extract_max, FloatType())


def _labels_from_model(model: PipelineModel) -> List[str]:
    for stage in model.stages:
        labels = getattr(stage, "labels", None)
        if isinstance(labels, list) and labels:
            return [str(label) for label in labels]
    return ["negativo", "neutral", "positivo"]


def _label_udf(labels: List[str]):
    from pyspark.sql.functions import udf

    def idx_to_label(idx: float) -> str:
        i = int(idx)
        return labels[i] if i < len(labels) else "unknown"

    return udf(idx_to_label, StringType())


def _probabilities_udf(labels: List[str]):
    from pyspark.sql.functions import udf

    def to_map(prob: Vector) -> Dict[str, float]:
        values = [float(x) for x in prob.toArray().tolist()]
        return {labels[i]: values[i] for i in range(min(len(labels), len(values)))}

    return udf(to_map, MapType(StringType(), FloatType()))


def classify_batch(
    spark: SparkSession,
    batch_df: DataFrame,
    model: Optional[PipelineModel] = None,
    model_path: str = "/app/data/models/v1.0.0",
    model_version: str = "v1.0.0",
) -> DataFrame:
    from pyspark.ml.feature import StringIndexerModel

    if model is None:
        model = PipelineModel.load(model_path)

    labels = _labels_from_model(model)

    # Clean text: lowercase, strip punctuation (same as training)
    cleaned = batch_df.withColumn(
        "text_clean",
        regexp_replace(
            regexp_replace(lower(col("value")), r"[^\w\s]", ""), r"\s+", " "
        ),
    )

    # Skip StringIndexer — no label column available during streaming inference
    result_df = cleaned
    for stage in model.stages:
        if not isinstance(stage, StringIndexerModel):
            result_df = stage.transform(result_df)

    # Map numeric prediction index → string label
    label_udf = _label_udf(labels)
    confidence_udf = _confidence_udf()
    probabilities_udf = _probabilities_udf(labels)

    result_df = result_df.withColumn(
        "predicted_label", label_udf(col("prediction"))
    ).withColumn("confidence", confidence_udf(col("probability")))

    mongo_df = result_df.select(
        monotonically_increasing_id().cast("long").alias("comment_id"),
        col("value").alias("text_original"),
        col("text_clean"),
        col("predicted_label").alias("prediction"),
        col("confidence"),
        probabilities_udf(col("probability")).alias("probabilities"),
        current_timestamp().alias("ingested_at"),
        lit(model_version).alias("model_version"),
    )

    return mongo_df
