import os
from datetime import datetime, timedelta
from random import Random

import pandas as pd


def main(
    raw_path: str = os.getenv("RAW_PATH", "/app/data/raw/dataset_sentimientos_500.csv"),
    bronze_path: str = os.path.join(os.getenv("BRONZE_PATH", "/app/data/bronze"), "comments_bronze.parquet"),
    seed: int = 42,
) -> None:
    df = pd.read_csv(raw_path)

    # Synthesize id (monotonic 0-499)
    df["id"] = range(len(df))

    # Synthesize fecha (random dates over last 90 days, deterministic)
    rng = Random(seed)
    base = datetime.now() - timedelta(days=90)
    df["fecha"] = [
        (base + timedelta(days=rng.uniform(0, 90))).strftime("%Y-%m-%d")
        for _ in range(len(df))
    ]

    # Rename etiqueta -> sentimiento
    df = df.rename(columns={"etiqueta": "sentimiento"})

    # Select + write
    out = df[["id", "texto", "sentimiento", "fecha"]]
    os.makedirs(os.path.dirname(bronze_path), exist_ok=True)
    out.to_parquet(bronze_path, index=False)
    print(f"Wrote {len(out)} rows to {bronze_path}")


if __name__ == "__main__":
    main()
