#!/usr/bin/env bash

set -e # Exit immediately if a command exits with a non-zero status.

working_dir="$(dirname ${0})"

echo "working_dir= ${working_dir}"
echo "ENV= ${ENV}"

source "${working_dir}/messages.sh"
source "${working_dir}/../../../.envs/.${ENV}/.postgres_readstash"

message_welcome "Restoring to '${POSTGRES_DB}' database..."

dump_dir_path="staticfiles/backups"
uploaded_dump="uploaded_dump"

cd ${dump_dir_path} || exit

export PGHOST="${POSTGRES_HOST}"
export PGPORT="${POSTGRES_PORT}"
export PGUSER="${POSTGRES_USER}"
export PGPASSWORD="${POSTGRES_PASSWORD}"
export PGDATABASE="${POSTGRES_DB}"

pg_restore -d ${POSTGRES_DB} --clean "${uploaded_dump}" || exit
message_success "'${POSTGRES_DB}' database was restored from '${dump_dir_path}/${uploaded_dump}'"
