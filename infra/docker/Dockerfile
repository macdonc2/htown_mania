FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv with locked versions
RUN uv pip install --system --no-cache \
    fastapi \
    uvicorn[standard] \
    sqlalchemy \
    asyncpg \
    httpx[http2] \
    itsdangerous \
    openai \
    twilio \
    beautifulsoup4 \
    jinja2 \
    alembic \
    pydantic-settings \
    greenlet \
    pydantic \
    pydantic-ai \
    pydantic-ai-slim[openai]

# Copy application code
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
