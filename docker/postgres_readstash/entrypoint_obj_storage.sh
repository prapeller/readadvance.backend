#!/usr/bin/env bash
# Set POSTGRES_* variables from POSTGRES_OBJECT_STORAGE_*
export POSTGRES_USER=${POSTGRES_OBJECT_STORAGE_USER}
export POSTGRES_DB=${POSTGRES_OBJECT_STORAGE_DB}
export POSTGRES_PASSWORD=${POSTGRES_OBJECT_STORAGE_PASSWORD}

# Call the original docker-entrypoint.sh
exec /usr/local/bin/docker-entrypoint.sh "$@"