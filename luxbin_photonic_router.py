"""
LUXBIN Photonic Router
Wavelength-based routing with quantum correlation path finding

Features:
- Wavelength-based routing (nodes specialize in 400-700nm ranges)
- Quantum correlation path finding
- Multipath routing for censorship resistance
- Content-addressable routing (hash-based)
- Automatic failover and redundancy
"""

import asyncio
import time
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json

from luxbin_address import LUXBINAddress, LUXBINAddressComponents
from luxbin_p2p_mesh import QuantumP2PNode, PeerInfo
from luxbin_light_converter import LuxbinLightConverter


@dataclass
class PhotonicPacket:
    """
    Photonic packet for LUXBIN network

    Encoded as LUXBIN wavelengths for quantum-native transmission
    """
    source_node: str
    destination_address: str
    data: bytes
    wavelength: float  # Primary wavelength for routing
    timestamp: float
    ttl: int  # Time to live (hops)
    packet_id: str
    luxbin_encoded: Optional[Dict] = None  # LUXBIN light show

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'source_node': self.source_node,
            'destination_address': self.destination_address,
            'data': self.data.hex(),
            'wavelength': self.wavelength,
            'timestamp': self.timestamp,
            'ttl': self.ttl,
            'packet_id': self.packet_id
        }


@dataclass
class RoutingPath:
    """Routing path through quantum network"""
    nodes: List[PeerInfo]
    total_correlation: float
    estimated_latency: float
    wavelength_compatibility: float
    path_id: str


