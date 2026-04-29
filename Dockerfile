# ============================================
# Stage 1 : BUILDER - compile les dépendances
# ============================================

FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# ============================================
# Stage 2 : FINAL - image de production
# ============================================
FROM python:3.12-slim

LABEL maintainer="Mina"
LABEL version="0.1.0"
LABEL description="Chainlit application for RNCP chatbot with RAG and referentiel data"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src

COPY . .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

CMD ["chainlit", "run", "src/app.py", "--host", "0.0.0.0", "--port", "7860"]