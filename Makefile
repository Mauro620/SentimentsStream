.PHONY: up down ingest train stream test clean

up:
	docker compose -f infra/compose/docker-compose.yml up -d --build

down:
	docker compose -f infra/compose/docker-compose.yml down

ingest:
	docker compose -f infra/compose/docker-compose.yml run --rm --user root spark-pipeline \
		bash -c "pip install -q -r requirements.txt && python3 -m src.application.ingest_csv_to_bronze"

train:
	docker compose -f infra/compose/docker-compose.yml run --rm --user root spark-pipeline \
		bash -c "pip install -q -r requirements.txt && python3 -m src.main.train_main"

stream:
	docker compose -f infra/compose/docker-compose.yml run --rm --user root spark-pipeline \
		bash -c "pip install -q -r requirements.txt && python3 -m src.main.stream_main"

test:
	docker compose -f infra/compose/docker-compose.yml run --rm spark-pipeline pytest tests/
	docker compose -f infra/compose/docker-compose.yml run --rm api pytest tests/

clean:
	docker compose -f infra/compose/docker-compose.yml down -v
	rm -rf data/bronze/* data/silver/* data/models/*
