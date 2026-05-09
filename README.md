SentimentStream
===============

## Descripcion del Proyecto
SentimentStream es un pipeline de Big Data de extremo a extremo que ingesta comentarios, clasifica sentimiento en tiempo casi real con PySpark, persiste resultados en MongoDB y los expone mediante una API REST en Flask para consumo en Power BI.

## Estructura del Proyecto
La organizacion sigue Clean Architecture con dependencias hacia adentro. Arbol principal:

```
SentimentStream/
├── README.md
├── docker-compose.yml
├── .env.example
├── Makefile
├── Jenkinsfile
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   └── models/
├── services/
│   ├── spark-pipeline/
│   │   └── src/
│   │       ├── domain/
│   │       ├── application/
│   │       ├── adapters/
│   │       ├── infrastructure/
│   │       └── main/
│   ├── api/
│   │   └── src/
│   │       ├── domain/
│   │       ├── application/
│   │       ├── adapters/
│   │       ├── infrastructure/
│   │       └── main/
│   └── frontend/
├── infra/
│   ├── docker/
│   ├── compose/
│   └── jenkins/
├── docs/
│   ├── architecture/
│   ├── api/
│   └── powerbi/
└── scripts/
```

## Requisitos Previos
- Docker
- Docker Compose
- Archivo `.env` configurado (puede partir de `.env.example`)

## Guia de Ejecucion Paso a Paso

### Paso 1: Preparacion
Clonar repositorio y levantar infraestructura base.

```bash
git clone <URL_DEL_REPOSITORIO>
cd SentimentStream
cp .env.example .env
make up
```

### Paso 2: Entrenamiento del Modelo (Guia Detallada)
Ejecuta el entrenamiento del modelo con PySpark y guarda el pipeline entrenado.

#### Entrenamiento del Modelo de IA
- Proceso offline/batch. Debe ejecutarse antes de iniciar la API.
- Comando exacto via Docker Compose:

```bash
make train
```

- Verificacion: revisar que existe `data/models/v1.0.0/metrics.json` y contiene las metricas del entrenamiento.

Durante este paso se lee el dataset desde `data/raw`, se ejecuta el pipeline NLP (limpieza, tokenizacion, stopwords, TF-IDF) y se entrena Naive Bayes. El modelo se persiste en `data/models/v1.0.0/`.

### Paso 3: Ingesta y Streaming
Inicia el flujo de datos en tiempo casi real. El `socket-producer` simula la entrada de comentarios y Spark consume el stream para escribir predicciones en MongoDB.

```bash
make stream
```

### Paso 4: API REST
API disponible en `http://localhost:5000`.

```bash
curl http://localhost:5000/health
curl http://localhost:5000/sentiments?limit=5
curl http://localhost:5000/stats
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"text":"excelente servicio"}'
```

### Paso 5: Visualizacion
Conectar Power BI a la API:
- Fuente Web: `http://localhost:5000/sentiments?limit=1000`
- Usar `/stats` para distribucion y tendencia temporal.

## Desarrollo Local: Lint, Formato y Tests

El pipeline de Jenkins ejecuta **ruff** (linter) y **black** (formato) antes de correr los tests.
Ejecuta estos comandos localmente antes de hacer push para evitar fallos en CI.

### Verificar formato y estilo (solo lectura, igual que Jenkins)

```bash
# via Makefile (recomendado)
make lint

# o manualmente con docker compose
# Nota: -v monta el codigo fuente actual; sin esto el container usa la imagen antigua
docker compose -f infra/compose/docker-compose.yml run --rm --user root \
    -v "$(pwd)/services/api/src:/app/src" api \
    bash -c "pip install -q ruff black && python3 -m ruff check src && python3 -m black --check src"

docker compose -f infra/compose/docker-compose.yml run --rm --user root \
    -v "$(pwd)/services/spark-pipeline/src:/app/src" spark-pipeline \
    bash -c "pip install -q ruff black && python3 -m ruff check src && python3 -m black --check src"
```

### Auto-corregir formato y estilo

```bash
# via Makefile (recomendado)
make format

# o manualmente con docker compose
docker compose -f infra/compose/docker-compose.yml run --rm --user root \
    -v "$(pwd)/services/api/src:/app/src" api \
    bash -c "pip install -q ruff black && python3 -m ruff check src --fix && python3 -m black src"

docker compose -f infra/compose/docker-compose.yml run --rm --user root \
    -v "$(pwd)/services/spark-pipeline/src:/app/src" spark-pipeline \
    bash -c "pip install -q ruff black && python3 -m ruff check src --fix && python3 -m black src"
```

> **Flujo recomendado:** `make format` primero para auto-corregir, luego `make lint` para confirmar que no quedan errores, luego `git commit`.

### Ejecutar tests unitarios

```bash
# via Makefile
make test

# o por servicio
docker compose -f infra/compose/docker-compose.yml run --rm --user root api \
    bash -c "pip install -q -r requirements.txt pytest  && \
             python3 -m pytest tests/unit -v --tb=short"

docker compose -f infra/compose/docker-compose.yml run --rm --user root spark-pipeline \
    bash -c "pip install -q -r requirements.txt pytest  && \
             python3 -m pytest tests/unit -v --tb=short"
```

### Jenkins ini
```bash
docker run -d -p 9090:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock --group-add $(stat -c '%g' /var/run/docker.sock) --name jenkins sentimentstream-jenkins
```

### Resumen de herramientas de calidad

| Herramienta | Que hace | Cuando falla el pipeline |
|-------------|----------|--------------------------|
| `ruff` | Linter (equivale a flake8 + isort) | Imports desordenados, variables sin usar, errores de estilo |
| `black` | Formatter de codigo | Formato inconsistente (espacios, comillas, longitud de linea) |
| `pytest` | Tests unitarios e integracion | Tests fallidos o sin tests que importar |

## Tecnologias Utilizadas
- PySpark
- MongoDB
- Flask
- Docker
- Jenkins
