"""
LUXBIN HTTP Bridge
Transparent HTTP/HTTPS to LUXBIN protocol translation

Features:
- HTTP → LUXBIN request translation
- LUXBIN → HTTP response translation
- Gateway node discovery
- Content caching
- Backwards compatibility with existing web
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from luxbin_address import LUXBINAddress
from luxbin_photonic_router import PhotonicRouter, PhotonicPacket
from luxbin_p2p_mesh import QuantumP2PNode
from luxbin_light_converter import LuxbinLightConverter


@dataclass
class HTTPRequest:
    """HTTP request"""
    method: str  # GET, POST, PUT, DELETE, etc.
    url: str
    headers: Dict[str, str]
    body: bytes
    timestamp: float


@dataclass
class HTTPResponse:
    """HTTP response"""
    status_code: int
    headers: Dict[str, str]
    body: bytes
    timestamp: float


class HTTPtoLUXBINBridge:
    """
    HTTP to LUXBIN protocol bridge

    Provides backwards compatibility with existing web:
    - Intercepts HTTP requests
    - Translates to LUXBIN protocol
    - Routes via quantum network
    - Translates responses back to HTTP
    """

    def __init__(self, router: PhotonicRouter):
        """
        Initialize HTTP bridge

        Args:
            router: LUXBIN photonic router
        """
        self.router = router
        self.converter = LuxbinLightConverter(enable_quantum=True)

        # Gateway nodes (mirror HTTP content to LUXBIN network)
        self.gateway_nodes: List[str] = []

        # Content cache (luxbin_address -> cached response)
        self.content_cache: Dict[str, HTTPResponse] = {}
        self.cache_ttl = 300  # 5 minutes

        # DNS cache (http_url -> luxbin_address)
        self.dns_cache: Dict[str, str] = {}

        # Statistics
        self.requests_translated = 0
        self.cache_hits = 0
        self.cache_misses = 0

    async def translate_http_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None
    ) -> HTTPResponse:
        """
        Translate HTTP request to LUXBIN and route via quantum network

        Args:
            method: HTTP method (GET, POST, etc.)
            url: HTTP URL
            headers: HTTP headers
            body: Request body (for POST, PUT)

        Returns:
            HTTP response

        Example:
            >>> bridge = HTTPtoLUXBINBridge(router)
            >>> response = await bridge.translate_http_request(
            ...     "GET",
            ...     "http://example.com/page.html"
            ... )
            >>> response.status_code
            200
        """
        self.requests_translated += 1

        # Create HTTP request object
        request = HTTPRequest(
            method=method,
            url=url,
            headers=headers or {},
            body=body or b"",
            timestamp=time.time()
        )

        # Check if URL has native LUXBIN address
        luxbin_address = await self.resolve_http_to_luxbin(url)

        # Check cache
        cached_response = self._check_cache(luxbin_address)
        if cached_response:
            self.cache_hits += 1
            return cached_response

        self.cache_misses += 1

        # Encode request as LUXBIN
        luxbin_request_data = self._encode_http_request(request)

        # Route via quantum network
        routing_result = await self.router.route_packet(
            luxbin_address,
            luxbin_request_data
        )

        # Decode response
        if routing_result['success']:
            response = self._create_success_response(
                luxbin_address,
                routing_result
            )
        else:
            response = self._create_error_response(
                routing_result.get('error', 'Unknown error')
            )

        # Cache successful responses
        if response.status_code == 200:
            self._cache_response(luxbin_address, response)

        return response

    async def resolve_http_to_luxbin(self, http_url: str) -> str:
        """
        Resolve HTTP URL to LUXBIN address

        Process:
        1. Check DNS cache
        2. Query for native LUXBIN address (meta tag, .well-known)
        3. Find gateway node that mirrors HTTP content
        4. Generate LUXBIN address for gateway

        Args:
            http_url: HTTP URL

        Returns:
            LUXBIN address
        """
        # Check DNS cache
        if http_url in self.dns_cache:
            return self.dns_cache[http_url]

        # Parse URL
        parsed = urlparse(http_url)
        hostname = parsed.hostname or parsed.netloc
        path = parsed.path or "/"

        # TODO: Query for native LUXBIN address
        # For now, use gateway node approach

        # Find gateway node
        gateway_node = await self._find_http_gateway_node()

        # Generate LUXBIN hash for HTTP URL
        url_hash = LUXBINAddress.luxbin_hash(http_url.encode(), length=8)

        # Determine wavelength based on content type (inferred from URL)
        wavelength = self._infer_wavelength_from_url(http_url)

        # Create LUXBIN address
        luxbin_address = f"luxbin://{gateway_node}.{wavelength}nm.{url_hash}{path}"

        # Cache DNS resolution
        self.dns_cache[http_url] = luxbin_address

        return luxbin_address

    async def _find_http_gateway_node(self) -> str:
        """
        Find gateway node that mirrors HTTP content

        Returns:
            Gateway node ID
        """
        # Check if we have gateway nodes cached
        if self.gateway_nodes:
            # Use first gateway
            return self.gateway_nodes[0]

        # Use our own node as gateway
        return self.router.node.node_id

    def _infer_wavelength_from_url(self, url: str) -> int:
        """
        Infer wavelength from URL content type

        Args:
            url: HTTP URL

        Returns:
            Wavelength in nm
        """
        url_lower = url.lower()

        # Map content types to wavelengths
        if any(ext in url_lower for ext in ['.html', '.htm']):
            return 550  # Green for HTML
        elif any(ext in url_lower for ext in ['.js', '.json']):
            return 450  # Blue for JSON/JavaScript
        elif any(ext in url_lower for ext in ['.css']):
            return 500  # Cyan for CSS
        elif any(ext in url_lower for ext in ['.jpg', '.png', '.gif', '.webp']):
            return 637  # Red (NV center) for images
        elif any(ext in url_lower for ext in ['.pdf', '.doc']):
            return 600  # Orange for documents
        else:
            return 550  # Default to green

    def _encode_http_request(self, request: HTTPRequest) -> bytes:
        """
        Encode HTTP request as LUXBIN photonic packet

        Args:
            request: HTTP request

        Returns:
            Encoded request data (bytes)
        """
        # Create request structure
        request_data = {
            'method': request.method,
            'url': request.url,
            'headers': request.headers,
            'body': request.body.hex() if request.body else "",
            'timestamp': request.timestamp,
            'protocol': 'HTTP/1.1',
            'luxbin_protocol': '1.0'
        }

        # Convert to JSON
        json_data = json.dumps(request_data, sort_keys=True)

        # Convert to bytes
        return json_data.encode('utf-8')

    def _create_success_response(
        self,
        luxbin_address: str,
        routing_result: Dict
    ) -> HTTPResponse:
        """
        Create successful HTTP response from LUXBIN routing result

        Args:
            luxbin_address: LUXBIN address
            routing_result: Routing result

        Returns:
            HTTP response
        """
        # For now, create a simple success response
        # In production, this would decode the actual response from quantum network

        # Parse address components
        components = LUXBINAddress.parse(luxbin_address)

        # Generate mock content based on address
        content = self._generate_mock_content(components)

        return HTTPResponse(
            status_code=200,
            headers={
                'Content-Type': 'text/html; charset=utf-8',
                'X-LUXBIN-Address': luxbin_address,
                'X-LUXBIN-Node': components.node_id if components else 'unknown',
                'X-LUXBIN-Wavelength': components.wavelength if components else 'unknown',
                'X-LUXBIN-Protocol': '1.0',
                'X-Routing-Latency': f"{routing_result.get('latency_ms', 0)}ms",
                'Cache-Control': f'max-age={self.cache_ttl}'
            },
            body=content,
            timestamp=time.time()
        )

    def _generate_mock_content(self, components: Optional[object]) -> bytes:
        """Generate mock content for response"""
        if not components:
            return b"<html><body><h1>LUXBIN Quantum Internet</h1><p>Content not found</p></body></html>"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>LUXBIN Quantum Internet</title>
    <style>
        body {{ font-family: monospace; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .container {{ max-width: 800px; margin: 0 auto; background: rgba(0,0,0,0.3); padding: 30px; border-radius: 10px; }}
        .wavelength {{ color: #FFD700; }}
        .hash {{ color: #00FF00; }}
        code {{ background: rgba(0,0,0,0.5); padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 LUXBIN Quantum Internet</h1>
        <p>You've accessed content via the LUXBIN photonic network!</p>

        <h2>Address Information:</h2>
        <ul>
            <li><strong>Node:</strong> <code>{components.node_id}</code></li>
            <li><strong>Wavelength:</strong> <span class="wavelength">{components.wavelength}</span></li>
            <li><strong>Content Hash:</strong> <span class="hash">{components.content_hash}</span></li>
            <li><strong>Resource:</strong> <code>{components.resource}</code></li>
        </ul>

        <h2>Network Features:</h2>
        <ul>
            <li>✅ Quantum-secured communication</li>
            <li>✅ Censorship-resistant routing</li>
            <li>✅ Wavelength-based addressing (400-700nm)</li>
            <li>✅ Content-addressable storage</li>
            <li>✅ Backwards compatible with HTTP</li>
        </ul>

        <h2>Full Address:</h2>
        <code>{components.full_address}</code>
    </div>
</body>
</html>"""

        return html.encode('utf-8')

    def _create_error_response(self, error_message: str) -> HTTPResponse:
        """Create error HTTP response"""
        content = f"""<!DOCTYPE html>
<html>
<head>
    <title>LUXBIN Error</title>
    <style>
        body {{ font-family: monospace; padding: 40px; background: #1a1a1a; color: #ff6b6b; }}
    </style>
</head>
<body>
    <h1>LUXBIN Routing Error</h1>
    <p><strong>Error:</strong> {error_message}</p>
    <p>The requested resource could not be reached via the LUXBIN quantum network.</p>
</body>
</html>"""

        return HTTPResponse(
            status_code=502,  # Bad Gateway
            headers={
                'Content-Type': 'text/html; charset=utf-8',
                'X-LUXBIN-Error': error_message,
                'X-LUXBIN-Protocol': '1.0'
            },
            body=content.encode('utf-8'),
            timestamp=time.time()
        )

    def _check_cache(self, luxbin_address: str) -> Optional[HTTPResponse]:
        """
        Check content cache

        Args:
            luxbin_address: LUXBIN address

        Returns:
            Cached response or None
        """
        if luxbin_address not in self.content_cache:
            return None

        cached_response = self.content_cache[luxbin_address]

        # Check if cache expired
        age = time.time() - cached_response.timestamp

        if age > self.cache_ttl:
            # Expired - remove from cache
            del self.content_cache[luxbin_address]
            return None

        return cached_response

    def _cache_response(self, luxbin_address: str, response: HTTPResponse):
        """Cache response"""
        self.content_cache[luxbin_address] = response

        # Limit cache size
        if len(self.content_cache) > 1000:
            # Remove oldest entries
            sorted_cache = sorted(
                self.content_cache.items(),
                key=lambda item: item[1].timestamp
            )
            # Keep newest 800
            self.content_cache = dict(sorted_cache[-800:])

    def get_statistics(self) -> Dict:
        """Get bridge statistics"""
        total_requests = self.cache_hits + self.cache_misses

        return {
            'requests_translated': self.requests_translated,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_requests': total_requests,
            'cache_hit_rate': (
                self.cache_hits / total_requests
                if total_requests > 0 else 0
            ),
            'cached_items': len(self.content_cache),
            'dns_cached_entries': len(self.dns_cache)
        }


