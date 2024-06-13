#!/bin/bash

python3 -m scripts.migrate -db postgres_readstash
python3 -m scripts.migrate -db postgres_obj_storage
python3 main.py
