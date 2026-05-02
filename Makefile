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
	docker compose -f infra/compose/docker-compose.yml run --rm --user root \
		-v "$(CURDIR)/services/api/src:/app/src" api \
		bash -c "export PATH=/usr/local/bin:$$PATH && pip install -q ruff black && ruff check src && black --check src"
	docker compose -f infra/compose/docker-compose.yml run --rm --user root \
		-v "$(CURDIR)/services/spark-pipeline/src:/app/src" spark-pipeline \
		bash -c "export PATH=/usr/local/bin:$$PATH && pip install -q ruff black && ruff check src && black --check src"

format:
	docker compose -f infra/compose/docker-compose.yml run --rm --user root \
		-v "$(CURDIR)/services/api/src:/app/src" api \
		bash -c "export PATH=/usr/local/bin:$$PATH && pip install -q ruff black && ruff check src --fix && black src"
	docker compose -f infra/compose/docker-compose.yml run --rm --user root \
		-v "$(CURDIR)/services/spark-pipeline/src:/app/src" spark-pipeline \
		bash -c "export PATH=/usr/local/bin:$$PATH && pip install -q ruff black && ruff check src --fix && black src"

test:
	docker compose -f infra/compose/docker-compose.yml run --rm spark-pipeline pytest tests/
	docker compose -f infra/compose/docker-compose.yml run --rm api pytest tests/

clean:
	docker compose -f infra/compose/docker-compose.yml down -v
	rm -rf data/bronze/* data/silver/* data/models/*
