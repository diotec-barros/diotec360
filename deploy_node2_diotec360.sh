#!/bin/bash
# ========================================
# Aethel v3.0.5 - Node 2 Deployment
# Target: diotec360.com Primary Server
# ========================================

set -e  # Exit on error

echo ""
echo "========================================"
echo "  AETHEL v3.0.5 - NODE 2 DEPLOYMENT"
echo "  Target: diotec360.com"
echo "========================================"
echo ""

# Configuration
SERVER="user@api.diotec360.com"
DEPLOY_DIR="/var/www/aethel"
SERVICE_NAME="aethel"

echo "[1/8] Connecting to diotec360.com server..."
ssh $SERVER "echo 'Connection successful'"

echo ""
echo "[2/8] Creating deployment directory..."
ssh $SERVER "mkdir -p $DEPLOY_DIR"

echo ""
echo "[3/8] Uploading application files..."
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
  aethel/ $SERVER:$DEPLOY_DIR/aethel/
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
  api/ $SERVER:$DEPLOY_DIR/api/

echo ""
echo "[4/8] Uploading configuration..."
scp requirements.txt $SERVER:$DEPLOY_DIR/
scp .env.node2.diotec360 $SERVER:$DEPLOY_DIR/.env

echo ""
echo "[5/8] Uploading genesis state..."
rsync -avz .aethel_vault/ $SERVER:$DEPLOY_DIR/.aethel_vault/
rsync -avz .aethel_state/ $SERVER:$DEPLOY_DIR/.aethel_state/

echo ""
echo "[6/8] Installing dependencies..."
ssh $SERVER "cd $DEPLOY_DIR && pip3 install -r requirements.txt"

echo ""
echo "[7/8] Creating systemd service..."
ssh $SERVER "sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << 'EOF'
[Unit]
Description=Aethel Lattice Node 2
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$DEPLOY_DIR
Environment=\"PATH=/usr/local/bin:/usr/bin:/bin\"
ExecStart=/usr/local/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

echo ""
echo "[8/8] Starting service..."
ssh $SERVER "sudo systemctl daemon-reload"
ssh $SERVER "sudo systemctl enable $SERVICE_NAME"
ssh $SERVER "sudo systemctl restart $SERVICE_NAME"

echo ""
echo "Waiting for service to start..."
sleep 5

echo ""
echo "Verifying deployment..."
ssh $SERVER "curl -s http://localhost:8000/health" || echo "Health check failed!"

echo ""
echo "========================================"
echo "  DEPLOYMENT SUCCESSFUL! 🎉"
echo "========================================"
echo ""
echo "Node 2 is running at:"
echo "  Internal: http://localhost:8000"
echo "  External: https://api.diotec360.com"
echo ""
echo "Verify deployment:"
echo "  curl https://api.diotec360.com/health"
echo "  curl https://api.diotec360.com/api/lattice/state"
echo ""
echo "Expected Merkle Root:"
echo "  5df3daee3a0ca23c388a16c3db2c2388aea63f1c4ed5fa12377fe0fef6bf3ce5"
echo ""
echo "Check logs:"
echo "  ssh $SERVER 'sudo journalctl -u $SERVICE_NAME -f'"
echo ""
