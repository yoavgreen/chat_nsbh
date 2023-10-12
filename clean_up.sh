#!/bin/bash

# kill process
pkillall -9 -f /home/dev/PythonProjects/chat_nsbh/client.py
ps -ef | grep python

# Find all processes listening on port 8888
pid_list=($(netstat -tuln | grep ":8888 " | awk '{print $7}' | cut -d '/' -f 1))

# Check if there are any processes to kill
if [ ${#pid_list[@]} -eq 0 ]; then
  echo "No processes listening on port 8888 found."
else
  echo "Processes listening on port 8888:"
  for pid in "${pid_list[@]}"; do
    echo "Killing process with PID $pid"
    kill -9 "$pid"
  done
fi

