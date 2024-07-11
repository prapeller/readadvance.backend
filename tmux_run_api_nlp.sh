#!/bin/bash

session="run_api_nlp"

# Ensure the session is not already running
if tmux has-session -t $session 2>/dev/null; then
  tmux kill-session -t $session
fi

# Start tmux server and new session
tmux start-server
tmux new-session -d -s $session

# Environment variables and entrypoint
tmux send-keys "source ./export_local_envs.sh" C-m
tmux send-keys "cd api_nlp" C-m

# Setup virtual environment and install dependencies
tmux send-keys "if [ ! -d venv ]; then python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements/local.txt; else source venv/bin/activate; fi" C-m

# Run the main application
tmux send-keys "../docker/api_nlp/entrypoint_api.sh" C-m
tmux send-keys "python main.py" C-m

# Attach to the session
tmux attach-session -t $session