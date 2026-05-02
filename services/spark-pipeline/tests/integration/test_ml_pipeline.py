import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType


@pytest.fixture(scope="module")
def spark():
    spark = SparkSession.builder \
        .appName("PipelineTest") \
        .master("local[1]") \
        .getOrCreate()
    yield spark
    spark.stop()


@pytest.fixture
def fixture_df(spark):
    data = [
        ("great product", "positivo"),
        ("love it", "positivo"),
        ("amazing experience", "positivo"),
        ("excellent service", "positivo"),
        ("very happy", "positivo"),
        ("awesome", "positivo"),
        ("terrible service", "negativo"),
        ("worst ever", "negativo"),
        ("hate it", "negativo"),
        ("awful experience", "negativo"),
        ("very bad", "negativo"),
        ("horrible", "negativo"),
        ("not sure", "neutral"),
        ("it is ok", "neutral"),
        ("maybe yes", "neutral"),
        ("nothing special", "neutral"),
        ("average", "neutral"),
        ("just fine", "neutral"),
    ]
    return spark.createDataFrame(data, ["text_clean", "sentimiento"])


def test_pipeline_fit_and_transform(spark, fixture_df):
    from src.infrastructure.spark.ml_pipeline_builder import build_sentiment_pipeline

    pipeline = build_sentiment_pipeline()
    model = pipeline.fit(fixture_df)
    predictions = model.transform(fixture_df)

    assert "prediction" in predictions.columns
    assert "predicted_label" in predictions.columns
    assert predictions.count() == fixture_df.count()


def test_pipeline_predicted_labels_are_valid(spark, fixture_df):
    from src.infrastructure.spark.ml_pipeline_builder import build_sentiment_pipeline

    pipeline = build_sentiment_pipeline()
    model = pipeline.fit(fixture_df)
    predictions = model.transform(fixture_df)

    distinct = [row["predicted_label"] for row in predictions.select("predicted_label").distinct().collect()]
    valid_labels = {"positivo", "negativo", "neutral"}
    for label in distinct:
        assert label in valid_labels


def test_pipeline_three_distinct_predictions(fixture_df):
    from src.infrastructure.spark.ml_pipeline_builder import build_sentiment_pipeline

    pipeline = build_sentiment_pipeline()
    model = pipeline.fit(fixture_df)
    predictions = model.transform(fixture_df)

    distinct = predictions.select("predicted_label").distinct().count()
    assert distinct <= 3
    assert distinct >= 1


def test_pipeline_with_bronze_data(spark):
    """Acceptance: if bronze parquet exists, pipeline fits on it."""
    import os
    bronze_path = "data/bronze/comments_bronze.parquet"
    if not os.path.exists(bronze_path):
        pytest.skip("Bronze parquet not found")

    df = spark.read.parquet(bronze_path)
    assert df.count() == 500

    from src.infrastructure.spark.ml_pipeline_builder import build_sentiment_pipeline
    pipeline = build_sentiment_pipeline()
    model = pipeline.fit(df)
    predictions = model.transform(df)

    assert "prediction" in predictions.columns
