# syntax=docker/dockerfile:1
# Multi-stage build for the FastAPI backend.

FROM python:3.11-slim AS builder
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY pyproject.toml ./
RUN pip install --prefix=/install .

FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Run as a non-root user.
RUN useradd --create-home --uid 10001 atoms
COPY --from=builder /install /usr/local
COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app
USER atoms

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/health').status==200 else 1)" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
