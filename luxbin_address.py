"""
LUXBIN Address System
Quantum internet addressing scheme

Address Format:
    luxbin://[node_id].[wavelength].[hash]/[resource]

Examples:
    luxbin://ibm_fez.637nm.A3F9D2/webpage
    luxbin://distributed.400-700nm.B8C4E1/file.txt
    luxbin://mywebsite.550nm.XYZ123/index.html

Features:
- Content-addressable (hash-based)
- Wavelength-based routing hints
- Human-readable names (via blockchain DNS)
- Quantum-native addressing
"""

import re
import hashlib
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from luxbin_light_converter import LuxbinLightConverter


@dataclass
class LUXBINAddressComponents:
    """Parsed LUXBIN address components"""
    node_id: str
    wavelength: str  # e.g., "637nm" or "400-700nm"
    content_hash: str
    resource: str
    full_address: str

    def __str__(self):
        return self.full_address

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'node_id': self.node_id,
            'wavelength': self.wavelength,
            'content_hash': self.content_hash,
            'resource': self.resource,
            'full_address': self.full_address
        }


class LUXBINAddress:
    """
    LUXBIN address parser and validator

    Handles quantum internet addresses with:
    - Node identification
    - Wavelength-based routing
    - Content-addressable hashing
    - Resource location
    """

    # Address pattern: luxbin://node_id.wavelength.hash/resource
    ADDRESS_PATTERN = re.compile(
        r'^luxbin://([^.]+)\.([^.]+)\.([^/]+)(?:/(.+))?$'
    )

    def __init__(self):
        self.converter = LuxbinLightConverter()

    @classmethod
    def parse(cls, address: str) -> Optional[LUXBINAddressComponents]:
        """
        Parse LUXBIN address into components

        Args:
            address: LUXBIN URL string

        Returns:
            LUXBINAddressComponents or None if invalid

        Example:
            >>> addr = LUXBINAddress.parse("luxbin://ibm_fez.637nm.ABC123/page.html")
            >>> addr.node_id
            'ibm_fez'
            >>> addr.wavelength
            '637nm'
        """
        if not address:
            return None

        # Validate and parse address
        match = cls.ADDRESS_PATTERN.match(address)

        if not match:
            return None

        node_id, wavelength, content_hash, resource = match.groups()

        # Resource is optional (defaults to root)
        if not resource:
            resource = "/"

        return LUXBINAddressComponents(
            node_id=node_id,
            wavelength=wavelength,
            content_hash=content_hash,
            resource=resource,
            full_address=address
        )

    @classmethod
    def create(
        cls,
        node_id: str,
        content: bytes,
        resource: str = "/",
        wavelength: Optional[float] = None
    ) -> str:
        """
        Create LUXBIN address for content

        Args:
            node_id: Node identifier
            content: Content to address (bytes)
            resource: Resource path (default: "/")
            wavelength: Preferred wavelength in nm (default: auto-detect)

        Returns:
            Full LUXBIN address string

        Example:
            >>> addr = LUXBINAddress.create(
            ...     node_id="mynode",
            ...     content=b"Hello World",
            ...     resource="index.html",
            ...     wavelength=550
            ... )
            >>> addr
            'luxbin://mynode.550nm.B1F2A3/index.html'
        """
        # Generate content hash using LUXBIN encoding
        content_hash = cls.luxbin_hash(content)

        # Determine wavelength
        if wavelength is None:
            # Auto-detect from content
            wavelength = cls._infer_wavelength_from_content(content)

        wavelength_str = f"{int(wavelength)}nm"

        # Build address
        address = f"luxbin://{node_id}.{wavelength_str}.{content_hash}"

        if resource and resource != "/":
            # Remove leading slash if present
            resource = resource.lstrip("/")
            address += f"/{resource}"

        return address

    @classmethod
    def create_name_address(
        cls,
        name: str,
        content: bytes,
        wavelength: Optional[float] = None
    ) -> str:
        """
        Create human-readable named address

        Args:
            name: Human-readable name (e.g., "mywebsite")
            content: Content to address
            wavelength: Preferred wavelength

        Returns:
            Named LUXBIN address

        Example:
            >>> addr = LUXBINAddress.create_name_address(
            ...     name="mywebsite",
            ...     content=b"<html>...</html>",
            ...     wavelength=637
            ... )
            >>> addr
            'luxbin://mywebsite.637nm.F3A2B1'
        """
        return cls.create(
            node_id=name,
            content=content,
            wavelength=wavelength
        )

    @classmethod
    def luxbin_hash(cls, content: bytes, length: int = 6) -> str:
        """
        Generate LUXBIN hash of content

        Uses LUXBIN encoding for quantum-native hashing

        Args:
            content: Content to hash
            length: Hash length in LUXBIN characters (default: 6)

        Returns:
            LUXBIN hash string

        Example:
            >>> LUXBINAddress.luxbin_hash(b"Hello World")
            'A3F9D2'
        """
        # SHA-256 hash
        sha_hash = hashlib.sha256(content).digest()

        # Convert to LUXBIN encoding
        converter = LuxbinLightConverter()
        luxbin = converter.binary_to_luxbin_chars(sha_hash, chunk_size=6)

        # Return first N characters as hash
        return luxbin[:length].upper()

    @classmethod
    def _infer_wavelength_from_content(cls, content: bytes) -> float:
        """
        Infer optimal wavelength for content

        Uses content hash to distribute across spectrum

        Args:
            content: Content bytes

        Returns:
            Wavelength in nm (400-700nm range)
        """
        # Hash content
        content_hash = hashlib.sha256(content).digest()

        # Use first byte to determine wavelength
        hash_value = content_hash[0]

        # Map 0-255 to 400-700nm
        wavelength = 400 + (hash_value / 255) * 300

        return round(wavelength)

    @classmethod
    def validate(cls, address: str) -> Tuple[bool, Optional[str]]:
        """
        Validate LUXBIN address

        Args:
            address: Address to validate

        Returns:
            (is_valid, error_message)

        Example:
            >>> LUXBINAddress.validate("luxbin://node.550nm.ABC123/file")
            (True, None)
            >>> LUXBINAddress.validate("http://example.com")
            (False, "Invalid protocol: expected 'luxbin://'")
        """
        if not address:
            return False, "Address is empty"

        # Check protocol
        if not address.startswith("luxbin://"):
            return False, "Invalid protocol: expected 'luxbin://'"

        # Parse address
        components = cls.parse(address)

        if not components:
            return False, "Invalid address format"

        # Validate components
        if not components.node_id:
            return False, "Missing node_id"

        if not components.wavelength:
            return False, "Missing wavelength"

        if not components.content_hash:
            return False, "Missing content_hash"

        # Validate wavelength format
        if not cls._validate_wavelength(components.wavelength):
            return False, f"Invalid wavelength format: {components.wavelength}"

        return True, None

    @classmethod
    def _validate_wavelength(cls, wavelength_str: str) -> bool:
        """
        Validate wavelength format

        Accepts:
        - Single wavelength: "550nm", "637nm"
        - Range: "400-700nm"

        Args:
            wavelength_str: Wavelength string

        Returns:
            True if valid format
        """
        # Single wavelength pattern: 400-700nm
        single_pattern = re.compile(r'^(\d{3})nm$')
        match = single_pattern.match(wavelength_str)

        if match:
            wavelength = int(match.group(1))
            return 400 <= wavelength <= 700

        # Range pattern: 400-700nm
        range_pattern = re.compile(r'^(\d{3})-(\d{3})nm$')
        match = range_pattern.match(wavelength_str)

        if match:
            min_wl = int(match.group(1))
            max_wl = int(match.group(2))
            return 400 <= min_wl <= max_wl <= 700

        return False

    @classmethod
    def extract_wavelength(cls, address: str) -> Optional[float]:
        """
        Extract wavelength value from address

        Args:
            address: LUXBIN address

        Returns:
            Wavelength in nm (or midpoint of range)

        Example:
            >>> LUXBINAddress.extract_wavelength("luxbin://node.550nm.ABC/file")
            550.0
            >>> LUXBINAddress.extract_wavelength("luxbin://node.400-700nm.ABC/file")
            550.0
        """
        components = cls.parse(address)

        if not components:
            return None

        wavelength_str = components.wavelength

        # Single wavelength
        if '-' not in wavelength_str:
            return float(wavelength_str.replace('nm', ''))

        # Range: return midpoint
        parts = wavelength_str.replace('nm', '').split('-')
        min_wl = float(parts[0])
        max_wl = float(parts[1])

        return (min_wl + max_wl) / 2

    @classmethod
    def is_compatible_wavelength(
        cls,
        address: str,
        node_wavelength_range: Tuple[float, float],
        tolerance: float = 50
    ) -> bool:
        """
        Check if address wavelength is compatible with node's range

        Args:
            address: LUXBIN address
            node_wavelength_range: Node's wavelength specialization (min, max)
            tolerance: Acceptable deviation in nm

        Returns:
            True if compatible

        Example:
            >>> LUXBINAddress.is_compatible_wavelength(
            ...     "luxbin://node.550nm.ABC/file",
            ...     (500, 600),
            ...     tolerance=50
            ... )
            True
        """
        addr_wavelength = cls.extract_wavelength(address)

        if addr_wavelength is None:
            return False

        min_wl, max_wl = node_wavelength_range

        # Check if wavelength falls within node's range (with tolerance)
        return (min_wl - tolerance) <= addr_wavelength <= (max_wl + tolerance)


