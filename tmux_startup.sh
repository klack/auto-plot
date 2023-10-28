#!/bin/bash
tmux new-session -d -s plotter -n auto-plot
tmux send-keys -t plotter:auto-plot "/usr/bin/python3 /home/klack/auto-plot/auto-plot.py" Enter