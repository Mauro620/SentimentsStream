**CURSO BIG DATA**

Enunciados de Actividades

_Actividad 1: SentimentStream_

Institución Universitaria de Envigado

Programa de Ingeniería - Curso Big Data

2026-1

**ACTIVIDAD**

**SentimentStream: Pipeline integrado de análisis de sentimientos en tiempo real**

## 1\. Información general

| **Nombre**      | SentimentStream - Pipeline integrado de análisis de sentimientos |
| --------------- | ---------------------------------------------------------------- |
| **Modalidad**   | Individual o en parejas                                          |
| **Duración**    | 15 días calendario                                               |
| **Valor**       | 25% de la nota final del curso                                   |
| **Dataset**     | dataset_sentimientos_500.csv (provisto por el docente)           |
| **Tecnologías** | PySpark, MongoDB, Flask, Docker Compose, Jenkins, Power BI       |
| **Entrega**     | Repositorio GitHub + video demo (3-5 min) + dashboard Power BI   |

## 2\. Contexto y motivación

Las organizaciones modernas generan millones de comentarios en redes sociales cada día. Detectar automáticamente si un comentario es positivo, negativo o neutral en tiempo real y a escal es una capacidad crítica para áreas como servicio al cliente, análisis de marca y monitoreo de reputación.

Esta actividad integra los tres componentes principales trabajados durante el curso: el procesamiento en streaming con Apache Spark (ejercicio de abril), la persistencia y exposición de datos con MongoDB y Flask (ejercicio de octubre), y la orquestación de infraestructura con Docker y Jenkins (ejercicios de pipeline). La novedad consiste en unir los tres en un sistema cohesionado que opera sobre un dataset real de 500 registros etiquetados.

## 3\. Objetivos de aprendizaje

- Implementar un pipeline de Big Data de extremo a extremo que integre ingesta, procesamiento, almacenamiento, exposición y visualización de datos.
- Aplicar técnicas de procesamiento de lenguaje natural (limpieza de texto, vectorización TF-IDF) dentro de un contexto de streaming simulado.
- Desplegar y orquestar múltiples servicios mediante Docker Compose, garantizando portabilidad y reproducibilidad del entorno.
- Automatizar el ciclo de construcción y despliegue mediante un pipeline Jenkins, siguiendo buenas prácticas de integración continua.
- Conectar Power BI a una API REST para construir dashboards dinámicos sobre los resultados del modelo.

## 4\. Dataset

El archivo dataset_sentimientos_500.csv contiene 500 registros con la siguiente estructura:

| **Campo**       | **Tipo**   | **Valores**                   | **Descripción**                                              |
| --------------- | ---------- | ----------------------------- | ------------------------------------------------------------ |
| **id**          | Entero     | 1 - 500                       | Identificador único del registro                             |
| **texto**       | Texto      | Cadena libre en español       | Comentario original tal como fue publicado                   |
| **sentimiento** | Categórico | positivo / negativo / neutral | Etiqueta de clase para entrenamiento y validación del modelo |
| **fecha**       | Fecha      | YYYY-MM-DD                    | Fecha simulada de publicación del comentario                 |

## 5\. Arquitectura del sistema

El sistema completo se compone de cinco capas funcionales que deben estar integradas y operativas al momento de la entrega:

- Capa de ingesta: lectura del CSV y simulación de flujo mediante socket Python o lectura por micro-lotes de Spark Structured Streaming.
- Capa de procesamiento: pipeline PySpark con etapas de limpieza de texto, tokenización, eliminación de stopwords, vectorización con HashingTF/IDF y clasificación con Naive Bayes.
- Capa de persistencia: almacenamiento de predicciones en una colección MongoDB. Cada documento incluye el texto original, la predicción, la confianza del modelo y la marca de tiempo.
- Capa de exposición: API REST en Flask con al menos tres endpoints: /sentiments (listado con filtros), /stats (distribución de clases y métricas) y /predict (inferencia sobre texto nuevo).
- Capa de visualización: dashboard en Power BI conectado a la API, con distribución de sentimientos, tendencia temporal y tabla de últimas predicciones.

Toda la infraestructura debe correr en contenedores Docker orquestados con docker-compose.yml, y el pipeline de construcción y despliegue debe definirse en un Jenkinsfile.

## 6\. Entregables

- Repositorio GitHub público con estructura organizada: carpetas /spark, /api, /infra (Docker + Jenkins) y /docs; README con instrucciones claras de despliegue.
- Notebooks o scripts Python debidamente comentados: ingesta, entrenamiento del modelo y pruebas de la API.
- Dashboard Power BI (.pbix o capturas de pantalla) con mínimo tres visualizaciones: distribución de sentimientos, evolución temporal y tabla de predicciones recientes.
- Video demo de 3 a 5 minutos mostrando el pipeline corriendo de extremo a extremo, la ejecución del build en Jenkins y el dashboard actualizándose.

## 7\. Criterios de evaluación

| **Criterio de evaluación**                                                          | **Ponderación** | **Puntos / 5.0** |
| ----------------------------------------------------------------------------------- | --------------- | ---------------- |
| Pipeline funcional: Spark Streaming + MongoDB + Flask operando de extremo a extremo | 35%             | 1.75             |
| Infraestructura: Docker Compose con todos los servicios + Jenkinsfile ejecutable    | 25%             | 1.25             |
| Dashboard Power BI con mínimo tres visualizaciones conectadas a la API              | 25%             | 1.25             |
| Documentación, calidad del código y presentación del video demo                     | 15%             | 0.75             |
| **TOTAL**                                                                           | **100%**        | **5.0**          |

## 9\. Extras opcionales (bonificación hasta 0.5 puntos adicionales)

- Implementar autenticación básica (token o API key) en la API Flask.
- Agregar un endpoint /wordcloud que retorne las palabras más frecuentes por categoría de sentimiento.
- Configurar ngrok para exponer la API externamente y conectar Power BI en línea.
- Incluir pruebas unitarias para el pipeline de procesamiento de texto.

_| 2025-1_
