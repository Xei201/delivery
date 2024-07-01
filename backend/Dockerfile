FROM python:3.12-slim-bullseye
WORKDIR /app
EXPOSE 8000

ENV POETRY_VERSION=1.5.1

# Устанавливаем зависимости проекта
COPY pyproject.toml poetry.lock ./
RUN pip install "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

RUN apt-get update && apt-get install -y curl gnupg2

COPY . .


CMD ["sh", "run.sh"]
