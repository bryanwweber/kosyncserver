# syntax=docker/dockerfile:1.9
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS build

SHELL ["sh", "-exc"]

ENV DEBIAN_FRONTEND=noninteractive

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_TOOL_BIN_DIR=/usr/local/bin \
    UV_PROJECT_ENVIRONMENT=/app

WORKDIR /tmp
COPY pyproject.toml uv.lock /tmp/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
    --locked \
    --no-dev \
    --no-install-project

COPY . /src
WORKDIR /src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS final

ENV PATH="/app/bin:$PATH" \
    DATABASE_PATH=/data/kosyncserver.db

STOPSIGNAL SIGINT

SHELL ["sh", "-exc"]

RUN groupadd -r app && \
    useradd -r -d /app -g app -N app && \
    mkdir -p /data && \
    chown -R app:app /data

COPY --from=build --chown=app:app /app /app
COPY healthcheck.py /app/healthcheck.py

USER app
WORKDIR /app

HEALTHCHECK --interval=5s --timeout=3s --start-period=3s --retries=3 \
    CMD ["python", "/app/healthcheck.py"]

CMD ["python", "-m", "kosyncserver"]
