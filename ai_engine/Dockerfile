FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY ai_engine/requirements.txt ai_engine/requirements.txt
RUN pip install --no-cache-dir -r ai_engine/requirements.txt

# Copy source code
COPY ai_engine/ ai_engine/

# Set Python path
ENV PYTHONPATH=/app

CMD ["uvicorn", "ai_engine.main:app", "--host", "0.0.0.0", "--port", "8001"]
