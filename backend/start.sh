#!/bin/bash

# Start FastAPI backend
source venv/bin/activate
echo "Starting FastAPI backend on http://localhost:8000"
echo "Press Ctrl+C to stop"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
