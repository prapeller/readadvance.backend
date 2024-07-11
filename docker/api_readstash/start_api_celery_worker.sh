#!/bin/bash

set -o errexit
set -o nounset

celery -A celery_app worker --loglevel=info --queues=default