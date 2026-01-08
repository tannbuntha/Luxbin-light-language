#!/bin/bash

# LUXBIN Gateway Startup Script
# Starts the LUXBIN quantum gateway node for HTTP bridge access

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                        LUXBIN GATEWAY NODE                                   ║"
echo "║                                                                              ║"
echo "║              HTTP Bridge to Quantum Internet                                 ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q aiohttp qiskit qiskit-ibm-runtime cirq requests

# Check for IBM Quantum API key
if [ -z "$IBM_QUANTUM_API_KEY" ]; then
    echo ""
    echo "⚠️  IBM_QUANTUM_API_KEY not set"
    echo ""
    echo "To use quantum computers, set your API key:"
    echo "   export IBM_QUANTUM_API_KEY='your-key-here'"
    echo ""
    echo "Get your key from: https://quantum.ibm.com/"
    echo ""
    read -p "Continue without quantum access? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for IonQ API key (optional)
if [ -z "$IONQ_API_KEY" ]; then
    echo "ℹ️  IonQ API key not set (optional)"
fi

echo ""
echo "🚀 Starting LUXBIN Gateway..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Gateway will be available at:"
echo "   📍 http://localhost:9000"
echo ""
echo "Your gaming apps will be accessible via:"
echo "   🎮 http://localhost:9000/globalblackjack.600nm.HASH/"
echo "   📱 http://localhost:9000/niche-app.500nm.HASH/"
echo "   🎯 http://localhost:9000/fortnite.600nm.GAME/"
echo ""
echo "API Endpoints:"
echo "   GET /status              - Gateway status"
echo "   GET /fetch?address=...   - Fetch from LUXBIN network"
echo "   POST /register           - Register name on blockchain"
echo "   GET /resolve?name=...    - Resolve name to address"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop the gateway"
echo ""

# Start the gateway
python3 luxbin_gateway_service.py

# Cleanup on exit
echo ""
echo "🛑 Gateway stopped"
deactivate
