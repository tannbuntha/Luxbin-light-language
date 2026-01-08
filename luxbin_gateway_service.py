"""
LUXBIN Gateway Service

Local HTTP gateway that connects browser extension to LUXBIN network
Runs on localhost:9000

Features:
- Fetch content from LUXBIN addresses
- Resolve names via blockchain DNS
- Register names on blockchain
- Serve as local quantum node
"""

import asyncio
import json
from aiohttp import web
import time

from luxbin_p2p_mesh import QuantumP2PNode
from luxbin_photonic_router import PhotonicRouter
from luxbin_name_system import LUXBINNameSystem
from luxbin_dht import LUXBINDistributedHashTable
from luxbin_http_bridge import HTTPtoLUXBINBridge


class LUXBINGatewayService:
    """
    Local gateway service for LUXBIN browser extension
    """

    def __init__(self, ionq_api_key: str):
        self.ionq_api_key = ionq_api_key

        # Network components
        self.p2p_node = None
        self.router = None
        self.name_system = None
        self.dht = None
        self.http_bridge = None

        # Status
        self.is_ready = False
        self.startup_time = None

    async def initialize(self):
        """Initialize LUXBIN network components"""
        print("🚀 Initializing LUXBIN Gateway Service...")

        self.startup_time = time.time()

        # Create P2P node
        print("\n📡 Creating quantum P2P node...")
        self.p2p_node = QuantumP2PNode(
            quantum_backends=['ibm_fez', 'ibm_torino', 'ibm_marrakesh'],
            ionq_api_key=self.ionq_api_key
        )

        # Bootstrap (async - don't wait)
        print("   Starting bootstrap (background)...")
        asyncio.create_task(self.p2p_node.bootstrap())

        # Create router
        print("\n🔀 Creating photonic router...")
        self.router = PhotonicRouter(self.p2p_node)

        # Create name system
        print("\n📝 Creating LUXBIN Name System...")
        self.name_system = LUXBINNameSystem()
        self.name_system.blockchain.initialize()

        # Create genesis block
        self.name_system.blockchain.add_transaction({
            'type': 'GENESIS',
            'timestamp': time.time(),
            'data': 'LUXBIN Gateway Genesis'
        })
        self.name_system.blockchain.mine_block()

        # Create DHT
        print("\n💾 Creating DHT...")
        self.dht = LUXBINDistributedHashTable(self.p2p_node, replication_factor=3)

        # Create HTTP bridge
        print("\n🌐 Creating HTTP bridge...")
        self.http_bridge = HTTPtoLUXBINBridge(self.router)

        self.is_ready = True

        print("\n✅ LUXBIN Gateway ready!")
        print(f"   Node ID: {self.p2p_node.node_id[:16]}...")
        print(f"   Listening on: http://localhost:9000")

    async def handle_status(self, request):
        """GET /status - Return gateway status"""
        if not self.is_ready:
            return web.json_response({
                'connected': False,
                'message': 'Gateway initializing...'
            })

        # Get network status
        network_status = self.p2p_node.get_network_status()

        return web.json_response({
            'connected': True,
            'node_id': self.p2p_node.node_id,
            'peers': len(self.p2p_node.peers),
            'quantumBackends': self.p2p_node.quantum_backends,
            'uptime': time.time() - self.startup_time,
            'network': network_status
        })

    async def handle_fetch(self, request):
        """GET /fetch?address=... - Fetch content from LUXBIN"""
        if not self.is_ready:
            return web.json_response({'error': 'Gateway not ready'}, status=503)

        address = request.query.get('address')
        if not address:
            return web.json_response({'error': 'Missing address parameter'}, status=400)

        print(f"\n🔍 Fetching: {address}")

        try:
            # Check if it's a name (no protocol)
            if not address.startswith('luxbin://'):
                # Try to resolve name
                print(f"   Resolving name: {address}")
                record = await self.name_system.resolve_name(address)

                if record:
                    address = record.luxbin_address
                    print(f"   ✅ Resolved to: {address}")
                else:
                    return web.json_response({
                        'error': f'Name not found: {address}'
                    }, status=404)

            # Fetch content
            print(f"   Routing packet...")
            result = await self.router.route_packet(
                destination_address=address,
                data=b"GET / HTTP/1.1\r\n\r\n"
            )

            if result['success']:
                content = result.get('response_data', b'')

                return web.json_response({
                    'success': True,
                    'content': content.decode('utf-8', errors='replace'),
                    'luxbin_address': address,
                    'latency_ms': result.get('latency_ms'),
                    'metadata': {
                        'wavelength': result.get('wavelength'),
                        'hops': result.get('hops', 1)
                    }
                })
            else:
                return web.json_response({
                    'error': 'Failed to fetch content',
                    'details': result.get('error')
                }, status=500)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_register_name(self, request):
        """POST /register-name - Register name on blockchain"""
        if not self.is_ready:
            return web.json_response({'error': 'Gateway not ready'}, status=503)

        try:
            data = await request.json()
            name = data.get('name')
            address = data.get('address')
            owner = data.get('owner', 'gateway_user')

            if not name or not address:
                return web.json_response({
                    'error': 'Missing name or address'
                }, status=400)

            print(f"\n📝 Registering name: {name} → {address}")

            # Register on blockchain
            record = await self.name_system.register_name(name, address, owner)

            if record:
                return web.json_response({
                    'success': True,
                    'record': {
                        'name': record.name,
                        'luxbin_address': record.luxbin_address,
                        'owner_public_key': record.owner_public_key,
                        'block_number': record.block_number,
                        'transaction_hash': record.transaction_hash
                    }
                })
            else:
                return web.json_response({
                    'error': 'Registration failed'
                }, status=500)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_resolve_name(self, request):
        """GET /resolve?name=... - Resolve name to LUXBIN address"""
        if not self.is_ready:
            return web.json_response({'error': 'Gateway not ready'}, status=503)

        name = request.query.get('name')
        if not name:
            return web.json_response({'error': 'Missing name parameter'}, status=400)

        print(f"\n🔍 Resolving name: {name}")

        try:
            record = await self.name_system.resolve_name(name)

            if record:
                return web.json_response({
                    'success': True,
                    'name': record.name,
                    'luxbin_address': record.luxbin_address,
                    'owner_public_key': record.owner_public_key,
                    'block_number': record.block_number
                })
            else:
                return web.json_response({
                    'error': f'Name not found: {name}'
                }, status=404)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def start_server(self):
        """Start HTTP server"""
        app = web.Application()

        # Add CORS headers
        async def cors_middleware(app, handler):
            async def middleware(request):
                if request.method == 'OPTIONS':
                    return web.Response(
                        headers={
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type'
                        }
                    )

                response = await handler(request)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response

            return middleware

        app.middlewares.append(cors_middleware)

        # Routes
        app.router.add_get('/status', self.handle_status)
        app.router.add_get('/fetch', self.handle_fetch)
        app.router.add_post('/register-name', self.handle_register_name)
        app.router.add_get('/resolve', self.handle_resolve_name)

        # Start server
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, 'localhost', 9000)
        await site.start()

        print("\n" + "=" * 70)
        print(" " * 15 + "LUXBIN GATEWAY SERVICE RUNNING")
        print("=" * 70)
        print("\n🌐 Server: http://localhost:9000")
        print("📡 Node ID:", self.p2p_node.node_id[:32], "...")
        print("🔗 Quantum Backends:", len(self.p2p_node.quantum_backends))
        print("\n✅ Ready to accept requests from browser extension")
        print("\n" + "=" * 70)

        # Keep running
        await asyncio.Event().wait()


async def main():
    """Run LUXBIN Gateway Service"""

    # IonQ API key
    ionq_api_key = "TH9yk8wG6PeJBh7ZmOQR22VTkarZ7Pf3"

    # Create gateway
    gateway = LUXBINGatewayService(ionq_api_key)

    # Initialize
    await gateway.initialize()

    # Start server
    await gateway.start_server()


if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "LUXBIN GATEWAY SERVICE")
    print(" " * 15 + "Browser Extension Backend")
    print("=" * 70)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Gateway stopped by user")
        print("=" * 70)
