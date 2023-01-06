FROM python:3.12.0a1-alpine as builder
COPY . /app
WORKDIR /app
RUN pip install flake8==3.8.4
RUN flake8 --ignore=E501,F401,W605,C901 .
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev libressl-dev
RUN pip wheel . --no-cache-dir --wheel-dir /usr/src/app/wheels
RUN apk del .build-deps gcc musl-dev

FROM python:3.12.0a1-alpine
ENV PYTHONUNBUFFERED 1
COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/* \
    && rm -rf /wheels/
WORKDIR /app
ENTRYPOINT ["cloud_discovery"]
