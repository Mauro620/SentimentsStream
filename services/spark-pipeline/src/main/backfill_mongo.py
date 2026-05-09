import os
import sys
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, lower, regexp_replace, to_timestamp


def main() -> None:
    bronze_path = os.getenv("BRONZE_PATH", "/app/data/bronze/comments_bronze.parquet")
    model_path = os.getenv("MODEL_PATH", "/app/data/models/v1.0.0")
    mongo_uri = os.getenv(
        "MONGO_URI", "mongodb://admin:root@mongo:27017/sentimentstream?authSource=admin"
    )

    spark = (
        SparkSession.builder.appName("SentimentStream-Backfill")
        .master("local[1]")
        .config("spark.driver.memory", "512m")
        .config("spark.executor.memory", "512m")
        .getOrCreate()
    )

    try:
        from pyspark.ml import PipelineModel
        from pyspark.ml.feature import StringIndexerModel

        model = PipelineModel.load(model_path)
        labels = []
        for stage in model.stages:
            lbls = getattr(stage, "labels", None)
            if isinstance(lbls, list) and lbls:
                labels = [str(label) for label in lbls]
                break
        if not labels:
            labels = ["negativo", "neutral", "positivo"]

        # Read bronze
        df = spark.read.parquet(bronze_path)

        # Clean text
        cleaned = df.withColumn(
            "text_clean",
            regexp_replace(
                regexp_replace(lower(col("texto")), r"[^\w\s]", ""), r"\s+", " "
            ),
        )

        # Rename for model compatibility
        ready = cleaned.withColumn("value", col("texto"))

        # Transform skipping StringIndexer
        result_df = ready
        for stage in model.stages:
            if not isinstance(stage, StringIndexerModel):
                result_df = stage.transform(result_df)

        # UDFs for mapping
        from pyspark.sql.functions import udf
        from pyspark.sql.types import FloatType, MapType, StringType

        def idx_to_label(idx):
            i = int(idx)
            return labels[i] if i < len(labels) else "unknown"

        def extract_max(prob):
            return float(max(prob))

        def to_map(prob):
            values = [float(x) for x in prob.toArray().tolist()]
            return {labels[i]: values[i] for i in range(min(len(labels), len(values)))}

        label_udf = udf(idx_to_label, StringType())
        confidence_udf = udf(extract_max, FloatType())
        probabilities_udf = udf(to_map, MapType(StringType(), FloatType()))

        result_df = result_df.withColumn(
            "predicted_label", label_udf(col("prediction"))
        ).withColumn("confidence", confidence_udf(col("probability")))

        # Preserve ingested_at from bronze
        if "ingested_at" in result_df.columns:
            ts_col = to_timestamp(col("ingested_at"))
        else:
            from pyspark.sql.functions import current_timestamp

            ts_col = current_timestamp()

        mongo_df = result_df.select(
            col("id").cast("long").alias("comment_id"),
            col("texto").alias("text_original"),
            col("text_clean"),
            col("predicted_label").alias("prediction"),
            col("confidence"),
            probabilities_udf(col("probability")).alias("probabilities"),
            ts_col.alias("ingested_at"),
            lit("v1.0.0").alias("model_version"),
        )

        # Write via pymongo to avoid mongo-spark-connector memory issues
        rows = mongo_df.collect()
        print(f"Backfilling {len(rows)} rows into MongoDB...")

        from pymongo import MongoClient

        client = MongoClient(mongo_uri)
        collection = client["sentimentstream"]["predictions"]
        collection.delete_many({})  # clear any stale data

        batch = []
        for row in rows:
            doc = row.asDict()
            # Ensure ingested_at is a Python datetime so pymongo stores BSON Date
            ingested_at = doc.get("ingested_at")
            if isinstance(ingested_at, str):
                doc["ingested_at"] = datetime.fromisoformat(ingested_at)
            batch.append(doc)

        if batch:
            collection.insert_many(batch)
            print(f"Inserted {len(batch)} predictions.")

        client.close()
        print("Backfill complete.")

    except Exception as e:
        print(f"Backfill failed: {e}")
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
