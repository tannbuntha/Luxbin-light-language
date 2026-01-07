"""
Quick Start: Mine 3 Blocks on Quantum Computers
Fast demo that mines 3 blocks with multiple transactions
"""

from quantum_blockchain_service import QuantumBlockchainService
import time

def main():
    print("="*70)
    print("🚀 QUICK START: QUANTUM BLOCKCHAIN DEMO")
    print("="*70)
    print("\nThis will mine 3 blocks with multiple transactions on IBM quantum computers")
    print("Estimated time: ~3-5 minutes\n")
    print("="*70)

    # Initialize service
    print("\n🔗 Initializing quantum blockchain service...")
    service = QuantumBlockchainService()
    service.initialize()

    # Block 1: Payment transactions
    print("\n" + "="*70)
    print("📦 BLOCK 1: Payment Transactions")
    print("="*70)

    service.add_transaction({
        'from': '0xAlice',
        'to': '0xBob',
        'amount': 100.0,
        'token': 'LUXBIN',
        'type': 'payment',
        'data': 'Coffee payment'
    })

    service.add_transaction({
        'from': '0xCarol',
        'to': '0xDave',
        'amount': 50.0,
        'token': 'LUXBIN',
        'type': 'payment',
        'data': 'Lunch money'
    })

    print("\n📝 Added 2 transactions to block 1")
    print("⛏️  Mining block 1 on quantum computers...")

    block1 = service.mine_block()

    if block1:
        print(f"\n✅ BLOCK 1 MINED!")
        print(f"   Hash: {block1['hash'][:32]}...")
        print(f"   Quantum Nonce: {block1['nonce']}")
        print(f"   Consensus: {block1['consensus_votes']['valid']}/{block1['consensus_votes']['total']}")

    # Block 2: Swap transactions
    print("\n" + "="*70)
    print("📦 BLOCK 2: Swap Transactions")
    print("="*70)

    service.add_transaction({
        'from': '0xEve',
        'to': '0xFrank',
        'amount': 250.0,
        'token': 'LUXBIN',
        'type': 'swap',
        'data': 'LUXBIN <-> ETH swap'
    })

    service.add_transaction({
        'from': '0xGrace',
        'to': '0xHank',
        'amount': 75.5,
        'token': 'LUXBIN',
        'type': 'swap',
        'data': 'Token exchange'
    })

    service.add_transaction({
        'from': '0xIvy',
        'to': '0xJack',
        'amount': 150.0,
        'token': 'LUXBIN',
        'type': 'payment',
        'data': 'Invoice payment'
    })

    print("\n📝 Added 3 transactions to block 2")
    print("⛏️  Mining block 2 on quantum computers...")

    block2 = service.mine_block()

    if block2:
        print(f"\n✅ BLOCK 2 MINED!")
        print(f"   Hash: {block2['hash'][:32]}...")
        print(f"   Quantum Nonce: {block2['nonce']}")
        print(f"   Consensus: {block2['consensus_votes']['valid']}/{block2['consensus_votes']['total']}")

    # Block 3: Hermetic mirror transactions
    print("\n" + "="*70)
    print("📦 BLOCK 3: Hermetic Mirror Transactions")
    print("="*70)

    service.add_transaction({
        'from': '0xMirror_Node_1',
        'to': '0xMirror_Node_2',
        'amount': 500.0,
        'token': 'LUXBIN',
        'type': 'hermetic_mirror',
        'data': 'Blockchain state synchronization'
    })

    service.add_transaction({
        'from': '0xQuantum_Validator',
        'to': '0xPhotonic_Bridge',
        'amount': 1000.0,
        'token': 'LUXBIN',
        'type': 'photonic_bridge',
        'data': 'Cross-chain quantum bridge'
    })

    print("\n📝 Added 2 transactions to block 3")
    print("⛏️  Mining block 3 on quantum computers...")

    block3 = service.mine_block()

    if block3:
        print(f"\n✅ BLOCK 3 MINED!")
        print(f"   Hash: {block3['hash'][:32]}...")
        print(f"   Quantum Nonce: {block3['nonce']}")
        print(f"   Consensus: {block3['consensus_votes']['valid']}/{block3['consensus_votes']['total']}")

    # Final summary
    print("\n" + "="*70)
    print("🎉 QUANTUM BLOCKCHAIN DEMO COMPLETE!")
    print("="*70)

    print(f"\n📊 Statistics:")
    print(f"   Total Blocks Mined: {len(service.blockchain)}")
    print(f"   Total Transactions: {sum(len(b['transactions']) for b in service.blockchain)}")
    print(f"   Quantum Validators: {len(service.validator_backends)}")

    print(f"\n📜 Blockchain:")
    for block in service.blockchain:
        print(f"   Block #{block['block_number']}: {block['hash'][:16]}... ({len(block['transactions'])} txs)")

    print(f"\n💾 Data saved to: quantum_blockchain_status.json")
    print(f"🌐 View on dashboard: http://localhost:3000/quantum-blockchain")
    print(f"\n✅ Your Vercel app will now show {len(service.blockchain)} blocks with {sum(len(b['transactions']) for b in service.blockchain)} transactions!")

if __name__ == "__main__":
    main()
