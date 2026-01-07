"""
Continuous Quantum Blockchain with Auto-Generated Transactions
Runs indefinitely, automatically creating and mining transactions on quantum computers
"""

from quantum_blockchain_service import QuantumBlockchainService
import time
import random
from datetime import datetime

# Sample wallet addresses for realistic transactions
WALLETS = [
    '0xAlice_Quantum',
    '0xBob_Photonic',
    '0xCarol_LUXBIN',
    '0xDave_Hermetic',
    '0xEve_Mirror',
    '0xFrank_Diamond',
    '0xGrace_NV_Center',
    '0xHank_Entangled'
]

# Transaction types
TX_TYPES = [
    'LUXBIN transfer',
    'Quantum swap',
    'Photonic payment',
    'Hermetic mirror',
    'Diamond storage',
    'NV center activation'
]

def generate_random_transaction():
    """Generate a random realistic transaction"""
    from_wallet = random.choice(WALLETS)
    to_wallet = random.choice([w for w in WALLETS if w != from_wallet])

    amount = round(random.uniform(0.1, 1000.0), 2)
    tx_type = random.choice(TX_TYPES)

    return {
        'from': from_wallet,
        'to': to_wallet,
        'amount': amount,
        'token': 'LUXBIN',
        'type': tx_type,
        'timestamp': datetime.now().isoformat(),
        'data': f'{tx_type} - Quantum validated transaction'
    }

def main():
    print("="*70)
    print("🔗 LUXBIN CONTINUOUS QUANTUM BLOCKCHAIN")
    print("="*70)
    print("\nThis will:")
    print("1. Generate random transactions automatically")
    print("2. Mine blocks on IBM quantum computers")
    print("3. Update dashboard data in real-time")
    print("4. Run indefinitely until stopped (Ctrl+C)")
    print("\n" + "="*70)

    # Initialize service
    service = QuantumBlockchainService(
        validator_backends=['ibm_fez', 'ibm_torino', 'ibm_marrakesh'],
        status_file='quantum_blockchain_status.json'
    )

    service.initialize()

    print("\n✅ Quantum blockchain service initialized")
    print(f"📁 Status file: quantum_blockchain_status.json")
    print(f"⚛️  Validators: {', '.join(service.validator_backends)}")

    # Configuration
    transactions_per_block = 3  # Number of transactions before mining
    mining_interval = 180  # Mine every 3 minutes (180 seconds)
    transaction_interval = 60  # Add new transaction every 60 seconds

    print(f"\n⚙️  Configuration:")
    print(f"   Transactions per block: {transactions_per_block}")
    print(f"   Mining interval: {mining_interval}s")
    print(f"   New transaction every: {transaction_interval}s")

    print("\n🚀 Starting continuous operation...\n")

    last_mine_time = time.time()
    last_tx_time = time.time()
    tx_count = 0

    try:
        while True:
            current_time = time.time()

            # Add new transaction periodically
            if current_time - last_tx_time >= transaction_interval:
                tx = generate_random_transaction()
                service.add_transaction(tx)
                tx_count += 1

                print(f"📝 Transaction #{tx_count} added:")
                print(f"   {tx['from']} → {tx['to']}")
                print(f"   Amount: {tx['amount']} {tx['token']}")
                print(f"   Type: {tx['type']}")
                print(f"   Pending: {len(service.pending_transactions)}")

                last_tx_time = current_time

            # Mine block when enough transactions accumulated OR interval passed
            should_mine = (
                len(service.pending_transactions) >= transactions_per_block or
                (len(service.pending_transactions) > 0 and
                 current_time - last_mine_time >= mining_interval)
            )

            if should_mine:
                print(f"\n⛏️  Mining block #{len(service.blockchain) + 1}...")
                print(f"   Transactions to include: {len(service.pending_transactions)}")

                block = service.mine_block()

                if block:
                    print(f"\n🎉 BLOCK MINED!")
                    print(f"   Block #{block['block_number']}")
                    print(f"   Hash: {block['hash'][:32]}...")
                    print(f"   Quantum Nonce: {block['nonce']}")
                    print(f"   Transactions: {len(block.get('transactions', []))}")
                    print(f"   Mining Backend: {block['quantum_backend']}")
                    print(f"   Consensus: {block.get('consensus_votes', {}).get('valid', 0)}/{block.get('consensus_votes', {}).get('total', 0)}")
                    print(f"\n📊 Blockchain Stats:")
                    print(f"   Total Blocks: {len(service.blockchain)}")
                    print(f"   Total Transactions: {sum(len(b.get('transactions', [])) for b in service.blockchain)}")

                    last_mine_time = current_time
                else:
                    print(f"\n❌ Mining failed (consensus not reached)")

            # Update status file periodically
            service.save_status()

            # Wait a bit before next iteration
            time.sleep(10)

    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print("🛑 STOPPING QUANTUM BLOCKCHAIN")
        print("="*70)

        # Final stats
        print(f"\n📊 Final Statistics:")
        print(f"   Total Blocks Mined: {len(service.blockchain)}")
        print(f"   Total Transactions: {sum(len(b.get('transactions', [])) for b in service.blockchain)}")
        print(f"   Pending Transactions: {len(service.pending_transactions)}")

        if service.blockchain:
            print(f"\n📜 Block History:")
            for i, block in enumerate(service.blockchain[-5:], 1):  # Show last 5 blocks
                print(f"   Block #{block.get('block_number', i)}: {block['hash'][:16]}... ({len(block.get('transactions', []))} txs)")

        # Save final state
        service.save_status()
        print(f"\n💾 Final state saved to quantum_blockchain_status.json")
        print(f"\n✅ Blockchain service stopped cleanly")

if __name__ == "__main__":
    main()
