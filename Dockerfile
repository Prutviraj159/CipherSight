# Builder keeps package-install tooling out of the runtime image.
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /service
COPY --from=builder /opt/venv /opt/venv
COPY app ./app
COPY alembic.ini .
COPY migrations ./migrations
COPY tests ./tests

# API and future worker processes must not run as root.
RUN groupadd --system appuser \
    && useradd --system --gid appuser --create-home appuser \
    && chown -R appuser:appuser /service
USER appuser
EXPOSE 8000
