#!/usr/bin/env bash
# Set POSTGRES_* variables from POSTGRES_OBJECT_STORAGE_*
export POSTGRES_DB=${POSTGRES_KEYCLOAK_DB}
export POSTGRES_USER=${POSTGRES_KEYCLOAK_USER}
export POSTGRES_PASSWORD=${POSTGRES_KEYCLOAK_PASSWORD}


# Call the original docker-entrypoint.sh
exec /usr/local/bin/docker-entrypoint.sh "$@"