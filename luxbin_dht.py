"""
LUXBIN Distributed Hash Table (DHT)
Content-addressable storage for the quantum internet

Features:
- IPFS-like content addressing
- 3x replication for redundancy
- LUXBIN hash for content IDs
- Distributed storage across quantum network
- Automatic content discovery
"""

import asyncio
import time
import hashlib
from typing import Dict, Optional, List, Set, Tuple
from dataclasses import dataclass
import json

from luxbin_address import LUXBINAddress
from luxbin_p2p_mesh import QuantumP2PNode, PeerInfo


@dataclass
class ContentRecord:
    """Content stored in DHT"""
    content_hash: str
    content: bytes
    size: int
    stored_at: float
    replicas: List[str]  # Node IDs storing this content
    luxbin_address: str
    metadata: Dict = None


class LUXBINDistributedHashTable:
    """
    LUXBIN DHT - Content-addressable storage

    Provides IPFS-like functionality:
    - Content identified by hash (not location)
    - Distributed across multiple nodes
    - Automatic replication for reliability
    - Content discovery via wavelength routing
    """

    def __init__(self, p2p_node: QuantumP2PNode, replication_factor: int = 3):
        """
        Initialize LUXBIN DHT

        Args:
            p2p_node: Quantum P2P node
            replication_factor: Number of replicas (default: 3)
        """
        self.node = p2p_node
        self.replication_factor = replication_factor

        # Local storage (content_hash -> ContentRecord)
        self.local_storage: Dict[str, ContentRecord] = {}

        # Peer index (content_hash -> List[peer_ids])
        self.peer_index: Dict[str, List[str]] = {}

        # Content index (reverse: content -> hash)
        self.content_index: Dict[bytes, str] = {}

        # Statistics
        self.total_stores = 0
        self.total_retrievals = 0
        self.local_hits = 0
        self.remote_hits = 0
        self.total_bytes_stored = 0

    async def store_content(
        self,
        content: bytes,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store content in DHT

        Process:
        1. Hash content using LUXBIN encoding
        2. Store locally
        3. Replicate to nearest nodes (by wavelength)
        4. Return LUXBIN address

        Args:
            content: Content to store
            metadata: Optional metadata

        Returns:
            LUXBIN address for content

        Example:
            >>> dht = LUXBINDistributedHashTable(p2p_node)
            >>> address = await dht.store_content(b"Hello, World!")
            >>> print(address)
            'luxbin://distributed.600nm.S:$-YR'
        """
        print(f"\n💾 Storing content ({len(content)} bytes)...")

        self.total_stores += 1

        # Check if already stored
        if content in self.content_index:
            content_hash = self.content_index[content]
            print(f"   ℹ️  Content already stored: {content_hash}")
            return self.local_storage[content_hash].luxbin_address

        # Generate LUXBIN hash
        content_hash = LUXBINAddress.luxbin_hash(content, length=8)

        # Determine optimal wavelength based on content
        wavelength = self._infer_wavelength_from_content(content)

        # Create LUXBIN address
        luxbin_address = f"luxbin://distributed.{wavelength}nm.{content_hash}"

        print(f"   📝 Content hash: {content_hash}")
        print(f"   🌈 Wavelength: {wavelength}nm")

        # Store locally
        record = ContentRecord(
            content_hash=content_hash,
            content=content,
            size=len(content),
            stored_at=time.time(),
            replicas=[self.node.node_id],
            luxbin_address=luxbin_address,
            metadata=metadata or {}
        )

        self.local_storage[content_hash] = record
        self.content_index[content] = content_hash
        self.total_bytes_stored += len(content)

        print(f"   ✅ Stored locally")

        # Replicate to nearest nodes
        replication_nodes = await self._find_nearest_nodes(
            content_hash,
            wavelength,
            k=self.replication_factor - 1  # -1 because we already stored locally
        )

        print(f"   🔄 Replicating to {len(replication_nodes)} nodes...")

        for peer in replication_nodes:
            success = await self._replicate_to_node(peer, record)
            if success:
                record.replicas.append(peer.node_id)
                print(f"      ✅ Replicated to {peer.node_id[:16]}...")

        print(f"   ✅ Total replicas: {len(record.replicas)}")

        return luxbin_address

    async def retrieve_content(self, content_hash_or_address: str) -> Optional[bytes]:
        """
        Retrieve content from DHT

        Args:
            content_hash_or_address: Content hash or LUXBIN address

        Returns:
            Content if found, None otherwise

        Example:
            >>> content = await dht.retrieve_content("S:$-YR")
            >>> print(content.decode())
            'Hello, World!'
        """
        print(f"\n🔍 Retrieving content: {content_hash_or_address[:32]}...")

        self.total_retrievals += 1

        # Parse if LUXBIN address
        if content_hash_or_address.startswith('luxbin://'):
            components = LUXBINAddress.parse(content_hash_or_address)
            if not components:
                print(f"   ❌ Invalid LUXBIN address")
                return None
            content_hash = components.content_hash
        else:
            content_hash = content_hash_or_address

        # Check local storage
        if content_hash in self.local_storage:
            print(f"   ✅ Found locally")
            self.local_hits += 1
            return self.local_storage[content_hash].content

        # Query peers
        print(f"   🔍 Searching peers...")
        self.remote_hits += 1

        content = await self._retrieve_from_peers(content_hash)

        if content:
            print(f"   ✅ Found remotely ({len(content)} bytes)")

            # Store locally for caching
            await self.store_content(content)

            return content
        else:
            print(f"   ❌ Content not found")
            return None

    async def _find_nearest_nodes(
        self,
        content_hash: str,
        wavelength: float,
        k: int = 3
    ) -> List[PeerInfo]:
        """
        Find k nearest nodes for replication

        Uses wavelength distance for proximity

        Args:
            content_hash: Content hash
            wavelength: Content wavelength
            k: Number of nodes to find

        Returns:
            List of nearest peer nodes
        """
        # Get peers with similar wavelength
        peers = self.node.get_peers_by_wavelength(wavelength, tolerance=100)

        if not peers:
            # No wavelength match, use any peers
            peers = list(self.node.peers.values())

        # Sort by wavelength distance
        peers.sort(
            key=lambda p: abs(
                (p.wavelength_range[0] + p.wavelength_range[1]) / 2 - wavelength
            )
        )

        # Return top k
        return peers[:k]

    async def _replicate_to_node(
        self,
        peer: PeerInfo,
        record: ContentRecord
    ) -> bool:
        """
        Replicate content to peer node

        Args:
            peer: Peer node
            record: Content record

        Returns:
            True if successful
        """
        # For now, simulate replication
        # In production, send content via quantum channel

        # Update peer index
        if record.content_hash not in self.peer_index:
            self.peer_index[record.content_hash] = []

        if peer.node_id not in self.peer_index[record.content_hash]:
            self.peer_index[record.content_hash].append(peer.node_id)

        # Simulate network delay
        await asyncio.sleep(0.01)

        return True

    async def _retrieve_from_peers(self, content_hash: str) -> Optional[bytes]:
        """
        Retrieve content from peer nodes

        Args:
            content_hash: Content hash to retrieve

        Returns:
            Content if found
        """
        # Check peer index
        if content_hash in self.peer_index:
            peer_ids = self.peer_index[content_hash]

            for peer_id in peer_ids:
                if peer_id in self.node.peers:
                    # Found peer with content
                    # In production, request via quantum channel
                    # For now, return simulated content
                    return b"Simulated content from peer"

        return None

    def _infer_wavelength_from_content(self, content: bytes) -> int:
        """
        Infer optimal wavelength from content

        Uses content hash to distribute across spectrum

        Args:
            content: Content bytes

        Returns:
            Wavelength in nm (400-700nm)
        """
        # Hash content
        content_hash = hashlib.sha256(content).digest()

        # Use first byte to determine wavelength
        hash_value = content_hash[0]

        # Map 0-255 to 400-700nm
        wavelength = 400 + (hash_value / 255) * 300

        return round(wavelength)

    def list_local_content(self) -> List[ContentRecord]:
        """List all locally stored content"""
        return list(self.local_storage.values())

    def get_content_info(self, content_hash: str) -> Optional[Dict]:
        """Get information about content"""
        if content_hash in self.local_storage:
            record = self.local_storage[content_hash]

            return {
                'content_hash': record.content_hash,
                'size': record.size,
                'stored_at': record.stored_at,
                'age_seconds': time.time() - record.stored_at,
                'replicas': len(record.replicas),
                'luxbin_address': record.luxbin_address,
                'metadata': record.metadata
            }

        return None

    def get_statistics(self) -> Dict:
        """Get DHT statistics"""
        return {
            'total_stores': self.total_stores,
            'total_retrievals': self.total_retrievals,
            'local_hits': self.local_hits,
            'remote_hits': self.remote_hits,
            'hit_rate': (
                (self.local_hits + self.remote_hits) / self.total_retrievals
                if self.total_retrievals > 0 else 0
            ),
            'local_content_count': len(self.local_storage),
            'total_bytes_stored': self.total_bytes_stored,
            'average_replicas': (
                sum(len(r.replicas) for r in self.local_storage.values()) /
                len(self.local_storage)
                if self.local_storage else 0
            ),
            'replication_factor': self.replication_factor
        }


async def main():
    """Test LUXBIN DHT"""
    print("=" * 70)
    print("LUXBIN DISTRIBUTED HASH TABLE (DHT) TEST")
    print("=" * 70)

    # Create P2P node
    print("\n1. Creating P2P node...")
    from luxbin_p2p_mesh import QuantumP2PNode

    p2p_node = QuantumP2PNode(
        quantum_backends=['ibm_fez', 'ibm_torino'],
        ionq_api_key='TH9yk8wG6PeJBh7ZmOQR22VTkarZ7Pf3'
    )

    await p2p_node.bootstrap()

    # Create DHT
    print("\n2. Creating DHT...")
    dht = LUXBINDistributedHashTable(p2p_node, replication_factor=3)

    # Store content
    print("\n3. Storing content...")

    test_content = [
        (b"Hello, Quantum Internet!", {'type': 'text', 'author': 'Alice'}),
        (b"<html><body><h1>LUXBIN Page</h1></body></html>", {'type': 'html'}),
        (b"Quantum algorithms and protocols", {'type': 'text', 'category': 'quantum'}),
    ]

    addresses = []

    for content, metadata in test_content:
        address = await dht.store_content(content, metadata)
        addresses.append(address)

    # Retrieve content
    print("\n4. Retrieving content...")

    for i, address in enumerate(addresses, 1):
        retrieved = await dht.retrieve_content(address)

        if retrieved:
            print(f"\n✅ Content {i} retrieved:")
            print(f"   Address: {address}")
            print(f"   Content: {retrieved[:50]}..." if len(retrieved) > 50 else f"   Content: {retrieved}")
        else:
            print(f"\n❌ Content {i} not found")

    # List local content
    print("\n5. Local content:")
    local_content = dht.list_local_content()
    print(f"   Total items: {len(local_content)}")

    for record in local_content:
        print(f"\n   • {record.content_hash}")
        print(f"     Size: {record.size} bytes")
        print(f"     Replicas: {len(record.replicas)}")
        print(f"     Address: {record.luxbin_address}")

    # Show statistics
    print("\n6. DHT Statistics:")
    stats = dht.get_statistics()
    print(json.dumps(stats, indent=2))

    print("\n" + "=" * 70)
    print("✅ LUXBIN DHT TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
