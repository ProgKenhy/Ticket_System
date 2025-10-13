FROM python:3.13.2-slim AS base

WORKDIR /app/src

ARG UID=1000
ARG GID=1000

RUN groupadd -g "${GID}" python \
    && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python

RUN chown python:python /app

USER python

FROM base AS app
COPY --chown=python:python requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt
COPY --chown=python:python . .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS consumer
COPY src/rabbit/consumer.py ./rabbit/
RUN pip install --user --no-cache-dir pika
CMD ["python", "rabbit/consumer.py"]