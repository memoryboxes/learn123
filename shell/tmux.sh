#!/bin/bash
# description "Start Tmux"

# Sleep for 5 seconds. If you are starting more than one tmux session
#   "at the same time", then make sure they all sleep for different periods
#   or you can experience problems
/bin/sleep 5
# Ensure the environment is available
source ~/.bashrc
# Create a new tmux session named newscrawler..
/usr/bin/tmux new-session -d -s work
# ...and control the tmux session (initially ensure the environment
#   is available, then run commands)

# /usr/bin/tmux send-keys -t workcash:0 "source ~/.bashrc" C-m
tmux new-window -n console -t work
/bin/sleep 3
/usr/bin/tmux send-keys -t work:0 "cd /opt/ && ./startwork.sh" C-m
/bin/sleep 3
/usr/bin/tmux send-keys -t work:1 "cd /opt/ && ./work start" C-m
