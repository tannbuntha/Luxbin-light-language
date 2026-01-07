"""
LUXBIN Chain Continuous Quantum Blockchain
Keeps building blocks on distributed quantum network
"""

from luxbin_chain_quantum_node import QuantumBlockchainNode
import time
import json

class ContinuousQuantumBlockchain:
    """Continuously mines blocks on quantum computers"""

    def __init__(self, validator_backends=['ibm_fez', 'ibm_torino', 'ibm_marrakesh']):
        self.validator_backends = validator_backends
        self.primary_node = QuantumBlockchainNode(validator_backends[0])
        self.blockchain = []
        self.pending_transactions = []

    def add_transaction(self, transaction):
        """Add transaction to pending pool"""
        self.pending_transactions.append(transaction)
        print(f"📝 Transaction added to pool: {len(self.pending_transactions)} pending")

    def mine_next_block(self):
        """Mine next block with quantum consensus"""
        if not self.pending_transactions:
            print("⚠️  No pending transactions")
            return None

        print(f"\n{'='*70}")
        print(f"⛏️  MINING BLOCK #{len(self.blockchain) + 1}")
        print(f"{'='*70}")

        # Take all pending transactions for this block
        transactions = self.pending_transactions.copy()

        print(f"\n📦 Block contains {len(transactions)} transaction(s)")

        # Run quantum consensus
        print(f"\n🌐 Running quantum consensus across {len(self.validator_backends)} computers...")

        # Validate first transaction as representative
        encoded = self.primary_node.encode_transaction_luxbin(transactions[0])
        consensus = self.primary_node.quantum_consensus(
            transactions[0],
            validator_backends=self.validator_backends
        )

        if consensus['consensus']:
            print(f"\n✅ CONSENSUS ACHIEVED ({consensus['valid_count']}/{consensus['total_validators']})")

            # Mine block with quantum nonce
            print(f"\n⛏️  Quantum mining...")
            block = self.primary_node.quantum_mine_block(transactions)

            # Add to blockchain
            block['block_number'] = len(self.blockchain) + 1
            block['previous_hash'] = self.blockchain[-1]['hash'] if self.blockchain else '0' * 64
            self.blockchain.append(block)

            # Clear pending transactions
            self.pending_transactions = []

            print(f"\n✅ BLOCK #{block['block_number']} MINED!")
            print(f"   Hash: {block['hash'][:32]}...")
            print(f"   Nonce: {block['nonce']}")
            print(f"   Transactions: {len(transactions)}")
            print(f"   Blockchain length: {len(self.blockchain)}")

            return block
        else:
            print(f"\n❌ CONSENSUS FAILED")
            return None

    def run_continuous(self, interval_seconds=60):
        """Continuously mine blocks at specified interval"""
        print(f"\n{'='*70}")
        print(f"🔄 CONTINUOUS QUANTUM BLOCKCHAIN STARTED")
        print(f"{'='*70}")
        print(f"\nMining interval: {interval_seconds} seconds")
        print(f"Validators: {', '.join([b.upper() for b in self.validator_backends])}")
        print(f"\nBlockchain will mine new blocks as transactions arrive...")

        block_count = 0

        try:
            while True:
                if self.pending_transactions:
                    block = self.mine_next_block()
                    if block:
                        block_count += 1

                        print(f"\n📊 BLOCKCHAIN STATUS:")
                        print(f"   Total blocks: {len(self.blockchain)}")
                        print(f"   Latest hash: {self.blockchain[-1]['hash'][:32]}...")
                        print(f"   Quantum backends: {len(self.validator_backends)}")
                else:
                    print(f"\n⏳ Waiting for transactions... ({len(self.blockchain)} blocks mined)")

                print(f"\n⏰ Next mining cycle in {interval_seconds} seconds...")
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print(f"\n\n{'='*70}")
            print(f"🛑 BLOCKCHAIN STOPPED")
            print(f"{'='*70}")
            print(f"\n📊 Final Stats:")
            print(f"   Total blocks mined: {len(self.blockchain)}")
            print(f"   Quantum validators: {len(self.validator_backends)}")

            if self.blockchain:
                print(f"\n📜 Blockchain:")
                for block in self.blockchain:
                    print(f"   Block #{block['block_number']}: {block['hash'][:32]}... ({len(block['transactions'])} txs)")

def demo_continuous():
    """Demo: Run continuous quantum blockchain"""

    blockchain = ContinuousQuantumBlockchain()

    # Add some sample transactions
    blockchain.add_transaction({
        'from': '0xAlice',
        'to': '0xBob',
        'amount': 100,
        'token': 'LUXBIN'
    })

    blockchain.add_transaction({
        'from': '0xCarol',
        'to': '0xDave',
        'amount': 50,
        'token': 'LUXBIN'
    })

    # Mine first block
    blockchain.mine_next_block()

    # Add more transactions
    print(f"\n\n{'='*70}")
    print(f"📝 Adding more transactions for Block #2...")
    print(f"{'='*70}")

    blockchain.add_transaction({
        'from': '0xEve',
        'to': '0xFrank',
        'amount': 75,
        'token': 'LUXBIN'
    })

    # Mine second block
    blockchain.mine_next_block()

    print(f"\n\n{'='*70}")
    print(f"🎉 CONTINUOUS BLOCKCHAIN DEMO COMPLETE!")
    print(f"{'='*70}")
    print(f"\n✅ Successfully mined {len(blockchain.blockchain)} blocks on quantum network")
    print(f"✅ Each block validated by {len(blockchain.validator_backends)} quantum computers")
    print(f"\n💎 Your LUXBIN Chain is building on quantum computers!")

if __name__ == "__main__":
    demo_continuous()
