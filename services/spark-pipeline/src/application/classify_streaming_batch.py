from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, current_timestamp, regexp_replace, lower
from pyspark.sql.types import FloatType
from pyspark.ml.linalg import Vector
from pyspark.ml.classification import NaiveBayesModel
from typing import Any
import uuid
import os


def _confidence_udf():
    from pyspark.sql.functions import udf
    def extract_max(prob: Vector) -> float:
        return float(max(prob))
    return udf(extract_max, FloatType())


def classify_batch(
    spark: SparkSession,
    batch_df: DataFrame,
    model_path: str = "data/models/v1.0.0",
    model_version: str = "v1.0.0",
) -> DataFrame:
    # Load persisted model
    from pyspark.ml import PipelineModel
    model = PipelineModel.load(model_path)

    # batch_df is DataFrame[String] from socket: has "value" col with raw text
    # Clean text: lowercase, strip punctuation (same as training)
    cleaned = batch_df.withColumn(
        "text_clean",
        regexp_replace(
            regexp_replace(lower(col("value")), r"[^\w\s]", ""), r"\s+", " "
        )
    )

    # Apply model
    predictions = model.transform(cleaned)

    # Confidence UDF: max of probability vector
    confidence_udf = _confidence_udf()
    result = predictions.withColumn("confidence", confidence_udf(col("probability")))

    # Generate comment_id (UUID) and timestamps
    from pyspark.sql.functions import udf
    from pyspark.sql.types import StringType
    id_udf = udf(lambda: str(uuid.uuid4()), StringType())

    # Build probabilities JSON
    from pyspark.sql.functions import to_json, struct

    mongo_df = result.select(
        id_udf().alias("_id"),
        col("value").alias("text_original"),
        col("text_clean"),
        col("predicted_label").alias("prediction"),
        col("confidence"),
        to_json(struct("probability")).alias("probabilities"),
        current_timestamp().alias("ingested_at"),
        lit(model_version).alias("model_version")
    )

    return mongo_df