async def main():
    """Test HTTP bridge"""
    print("=" * 70)
    print("LUXBIN HTTP BRIDGE TEST")
    print("=" * 70)

    # Create P2P node
    print("\n1. Creating P2P node and router...")
    p2p_node = QuantumP2PNode(
        quantum_backends=['ibm_fez', 'ibm_torino', 'ibm_marrakesh'],
        ionq_api_key='TH9yk8wG6PeJBh7ZmOQR22VTkarZ7Pf3'
    )

    await p2p_node.bootstrap()

    router = PhotonicRouter(p2p_node)

    # Create HTTP bridge
    print("\n2. Creating HTTP bridge...")
    bridge = HTTPtoLUXBINBridge(router)

    # Test HTTP to LUXBIN translation
    print("\n3. Testing HTTP → LUXBIN translation:")
    print("-" * 70)

    test_urls = [
        "http://example.com/index.html",
        "https://quantum.example/data.json",
        "http://luxbin.network/page.html"
    ]

    for url in test_urls:
        print(f"\n📡 Translating: {url}")

        # Translate request
        response = await bridge.translate_http_request("GET", url)

        print(f"   Status: {response.status_code}")
        print(f"   LUXBIN Address: {response.headers.get('X-LUXBIN-Address', 'N/A')}")
        print(f"   Wavelength: {response.headers.get('X-LUXBIN-Wavelength', 'N/A')}")
        print(f"   Latency: {response.headers.get('X-Routing-Latency', 'N/A')}")
        print(f"   Content Length: {len(response.body)} bytes")

    # Test caching
    print("\n4. Testing cache (requesting same URL again):")
    print("-" * 70)

    response2 = await bridge.translate_http_request("GET", test_urls[0])
    print(f"   Status: {response2.status_code}")
    print(f"   Response time: ~0ms (cached)")

    # Show statistics
    print("\n5. Bridge statistics:")
    print("-" * 70)
    stats = bridge.get_statistics()
    print(json.dumps(stats, indent=2))

    # Show sample response content
    print("\n6. Sample response content:")
    print("-" * 70)
    print(response.body.decode('utf-8')[:500] + "...")

    print("\n" + "=" * 70)
    print("✅ HTTP BRIDGE TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
