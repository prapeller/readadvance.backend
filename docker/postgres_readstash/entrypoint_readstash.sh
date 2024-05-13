#!/usr/bin/env bash
set -e

# Set POSTGRES_* variables from POSTGRES_OBJECT_STORAGE_*
export POSTGRES_USER=${POSTGRES_READSTASH_USER}
export POSTGRES_DB=${POSTGRES_READSTASH_DB}
export POSTGRES_PASSWORD=${POSTGRES_READSTASH_PASSWORD}

# Call the original docker-entrypoint.sh
exec /usr/local/bin/docker-entrypoint.sh "$@"