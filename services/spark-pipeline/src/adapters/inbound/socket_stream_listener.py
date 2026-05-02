from pyspark.sql import DataFrame, SparkSession


def create_socket_stream(
    spark: SparkSession,
    host: str = "socket-producer",
    port: int = 9999,
) -> DataFrame:
    return (
        spark.readStream.format("socket")
        .option("host", host)
        .option("port", port)
        .load()
    )
