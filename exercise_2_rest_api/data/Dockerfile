FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ingest_data.py .
COPY sample.csv .

CMD ["python", "ingest_data.py"]