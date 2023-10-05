#!/bin/bash

# kill process
pkillall -9 -f /home/dev/PythonProjects/chat_nsbh/client.py
pkill -9 -f /home/dev/PythonProjects/chat_nsbh/server.py
ps -ef | grep python

