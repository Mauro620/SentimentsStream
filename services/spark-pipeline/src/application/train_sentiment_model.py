from pyspark.sql import SparkSession
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import StringIndexer
from pyspark.sql.functions import lower, regexp_replace, col
import json
import os
from datetime import datetime

from src.infrastructure.spark.ml_pipeline_builder import build_sentiment_pipeline


def train_model(
    spark: SparkSession,
    bronze_path: str = "data/bronze/comments_bronze.parquet",
    model_path: str = "data/models/v1.0.0",
    metrics_path: str = "data/models/v1.0.0/metrics.json",
) -> dict:
    # Read bronze data
    df = spark.read.parquet(bronze_path)

    # Clean text: lowercase, strip punctuation, accents
    df_clean = df.withColumn(
        "text_clean",
        regexp_replace(regexp_replace(lower(col("texto")), r"[^\w\s]", ""), r"\s+", " ").alias("text_clean")
    )

    # Fit StringIndexer to create label_idx for stratified split
    indexer = StringIndexer(inputCol="sentimiento", outputCol="label_idx", handleInvalid="skip")
    df_indexed = indexer.fit(df_clean).transform(df_clean)

    # Stratified 80/20 split using label_idx (per plan.md)
    label_counts = df_indexed.groupBy("label_idx").count().collect()
    fractions = {row["label_idx"]: 0.8 for row in label_counts}
    train_df = df_indexed.sampleBy("label_idx", fractions, seed=42)
    test_df = df_indexed.subtract(train_df)

    # Build and fit full pipeline (includes its own StringIndexer)
    pipeline = build_sentiment_pipeline()
    model = pipeline.fit(train_df)

    # Evaluate
    predictions = model.transform(test_df)
    evaluator_f1 = MulticlassClassificationEvaluator(
        labelCol="label_idx", predictionCol="prediction", metricName="f1"
    )
    evaluator_acc = MulticlassClassificationEvaluator(
        labelCol="label_idx", predictionCol="prediction", metricName="accuracy"
    )

    f1_score = evaluator_f1.evaluate(predictions)
    accuracy = evaluator_acc.evaluate(predictions)

    # Persist model
    os.makedirs(model_path, exist_ok=True)
    model.write().overwrite().save(model_path)

    # Save metrics
    metrics = {
        "model_version": "v1.0.0",
        "f1_score": f1_score,
        "accuracy": accuracy,
        "trained_at": datetime.now().isoformat(),
        "train_rows": train_df.count(),
        "test_rows": test_df.count(),
    }
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Model saved to {model_path}")
    print(f"F1 Score: {f1_score:.4f}, Accuracy: {accuracy:.4f}")

    return metrics
