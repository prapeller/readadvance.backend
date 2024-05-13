#!/bin/bash

session="run_api_head"

# Ensure the session is not already running
if tmux has-session -t $session 2>/dev/null; then
  tmux kill-session -t $session
fi

# Start tmux server and new session
tmux start-server
tmux new-session -d -s $session

# environment variables
tmux send-keys "source ./export_vars_readstash.sh" C-m

# initial setup, entrypoint and run the api_head
tmux send-keys "cd api_readstash" C-m
tmux send-keys "python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements/local.txt" C-m
tmux send-keys "../docker/api_readstash/entrypoint_api.sh" C-m
tmux send-keys "python -m scripts.migrate -db='postgres_readstash'" C-m
tmux send-keys "python -m scripts.migrate -db='postgres_obj_storage'" C-m
tmux send-keys "python main.py" C-m

# Attach to the session
tmux attach-session -t $session