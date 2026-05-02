import os
from pyspark.sql import SparkSession


def main() -> None:
    model_path: str = os.getenv("MODEL_PATH", "/app/data/models/v1.0.0")
    checkpoint_dir: str = "/app/data/checkpoints/"
    trigger_interval: str = "5 seconds"

    spark = (
        SparkSession.builder.appName("SentimentStream-Streaming")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setCheckpointDir(checkpoint_dir)

    # Load model once
    from pyspark.ml import PipelineModel

    model = PipelineModel.load(model_path)
    print(f"Model loaded from {model_path}")

    # Create socket stream
    from src.adapters.inbound.socket_stream_listener import create_socket_stream

    stream_df = create_socket_stream(spark, host="socket-producer", port=9999)
    print("Socket stream listening on socket-producer:9999")

    # Classify each micro-batch
    from src.application.classify_streaming_batch import classify_batch

    def process_batch(batch_df, batch_id):
        if batch_df.rdd.isEmpty():
            return
        result_df = classify_batch(spark, batch_df, model=model, model_path=model_path)
        # Write to Mongo via foreachBatch-compatible function
        from src.adapters.outbound.mongo_prediction_writer import write_mongo_batch

        write_mongo_batch(result_df, batch_id)
        print(f"Batch {batch_id}: wrote {result_df.count()} predictions to Mongo")

    query = (
        stream_df.writeStream.foreachBatch(process_batch)
        .trigger(processingTime=trigger_interval)
        .option("checkpointLocation", checkpoint_dir)
        .start()
    )

    print(
        f"Streaming query started. Checkpoint: {checkpoint_dir}, Trigger: {trigger_interval}"
    )
    query.awaitTermination()


if __name__ == "__main__":
    main()
