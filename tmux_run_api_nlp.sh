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

# Function to check if a spaCy model is installed
check_and_install_model() {
  model=$1
  tmux send-keys "python -c 'import spacy; spacy.load(\"$model\")' 2>/dev/null || python -m spacy download $model" C-m
}

# List of spaCy language models
models=(
"en_core_web_sm"
"de_core_news_sm"
"fr_core_news_sm"
"it_core_news_sm"
"es_core_news_sm"
"pt_core_news_sm"
"ru_core_news_sm"
)

# Install spaCy language models if not already installed
for model in "${models[@]}"; do
  check_and_install_model $model
done

# Run the main application
tmux send-keys "../docker/api_nlp/entrypoint_api.sh" C-m
tmux send-keys "python main.py" C-m

# Attach to the session
tmux attach-session -t $session