import argparse
import sys
from pyspark.sql import SparkSession


def main() -> None:
    parser = argparse.ArgumentParser(description="Train sentiment model")
    parser.add_argument(
        "--bronze-path", type=str, default="/app/data/bronze/comments_bronze.parquet"
    )
    parser.add_argument("--model-path", type=str, default="/app/data/models/v1.0.0")
    parser.add_argument(
        "--metrics-path", type=str, default="/app/data/models/v1.0.0/metrics.json"
    )
    args = parser.parse_args()

    spark = (
        SparkSession.builder.appName("SentimentStream-Train")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setCheckpointDir("/tmp/spark-checkpoints")

    try:
        from src.application.train_sentiment_model import train_model

        metrics = train_model(
            spark=spark,
            bronze_path=args.bronze_path,
            model_path=args.model_path,
            metrics_path=args.metrics_path,
        )
        print(f"Training complete. Metrics: {metrics}")
    except Exception as e:
        print(f"Training failed: {e}")
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
