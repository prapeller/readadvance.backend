#!/bin/bash

set -o errexit # if any command fails any reason, script fails
set -o pipefail # if none of of you pipecommand fails, exit fails
set -o nounset # if none of variables set, exit


redis_ready(){
   nc -z ${REDIS_HOST} ${REDIS_PORT}
}

until redis_ready; do
   >&2 echo "Waiting for Redis at ${REDIS_HOST}:${REDIS_PORT} to become available... 8-(("
   sleep 1
done
>&2 echo "Redis is ready!!! 8-))"


postgres_readstash_ready() {
python3 << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${POSTGRES_READSTASH_DB}",
        user="${POSTGRES_READSTASH_USER}",
        password="${POSTGRES_READSTASH_PASSWORD}",
        host="${POSTGRES_READSTASH_HOST}",
        port="${POSTGRES_READSTASH_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}


until postgres_readstash_ready; do
>&2 echo "Waiting for PostgreSQL db at(${POSTGRES_READSTASH_HOST}:${POSTGRES_READSTASH_PORT}) to become available... 8-(("
sleep 1
done
>&2 echo "PostgreSQL is ready!!! 8-))"

object_storage_ready() {
python3 << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${POSTGRES_OBJECT_STORAGE_DB}",
        user="${POSTGRES_OBJECT_STORAGE_USER}",
        password="${POSTGRES_OBJECT_STORAGE_PASSWORD}",
        host="${POSTGRES_OBJECT_STORAGE_HOST}",
        port="${POSTGRES_OBJECT_STORAGE_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until object_storage_ready; do
>&2 echo "Waiting for ObjectStorage at ${POSTGRES_OBJECT_STORAGE_HOST}:${POSTGRES_OBJECT_STORAGE_PORT} to become available... 8-(("
sleep 1
done
>&2 echo "ObjectStorage is ready!!! 8-))"


keycloak_ready() {
    response=$(curl --write-out "%{http_code}" --location --silent --output /dev/null "$KEYCLOAK_BASE_URL")
    if [ "$response" -eq 200 ]; then
        return 0
    else
        return 1
    fi
}

until keycloak_ready; do
>&2 echo "Waiting for Keycloak at (${KEYCLOAK_BASE_URL}) to become available... 8-(("
sleep 1
done
>&2 echo "Keycloak is ready!!! 8-))"

exec "$@"
