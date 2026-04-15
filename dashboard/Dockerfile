FROM python:3.12-slim

WORKDIR /dashboard

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=300 -r requirements.txt

# Copy application code
COPY .streamlit/ .streamlit/
COPY app/ app/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app/main.py", "--server.address=0.0.0.0"]
