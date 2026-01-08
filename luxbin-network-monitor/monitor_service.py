"""
LUXBIN Network Monitor Service

Real-time network monitoring dashboard

Features:
- Live network statistics
- Bootstrap node health monitoring
- Peer connectivity visualization
- Blockchain sync status
- Performance metrics
- Historical data tracking
"""

import asyncio
import time
import json
from typing import Dict, List
from aiohttp import web
import aiohttp
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('luxbin.monitor')


class LUXBINNetworkMonitor:
    """
    Network monitoring service for LUXBIN

    Tracks:
    - Bootstrap node health
    - Network-wide statistics
    - Performance metrics
    - Historical trends
    """

    def __init__(self, port: int = 3000):
        """
        Initialize network monitor

        Args:
            port: HTTP server port
        """
        self.port = port

        # Bootstrap nodes to monitor
        self.bootstrap_nodes = [
            {'name': 'bootstrap-1', 'url': 'http://localhost:8080', 'region': 'us-east'},
            # Add more bootstrap nodes here
        ]

        # Metrics storage
        self.metrics_history = []
        self.max_history = 1000  # Keep last 1000 data points

        # Current network status
        self.network_status = {
            'total_nodes': 0,
            'total_peers': 0,
            'bootstrap_nodes_healthy': 0,
            'last_update': None
        }

    async def fetch_bootstrap_metrics(self, bootstrap_node: Dict) -> Dict:
        """
        Fetch metrics from bootstrap node

        Args:
            bootstrap_node: Bootstrap node info

        Returns:
            Metrics dict
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Get status
                async with session.get(f"{bootstrap_node['url']}/status", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            'success': True,
                            'node': bootstrap_node['name'],
                            'region': bootstrap_node['region'],
                            'metrics': data.get('metrics', {}),
                            'timestamp': time.time()
                        }

        except Exception as e:
            logger.error(f"Failed to fetch metrics from {bootstrap_node['name']}: {e}")

        return {
            'success': False,
            'node': bootstrap_node['name'],
            'region': bootstrap_node['region'],
            'error': 'Connection failed',
            'timestamp': time.time()
        }

    async def collect_network_metrics(self) -> Dict:
        """
        Collect metrics from all bootstrap nodes

        Returns:
            Aggregated network metrics
        """
        logger.info("📊 Collecting network metrics...")

        # Fetch from all bootstrap nodes
        tasks = [
            self.fetch_bootstrap_metrics(node)
            for node in self.bootstrap_nodes
        ]

        results = await asyncio.gather(*tasks)

        # Aggregate metrics
        total_nodes = 0
        total_peers = 0
        healthy_nodes = 0
        total_content = 0
        total_names = 0

        node_metrics = []

        for result in results:
            if result['success']:
                metrics = result['metrics']

                total_peers += metrics.get('peers_connected', 0)
                total_nodes += 1

                if metrics.get('is_healthy'):
                    healthy_nodes += 1

                total_content += metrics.get('dht_content_count', 0)
                total_names += metrics.get('blockchain_height', 0)

                node_metrics.append({
                    'node': result['node'],
                    'region': result['region'],
                    'healthy': metrics.get('is_healthy', False),
                    'peers': metrics.get('peers_connected', 0),
                    'uptime_hours': round(metrics.get('uptime_hours', 0), 2),
                    'requests_handled': metrics.get('requests_handled', 0)
                })

        network_metrics = {
            'timestamp': time.time(),
            'bootstrap_nodes': {
                'total': len(self.bootstrap_nodes),
                'healthy': healthy_nodes,
                'unhealthy': len(self.bootstrap_nodes) - healthy_nodes
            },
            'network': {
                'total_peers': total_peers,
                'total_content': total_content,
                'blockchain_height': total_names
            },
            'nodes': node_metrics
        }

        # Store in history
        self.metrics_history.append(network_metrics)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)

        # Update current status
        self.network_status = {
            'total_nodes': total_nodes,
            'total_peers': total_peers,
            'bootstrap_nodes_healthy': healthy_nodes,
            'last_update': datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        }

        logger.info(f"   ✅ Nodes: {total_nodes}, Peers: {total_peers}, Healthy: {healthy_nodes}/{len(self.bootstrap_nodes)}")

        return network_metrics

    async def handle_dashboard(self, request):
        """GET / - Main dashboard"""
        html = open('/Users/nicholechristie/luxbin-light-language/luxbin-network-monitor/templates/dashboard.html').read()
        return web.Response(text=html, content_type='text/html')

    async def handle_metrics(self, request):
        """GET /api/metrics - Current metrics"""
        if not self.metrics_history:
            await self.collect_network_metrics()

        latest_metrics = self.metrics_history[-1] if self.metrics_history else {}

        return web.json_response({
            'success': True,
            'metrics': latest_metrics,
            'network_status': self.network_status
        })

    async def handle_history(self, request):
        """GET /api/history - Historical metrics"""
        limit = int(request.query.get('limit', 100))

        history = self.metrics_history[-limit:]

        return web.json_response({
            'success': True,
            'history': history,
            'count': len(history)
        })

    async def handle_nodes(self, request):
        """GET /api/nodes - Bootstrap node list"""
        return web.json_response({
            'success': True,
            'nodes': self.bootstrap_nodes
        })

    async def start_server(self):
        """Start monitoring dashboard server"""
        app = web.Application()

        # Routes
        app.router.add_get('/', self.handle_dashboard)
        app.router.add_get('/api/metrics', self.handle_metrics)
        app.router.add_get('/api/history', self.handle_history)
        app.router.add_get('/api/nodes', self.handle_nodes)

        # Static files
        app.router.add_static('/static', '/Users/nicholechristie/luxbin-light-language/luxbin-network-monitor/static')

        # Start server
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()

        logger.info("")
        logger.info("=" * 70)
        logger.info(" LUXBIN NETWORK MONITOR")
        logger.info("=" * 70)
        logger.info(f"🌐 Dashboard: http://localhost:{self.port}")
        logger.info(f"📊 Monitoring {len(self.bootstrap_nodes)} bootstrap nodes")
        logger.info("=" * 70)
        logger.info("✅ Monitor service running")
        logger.info("=" * 70)

        # Background metrics collection
        asyncio.create_task(self.periodic_metrics_collection())

        # Keep running
        await asyncio.Event().wait()

    async def periodic_metrics_collection(self):
        """Periodically collect metrics"""
        while True:
            try:
                await self.collect_network_metrics()
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")

            # Collect every 30 seconds
            await asyncio.sleep(30)


async def main():
    """Run network monitor"""
    import argparse

    parser = argparse.ArgumentParser(description='LUXBIN Network Monitor')
    parser.add_argument('--port', type=int, default=3000, help='Dashboard port')
    args = parser.parse_args()

    # Create monitor
    monitor = LUXBINNetworkMonitor(port=args.port)

    # Start server
    await monitor.start_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Network monitor stopped")
        logger.info("=" * 70)
