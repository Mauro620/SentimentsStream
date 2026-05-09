import pandas as pd
import pyarrow.parquet as pq
import pytest
from datetime import datetime

from src.application.ingest_csv_to_bronze import IngestCsvToBronzeUseCase
from src.infrastructure.generators.deterministic_timestamp_generator import (
    DeterministicTimestampGenerator,
)

N_ROWS = 10
SEED = 42
ANCHOR_NOW = datetime(2026, 5, 8, 12, 0, 0)


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


def run(sample_csv, bronze_dir, n=N_ROWS, now=ANCHOR_NOW):
    generator = DeterministicTimestampGenerator(seed=SEED, now=now)
    use_case = IngestCsvToBronzeUseCase(timestamp_generator=generator)
    use_case.execute(raw_path=str(sample_csv), bronze_path=str(bronze_dir / "out.parquet"))
    return pq.read_table(str(bronze_dir / "out.parquet"))


def test_bronze_parquet_created(sample_csv, bronze_dir):
    table = run(sample_csv, bronze_dir)
    assert table is not None


def test_bronze_row_count(sample_csv, bronze_dir):
    table = run(sample_csv, bronze_dir)
    assert table.num_rows == N_ROWS


def test_bronze_required_columns(sample_csv, bronze_dir):
    table = run(sample_csv, bronze_dir)
    assert {"id", "texto", "sentimiento", "ingested_at"}.issubset(set(table.column_names))


def test_bronze_id_is_monotonic(sample_csv, bronze_dir):
    table = run(sample_csv, bronze_dir)
    ids = table.column("id").to_pylist()
    assert ids == list(range(N_ROWS))


def test_bronze_etiqueta_renamed_to_sentimiento(sample_csv, bronze_dir):
    table = run(sample_csv, bronze_dir)
    assert "sentimiento" in table.column_names
    assert "etiqueta" not in table.column_names


def test_bronze_ingested_at_is_deterministic(sample_csv, bronze_dir):
    table_a = run(sample_csv, bronze_dir)
    table_b = run(sample_csv, bronze_dir)
    ts_a = table_a.column("ingested_at").to_pylist()
    ts_b = table_b.column("ingested_at").to_pylist()
    assert ts_a == ts_b


def test_bronze_ingested_at_spans_90_days(sample_csv, bronze_dir):
    # more rows → better statistical coverage of the 90-day window
    csv_file = sample_csv.parent / "big_dataset.csv"
    big_n = 500
    labels = ["positivo", "negativo", "neutral"] * (big_n // 3 + 1)
    labels = labels[:big_n]
    df = pd.DataFrame(
        {
            "texto": [f"comment {i}" for i in range(big_n)],
            "etiqueta": labels,
        }
    )
    df.head(big_n).to_csv(csv_file, index=False)

    table = run(csv_file, bronze_dir, n=big_n)
    ts = [pd.Timestamp(t) for t in table.column("ingested_at").to_pylist()]
    span = (max(ts) - min(ts)).days
    assert span >= 80
