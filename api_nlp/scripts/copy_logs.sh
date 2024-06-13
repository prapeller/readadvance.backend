#!/bin/bash

session="logs"

tmux start-server

tmux new-session -d -s $session

tmux send-keys "  # window 1, pane 0 (dev3.kaisaco.com://api_menu)" C-m
tmux send-keys "ssh dev3.kaisaco.com" C-m
tmux send-keys "docker cp api_menu:/app/api_menu/logs /home/pavelmirosh/" C-m
sleep 6

tmux splitw -h
tmux send-keys "  # window 1, pane 1 (localhost)" C-m
tmux send-keys "scp -r dev3.kaisaco.com:/home/pavelmirosh/logs .." C-m


tmux attach-session -t $session
