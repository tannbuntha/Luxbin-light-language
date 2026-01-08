"""
LUXBIN Bootstrap Node

Production-ready bootstrap node for LUXBIN network

Features:
- High availability (99.9% uptime target)
- Peer discovery assistance
- Network metrics collection
- Automatic peer management
- Health monitoring
- API for network status

Deploy on cloud infrastructure (AWS, GCP, Azure, etc.)
"""

import asyncio
import time
import json
from typing import Dict, List
from aiohttp import web
import logging

from luxbin_p2p_mesh import QuantumP2PNode
from luxbin_photonic_router import PhotonicRouter
from luxbin_name_system import LUXBINNameSystem
from luxbin_dht import LUXBINDistributedHashTable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('luxbin.bootstrap')


class LUXBINBootstrapNode:
    """
    Production bootstrap node for LUXBIN network

    Provides:
    - Peer discovery assistance
    - Network health monitoring
    - Metrics collection
    - High availability
    """

    def __init__(
        self,
        node_name: str,
        ionq_api_key: str,
        region: str = 'us-east',
        port: int = 8080
    ):
        """
        Initialize bootstrap node

        Args:
            node_name: Bootstrap node identifier
            ionq_api_key: IonQ API key
            region: Geographic region (us-east, eu-west, asia-pacific)
            port: HTTP API port
        """
        self.node_name = node_name
        self.ionq_api_key = ionq_api_key
        self.region = region
        self.port = port

        # Network components
        self.p2p_node = None
        self.router = None
        self.name_system = None
        self.dht = None

        # Metrics
        self.start_time = time.time()
        self.total_peers_assisted = 0
        self.active_connections = 0
        self.requests_handled = 0

        # Peer tracking
        self.known_peers = {}  # node_id -> PeerInfo
        self.peer_timestamps = {}  # node_id -> last_seen

        # Health status
        self.is_healthy = False
        self.last_health_check = None

    async def initialize(self):
        """Initialize bootstrap node"""
        logger.info(f"🚀 Initializing LUXBIN Bootstrap Node: {self.node_name}")
        logger.info(f"   Region: {self.region}")

        # Create P2P node
        logger.info("📡 Creating quantum P2P node...")
        self.p2p_node = QuantumP2PNode(
            quantum_backends=['ibm_fez', 'ibm_torino', 'ibm_marrakesh'],
            ionq_api_key=self.ionq_api_key
        )

        # Bootstrap
        logger.info("🔗 Bootstrapping into network...")
        await self.p2p_node.bootstrap()

        logger.info(f"✅ Node ID: {self.p2p_node.node_id}")

        # Create router
        logger.info("🔀 Creating photonic router...")
        self.router = PhotonicRouter(self.p2p_node)

        # Create name system
        logger.info("📝 Creating LUXBIN Name System...")
        self.name_system = LUXBINNameSystem()
        self.name_system.blockchain.initialize()

        # Create genesis block
        self.name_system.blockchain.add_transaction({
            'type': 'GENESIS',
            'timestamp': time.time(),
            'data': f'Bootstrap Node {self.node_name} Genesis',
            'region': self.region
        })
        self.name_system.blockchain.mine_block()

        # Create DHT
        logger.info("💾 Creating DHT...")
        self.dht = LUXBINDistributedHashTable(self.p2p_node, replication_factor=3)

        self.is_healthy = True
        self.last_health_check = time.time()

        logger.info("✅ Bootstrap node initialized")

    async def peer_discovery_assist(self, requesting_node_info: Dict) -> List[Dict]:
        """
        Assist new node with peer discovery

        Args:
            requesting_node_info: Info about requesting node

        Returns:
            List of peer information
        """
        logger.info(f"🔍 Assisting peer discovery for node: {requesting_node_info.get('node_id', 'unknown')[:16]}...")

        self.total_peers_assisted += 1

        # Get current peers
        peers = list(self.p2p_node.peers.values())

        # Filter by wavelength compatibility if requested
        wavelength_pref = requesting_node_info.get('wavelength_preference')
        if wavelength_pref:
            compatible_peers = self.p2p_node.get_peers_by_wavelength(
                wavelength_pref,
                tolerance=100
            )
            peers = compatible_peers if compatible_peers else peers

        # Return top 10 peers
        peer_list = []
        for peer in peers[:10]:
            peer_list.append({
                'node_id': peer.node_id,
                'wavelength_range': peer.wavelength_range,
                'endpoint': f'luxbin://{peer.node_id}',
                'last_seen': self.peer_timestamps.get(peer.node_id, time.time())
            })

        logger.info(f"   ✅ Returning {len(peer_list)} peers")

        return peer_list

    async def health_check(self) -> Dict:
        """
        Perform health check

        Returns:
            Health status dict
        """
        checks = {
            'node_running': self.p2p_node is not None,
            'peers_connected': len(self.p2p_node.peers) > 0 if self.p2p_node else False,
            'blockchain_synced': len(self.name_system.blockchain.blockchain) > 0 if self.name_system else False,
            'uptime_ok': (time.time() - self.start_time) > 60  # At least 1 minute
        }

        self.is_healthy = all(checks.values())
        self.last_health_check = time.time()

        return {
            'healthy': self.is_healthy,
            'checks': checks,
            'timestamp': self.last_health_check
        }

    async def collect_metrics(self) -> Dict:
        """
        Collect network metrics

        Returns:
            Metrics dict
        """
        uptime = time.time() - self.start_time

        metrics = {
            'node_name': self.node_name,
            'region': self.region,
            'node_id': self.p2p_node.node_id if self.p2p_node else None,
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'peers_connected': len(self.p2p_node.peers) if self.p2p_node else 0,
            'peers_assisted': self.total_peers_assisted,
            'requests_handled': self.requests_handled,
            'blockchain_height': len(self.name_system.blockchain.blockchain) if self.name_system else 0,
            'dht_content_count': len(self.dht.local_storage) if self.dht else 0,
            'is_healthy': self.is_healthy,
            'last_health_check': self.last_health_check,
            'quantum_backends': self.p2p_node.quantum_backends if self.p2p_node else []
        }

        return metrics

    # HTTP API Handlers

    async def handle_status(self, request):
        """GET /status - Bootstrap node status"""
        self.requests_handled += 1

        metrics = await self.collect_metrics()

        return web.json_response({
            'success': True,
            'bootstrap_node': self.node_name,
            'metrics': metrics
        })

    async def handle_health(self, request):
        """GET /health - Health check endpoint"""
        health = await self.health_check()

        status_code = 200 if health['healthy'] else 503

        return web.json_response(health, status=status_code)

    async def handle_discover_peers(self, request):
        """POST /discover-peers - Assist with peer discovery"""
        self.requests_handled += 1

        try:
            data = await request.json()
            node_info = data.get('node_info', {})

            peers = await self.peer_discovery_assist(node_info)

            return web.json_response({
                'success': True,
                'peers': peers,
                'bootstrap_node': self.node_name
            })

        except Exception as e:
            logger.error(f"Peer discovery error: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def handle_network_info(self, request):
        """GET /network-info - Overall network information"""
        self.requests_handled += 1

        network_status = self.p2p_node.get_network_status() if self.p2p_node else {}

        # Aggregate network stats
        total_peers = len(self.known_peers)
        active_peers = len([
            p for p, t in self.peer_timestamps.items()
            if time.time() - t < 300  # Active in last 5 minutes
        ])

        return web.json_response({
            'success': True,
            'network': {
                'total_known_peers': total_peers,
                'active_peers': active_peers,
                'bootstrap_nodes': 1,  # This node
                'network_status': network_status
            },
            'bootstrap_node': self.node_name
        })

    async def handle_register_peer(self, request):
        """POST /register-peer - Register peer with bootstrap"""
        self.requests_handled += 1

        try:
            data = await request.json()
            node_id = data.get('node_id')
            node_info = data.get('info', {})

            if node_id:
                self.known_peers[node_id] = node_info
                self.peer_timestamps[node_id] = time.time()

                logger.info(f"📝 Registered peer: {node_id[:16]}...")

                return web.json_response({
                    'success': True,
                    'message': 'Peer registered with bootstrap node'
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': 'Missing node_id'
                }, status=400)

        except Exception as e:
            logger.error(f"Peer registration error: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def start_server(self):
        """Start HTTP API server"""
        app = web.Application()

        # Routes
        app.router.add_get('/status', self.handle_status)
        app.router.add_get('/health', self.handle_health)
        app.router.add_post('/discover-peers', self.handle_discover_peers)
        app.router.add_get('/network-info', self.handle_network_info)
        app.router.add_post('/register-peer', self.handle_register_peer)

        # Start server
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()

        logger.info("")
        logger.info("=" * 70)
        logger.info(f" LUXBIN BOOTSTRAP NODE: {self.node_name}")
        logger.info("=" * 70)
        logger.info(f"🌐 HTTP API: http://0.0.0.0:{self.port}")
        logger.info(f"📡 Node ID: {self.p2p_node.node_id}")
        logger.info(f"🌍 Region: {self.region}")
        logger.info(f"🔗 Peers: {len(self.p2p_node.peers)}")
        logger.info("=" * 70)
        logger.info("✅ Bootstrap node ready to accept connections")
        logger.info("=" * 70)

        # Background tasks
        asyncio.create_task(self.periodic_health_check())

        # Keep running
        await asyncio.Event().wait()

    async def periodic_health_check(self):
        """Periodically check health"""
        while True:
            await asyncio.sleep(60)  # Every minute

            try:
                health = await self.health_check()
                if not health['healthy']:
                    logger.warning("⚠️  Health check failed!")
                    logger.warning(f"   Checks: {health['checks']}")
                else:
                    logger.info(f"✅ Health check passed (peers: {len(self.p2p_node.peers)})")

            except Exception as e:
                logger.error(f"Health check error: {e}")


async def main():
    """Run LUXBIN Bootstrap Node"""
    import argparse

    parser = argparse.ArgumentParser(description='LUXBIN Bootstrap Node')
    parser.add_argument('--name', default='bootstrap-1', help='Node name')
    parser.add_argument('--region', default='us-east', help='Geographic region')
    parser.add_argument('--port', type=int, default=8080, help='HTTP API port')
    args = parser.parse_args()

    # IonQ API key
    ionq_api_key = "TH9yk8wG6PeJBh7ZmOQR22VTkarZ7Pf3"

    # Create bootstrap node
    bootstrap = LUXBINBootstrapNode(
        node_name=args.name,
        ionq_api_key=ionq_api_key,
        region=args.region,
        port=args.port
    )

    # Initialize
    await bootstrap.initialize()

    # Start server
    await bootstrap.start_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Bootstrap node stopped by user")
        logger.info("=" * 70)
