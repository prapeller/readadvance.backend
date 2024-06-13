#!/bin/bash

session="run_api_readstash_and_celery"

# Ensure the session is not already running
if tmux has-session -t $session 2>/dev/null; then
  tmux kill-session -t $session
fi

# Start tmux server and new session
tmux start-server
tmux new-session -d -s $session
# environment variables and entrypoint
tmux send-keys "source ./export_local_envs.sh" C-m
tmux send-keys "cd api_readstash" C-m
tmux send-keys "if [ ! -d venv ]; then python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements/local.txt; else source venv/bin/activate; fi" C-m
tmux send-keys "../docker/api_readstash/entrypoint_api.sh" C-m
# migrate and run
tmux send-keys "python -m scripts.migrate -db='postgres_readstash'" C-m
tmux send-keys "python -m scripts.migrate -db='postgres_obj_storage'" C-m
tmux send-keys "python main.py" C-m

tmux splitw -h

# environment variables and entrypoint
tmux send-keys "source ./export_local_envs.sh" C-m
tmux send-keys "cd api_readstash" C-m
tmux send-keys "if [ ! -d venv ]; then python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements/local.txt; else source venv/bin/activate; fi" C-m
tmux send-keys "../docker/api_readstash/entrypoint_api.sh" C-m
tmux send-keys "celery -A celery_app worker --loglevel=INFO" C-m

tmux splitw -h

# environment variables and entrypoint
tmux send-keys "source ./export_local_envs.sh" C-m
tmux send-keys "cd api_readstash" C-m
tmux send-keys "if [ ! -d venv ]; then python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements/local.txt; else source venv/bin/activate; fi" C-m
tmux send-keys "../docker/api_readstash/entrypoint_api.sh" C-m
tmux send-keys "celery -A celery_app flower --loglevel=INFO" C-m

# Attach to the session
tmux attach-session -t $session