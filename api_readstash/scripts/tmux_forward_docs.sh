#!/bin/bash

session="dev-local-report"

tmux start-server

tmux new-session -d -s $session

tmux send-keys "ssh dev3.kaisaco.com -L 127.0.0.1:8080:127.0.0.1:8080" C-m
tmux send-keys "top" C-m

tmux splitw -h
tmux send-keys "ssh dev3.kaisaco.com -L 127.0.0.1:5555:127.0.0.1:5555" C-m
tmux send-keys "top" C-m

tmux splitw -h
tmux send-keys "ssh dev3.kaisaco.com -L 127.0.0.1:3000:127.0.0.1:3000" C-m
tmux send-keys "top" C-m

tmux attach-session -t $session