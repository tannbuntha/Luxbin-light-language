#!/bin/bash

# LUXBIN Network Deployment Script

set -e

echo "=========================================="
echo " LUXBIN Network Deployment"
echo "=========================================="

# Check for required environment variables
if [ -z "$IONQ_API_KEY" ]; then
    echo "❌ Error: IONQ_API_KEY environment variable not set"
    echo "   Please set it: export IONQ_API_KEY='your_key_here'"
    exit 1
fi

# Function to deploy bootstrap nodes
deploy_bootstrap_nodes() {
    echo ""
    echo "📡 Deploying Bootstrap Nodes..."

    cd deployment/docker

    # Build and start containers
    docker-compose up -d bootstrap-us-east bootstrap-eu-west bootstrap-asia-pacific

    echo "   ✅ Bootstrap nodes deployed"
}

# Function to deploy network monitor
deploy_network_monitor() {
    echo ""
    echo "📊 Deploying Network Monitor..."

    cd deployment/docker

    # Build and start monitor
    docker-compose up -d network-monitor

    echo "   ✅ Network monitor deployed"
}

# Function to check status
check_status() {
    echo ""
    echo "🔍 Checking deployment status..."

    cd deployment/docker

    docker-compose ps

    echo ""
    echo "Health checks:"

    # Check bootstrap nodes
    for port in 8080 8081 8082; do
        echo -n "   Bootstrap (port $port): "
        if curl -sf http://localhost:$port/health > /dev/null 2>&1; then
            echo "✅ Healthy"
        else
            echo "⏳ Initializing (may take 1-2 minutes)..."
        fi
    done

    # Check monitor
    echo -n "   Network Monitor: "
    if curl -sf http://localhost:3000/api/metrics > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "⏳ Initializing..."
    fi
}

# Function to show logs
show_logs() {
    echo ""
    echo "📋 Showing logs (Ctrl+C to exit)..."

    cd deployment/docker

    docker-compose logs -f
}

# Main menu
case "${1:-deploy}" in
    deploy)
        deploy_bootstrap_nodes
        deploy_network_monitor

        echo ""
        echo "=========================================="
        echo " Deployment Complete!"
        echo "=========================================="
        echo ""
        echo "📊 Network Monitor: http://localhost:3000"
        echo "📡 Bootstrap Nodes:"
        echo "   - US East: http://localhost:8080"
        echo "   - EU West: http://localhost:8081"
        echo "   - Asia Pacific: http://localhost:8082"
        echo ""
        echo "⏳ Nodes are initializing (1-2 minutes)..."
        echo ""
        echo "Run './deploy.sh status' to check health"
        echo "Run './deploy.sh logs' to view logs"
        ;;

    status)
        check_status
        ;;

    logs)
        show_logs
        ;;

    stop)
        echo "🛑 Stopping LUXBIN network..."
        cd deployment/docker
        docker-compose down
        echo "   ✅ Network stopped"
        ;;

    restart)
        echo "🔄 Restarting LUXBIN network..."
        cd deployment/docker
        docker-compose restart
        echo "   ✅ Network restarted"
        ;;

    *)
        echo "Usage: $0 {deploy|status|logs|stop|restart}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy all services"
        echo "  status  - Check service health"
        echo "  logs    - View service logs"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        exit 1
        ;;
esac
