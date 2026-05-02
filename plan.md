Context                             

 Course: IUE Big Data 2026-1 — Activity 1 (25% of final grade, 15-day timeline).
 Goal: Build an end-to-end Big Data pipeline that ingests social-media-style comments, classifies sentiment in (simulated) real time with PySpark, persists results in MongoDB,
 exposes them through a Flask REST API, orchestrates everything with Docker Compose + Jenkins, and visualizes the output in Power BI.

 Why this plan exists: the user asked for a senior-architect-level execution blueprint before any code is written. Clean Architecture is mandated by the user, adapted to a Big
 Data + microservices context. The plan has to cover folder layout, component interaction, phase-by-phase delivery, and bonus/frontend strategy.

 Critical discovery — dataset/spec mismatch (must reconcile day 1):
 - Spec (comments_natural_language.md §4) declares columns id, texto, sentimiento, fecha.
 - Actual file dataset_sentimientos_500.csv (501 rows incl. header) only has texto, etiqueta, and the comments are mostly English, not Spanish.
 - Decision: treat the real CSV as ground truth. Synthesize id (row index) and fecha (random dates over the last 90 days, deterministic seed) at ingest time. Rename etiqueta →
 sentimiento in the bronze layer. Use a multilingual stopword set (spaCy/NLTK English + Spanish) so the pipeline stays robust regardless of language drift.

 Intended outcome: a reproducible, dockerized monorepo whose docker compose up boots the full system, plus a Jenkins job that builds + tests + deploys it, plus a Power BI report
 consuming /stats and /sentiments.

 ---
 1. Initial Infrastructure & Clean Architecture Tree

 Clean Architecture rules drive this layout (Robert C. Martin, adapted):
 - dep-inward-only — dependencies flow infrastructure → adapters → application → domain.
 - comp-screaming-architecture — top-level folders name domains (sentiment classification, comment ingestion), not frameworks.
 - bound-service-internal-architecture — each microservice (spark-pipeline, api) owns its internal layered architecture.
 - frame-domain-purity — domain models live in pure Python, no PySpark/Flask/PyMongo imports.

 SentimentStream/
 ├── README.md                              # Quickstart, architecture diagram, deploy steps
 ├── docker-compose.yml                     # Orchestrates: spark-master, spark-worker, mongo, api, jenkins, frontend
 ├── .env.example                           # Template for secrets (Mongo creds, API_KEY, JWT_SECRET)
 ├── .gitignore
 ├── Makefile                               # `make up`, `make train`, `make stream`, `make test`
 ├── Jenkinsfile                            # CI/CD pipeline (lint → test → build → deploy)
 │
 ├── data/                                  # Local dev data (gitignored except .gitkeep)
 │   ├── raw/                               # Original dataset_sentimientos_500.csv (read-only mount)
 │   ├── bronze/                            # Cleaned, schema-aligned parquet
 │   ├── silver/                            # Tokenized + feature-extracted parquet
 │   └── models/                            # Persisted Spark MLlib pipeline (NaiveBayes + IDF)
 │
 ├── services/                              # One folder per deployable microservice
 │   │
 │   ├── spark-pipeline/                    # PySpark service: training (batch) + streaming inference
 │   │   ├── Dockerfile                     # bitnami/spark base + project deps
 │   │   ├── requirements.txt
 │   │   ├── pyproject.toml
 │   │   ├── conf/
 │   │   │   └── spark-defaults.conf        # Mongo connector, executor memory tuning
 │   │   ├── src/
 │   │   │   ├── domain/                    # Pure business rules — NO PySpark imports
 │   │   │   │   ├── entities/              # Comment, SentimentPrediction, ConfidenceScore (value object)
 │   │   │   │   ├── value_objects/         # SentimentLabel enum, CleanedText
 │   │   │   │   └── ports/                 # Abstract repos: CommentSource, PredictionSink, ModelStore
 │   │   │   ├── application/               # Use cases — orchestrate domain
 │   │   │   │   ├── train_sentiment_model.py
 │   │   │   │   ├── classify_streaming_batch.py
 │   │   │   │   └── ingest_csv_to_bronze.py
 │   │   │   ├── adapters/                  # Inbound/outbound adapters
 │   │   │   │   ├── inbound/
 │   │   │   │   │   ├── socket_stream_listener.py    # Reads from TCP socket producer
 │   │   │   │   │   └── batch_csv_reader.py
 │   │   │   │   └── outbound/
 │   │   │   │       ├── mongo_prediction_writer.py   # Implements PredictionSink port
 │   │   │   │       └── filesystem_model_store.py
 │   │   │   ├── infrastructure/            # Framework-coupled code (Spark sessions, MongoDB driver)
 │   │   │   │   ├── spark/
 │   │   │   │   │   ├── session_factory.py
 │   │   │   │   │   └── ml_pipeline_builder.py       # Tokenizer → StopWords → HashingTF → IDF → NaiveBayes
 │   │   │   │   └── mongo/
 │   │   │   │       └── connection.py
 │   │   │   ├── producers/                 # Standalone scripts that simulate streaming
 │   │   │   │   └── socket_producer.py     # Replays CSV row-by-row over TCP
 │   │   │   └── main/                      # Composition root — wires DI, parses CLI args
 │   │   │       ├── train_main.py
 │   │   │       └── stream_main.py
 │   │   └── tests/
 │   │       ├── unit/                      # Pure-Python domain + use case tests (no Spark)
 │   │       └── integration/               # Tests with local SparkSession + Mongomock
 │   │
 │   ├── api/                               # Flask REST service
 │   │   ├── Dockerfile
 │   │   ├── requirements.txt
 │   │   ├── src/
 │   │   │   ├── domain/
 │   │   │   │   ├── entities/              # SentimentPrediction (mirrors Spark domain — duplicated by design, no shared code)
 │   │   │   │   └── ports/                 # PredictionRepository, SentimentClassifier
 │   │   │   ├── application/               # Use cases
 │   │   │   │   ├── list_sentiments.py
 │   │   │   │   ├── compute_stats.py
 │   │   │   │   ├── predict_sentiment.py
 │   │   │   │   └── generate_wordcloud.py  # bonus
 │   │   │   ├── adapters/
 │   │   │   │   ├── inbound/               # HTTP layer (Flask blueprints + controllers)
 │   │   │   │   │   ├── http/
 │   │   │   │   │   │   ├── controllers/
 │   │   │   │   │   │   │   ├── sentiments_controller.py
 │   │   │   │   │   │   │   ├── stats_controller.py
 │   │   │   │   │   │   │   ├── predict_controller.py
 │   │   │   │   │   │   │   └── wordcloud_controller.py
 │   │   │   │   │   │   ├── presenters/    # Format domain → JSON
 │   │   │   │   │   │   ├── schemas/       # Marshmallow / Pydantic request/response DTOs
 │   │   │   │   │   │   └── middleware/
 │   │   │   │   │   │       ├── auth.py    # bonus: API key / JWT
 │   │   │   │   │   │       └── error_handler.py
 │   │   │   │   │   └── routes.py
 │   │   │   ├── infrastructure/
 │   │   │   │   ├── mongo/
 │   │   │   │   │   └── prediction_repository.py     # Implements PredictionRepository port
 │   │   │   │   └── ml/
 │   │   │   │       └── spark_model_loader.py        # Loads persisted pipeline for /predict
 │   │   │   └── main/
 │   │   │       ├── app_factory.py         # create_app() — wires DI container
 │   │   │       └── wsgi.py                # gunicorn entrypoint
 │   │   └── tests/
 │   │       ├── unit/                      # Use case + controller tests with mocked ports
 │   │       └── integration/               # Real Mongo (testcontainers) + Flask test client
 │   │
 │   └── frontend/                          # Optional minimal SPA for video demo
 │       ├── Dockerfile                     # nginx serving static build
 │       ├── index.html                     # Single page calling /predict
 │       └── app.js                         # Fetch + render result
 │
 ├── infra/                                 # All ops/devops concerns
 │   ├── docker/
 │   │   ├── spark.Dockerfile               # Custom Spark image with mongo-spark-connector pre-baked
 │   │   ├── mongo/
 │   │   │   └── init-scripts/              # JS scripts to create user, indexes on startup
 │   │   │       └── 01-init-collections.js
 │   │   └── jenkins/
 │   │       ├── Dockerfile                 # Jenkins LTS + docker CLI + python
 │   │       └── plugins.txt
 │   ├── compose/
 │   │   ├── docker-compose.yml             # Production-ish orchestration
 │   │   ├── docker-compose.override.yml    # Local dev overrides (volume mounts, hot reload)
 │   │   └── networks.md                    # Documents the bridge network topology
 │   └── jenkins/
 │       ├── Jenkinsfile                    # Declarative pipeline (lint, test, build, push, deploy)
 │       └── jobs/
 │           └── seed.groovy                # Job DSL for bootstrapping
 │
 ├── docs/                                  # All documentation
 │   ├── architecture/
 │   │   ├── c4-context.md                  # System-context diagram (mermaid)
 │   │   ├── c4-containers.md               # Container diagram
 │   │   ├── data-flow.md                   # Sequence diagram of streaming flow
 │   │   └── adr/                           # Architecture Decision Records
 │   │       ├── 0001-clean-architecture-monorepo.md
 │   │       ├── 0002-socket-vs-kafka-for-streaming-simulation.md
 │   │       └── 0003-naive-bayes-vs-logistic-regression.md
 │   ├── api/
 │   │   └── openapi.yaml                   # OpenAPI 3.0 spec for /sentiments, /stats, /predict, /wordcloud
 │   ├── powerbi/
 │   │   ├── connection-guide.md            # How to bind Power BI to API
 │   │   └── dashboard.pbix                 # Final report
 │   └── video-script.md                    # Outline for the 3-5 min demo
 │
 └── scripts/                               # Top-level dev helpers
     ├── bootstrap.sh                       # First-time setup (creates .env, pulls images)
     ├── seed_mongo.sh                      # Loads sample predictions for Power BI iteration
     └── run_e2e_smoke.sh                   # End-to-end smoke test invoked by Jenkins

 ---
 2. Architecture Strategy & Component Interaction

 2.1 Logical data flow

 [CSV file]
     │
     ▼
 [socket_producer.py]  ── TCP :9999 ──▶  [Spark Structured Streaming readStream("socket")]
                                               │
                                               ▼
                                    [ML Pipeline: clean → tokenize → stopwords →
                                     HashingTF → IDF → NaiveBayes.transform]
                                               │
                                               ▼
                                    [foreachBatch → Mongo writer]
                                               │
                                               ▼
                                        MongoDB (sentimentstream.predictions)
                                               │
                                               ▼
                                        Flask API (/sentiments, /stats, /predict, /wordcloud)
                                               │
                                               ├──▶ Power BI (Web connector)
                                               └──▶ Frontend SPA (browser)

 2.2 Container topology

 Single user-defined bridge network sentimentstream_net so containers resolve each other by service name (Docker's embedded DNS). No links:, no published ports for inter-service
 traffic — only api and frontend and jenkins expose host ports.

 ┌─────────────────┬─────────────────────────┬───────────────┬──────────────────┬────────────────────────┐
 │     Service     │      Image / Build      │ Internal port │    Host port     │        Talks to        │
 ├─────────────────┼─────────────────────────┼───────────────┼──────────────────┼────────────────────────┤
 │ mongo           │ mongo:7                 │ 27017         │ 27017 (dev only) │ —                      │
 ├─────────────────┼─────────────────────────┼───────────────┼──────────────────┼────────────────────────┤
 │ spark-master    │ custom spark.Dockerfile │ 7077, 8080    │ 8080             │ mongo, socket-producer │
 ├─────────────────┼─────────────────────────┼───────────────┼──────────────────┼────────────────────────┤
 │ spark-worker    │ same image, worker cmd  │ 8081          │ 8081             │ spark-master           │
 ├─────────────────┼─────────────────────────┼───────────────┼──────────────────┼────────────────────────┤
 │ socket-producer │ python:3.11-slim        │ 9999          │ —                │ (Spark consumes)       │
 ├─────────────────┼─────────────────────────┼───────────────┼──────────────────┼────────────────────────┤
 │ api             │ custom Flask image      │ 5000          │ 5000             │ mongo, model volume    │
 ├─────────────────┼─────────────────────────┼───────────────┼──────────────────┼────────────────────────┤
 │ frontend        │ nginx-alpine            │ 80            │ 8090             │ api                    │
 ├─────────────────┼─────────────────────────┼───────────────┼──────────────────┼────────────────────────┤
 │ jenkins         │ custom Jenkins LTS      │ 8080          │ 8088             │ host docker socket     │
 └─────────────────┴─────────────────────────┴───────────────┴──────────────────┴────────────────────────┘

 2.3 Persistence strategy (volumes)

 - mongo_data (named volume) → /data/db — survives container recreation.
 - spark_models (named volume) → mounted into both spark-pipeline (writer) and api (reader) so the trained pipeline is shared. Read-only from API side.
 - ./data/raw:/data/raw:ro — bind mount of the original CSV into the producer.
 - jenkins_home — persists Jenkins config, jobs, credentials.
 - /var/run/docker.sock:/var/run/docker.sock — Jenkins agent runs Docker builds on host daemon (docker-out-of-docker). Acceptable for academic project; documented as ADR risk.

 2.4 Inter-service contracts

 - Spark → Mongo: mongo-spark-connector_2.12:10.x writing to sentimentstream.predictions with the schema below.
 - API → Mongo: PyMongo + connection pool created at app factory time.
 - API → Spark Model: load persisted PipelineModel.load(path) once at startup (using a lightweight local SparkSession in local[1] mode inside the API container) — this is the only
  place the API embeds Spark. ADR documents the alternative (calling out to Spark via REST/Livy) and why it was rejected as overkill.
 - MongoDB document schema:
 {
   "_id": "ObjectId",
   "comment_id": 137,
   "text_original": "Amazing experience with the service",
   "text_clean": "amazing experience service",
   "prediction": "positivo",
   "confidence": 0.91,
   "probabilities": {"positivo": 0.91, "negativo": 0.04, "neutral": 0.05},
   "ingested_at": "ISODate(...)",
   "model_version": "v1.0.0"
 }
 - Indexes: {ingested_at: -1}, {prediction: 1}, {ingested_at: -1, prediction: 1} (compound for /stats time-bucketed aggregations).

 ---
 3. Phase-by-Phase Execution Plan

 Five phases, ~3 days each within the 15-day window. Each phase ends with a green smoke test.

 Phase 1 — Repo skeleton, dataset reconciliation, dev environment (Days 1–2)

 Actionable tasks
 - Initialize the directory tree from §1.
 - Write .env.example, Makefile, pyproject.toml per service, .gitignore.
 - Write infra/compose/docker-compose.yml with only mongo + api (stub) + spark-master + spark-worker to validate networking.
 - Implement scripts/bootstrap.sh and a make up target.
 - Author docs/architecture/adr/0001-clean-architecture-monorepo.md + 0002-socket-vs-kafka.md.
 - Reconcile dataset: add services/spark-pipeline/src/application/ingest_csv_to_bronze.py that reads texto,etiqueta, synthesizes id (monotonic) and fecha (deterministic random
 over last 90 days), renames to sentimiento, writes parquet to data/bronze/.

 Technical considerations
 - Pin Spark to 3.5.x (stable LTS, mongo-spark-connector 10.3 compatible). PySpark must match host Python (3.11 is safest).
 - Use bitnami/spark:3.5 as base — well-documented, multi-arch, predictable env vars.
 - Mongo connector requires a JAR — bake it into the Spark image (spark.Dockerfile) with --packages resolution at build time, not runtime, to avoid network flakiness.
 - Use healthchecks in compose (mongo: mongosh --eval, api: curl /health, spark-master: tcp 7077) so depends_on: condition: service_healthy actually works.

 Testing strategy
 - docker compose up → all containers healthy.
 - docker compose exec api python -c "from pymongo import MongoClient; print(MongoClient('mongodb://mongo:27017').list_database_names())" returns a list.
 - docker compose exec spark-master spark-submit --version succeeds.
 - Unit test: ingest produces parquet with exactly 500 rows and 4 columns.

 ---
 Phase 2 — Batch training pipeline (Days 3–5)

 Actionable tasks
 - Implement domain entities (Comment, SentimentPrediction, SentimentLabel enum) in spark-pipeline/src/domain/.
 - Define ports: CommentSource, PredictionSink, ModelStore (abstract base classes, no framework deps).
 - Implement infrastructure/spark/ml_pipeline_builder.py:
 Tokenizer(textCol="text_clean", outputCol="tokens")
   → StopWordsRemover(stopWords=multilingual_set, outputCol="tokens_clean")
   → HashingTF(numFeatures=2**14, outputCol="tf")
   → IDF(inputCol="tf", outputCol="features")
   → NaiveBayes(labelCol="label_idx", featuresCol="features", smoothing=1.0)
 - Wrapped in StringIndexer for label, IndexToString for output.
 - Implement application/train_sentiment_model.py use case: 80/20 split, fit pipeline, evaluate with MulticlassClassificationEvaluator (F1 + accuracy), persist to
 data/models/v1.0.0/.
 - Composition root main/train_main.py: argparse, DI wiring, calls use case.
 - make train target: docker compose run --rm spark-pipeline python -m main.train_main.

 Technical considerations
 - 500 rows is tiny — class imbalance is likely. Add stratified split via df.sampleBy("label_idx", fractions, seed).
 - Multilingual stopwords: union of StopWordsRemover.loadDefaultStopWords("english") + ("spanish") to cover the dataset/spec mismatch.
 - Persist a metrics.json alongside the model (accuracy, per-class F1, confusion matrix) — Power BI will read it via API for the "model card" tile.
 - Naive Bayes vs. Logistic Regression: NB is in the spec → use it. But ADR-0003 records that LR with the same features performed comparably for future iterations.

 Testing strategy
 - Unit test (no Spark): domain entities round-trip, SentimentLabel.from_string rejects unknowns.
 - Integration test (local SparkSession): pipeline fits on a 50-row fixture, prediction column has 3 distinct values.
 - Acceptance: train_main produces data/models/v1.0.0/ (a real Spark PipelineModel directory) and a metrics.json with F1 ≥ 0.6 (low bar; dataset is small).

 ---
 Phase 3 — Streaming inference + Mongo persistence (Days 6–8)

 Actionable tasks
 - Implement producers/socket_producer.py: opens a TCP server on 0.0.0.0:9999, on accept iterates the CSV one row per ~200 ms, sends text\n. Configurable replay rate via env var
 STREAM_RATE_HZ.
 - Implement application/classify_streaming_batch.py use case: takes a DataFrame[String] micro-batch, applies model, returns DataFrame matching the Mongo schema.
 - Implement adapters/inbound/socket_stream_listener.py: spark.readStream.format("socket").option("host", "socket-producer").option("port", 9999).
 - Implement adapters/outbound/mongo_prediction_writer.py using foreachBatch (allows idempotent writes + retries).
 - Composition root main/stream_main.py: loads model from data/models/v1.0.0/, runs streaming query indefinitely with trigger=processingTime="5 seconds" and a checkpoint dir at
 data/checkpoints/.
 - Add socket-producer and spark-pipeline (streaming) services to docker-compose.yml with proper depends_on ordering.

 Technical considerations
 - Socket source caveat: Spark's socket source is documented as not fault-tolerant — fine for academic demo, but ADR-0002 must say so. Alternative for production: Kafka.
 - Checkpointing is mandatory even with socket source, otherwise foreachBatch cannot guarantee exactly-once semantics.
 - Confidence score: udf that takes the probability Vector and returns float(max(probability)).
 - Watermark not strictly needed (no aggregation), but if /stats is computed via continuous aggregation later, add withWatermark("ingested_at", "10 minutes").
 - Backpressure: with 500 rows at 5 Hz the whole stream finishes in ~100 s — enough for a demo. Producer should optionally loop forever (env flag STREAM_LOOP=true) so reviewers
 can replay during the demo.

 Testing strategy
 - Manual: docker compose up, then docker compose exec mongo mongosh --eval "db.predictions.countDocuments()" should grow over time.
 - Integration test: replace socket source with MemoryStream, feed 10 rows, assert 10 documents written to mongomock.
 - Acceptance: after 60 s of streaming, db.predictions has ≥ 100 documents and a healthy mix of all 3 labels.

 ---
 Phase 4 — Flask API + Power BI (Days 9–11)

 Actionable tasks
 - Implement domain + ports in services/api/src/domain/.
 - Implement use cases: list_sentiments (filters: prediction, from, to, pagination), compute_stats (counts per class + daily trend), predict_sentiment (calls
 SparkModelLoader.transform_one_text).
 - Implement controllers, presenters, schemas (Pydantic v2 for validation, easy OpenAPI gen).
 - Implement infrastructure/ml/spark_model_loader.py: SparkSession.builder.master("local[1]").getOrCreate() + PipelineModel.load(...) cached at module level.
 - App factory in main/app_factory.py: registers blueprints, error handler, optional auth middleware (off by default), wires DI.
 - Write docs/api/openapi.yaml.
 - Power BI:
   - Create blank report → Get Data → Web → http://<host>:5000/sentiments?limit=1000.
   - For local dev expose API on localhost:5000; for cloud Power BI use ngrok (bonus).
   - Three required visuals: donut chart (distribution from /stats), line chart (daily trend), table (latest 50 predictions).

 Technical considerations
 - Spark inside the API is heavy: ~2 GB RAM for a local[1] JVM. Document RAM expectations in README. Alternative considered: re-implement preprocessing + load only the IDF
 vocabulary + NB priors as JSON and predict in pure Python — faster but brittle if the pipeline changes. Reject for v1, log as future work.
 - Cache /stats for 30 s using flask-caching (in-memory) — Power BI hits this every refresh.
 - CORS: enable for the frontend container origin only (flask-cors).
 - Pagination contract: ?limit= (default 100, max 1000) + ?cursor=<ObjectId> — avoids skip() performance trap.

 Testing strategy
 - Unit: each use case with mocked port. Schema validators reject malformed bodies.
 - Integration (testcontainers): real Mongo, Flask test client, assert /sentiments filters work, /predict returns one of 3 labels.
 - Manual: hit each endpoint via curl, then load Power BI Desktop and confirm all 3 visuals render.

 ---
 Phase 5 — Jenkins CI/CD, hardening, documentation, demo (Days 12–15)

 Actionable tasks
 - Write infra/jenkins/Jenkinsfile (declarative) with stages:
   a. Checkout
   b. Lint (ruff + black --check)
   c. Unit Tests (parallel: spark-pipeline, api)
   d. Build Images (docker build per service, tag with ${GIT_SHA})
   e. Integration Tests (compose up the test profile, run pytest, compose down)
   f. Deploy (compose up -d on the same host — academic-grade; document as ADR risk)
   g. Smoke (scripts/run_e2e_smoke.sh — trains, streams 30 s, calls API, asserts ≥ 1 prediction)
 - Configure infra/docker/jenkins/Dockerfile with seeded plugins.txt (workflow-aggregator, docker-workflow, blueocean).
 - Bring up Jenkins via compose, register the Jenkinsfile as a Pipeline job (seed via Job DSL infra/jenkins/jobs/seed.groovy).
 - Write final README.md: architecture diagram (mermaid), quickstart, troubleshooting, evaluation-criteria mapping table.
 - Record video demo (script in docs/video-script.md).

 Technical considerations
 - Jenkins runs Docker against the host daemon — never mount Docker-in-Docker for a class project. Use docker.sock bind mount and document the trust boundary.
 - Use a .dockerignore per service to avoid 2 GB build contexts.
 - Tag images with both latest and ${GIT_SHA} so rollbacks are trivial.
 - Don't push images anywhere remote unless Docker Hub creds are required by the rubric — the spec does not require a registry.

 Testing strategy
 - The Jenkins pipeline itself is the test. A green run = system ships.
 - Manual demo rehearsal: make clean && make up && make train && make stream from a fresh clone, end-to-end in < 5 minutes.

 ---
 4. Advanced Extras & Frontend Integration

 4.1 Authentication (bonus, +0.15 est.)

 - Recommended: API key in X-API-Key header, validated by middleware/auth.py.
 - Key stored in .env as API_KEY=..., injected into the API container only.
 - Apply selectively via decorator @require_api_key on /predict and /wordcloud (write-/expensive-side); leave /sentiments and /stats open so Power BI works without OAuth
 gymnastics.
 - Upgrade path documented in ADR: switch to JWT (flask-jwt-extended) with a /auth/login endpoint when multi-user is needed.

 4.2 /wordcloud endpoint (bonus, +0.15 est.)

 - Use case generate_wordcloud(sentiment: SentimentLabel, top_n: int = 50):
   - Mongo aggregation: $match {prediction: X} → $project {tokens: split(text_clean, ' ')} → $unwind → $group {_id: token, count: $sum: 1} → $sort {count: -1} → $limit top_n.
   - Filter out short tokens (len < 3) and the same multilingual stopwords used in training.
 - Response shape: {"sentiment": "positivo", "words": [{"word":"service","count":42}, ...]}.
 - Cache 60 s. Frontend can render with wordcloud2.js.

 4.3 ngrok exposure (bonus, +0.1 est.)

 - docker-compose.override.yml adds an ngrok/ngrok:latest sidecar with command: http api:5000.
 - Authtoken from .env (NGROK_AUTHTOKEN).
 - Document in docs/powerbi/connection-guide.md: copy ngrok URL → Power BI Service (online) → Web data source.

 4.4 Pipeline unit tests (bonus, +0.1 est.)

 - Already accounted for in Phase 2 testing strategy. To claim the bonus, add explicit tests for clean_text (lowercasing, punctuation strip, accent fold) and
 multilingual_stopwords membership.

 4.5 Minimal frontend for video demo

 Since the rubric does not require a frontend but the video does, ship a single static HTML page that punches above its weight:

 services/frontend/
 ├── index.html      # form: textarea + button + result card + last-5 predictions table
 ├── app.js          # fetch('/predict', POST) and fetch('/sentiments?limit=5')
 └── style.css       # one-file Pico.css or a few Tailwind utility classes inlined

 - Served by nginx:alpine on :8090.
 - Reverse-proxies /api/* to api:5000 via nginx config — avoids CORS entirely and is the single host the demo URL bar shows.
 - In the video: paste a comment → see prediction + confidence → table refreshes → cut to Power BI dashboard already open in another tab.

 Why this beats a React/Vue SPA for this deliverable: zero build step, zero node_modules, zero Dockerfile complexity — fits the "production-ready but pragmatic" brief, and the
 demo is the only audience.

 ---
     │ Why this beats a React/Vue SPA for this deliverable: zero build step, zero node_modules, zero Dockerfile complexity — fits the "production-ready but pragmatic" brief, and  │
     │ the demo is the only audience.                                                                                                                                              │
     │                                                                                                                                                                             │
     │ ---                                                                                                                                                                         │
     │ 5. Critical Files (paths to create)                                                                                                                                         │
     │                                                                                                                                                                             │
     │ - infra/compose/docker-compose.yml — orchestration spine.                                                                                                                   │
     │ - infra/jenkins/Jenkinsfile — CI/CD spine.                                                                                                                                  │
     │ - services/spark-pipeline/src/infrastructure/spark/ml_pipeline_builder.py — ML core.                                                                                        │
     │ - services/spark-pipeline/src/main/stream_main.py — streaming composition root.                                                                                             │
     │ - services/api/src/main/app_factory.py — API composition root.                                                                                                              │
     │ - services/api/src/infrastructure/ml/spark_model_loader.py — model serving boundary.                                                                                        │
     │ - docs/architecture/adr/0001-clean-architecture-monorepo.md — anchors the architecture story for the rubric's "documentation" criterion.                                    │
     │                                                                                                                                                                             │
     │ ---                                                                                                                                                                         │
     │ 6. End-to-End Verification                                                                                                                                                  │
     │                                                                                                                                                                             │
     │ # 0. Fresh clone, fresh state                                                                                                                                               │
     │ git clean -xfd && cp .env.example .env                                                                                                                                      │
     │                                                                                                                                                                             │
     │ # 1. Boot the stack                                                                                                                                                         │
     │ docker compose -f infra/compose/docker-compose.yml up -d --build                                                                                                            │
     │ # Expect: 7 containers healthy within 90 s                                                                                                                                  │
     │                                                                                                                                                                             │
     │ # 2. Train the model (one-off batch job)                                                                                                                                    │
     │ make train                                                                                                                                                                  │
     │ # Expect: data/models/v1.0.0/ created, metrics.json shows accuracy >= 0.6                                                                                                   │
     │                                                                                                                                                                             │
     │ # 3. Start the producer + streaming consumer                                                                                                                                │
     │ make stream                                                                                                                                                                 │
     │ # In another terminal, watch Mongo grow:                                                                                                                                    │
     │ docker compose exec mongo mongosh --eval \                                                                                                                                  │
     │   "db.getSiblingDB('sentimentstream').predictions.countDocuments()"                                                                                                         │
     │ # Expect: number rising every ~5 s                                                                                                                                          │
     │                                                                                                                                                                             │
     │ # 4. Hit each API endpoint                                                                                                                                                  │
     │ curl http://localhost:5000/health                          # 200 OK                                                                                                         │
     │ curl http://localhost:5000/sentiments?limit=5              # JSON list                                                                                                      │
     │ curl http://localhost:5000/stats                           # JSON with class distribution + trend                                                                           │
     │ curl -X POST http://localhost:5000/predict \                                                                                                                                │
     │      -H "Content-Type: application/json" \                                                                                                                                  │
     │      -H "X-API-Key: $API_KEY" \                                                                                                                                             │
     │      -d '{"text":"excellent product, very happy"}'         # {"prediction":"positivo","confidence":0.9...}                                                                  │
     │                                                                                                                                                                             │
     │ # 5. Open the frontend                                                                                                                                                      │
     │ xdg-open http://localhost:8090                                                                                                                                              │
     │                                                                                                                                                                             │
     │ # 6. Open Jenkins, trigger the pipeline                                                                                                                                     │
     │ xdg-open http://localhost:8088                                                                                                                                              │
     │ # Expect: green pipeline end-to-end in < 10 min                                                                                                                             │
     │                                                                                                                                                                             │
     │ # 7. Open Power BI Desktop, refresh the report                                                                                                                              │
     │ # Expect: 3 visuals populated; refresh succeeds                                                                                                                             │
     │                                                                                                                                                                             │
     │ If all 7 steps pass on a fresh machine, the rubric's 100% (Pipeline 35% + Infra 25% + Dashboard 25% + Docs 15%) is mechanically satisfied; bonuses are layered on top.     