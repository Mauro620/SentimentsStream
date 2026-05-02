FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install flask pymongo
WORKDIR /app
COPY src/ /app/src/
COPY app.py /app/app.py
EXPOSE 5000
CMD ["python", "/app/app.py"]