class PhotonicRouter:
    """
    LUXBIN photonic router

    Routes packets based on:
    1. Wavelength compatibility (nodes specialize in wavelength ranges)
    2. Quantum correlation strength (entanglement-based trust)
    3. Network topology (shortest path)
    """

    def __init__(self, p2p_node: QuantumP2PNode):
        """
        Initialize photonic router

        Args:
            p2p_node: Quantum P2P mesh node
        """
        self.node = p2p_node
        self.converter = LuxbinLightConverter(enable_quantum=True)

        # Routing table: wavelength range -> list of peer nodes
        self.routing_table: Dict[Tuple[int, int], List[PeerInfo]] = {}

        # Packet cache (for deduplication)
        self.packet_cache: Dict[str, float] = {}  # packet_id -> timestamp

        # Statistics
        self.packets_routed = 0
        self.packets_failed = 0
        self.avg_latency = 0.0

        # Build initial routing table
        self._build_routing_table()

    def _build_routing_table(self):
        """
        Build routing table from peer connections

        Groups peers by wavelength specialization
        """
        self.routing_table.clear()

        for peer in self.node.peers.values():
            # Round wavelength range to nearest 100nm
            min_wl = int(peer.wavelength_range[0] / 100) * 100
            max_wl = int(peer.wavelength_range[1] / 100) * 100

            key = (min_wl, max_wl)

            if key not in self.routing_table:
                self.routing_table[key] = []

            self.routing_table[key].append(peer)

        # Sort peers in each bucket by correlation
        for peers in self.routing_table.values():
            peers.sort(key=lambda p: p.entanglement_correlation, reverse=True)

    async def route_packet(
        self,
        destination_address: str,
        data: bytes,
        ttl: int = 10
    ) -> Dict:
        """
        Route photonic packet to destination

        Args:
            destination_address: LUXBIN address
            data: Packet data (bytes)
            ttl: Time to live (max hops)

        Returns:
            Routing result dict

        Example:
            >>> router = PhotonicRouter(p2p_node)
            >>> result = await router.route_packet(
            ...     "luxbin://mysite.550nm.ABC123/page.html",
            ...     b"<html>...</html>"
            ... )
        """
        start_time = time.time()

        # Parse destination address
        components = LUXBINAddress.parse(destination_address)

        if not components:
            self.packets_failed += 1
            return {
                'success': False,
                'error': 'Invalid LUXBIN address',
                'address': destination_address
            }

        # Create photonic packet
        packet = self._create_photonic_packet(
            destination_address=destination_address,
            data=data,
            ttl=ttl,
            components=components
        )

        # Check packet cache (deduplication)
        if self._is_duplicate_packet(packet):
            return {
                'success': True,
                'cached': True,
                'packet_id': packet.packet_id,
                'latency_ms': 0
            }

        # Find routing path
        paths = await self._find_routing_paths(packet, components)

        if not paths:
            self.packets_failed += 1
            return {
                'success': False,
                'error': 'No route to destination',
                'address': destination_address
            }

        # Try multipath routing (parallel transmission)
        result = await self._forward_multipath(packet, paths)

        # Update statistics
        latency = (time.time() - start_time) * 1000  # ms
        self.packets_routed += 1
        self.avg_latency = (
            (self.avg_latency * (self.packets_routed - 1) + latency) /
            self.packets_routed
        )

        result['latency_ms'] = latency

        return result

    def _create_photonic_packet(
        self,
        destination_address: str,
        data: bytes,
        ttl: int,
        components: LUXBINAddressComponents
    ) -> PhotonicPacket:
        """Create photonic packet with LUXBIN encoding"""

        # Extract wavelength for routing
        wavelength = LUXBINAddress.extract_wavelength(destination_address)

        if wavelength is None:
            wavelength = 550  # Default to green

        # Generate packet ID
        packet_id = hashlib.sha256(
            f"{self.node.node_id}{destination_address}{time.time()}".encode()
        ).hexdigest()[:16]

        # Create packet
        packet = PhotonicPacket(
            source_node=self.node.node_id,
            destination_address=destination_address,
            data=data,
            wavelength=wavelength,
            timestamp=time.time(),
            ttl=ttl,
            packet_id=packet_id
        )

        # Encode packet data as LUXBIN photonic signal
        packet.luxbin_encoded = self.converter.create_light_show(data)

        return packet

    def _is_duplicate_packet(self, packet: PhotonicPacket) -> bool:
        """Check if packet is duplicate (already routed)"""

        # Clean old cache entries (>60 seconds)
        current_time = time.time()
        self.packet_cache = {
            pid: ts for pid, ts in self.packet_cache.items()
            if current_time - ts < 60
        }

        # Check if packet ID exists
        if packet.packet_id in self.packet_cache:
            return True

        # Add to cache
        self.packet_cache[packet.packet_id] = packet.timestamp

        return False

    async def _find_routing_paths(
        self,
        packet: PhotonicPacket,
        components: LUXBINAddressComponents
    ) -> List[RoutingPath]:
        """
        Find routing paths to destination

        Uses:
        1. Wavelength compatibility
        2. Quantum correlation strength
        3. Node reputation

        Returns:
            List of routing paths (sorted by quality)
        """
        paths = []

        # Get target wavelength
        target_wavelength = packet.wavelength

        # Find peers with compatible wavelength ranges
        compatible_peers = self.node.get_peers_by_wavelength(
            target_wavelength,
            tolerance=100  # ±100nm tolerance
        )

        if not compatible_peers:
            # No direct compatible peers, find any peers as relay
            compatible_peers = list(self.node.peers.values())

        # Create routing paths
        for peer in compatible_peers[:5]:  # Top 5 candidates
            # Single-hop path for now
            # TODO: Implement multi-hop pathfinding

            path = RoutingPath(
                nodes=[peer],
                total_correlation=peer.entanglement_correlation,
                estimated_latency=self._estimate_latency(peer),
                wavelength_compatibility=self._calculate_wavelength_compatibility(
                    peer.wavelength_range,
                    target_wavelength
                ),
                path_id=hashlib.sha256(
                    f"{peer.node_id}{target_wavelength}".encode()
                ).hexdigest()[:8]
            )

            paths.append(path)

        # Sort paths by quality (correlation * wavelength_compatibility)
        paths.sort(
            key=lambda p: p.total_correlation * p.wavelength_compatibility,
            reverse=True
        )

        return paths

    def _calculate_wavelength_compatibility(
        self,
        peer_range: Tuple[float, float],
        target_wavelength: float
    ) -> float:
        """
        Calculate wavelength compatibility score (0.0-1.0)

        Args:
            peer_range: Peer's wavelength specialization (min, max)
            target_wavelength: Target wavelength

        Returns:
            Compatibility score (1.0 = perfect match, 0.0 = incompatible)
        """
        min_wl, max_wl = peer_range

        if min_wl <= target_wavelength <= max_wl:
            # Within range: perfect compatibility
            return 1.0

        # Outside range: calculate distance penalty
        if target_wavelength < min_wl:
            distance = min_wl - target_wavelength
        else:
            distance = target_wavelength - max_wl

        # Exponential decay: compatibility drops off with distance
        # 50nm distance = 0.5 compatibility, 100nm = 0.25, 200nm = 0.0625
        compatibility = 2 ** (-distance / 50)

        return max(0.0, min(1.0, compatibility))

    def _estimate_latency(self, peer: PeerInfo) -> float:
        """
        Estimate routing latency to peer

        Args:
            peer: Peer node

        Returns:
            Estimated latency in milliseconds
        """
        # Base latency
        base_latency = 10  # ms

        # Add latency based on correlation (lower correlation = higher latency)
        correlation_latency = (1.0 - peer.entanglement_correlation) * 50

        # Add latency based on time since last seen
        staleness = time.time() - peer.last_seen
        staleness_latency = min(staleness * 0.1, 100)  # Cap at 100ms

        return base_latency + correlation_latency + staleness_latency

    async def _forward_multipath(
        self,
        packet: PhotonicPacket,
        paths: List[RoutingPath]
    ) -> Dict:
        """
        Forward packet via multiple paths (parallel transmission)

        Provides censorship resistance and reliability

        Args:
            packet: Photonic packet
            paths: List of routing paths

        Returns:
            Routing result
        """
        if not paths:
            return {
                'success': False,
                'error': 'No paths available'
            }

        # Use top 3 paths for multipath
        selected_paths = paths[:3]

        # Forward via all paths in parallel
        tasks = [
            self._forward_via_path(packet, path)
            for path in selected_paths
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check if any path succeeded
        successful = [r for r in results if isinstance(r, dict) and r.get('success')]

        if successful:
            return {
                'success': True,
                'packet_id': packet.packet_id,
                'paths_tried': len(selected_paths),
                'paths_succeeded': len(successful),
                'primary_path': selected_paths[0].path_id,
                'multipath': len(selected_paths) > 1
            }
        else:
            return {
                'success': False,
                'error': 'All paths failed',
                'paths_tried': len(selected_paths),
                'errors': [str(r) if isinstance(r, Exception) else r.get('error') for r in results]
            }

    async def _forward_via_path(
        self,
        packet: PhotonicPacket,
        path: RoutingPath
    ) -> Dict:
        """
        Forward packet via specific path

        Args:
            packet: Photonic packet
            path: Routing path

        Returns:
            Forwarding result
        """
        # Get next hop
        next_hop = path.nodes[0]

        # Check if we have Bell pair with next hop
        if next_hop.node_id not in self.node.bell_pairs:
            return {
                'success': False,
                'error': f'No Bell pair with {next_hop.node_id}',
                'path_id': path.path_id
            }

        # Simulate forwarding (in production, this would use quantum channel)
        await asyncio.sleep(path.estimated_latency / 1000)  # Convert ms to seconds

        return {
            'success': True,
            'path_id': path.path_id,
            'next_hop': next_hop.node_id,
            'correlation': next_hop.entanglement_correlation,
            'simulated': True  # Mark as simulated for now
        }

    def get_routing_table_summary(self) -> Dict:
        """Get routing table summary"""
        return {
            'wavelength_regions': len(self.routing_table),
            'total_peers': sum(len(peers) for peers in self.routing_table.values()),
            'regions': [
                {
                    'range': f"{min_wl}-{max_wl}nm",
                    'peers': len(peers),
                    'top_peer_correlation': peers[0].entanglement_correlation if peers else 0
                }
                for (min_wl, max_wl), peers in sorted(self.routing_table.items())
            ]
        }

    def get_routing_statistics(self) -> Dict:
        """Get routing statistics"""
        total_packets = self.packets_routed + self.packets_failed

        return {
            'packets_routed': self.packets_routed,
            'packets_failed': self.packets_failed,
            'total_packets': total_packets,
            'success_rate': (
                self.packets_routed / total_packets
                if total_packets > 0 else 0
            ),
            'avg_latency_ms': self.avg_latency,
            'cached_packets': len(self.packet_cache)
        }


async def main():
    """Test photonic router"""
    print("=" * 70)
    print("LUXBIN PHOTONIC ROUTER TEST")
    print("=" * 70)

    # Create P2P node
    print("\n1. Creating P2P node...")
    p2p_node = QuantumP2PNode(
        quantum_backends=['ibm_fez', 'ibm_torino', 'ibm_marrakesh'],
        ionq_api_key='TH9yk8wG6PeJBh7ZmOQR22VTkarZ7Pf3'
    )

    # Bootstrap node
    print("\n2. Bootstrapping node into network...")
    await p2p_node.bootstrap()

    # Create router
    print("\n3. Creating photonic router...")
    router = PhotonicRouter(p2p_node)

    # Show routing table
    print("\n4. Routing table summary:")
    print("-" * 70)
    summary = router.get_routing_table_summary()
    print(json.dumps(summary, indent=2))

    # Test routing
    print("\n5. Testing packet routing:")
    print("-" * 70)

    test_destinations = [
        ("luxbin://ibm_fez.637nm.ABC123/page.html", b"<html>Diamond NV content</html>"),
        ("luxbin://mysite.450nm.XYZ789/data.json", b'{"quantum": "data"}'),
        ("luxbin://network.550nm.DEF456/index.html", b"<html>Green region content</html>"),
    ]

    for address, data in test_destinations:
        print(f"\nRouting to: {address}")
        result = await router.route_packet(address, data)

        print(f"  Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        if result['success']:
            print(f"  Latency: {result['latency_ms']:.2f}ms")
            if result.get('multipath'):
                print(f"  Paths: {result['paths_tried']} tried, {result['paths_succeeded']} succeeded")
        else:
            print(f"  Error: {result.get('error')}")

    # Show routing statistics
    print("\n6. Routing statistics:")
    print("-" * 70)
    stats = router.get_routing_statistics()
    print(json.dumps(stats, indent=2))

    print("\n" + "=" * 70)
    print("✅ PHOTONIC ROUTER TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
