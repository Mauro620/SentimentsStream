.PHONY: up down ingest train stream lint format test clean

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

lint:
	docker compose -f infra/compose/docker-compose.yml run --rm --user root api \
		bash -c "pip install -q ruff black --break-system-packages && python3 -m ruff check src && python3 -m black --check src"
	docker compose -f infra/compose/docker-compose.yml run --rm --user root spark-pipeline \
		bash -c "pip install -q ruff black --break-system-packages && python3 -m ruff check src && python3 -m black --check src"

format:
	docker compose -f infra/compose/docker-compose.yml run --rm --user root api \
		bash -c "pip install -q ruff black --break-system-packages && python3 -m ruff check src --fix && python3 -m black src"
	docker compose -f infra/compose/docker-compose.yml run --rm --user root spark-pipeline \
		bash -c "pip install -q ruff black --break-system-packages && python3 -m ruff check src --fix && python3 -m black src"

test:
	docker compose -f infra/compose/docker-compose.yml run --rm spark-pipeline pytest tests/
	docker compose -f infra/compose/docker-compose.yml run --rm api pytest tests/

clean:
	docker compose -f infra/compose/docker-compose.yml down -v
	rm -rf data/bronze/* data/silver/* data/models/*
