import pandas as pd
import pyarrow.parquet as pq
import pytest

from src.application.ingest_csv_to_bronze import main

N_ROWS = 10


@pytest.fixture
def sample_csv(tmp_path):
    csv_file = tmp_path / "dataset.csv"
    df = pd.DataFrame(
        {
            "texto": [f"comment {i}" for i in range(N_ROWS)],
            "etiqueta": ["positivo", "negativo", "neutral"] * 3 + ["positivo"],
        }
    )
    df.to_csv(csv_file, index=False)
    return csv_file


@pytest.fixture
def bronze_dir(tmp_path):
    return tmp_path / "bronze"


def run(sample_csv, bronze_dir):
    main(raw_path=str(sample_csv), bronze_path=str(bronze_dir / "out.parquet"))
    return pq.read_table(str(bronze_dir / "out.parquet"))


def test_bronze_parquet_created(sample_csv, bronze_dir):
    table = run(sample_csv, bronze_dir)
    assert table is not None


def test_bronze_row_count(sample_csv, bronze_dir):
    table = run(sample_csv, bronze_dir)
    assert table.num_rows == N_ROWS


def test_bronze_required_columns(sample_csv, bronze_dir):
    table = run(sample_csv, bronze_dir)
    assert {"id", "texto", "sentimiento", "fecha"}.issubset(set(table.column_names))


def test_bronze_id_is_monotonic(sample_csv, bronze_dir):
    table = run(sample_csv, bronze_dir)
    ids = table.column("id").to_pylist()
    assert ids == list(range(N_ROWS))


def test_bronze_etiqueta_renamed_to_sentimiento(sample_csv, bronze_dir):
    table = run(sample_csv, bronze_dir)
    assert "sentimiento" in table.column_names
    assert "etiqueta" not in table.column_names
