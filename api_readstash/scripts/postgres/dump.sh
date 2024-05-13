#!/usr/bin/env bash

set -e # Exit immediately if a command exits with a non-zero status.

working_dir="$(dirname ${0})"

echo "working_dir= ${working_dir}"
echo "ENV= ${ENV}"

source "${working_dir}/messages.sh"
source "${working_dir}/../../../.envs/.${ENV}/.postgres_readstash"

message_welcome "Backing up the '${POSTGRES_DB}' database..."

dump_dir_path="staticfiles/backups"
dump_file_name="dump_last"

export PGHOST="${POSTGRES_HOST}"
export PGPORT="${POSTGRES_PORT}"
export PGUSER="${POSTGRES_USER}"
export PGPASSWORD="${POSTGRES_PASSWORD}"
export PGDATABASE="${POSTGRES_DB}"

pg_dump -Fc > "${dump_dir_path}/${dump_file_name}" || exit
message_success "'${POSTGRES_DB}' database made backup to '${dump_dir_path}/${dump_file_name}'"
