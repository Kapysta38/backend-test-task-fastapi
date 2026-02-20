FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

ENV PATH="/app/.venv/bin:$PATH"

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

RUN apt-get update && apt-get install -y \
    python3-setuptools \
    build-essential \
    python3-dev \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*


ENV PYTHONPATH=/app

COPY ./scripts /app/scripts

COPY ./pyproject.toml ./uv.lock ./alembic.ini ./tests  /app/

COPY ./app /app/app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

RUN chmod +x scripts/prestart.sh

ENTRYPOINT ["scripts/prestart.sh"]

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
