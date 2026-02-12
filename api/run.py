#!/usr/bin/env python3
"""
Railway-compatible startup script
Reads PORT from environment variable correctly
"""
import os
import sys
from pathlib import Path

def main():
    # Add parent directory to Python path
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    
    # Get port from environment, default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting Aethel API on port {port}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[0]}")
    
    # Import uvicorn
    import uvicorn
    
    # Run the app
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
