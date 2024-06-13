#!/bin/bash

set -o errexit # if any command fails any reason, script fails
set -o pipefail # if none of of you pipecommand fails, exit fails
set -o nounset # if none of variables set, exit

exec "$@"
