import os

import pandas as pd

from src.domain.ports.timestamp_generator import TimestampGenerator


class IngestCsvToBronzeUseCase:
    """Application layer: orchestrate CSV ingestion with deterministic timestamps."""

    def __init__(self, timestamp_generator: TimestampGenerator) -> None:
        self._timestamp_generator = timestamp_generator

    def execute(
        self,
        raw_path: str,
        bronze_path: str,
    ) -> None:
        df = pd.read_csv(raw_path)
        n = len(df)

        # deterministic temporal dispersion
        timestamps = self._timestamp_generator.generate_batch(n)

        df["id"] = range(n)
        df["ingested_at"] = [ts.isoformat() for ts in timestamps]
        df = df.rename(columns={"etiqueta": "sentimiento"})

        out = df[["id", "texto", "sentimiento", "ingested_at"]]
        os.makedirs(os.path.dirname(bronze_path), exist_ok=True)
        out.to_parquet(bronze_path, index=False)


def main(
    raw_path: str = os.getenv("RAW_PATH", "/app/data/raw/dataset_sentimientos_500.csv"),
    bronze_path: str = os.path.join(
        os.getenv("BRONZE_PATH", "/app/data/bronze"), "comments_bronze.parquet"
    ),
    seed: int = 42,
) -> None:
    from src.infrastructure.generators.deterministic_timestamp_generator import (
        DeterministicTimestampGenerator,
    )

    generator: TimestampGenerator = DeterministicTimestampGenerator(seed=seed)
    use_case = IngestCsvToBronzeUseCase(timestamp_generator=generator)
    use_case.execute(raw_path=raw_path, bronze_path=bronze_path)
    print(f"Wrote bronze to {bronze_path}")
