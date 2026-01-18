#!/bin/bash

# Automatically kill any old process on 8005
kill -9 $(lsof -t -i:8005) 2>/dev/null

echo "Starting YAML Engine on port 8005..."

python3 -m uvicorn api:app --port 8005 --reload

