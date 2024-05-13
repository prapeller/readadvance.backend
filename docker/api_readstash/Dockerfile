ARG PYTHON_VERSION=3.11-slim-bullseye
FROM python:${PYTHON_VERSION} as my_python

FROM my_python as python-build-stage
ARG BUILD_ENV
ENV BUILD_ENV $BUILD_ENV

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev build-essential &&  \
    apt-get clean &&  \
    rm -rf /var/lib/apt/lists/*
COPY ./api_readstash/requirements .
COPY ./.envs .
RUN pip wheel --wheel-dir /usr/src/app/wheels -r ${BUILD_ENV}.txt

FROM my_python as python-run-stage

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies required for fetching the PostgreSQL key
RUN apt-get update && apt-get install -y --no-install-recommends gnupg2 wget ca-certificates lsb-release
# Add the PostgreSQL APT Repository for newer PostgreSQL versions
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list
# Import the repository signing key
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# Update, intall (with postgres tools incl pg_dump), cleanup
RUN apt-get update && apt-get install --no-install-recommends -y  \
    libpq-dev  \
    gettext  \
    curl netcat  \
    postgresql-client-14  \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-build-stage /usr/src/app/wheels /wheels/
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

COPY ./docker/api_readstash/entrypoint_api.sh /entrypoint_api.sh
COPY ./docker/api_readstash/start_api_prod.sh /start_api_prod.sh
COPY ./docker/api_readstash/start_api_local.sh /start_api_local.sh
COPY ./docker/api_readstash/start_api_tests.sh /start_api_tests.sh
RUN chmod +x /entrypoint_api.sh && \
    chmod +x /start_api_prod.sh &&  \
    chmod +x /start_api_local.sh &&  \
    chmod +x /start_api_tests.sh

ARG APP_HOME=/app/api_readstash
WORKDIR ${APP_HOME}
COPY ./api_readstash ${APP_HOME}
ENTRYPOINT ["/entrypoint_api.sh"]