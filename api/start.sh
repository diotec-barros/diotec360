#!/bin/bash
# Start script for Railway deployment

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    source /opt/venv/bin/activate
    echo "Virtual environment activated"
fi

# Set default port if not provided
PORT=${PORT:-8000}

echo "Starting Aethel API on port $PORT"
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Python path: $(which python)"

# Try to find uvicorn
if [ -f "/opt/venv/bin/uvicorn" ]; then
    echo "Using uvicorn from: /opt/venv/bin/uvicorn"
    exec /opt/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port $PORT --log-level info
elif command -v uvicorn &> /dev/null; then
    echo "Using uvicorn from PATH: $(which uvicorn)"
    exec uvicorn api.main:app --host 0.0.0.0 --port $PORT --log-level info
else
    echo "ERROR: uvicorn not found!"
    echo "Checking /opt/venv/bin contents:"
    ls -la /opt/venv/bin/ | head -20
    exit 1
fi
