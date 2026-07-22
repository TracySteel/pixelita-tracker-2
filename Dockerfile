FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY transparent.png .
COPY pixelita ./pixelita

CMD gunicorn app:app --bind 0.0.0.0:${PORT:-8080}
