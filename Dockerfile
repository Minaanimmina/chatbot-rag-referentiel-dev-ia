# ============================================
# Stage 1 : BUILDER - compile les dépendances
# ============================================

FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# ============================================
# Stage 2 : FINAL - image de production
# ============================================
FROM python:3.12-slim

LABEL maintainer="Mina"
LABEL version="0.1.0"
LABEL description="Chainlit application for RNCP chatbot with RAG and referentiel data"

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["./entrypoint.sh"]