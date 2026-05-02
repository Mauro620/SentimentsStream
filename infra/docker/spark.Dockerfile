FROM apache/spark:3.5.1-python3

# Download mongo-spark-connector JAR for Spark-Mongo integration
RUN wget -O /opt/spark/jars/mongo-spark-connector_2.12-10.3.0.jar \
    https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar

# Set extra classpath to include the connector
ENV SPARK_EXTRA_JARS=/opt/spark/jars/mongo-spark-connector_2.12-10.3.0.jar
