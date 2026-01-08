"""
LUXBIN Desktop Node Backend

Full quantum node for desktop application
Provides same functionality as gateway service but optimized for desktop use
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.append('../')

from luxbin_gateway_service import LUXBINGatewayService
import asyncio


async def main():
    parser = argparse.ArgumentParser(description='LUXBIN Desktop Node')
    parser.add_argument('--port', type=int, default=9001, help='HTTP server port')
    args = parser.parse_args()

    print("=" * 70)
    print(" " * 18 + "LUXBIN DESKTOP NODE")
    print(" " * 15 + "Quantum Internet Backend")
    print("=" * 70)

    # IonQ API key
    ionq_api_key = "TH9yk8wG6PeJBh7ZmOQR22VTkarZ7Pf3"

    # Create gateway service (same as browser extension backend)
    gateway = LUXBINGatewayService(ionq_api_key)

    # Initialize
    await gateway.initialize()

    # Modify port
    import aiohttp.web as web

    app = web.Application()

    # Add CORS
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
    app.router.add_get('/status', gateway.handle_status)
    app.router.add_get('/fetch', gateway.handle_fetch)
    app.router.add_post('/register-name', gateway.handle_register_name)
    app.router.add_get('/resolve', gateway.handle_resolve_name)

    # Add publish endpoint
    async def handle_publish(request):
        """POST /publish - Publish content to LUXBIN"""
        if not gateway.is_ready:
            return web.json_response({'error': 'Gateway not ready'}, status=503)

        try:
            data = await request.json()
            content = data.get('content', '').encode()
            metadata = data.get('metadata', {})

            # Store in DHT
            address = await gateway.dht.store_content(content, metadata)

            return web.json_response({
                'success': True,
                'luxbin_address': address
            })

        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    app.router.add_post('/publish', handle_publish)

    # Start server
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, 'localhost', args.port)
    await site.start()

    print(f"\n🌐 Desktop node server: http://localhost:{args.port}")
    print(f"📡 Node ID: {gateway.p2p_node.node_id[:32]}...")
    print("\n✅ LUXBIN Node ready")
    print("=" * 70)

    # Keep running
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Desktop node stopped")
        print("=" * 70)
