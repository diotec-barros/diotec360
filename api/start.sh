#!/bin/bash
# Simplified start script for Railway

set -e

PORT=${PORT:-8000}

echo "🚀 Starting Aethel API"
echo "📍 Port: $PORT"
echo "📂 Working directory: $(pwd)"
echo "🐍 Python: $(python --version)"

# Direct execution - no complexity
exec python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT --log-level info
