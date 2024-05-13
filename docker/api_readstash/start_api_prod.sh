#!/bin/bash

mkdir -p ${PROMETHEUS_MULTIPROC_DIR}
chmod +R 777 ${PROMETHEUS_MULTIPROC_DIR}

python3 -m scripts.migrate -db banner
python3 -m scripts.migrate -db os_banner
gunicorn main:app --bind "${API_BANNER_HOST}:${API_BANNER_PORT}" --workers=12 --timeout=300 --worker-class uvicorn.workers.UvicornWorker