# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY hello_kube.py .

CMD ["python", "hello_kube.py"]

