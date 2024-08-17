#!/bin/bash

mkdir -p ${PROMETHEUS_MULTIPROC_DIR}
chmod +R 777 ${PROMETHEUS_MULTIPROC_DIR}

gunicorn main:app --bind "${API_BANNER_HOST}:${API_BANNER_PORT}" --workers=12 --timeout=300 --worker-class uvicorn.workers.UvicornWorker