def main():
    """Test LUXBIN address system"""
    print("=" * 70)
    print("LUXBIN ADDRESS SYSTEM TEST")
    print("=" * 70)

    # Test 1: Create address
    print("\n1. Creating LUXBIN addresses:")
    print("-" * 70)

    content = b"Hello, Quantum Internet!"

    addr1 = LUXBINAddress.create(
        node_id="ibm_fez",
        content=content,
        resource="index.html",
        wavelength=637
    )
    print(f"Address 1: {addr1}")

    addr2 = LUXBINAddress.create_name_address(
        name="mywebsite",
        content=content,
        wavelength=550
    )
    print(f"Address 2: {addr2}")

    # Test 2: Parse address
    print("\n2. Parsing LUXBIN addresses:")
    print("-" * 70)

    for addr in [addr1, addr2]:
        components = LUXBINAddress.parse(addr)
        if components:
            print(f"\nAddress: {addr}")
            print(f"  Node ID: {components.node_id}")
            print(f"  Wavelength: {components.wavelength}")
            print(f"  Hash: {components.content_hash}")
            print(f"  Resource: {components.resource}")

    # Test 3: Validate addresses
    print("\n3. Validating addresses:")
    print("-" * 70)

    test_addresses = [
        "luxbin://ibm_fez.637nm.ABC123/index.html",
        "luxbin://mysite.550nm.XYZ789",
        "luxbin://node.400-700nm.FULL/spectrum",
        "http://example.com",  # Invalid
        "luxbin://invalid",  # Invalid
    ]

    for addr in test_addresses:
        is_valid, error = LUXBINAddress.validate(addr)
        status = "✅ VALID" if is_valid else f"❌ INVALID: {error}"
        print(f"{status:40s} {addr}")

    # Test 4: Wavelength extraction
    print("\n4. Extracting wavelengths:")
    print("-" * 70)

    for addr in test_addresses[:3]:
        wavelength = LUXBINAddress.extract_wavelength(addr)
        if wavelength:
            print(f"{wavelength}nm <- {addr}")

    # Test 5: Wavelength compatibility
    print("\n5. Testing wavelength compatibility:")
    print("-" * 70)

    node_range = (500, 600)  # Green region node
    print(f"Node wavelength range: {node_range[0]}-{node_range[1]}nm\n")

    for addr in test_addresses[:3]:
        compatible = LUXBINAddress.is_compatible_wavelength(addr, node_range)
        status = "✅ Compatible" if compatible else "❌ Incompatible"
        print(f"{status:20s} {addr}")

    # Test 6: LUXBIN hashing
    print("\n6. LUXBIN content hashing:")
    print("-" * 70)

    test_contents = [
        b"Hello World",
        b"Quantum Internet",
        b"LUXBIN Protocol"
    ]

    for content in test_contents:
        hash_value = LUXBINAddress.luxbin_hash(content, length=8)
        print(f"{hash_value:12s} <- {content.decode()}")

    print("\n" + "=" * 70)
    print("✅ LUXBIN ADDRESS SYSTEM TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
