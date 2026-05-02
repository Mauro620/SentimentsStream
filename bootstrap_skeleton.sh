#!/bin/bash
set -e

# Root files
touch README.md .env.example .gitignore Makefile Jenkinsfile

# Data dirs
mkdir -p data/raw data/bronze data/silver data/models
touch data/raw/.gitkeep data/bronze/.gitkeep data/silver/.gitkeep data/models/.gitkeep

# spark-pipeline service
mkdir -p services/spark-pipeline/{conf,src/domain/{entities,value_objects,ports},src/application,src/adapters/{inbound,outbound},src/infrastructure/{spark,mongo},src/producers,src/main,tests/{unit,integration}}

touch services/spark-pipeline/{Dockerfile,requirements.txt,pyproject.toml}
touch services/spark-pipeline/conf/spark-defaults.conf

touch services/spark-pipeline/src/domain/entities/__init__.py
touch services/spark-pipeline/src/domain/value_objects/__init__.py
touch services/spark-pipeline/src/domain/ports/__init__.py

touch services/spark-pipeline/src/application/{ingest_csv_to_bronze.py,train_sentiment_model.py,classify_streaming_batch.py}

touch services/spark-pipeline/src/adapters/inbound/{socket_stream_listener.py,batch_csv_reader.py}
touch services/spark-pipeline/src/adapters/outbound/{mongo_prediction_writer.py,filesystem_model_store.py}

touch services/spark-pipeline/src/infrastructure/spark/{session_factory.py,ml_pipeline_builder.py}
touch services/spark-pipeline/src/infrastructure/mongo/connection.py

touch services/spark-pipeline/src/producers/socket_producer.py
touch services/spark-pipeline/src/main/{train_main.py,stream_main.py}

touch services/spark-pipeline/tests/unit/__init__.py services/spark-pipeline/tests/integration/__init__.py

# api service
mkdir -p services/api/src/domain/{entities,ports}
mkdir -p services/api/src/application
mkdir -p services/api/src/adapters/inbound/http/{controllers,presenters,schemas,middleware}
mkdir -p services/api/src/infrastructure/{mongo,ml}
mkdir -p services/api/src/main
mkdir -p services/api/tests/{unit,integration}

touch services/api/{Dockerfile,requirements.txt}
touch services/api/src/domain/entities/__init__.py services/api/src/domain/ports/__init__.py
touch services/api/src/application/{list_sentiments.py,compute_stats.py,predict_sentiment.py,generate_wordcloud.py}
touch services/api/src/adapters/inbound/http/controllers/{sentiments_controller.py,stats_controller.py,predict_controller.py,wordcloud_controller.py}
touch services/api/src/adapters/inbound/http/middleware/{auth.py,error_handler.py}
touch services/api/src/adapters/routes.py
touch services/api/src/infrastructure/mongo/prediction_repository.py
touch services/api/src/infrastructure/ml/spark_model_loader.py
touch services/api/src/main/{app_factory.py,wsgi.py}
touch services/api/tests/unit/__init__.py services/api/tests/integration/__init__.py

# frontend service
mkdir -p services/frontend
touch services/frontend/{Dockerfile,index.html,app.js}

# infra
mkdir -p infra/docker/{mongo/init-scripts,jenkins} infra/compose infra/jenkins/jobs
touch infra/docker/spark.Dockerfile
touch infra/docker/mongo/init-scripts/01-init-collections.js
touch infra/docker/jenkins/{Dockerfile,plugins.txt}
touch infra/compose/{docker-compose.yml,docker-compose.override.yml,networks.md}
touch infra/jenkins/Jenkinsfile infra/jenkins/jobs/seed.groovy

# docs
mkdir -p docs/architecture/adr docs/api docs/powerbi
touch docs/architecture/{c4-context.md,c4-containers.md,data-flow.md}
touch docs/architecture/adr/{0001-clean-architecture-monorepo.md,0002-socket-vs-kafka-for-streaming-simulation.md,0003-naive-bayes-vs-logistic-regression.md}
touch docs/api/openapi.yaml
touch docs/powerbi/{connection-guide.md,dashboard.pbix}
touch docs/video-script.md

# scripts
mkdir -p scripts
touch scripts/{bootstrap.sh,seed_mongo.sh,run_e2e_smoke.sh}

echo "Skeleton done."
