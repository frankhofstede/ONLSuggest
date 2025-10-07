# ONLSuggest Backend Dockerfile for Render.com
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy Dutch model
RUN python -m spacy download nl_core_news_sm

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run database migrations and start server
CMD alembic upgrade head && \
    python scripts/create_admin.py && \
    python scripts/seed_data.py && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000
