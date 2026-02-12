@echo off
REM Local Simulation - Node 1 Activation Script
REM Aethel Real Lattice v3.0.4 - HTTP Resilience Mode

echo ========================================
echo AETHEL TRIANGLE - NODE 1 LOCAL SIMULATION
echo ========================================
echo.
echo [INFO] Activating Node 1 (Hugging Face Simulation)
echo [INFO] Running on PORT 8001
echo [INFO] HTTP-Only Mode
echo.

REM Create local config
echo [STEP 1] Creating local configuration...
(
echo # Aethel Node 1 - Local Simulation
echo # Simulating Hugging Face Space
echo.
echo # P2P Configuration - DISABLED
echo AETHEL_P2P_ENABLED=false
echo AETHEL_P2P_LISTEN=/ip4/0.0.0.0/tcp/9001
echo AETHEL_P2P_TOPIC=aethel/lattice/v1
echo.
echo # Bootstrap Peers
echo AETHEL_P2P_BOOTSTRAP=
echo.
echo # HTTP Sync Fallback Nodes
echo AETHEL_LATTICE_NODES=http://localhost:8000,http://localhost:8002
echo.
echo # Storage Directories
echo AETHEL_STATE_DIR=.aethel_state_node1
echo AETHEL_VAULT_DIR=.aethel_vault_node1
echo AETHEL_SENTINEL_DIR=.aethel_sentinel_node1
echo.
echo # Heartbeat Configuration
echo AETHEL_HEARTBEAT_INTERVAL=5
echo AETHEL_PEERLESS_TIMEOUT=60
echo AETHEL_HTTP_POLL_INTERVAL=10
echo.
echo # Node Identity
echo AETHEL_NODE_NAME=node1-huggingface-local
echo AETHEL_NODE_ROLE=genesis-cloud
echo.
echo # Production Settings
echo AETHEL_ENVIRONMENT=development
echo AETHEL_LOG_LEVEL=INFO
) > .env.node1.local

echo [OK] Local configuration created
echo.

REM Display configuration
echo [STEP 2] Configuration Summary:
echo   - Node Name: node1-huggingface-local
echo   - Role: genesis-cloud
echo   - Mode: HTTP-ONLY RESILIENCE
echo   - Port: 8001
echo   - P2P: DISABLED
echo   - HTTP Sync: ENABLED
echo   - Peer Nodes: localhost:8000, localhost:8002
echo.

REM Start the server
echo [STEP 3] Starting Aethel API Server on PORT 8001...
echo [INFO] This simulates Hugging Face Space locally
echo [INFO] Press Ctrl+C to stop the server
echo.
echo ========================================
echo SERVER OUTPUT:
echo ========================================
echo.

python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --env-file .env.node1.local

echo.
echo ========================================
echo [INFO] Server stopped
echo ========================================
pause
