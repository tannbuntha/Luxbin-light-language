"""
LUXBIN Quantum Blockchain Service
Provides real-time blockchain data to Vercel app
"""

from luxbin_chain_quantum_node import QuantumBlockchainNode
import json
import time
import os
from datetime import datetime
from threading import Thread

class QuantumBlockchainService:
    """Service that runs quantum blockchain and exposes data"""

    def __init__(self,
                 validator_backends=['ibm_fez', 'ibm_torino', 'ibm_marrakesh'],
                 status_file='quantum_blockchain_status.json'):
        self.validator_backends = validator_backends
        self.status_file = status_file
        self.primary_node = None
        self.blockchain = []
        self.pending_transactions = []
        self.latest_validators_status = []

    def initialize(self):
        """Initialize quantum blockchain node"""
        print("🔗 Initializing LUXBIN Quantum Blockchain Service...")
        self.primary_node = QuantumBlockchainNode(self.validator_backends[0])
        self.update_validator_status()
        print("✅ Service initialized")

    def update_validator_status(self):
        """Get current status of all quantum validators"""
        from qiskit_ibm_runtime import QiskitRuntimeService

        service = QiskitRuntimeService()
        self.latest_validators_status = []

        for backend_name in self.validator_backends:
            try:
                backend = service.backend(backend_name)
                status = backend.status()

                self.latest_validators_status.append({
                    'name': backend_name,
                    'location': 'Yorktown Heights, NY',  # IBM Quantum location
                    'qubits': backend.num_qubits,
                    'queue': status.pending_jobs,
                    'status': 'active' if status.operational else 'offline',
                    'lastValidation': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"⚠️  Could not get status for {backend_name}: {e}")
                self.latest_validators_status.append({
                    'name': backend_name,
                    'location': 'Unknown',
                    'qubits': 0,
                    'queue': 0,
                    'status': 'offline',
                    'lastValidation': datetime.now().isoformat()
                })

    def add_transaction(self, transaction):
        """Add transaction to pending pool"""
        self.pending_transactions.append(transaction)
        self.save_status()
        print(f"📝 Transaction added: {len(self.pending_transactions)} pending")

    def mine_block(self):
        """Mine next block with quantum consensus"""
        if not self.pending_transactions:
            print("⏳ No pending transactions")
            return None

        print(f"\n⛏️  Mining block #{len(self.blockchain) + 1}...")

        transactions = self.pending_transactions.copy()

        try:
            # Validate with quantum consensus
            encoded = self.primary_node.encode_transaction_luxbin(transactions[0])
            consensus = self.primary_node.quantum_consensus(
                transactions[0],
                validator_backends=self.validator_backends
            )

            if consensus['consensus']:
                # Mine block
                block = self.primary_node.quantum_mine_block(transactions)

                # Add to blockchain
                block['block_number'] = len(self.blockchain) + 1
                block['previous_hash'] = self.blockchain[-1]['hash'] if self.blockchain else '0' * 64
                block['consensus_votes'] = {
                    'total': consensus['total_validators'],
                    'valid': consensus['valid_count'],
                    'validators': [
                        {
                            'backend': v['backend'],
                            'vote': 'valid' if v.get('valid', False) else 'invalid',
                            'jobId': v.get('job_id', 'N/A')
                        }
                        for v in consensus['validations']
                    ]
                }

                self.blockchain.append(block)
                self.pending_transactions = []

                print(f"✅ Block #{block['block_number']} mined!")
                print(f"   Hash: {block['hash'][:32]}...")

                # Update status file
                self.save_status()

                return block
            else:
                print(f"❌ Consensus failed")
                return None

        except Exception as e:
            print(f"❌ Mining error: {e}")
            return None

    def get_blockchain_status(self):
        """Get current blockchain status for API"""
        self.update_validator_status()

        # Calculate stats
        total_qubits = sum(v['qubits'] for v in self.latest_validators_status)
        total_transactions = sum(
            len(block.get('transactions', []))
            for block in self.blockchain
        )

        # Get latest block
        latest_block = None
        if self.blockchain:
            block = self.blockchain[-1]
            latest_block = {
                'number': block.get('block_number', len(self.blockchain)),
                'hash': block['hash'],
                'quantumNonce': block['nonce'],
                'timestamp': block['timestamp'],
                'transactions': len(block.get('transactions', [])),
                'miningBackend': block['quantum_backend'],
                'jobId': block.get('job_id', 'N/A'),
                'consensusVotes': block.get('consensus_votes', {
                    'total': 0,
                    'valid': 0,
                    'validators': []
                })
            }

        status = {
            'network': {
                'status': 'online',
                'validators': self.latest_validators_status,
                'totalValidators': len(self.validator_backends),
                'consensusThreshold': 2
            },
            'blockchain': {
                'latestBlock': latest_block,
                'totalBlocks': len(self.blockchain),
                'totalTransactions': total_transactions,
                'pendingTransactions': len(self.pending_transactions)
            },
            'quantum': {
                'activeJobs': 0,  # Would need to track this separately
                'completedJobs': len(self.blockchain),
                'totalQubitsAvailable': total_qubits,
                'luxbinEncoding': True,
                'photomicCommunication': 'active'
            },
            'timestamp': datetime.now().isoformat()
        }

        return status

    def save_status(self):
        """Save current status to file"""
        status = self.get_blockchain_status()

        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)

        print(f"💾 Status saved to {self.status_file}")

    def run_continuous(self, mining_interval=120):
        """Run blockchain continuously"""
        print(f"\n{'='*70}")
        print(f"🔄 QUANTUM BLOCKCHAIN SERVICE STARTED")
        print(f"{'='*70}")
        print(f"\nMining interval: {mining_interval} seconds")
        print(f"Status file: {self.status_file}")
        print(f"Validators: {', '.join(self.validator_backends)}")

        try:
            while True:
                # Mine block if there are pending transactions
                if self.pending_transactions:
                    self.mine_block()
                else:
                    # Still update status even if no mining
                    self.save_status()
                    print(f"\n⏳ Waiting for transactions... (Blocks: {len(self.blockchain)})")

                # Wait before next cycle
                print(f"\n⏰ Next cycle in {mining_interval} seconds...")
                time.sleep(mining_interval)

        except KeyboardInterrupt:
            print(f"\n\n🛑 Service stopped")
            print(f"📊 Final: {len(self.blockchain)} blocks mined")

def main():
    """Run the quantum blockchain service"""

    service = QuantumBlockchainService()
    service.initialize()

    # Add a sample transaction to start
    print("\n📝 Adding initial transaction...")
    service.add_transaction({
        'from': '0xAlice',
        'to': '0xBob',
        'amount': 100,
        'token': 'LUXBIN',
        'data': 'Genesis transaction'
    })

    # Mine first block
    service.mine_block()

    print("\n✅ Service ready!")
    print("\nYour Vercel app can now read from:")
    print(f"   → {service.status_file}")
    print("\nThe API should read this file to get real-time data.")

    # Optionally run continuously
    run_continuous = input("\nRun continuously? (y/n): ").lower() == 'y'

    if run_continuous:
        # Add another transaction for continuous mining
        service.add_transaction({
            'from': '0xCarol',
            'to': '0xDave',
            'amount': 50,
            'token': 'LUXBIN',
            'data': 'Second transaction'
        })

        service.run_continuous(mining_interval=180)  # Mine every 3 minutes
    else:
        print("\n💾 Status saved. Service stopped.")

if __name__ == "__main__":
    main()
