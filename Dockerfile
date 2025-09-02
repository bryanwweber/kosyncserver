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

RUN groupadd -r app && \
    useradd -r -d /app -g app -N app

STOPSIGNAL SIGINT
COPY --from=build --chown=app:app /app /app
ENV PATH="/app/bin:$PATH"

USER app
WORKDIR /app

CMD ["python", "-m", "kosyncserver"]
