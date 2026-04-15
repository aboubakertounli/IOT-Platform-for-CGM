FROM python:3.12-slim

WORKDIR /edge

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=300 -r requirements.txt

COPY app/ app/
COPY data/ data/

CMD ["python", "-m", "app.main"]
