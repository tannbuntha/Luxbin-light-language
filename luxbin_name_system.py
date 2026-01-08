"""
LUXBIN Name System (LNS)
Decentralized blockchain-based DNS for the quantum internet

Features:
- On-chain name registration (no central DNS)
- Quantum blockchain immutability
- Censorship-resistant naming
- Byzantine fault tolerance
- Human-readable names → LUXBIN addresses
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass

from quantum_blockchain_service import QuantumBlockchainService
from luxbin_address import LUXBINAddress


@dataclass
class NameRecord:
    """DNS name record stored on blockchain"""
    name: str
    luxbin_address: str
    owner_public_key: str
    registered_at: float
    expires_at: float
    block_number: int
    transaction_hash: str
    metadata: Dict = None


class LUXBINNameSystem:
    """
    LUXBIN Name System - Decentralized DNS on quantum blockchain

    Provides censorship-resistant naming:
    - Names registered on quantum blockchain
    - No central authority can revoke names
    - Byzantine fault tolerant (2/3 consensus)
    - Immutable ownership records
    """

    def __init__(
        self,
        blockchain_service: Optional[QuantumBlockchainService] = None
    ):
        """
        Initialize LUXBIN Name System

        Args:
            blockchain_service: Quantum blockchain service instance
        """
        self.blockchain = blockchain_service or QuantumBlockchainService()

        # Name cache (name -> NameRecord)
        self.name_cache: Dict[str, NameRecord] = {}

        # Reverse cache (luxbin_address -> List[names])
        self.reverse_cache: Dict[str, List[str]] = {}

        # Owner cache (public_key -> List[names])
        self.owner_cache: Dict[str, List[str]] = {}

        # Statistics
        self.total_registrations = 0
        self.total_lookups = 0
        self.cache_hits = 0
        self.cache_misses = 0

        # Configuration
        self.registration_fee = 0.0  # Free for now
        self.name_ttl = 31536000  # 1 year default

    async def register_name(
        self,
        name: str,
        luxbin_address: str,
        owner_public_key: str,
        ttl: Optional[int] = None
    ) -> Optional[NameRecord]:
        """
        Register name on quantum blockchain

        Args:
            name: Human-readable name (e.g., "mywebsite")
            luxbin_address: LUXBIN address to map to
            owner_public_key: Owner's public key
            ttl: Time to live in seconds (default: 1 year)

        Returns:
            NameRecord if successful, None otherwise

        Example:
            >>> lns = LUXBINNameSystem()
            >>> record = await lns.register_name(
            ...     "mywebsite",
            ...     "luxbin://node1.550nm.ABC123/index.html",
            ...     "pubkey_xyz"
            ... )
        """
        print(f"\n📝 Registering name: {name}")

        # Validate name
        if not self._validate_name(name):
            print(f"   ❌ Invalid name: {name}")
            return None

        # Validate LUXBIN address
        is_valid, error = LUXBINAddress.validate(luxbin_address)
        if not is_valid:
            print(f"   ❌ Invalid LUXBIN address: {error}")
            return None

        # Check if name already exists
        existing = await self.resolve_name(name)
        if existing and not self._is_expired(existing):
            print(f"   ❌ Name already registered")
            return None

        # Create registration transaction
        ttl = ttl or self.name_ttl
        expires_at = time.time() + ttl

        transaction = {
            'type': 'NAME_REGISTER',
            'name': name,
            'luxbin_address': luxbin_address,
            'owner_public_key': owner_public_key,
            'registered_at': time.time(),
            'expires_at': expires_at,
            'ttl': ttl,
            'fee': self.registration_fee
        }

        print(f"   📤 Submitting to quantum blockchain...")

        # Submit to quantum blockchain
        try:
            # Add transaction to blockchain
            self.blockchain.add_transaction(transaction)

            # Mine block
            block = self.blockchain.mine_block()

            if block:
                # Create name record
                record = NameRecord(
                    name=name,
                    luxbin_address=luxbin_address,
                    owner_public_key=owner_public_key,
                    registered_at=transaction['registered_at'],
                    expires_at=expires_at,
                    block_number=block['block_number'],
                    transaction_hash=block['hash'][:16],
                    metadata={'ttl': ttl}
                )

                # Update caches
                self.name_cache[name] = record

                if luxbin_address not in self.reverse_cache:
                    self.reverse_cache[luxbin_address] = []
                self.reverse_cache[luxbin_address].append(name)

                if owner_public_key not in self.owner_cache:
                    self.owner_cache[owner_public_key] = []
                self.owner_cache[owner_public_key].append(name)

                self.total_registrations += 1

                print(f"   ✅ Name registered successfully!")
                print(f"      Block: #{block['block_number']}")
                print(f"      TX Hash: {block['hash'][:32]}...")
                print(f"      Expires: {time.strftime('%Y-%m-%d', time.localtime(expires_at))}")

                return record
            else:
                print(f"   ❌ Failed to mine block")
                return None

        except Exception as e:
            print(f"   ❌ Registration error: {e}")
            return None

    async def resolve_name(self, name: str) -> Optional[NameRecord]:
        """
        Resolve name to LUXBIN address

        Args:
            name: Name to resolve

        Returns:
            NameRecord if found, None otherwise

        Example:
            >>> record = await lns.resolve_name("mywebsite")
            >>> print(record.luxbin_address)
            'luxbin://node1.550nm.ABC123/index.html'
        """
        self.total_lookups += 1

        # Check cache
        if name in self.name_cache:
            record = self.name_cache[name]

            # Check if expired
            if self._is_expired(record):
                del self.name_cache[name]
                self.cache_misses += 1
            else:
                self.cache_hits += 1
                return record

        # Query blockchain
        self.cache_misses += 1

        try:
            # Search blockchain for name registration
            for block in reversed(self.blockchain.blockchain):
                for tx in block.get('transactions', []):
                    if (tx.get('type') == 'NAME_REGISTER' and
                        tx.get('name') == name):

                        # Found registration
                        record = NameRecord(
                            name=name,
                            luxbin_address=tx['luxbin_address'],
                            owner_public_key=tx['owner_public_key'],
                            registered_at=tx['registered_at'],
                            expires_at=tx['expires_at'],
                            block_number=block['block_number'],
                            transaction_hash=block['hash'][:16],
                            metadata={'ttl': tx.get('ttl', self.name_ttl)}
                        )

                        # Check if expired
                        if self._is_expired(record):
                            return None

                        # Cache and return
                        self.name_cache[name] = record
                        return record

            return None

        except Exception as e:
            print(f"❌ Lookup error: {e}")
            return None

    async def update_name(
        self,
        name: str,
        new_address: str,
        owner_public_key: str
    ) -> bool:
        """
        Update name registration (must be owner)

        Args:
            name: Name to update
            new_address: New LUXBIN address
            owner_public_key: Owner's public key (for verification)

        Returns:
            True if updated successfully
        """
        # Verify ownership
        existing = await self.resolve_name(name)

        if not existing:
            print(f"❌ Name not found: {name}")
            return False

        if existing.owner_public_key != owner_public_key:
            print(f"❌ Not authorized to update {name}")
            return False

        # Create update transaction
        transaction = {
            'type': 'NAME_UPDATE',
            'name': name,
            'old_address': existing.luxbin_address,
            'new_address': new_address,
            'owner_public_key': owner_public_key,
            'updated_at': time.time()
        }

        # Submit to blockchain
        self.blockchain.add_transaction(transaction)
        block = self.blockchain.mine_block()

        if block:
            # Update cache
            existing.luxbin_address = new_address

            print(f"✅ Name updated: {name} → {new_address}")
            return True

        return False

    async def transfer_name(
        self,
        name: str,
        new_owner_public_key: str,
        current_owner_public_key: str
    ) -> bool:
        """
        Transfer name ownership

        Args:
            name: Name to transfer
            new_owner_public_key: New owner's public key
            current_owner_public_key: Current owner's public key

        Returns:
            True if transferred successfully
        """
        # Verify current ownership
        existing = await self.resolve_name(name)

        if not existing:
            return False

        if existing.owner_public_key != current_owner_public_key:
            return False

        # Create transfer transaction
        transaction = {
            'type': 'NAME_TRANSFER',
            'name': name,
            'old_owner': current_owner_public_key,
            'new_owner': new_owner_public_key,
            'transferred_at': time.time()
        }

        # Submit to blockchain
        self.blockchain.add_transaction(transaction)
        block = self.blockchain.mine_block()

        if block:
            # Update cache
            existing.owner_public_key = new_owner_public_key

            print(f"✅ Name transferred: {name}")
            return True

        return False

    def _validate_name(self, name: str) -> bool:
        """
        Validate name format

        Rules:
        - 3-64 characters
        - Lowercase alphanumeric + hyphens
        - Cannot start/end with hyphen
        """
        if len(name) < 3 or len(name) > 64:
            return False

        if not name.replace('-', '').isalnum():
            return False

        if name.startswith('-') or name.endswith('-'):
            return False

        return True

    def _is_expired(self, record: NameRecord) -> bool:
        """Check if name record has expired"""
        return time.time() > record.expires_at

    def get_names_by_owner(self, owner_public_key: str) -> List[NameRecord]:
        """Get all names owned by public key"""
        if owner_public_key in self.owner_cache:
            names = self.owner_cache[owner_public_key]
            return [
                self.name_cache[name]
                for name in names
                if name in self.name_cache and not self._is_expired(self.name_cache[name])
            ]

        return []

    def get_statistics(self) -> Dict:
        """Get LNS statistics"""
        return {
            'total_registrations': self.total_registrations,
            'total_lookups': self.total_lookups,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': (
                self.cache_hits / self.total_lookups
                if self.total_lookups > 0 else 0
            ),
            'cached_names': len(self.name_cache),
            'unique_owners': len(self.owner_cache)
        }


async def main():
    """Test LUXBIN Name System"""
    print("=" * 70)
    print("LUXBIN NAME SYSTEM (LNS) TEST")
    print("=" * 70)

    # Create LNS instance
    print("\n1. Initializing LUXBIN Name System...")
    lns = LUXBINNameSystem()

    # Initialize blockchain
    lns.blockchain.initialize()
    print("   ✅ Blockchain initialized")

    # Register names
    print("\n2. Registering names...")

    names_to_register = [
        ("mywebsite", "luxbin://node1.550nm.ABC123/index.html", "owner1_pubkey"),
        ("quantum-blog", "luxbin://node2.637nm.XYZ789/blog.html", "owner2_pubkey"),
        ("luxbin-docs", "luxbin://distributed.450nm.DEF456/docs.html", "owner1_pubkey"),
    ]

    registered_records = []

    for name, address, owner in names_to_register:
        record = await lns.register_name(name, address, owner)
        if record:
            registered_records.append(record)

    # Resolve names
    print("\n3. Resolving names...")

    for name, _, _ in names_to_register:
        record = await lns.resolve_name(name)

        if record:
            print(f"\n✅ {name}")
            print(f"   Address: {record.luxbin_address}")
            print(f"   Owner: {record.owner_public_key}")
            print(f"   Block: #{record.block_number}")
        else:
            print(f"\n❌ {name} not found")

    # Update name
    print("\n4. Updating name...")
    success = await lns.update_name(
        "mywebsite",
        "luxbin://node1.550nm.UPDATED/new-index.html",
        "owner1_pubkey"
    )

    if success:
        updated_record = await lns.resolve_name("mywebsite")
        print(f"   New address: {updated_record.luxbin_address}")

    # Get names by owner
    print("\n5. Listing names by owner...")
    owner_names = lns.get_names_by_owner("owner1_pubkey")
    print(f"   Owner 'owner1_pubkey' has {len(owner_names)} names:")
    for record in owner_names:
        print(f"   - {record.name} → {record.luxbin_address}")

    # Show statistics
    print("\n6. LNS Statistics:")
    stats = lns.get_statistics()
    print(json.dumps(stats, indent=2))

    print("\n" + "=" * 70)
    print("✅ LUXBIN NAME SYSTEM TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
