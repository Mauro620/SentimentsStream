import os
import pyarrow.parquet as pq
import pytest

BRONZE_PATH = "data/bronze/comments_bronze.parquet"
RAW_CSV = "data/raw/dataset_sentimientos_500.csv"


def test_bronze_parquet_exists_after_ingest():
    from src.application.ingest_csv_to_bronze import main
    main()
    assert os.path.exists(BRONZE_PATH), "Bronze parquet not created"


def test_bronze_has_500_rows():
    from src.application.ingest_csv_to_bronze import main
    main()
    table = pq.read_table(BRONZE_PATH)
    assert table.num_rows == 500, f"Expected 500 rows, got {table.num_rows}"


def test_bronze_has_required_columns():
    from src.application.ingest_csv_to_bronze import main
    main()
    table = pq.read_table(BRONZE_PATH)
    expected = {"id", "texto", "sentimiento", "fecha"}
    assert expected.issubset(set(table.column_names)), \
        f"Missing columns: {expected - set(table.column_names)}"


def test_bronze_id_is_monotonic():
    from src.application.ingest_csv_to_bronze import main
    main()
    table = pq.read_table(BRONZE_PATH)
    ids = table.column("id").to_pylist()
    assert ids == list(range(500)), "IDs not monotonic 0-499"


def test_bronze_sentimiento_renamed_from_etiqueta():
    from src.application.ingest_csv_to_bronze import main
    main()
    table = pq.read_table(BRONZE_PATH)
    assert "sentimiento" in table.column_names
    assert "etiqueta" not in table.column_names
