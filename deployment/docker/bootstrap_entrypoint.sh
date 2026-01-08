#!/bin/bash

# LUXBIN Bootstrap Node Entrypoint

set -e

echo "🚀 Starting LUXBIN Bootstrap Node..."
echo "   Node Name: ${NODE_NAME:-bootstrap-1}"
echo "   Region: ${REGION:-us-east}"
echo "   Port: ${PORT:-8080}"

# Set defaults
export NODE_NAME=${NODE_NAME:-bootstrap-1}
export REGION=${REGION:-us-east}
export PORT=${PORT:-8080}

# Run bootstrap node
exec python3 luxbin_bootstrap_node.py \
    --name "$NODE_NAME" \
    --region "$REGION" \
    --port "$PORT"
