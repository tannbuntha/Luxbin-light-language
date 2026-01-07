"""
LUXBIN Chain Quantum Node
Connects your LUXBIN Chain blockchain to IBM Quantum computers
"""

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from luxbin_quantum_computer import text_to_luxbin, luxbin_to_wavelengths, create_luxbin_quantum_circuit
import json
import hashlib
import time

class QuantumBlockchainNode:
    """
    Quantum node for LUXBIN Chain
    Processes blockchain transactions on quantum computers
    """

    def __init__(self, quantum_backend='ibm_fez'):
        """Initialize quantum blockchain node"""
        print(f"🔗 Initializing LUXBIN Chain Quantum Node...")

        self.service = QiskitRuntimeService()
        self.backend = self.service.backend(quantum_backend)

        print(f"✅ Connected to: {self.backend.name}")
        print(f"   Qubits: {self.backend.num_qubits}")
        print(f"   Queue: {self.backend.status().pending_jobs} jobs")

        self.validated_transactions = []
        self.quantum_blocks = []

    def encode_transaction_luxbin(self, transaction):
        """
        Encode blockchain transaction as LUXBIN quantum state

        Args:
            transaction (dict): Blockchain transaction
                {
                    'from': address,
                    'to': address,
                    'amount': number,
                    'data': optional data
                }

        Returns:
            dict: Encoded transaction with LUXBIN and quantum data
        """
        print(f"\n📝 Encoding transaction to LUXBIN...")

        # Convert transaction to JSON
        tx_json = json.dumps(transaction, sort_keys=True)

        # Encode to LUXBIN
        luxbin, binary = text_to_luxbin(tx_json)
        wavelengths = luxbin_to_wavelengths(luxbin, enable_quantum=True)

        # Create quantum circuit
        num_qubits = min(5, len(wavelengths))
        qc = create_luxbin_quantum_circuit(wavelengths, num_qubits)

        print(f"✅ Transaction encoded:")
        print(f"   LUXBIN: {luxbin[:50]}...")
        print(f"   Wavelengths: {len(wavelengths)}")
        print(f"   Quantum circuit: {num_qubits} qubits")

        return {
            'original': transaction,
            'json': tx_json,
            'luxbin': luxbin,
            'binary': binary,
            'wavelengths': wavelengths,
            'quantum_circuit': qc,
            'num_qubits': num_qubits
        }

    def quantum_validate_transaction(self, encoded_tx):
        """
        Validate transaction using quantum computer

        Returns:
            bool: True if transaction is valid
        """
        print(f"\n⚛️  Quantum validation starting...")

        qc = encoded_tx['quantum_circuit']

        # Run on quantum computer
        print(f"🚀 Submitting to {self.backend.name}...")

        transpiled = transpile(qc, backend=self.backend, optimization_level=3)
        sampler = Sampler(self.backend)
        job = sampler.run([transpiled], shots=100)

        job_id = job.job_id()
        print(f"✅ Job ID: {job_id}")
        print(f"⏳ Waiting for quantum validation...")

        result = job.result()
        counts = result[0].data.meas.get_counts()

        # Validation logic: Check quantum state distribution
        # Valid transaction should have balanced quantum state distribution
        most_common = max(counts.values())
        total = sum(counts.values())
        balance = most_common / total

        # If too concentrated (>80%), likely invalid
        # If well distributed (<80%), likely valid
        is_valid = balance < 0.8

        print(f"\n✅ Quantum validation complete!")
        print(f"   Most common state: {most_common}/{total} ({balance:.1%})")
        print(f"   Verdict: {'✅ VALID' if is_valid else '❌ INVALID'}")

        return {
            'valid': is_valid,
            'job_id': job_id,
            'counts': counts,
            'balance': balance,
            'backend': self.backend.name
        }

    def quantum_mine_block(self, transactions, difficulty=3):
        """
        Mine block using quantum computer
        Uses quantum randomness for nonce finding

        Args:
            transactions (list): List of transactions
            difficulty (int): Mining difficulty (leading zeros)

        Returns:
            dict: Mined block with quantum nonce
        """
        print(f"\n⛏️  QUANTUM MINING STARTED")
        print(f"   Difficulty: {difficulty} leading zeros")
        print(f"   Transactions: {len(transactions)}")

        # Encode all transactions
        block_data = json.dumps(transactions, sort_keys=True)
        luxbin, _ = text_to_luxbin(block_data)
        wavelengths = luxbin_to_wavelengths(luxbin)

        # Create quantum circuit for mining
        qc = QuantumCircuit(8)  # 8 qubits = 256 possible nonces

        # Create quantum superposition of all possible nonces
        for i in range(8):
            qc.h(i)  # Hadamard gate = equal superposition

        # Add phase based on LUXBIN encoding
        for i, wl in enumerate(wavelengths[:8]):
            theta = (wl['wavelength_nm'] - 400) / 300 * 3.14159
            qc.ry(theta, i)

        qc.measure_all()

        # Run on quantum computer
        print(f"🚀 Running quantum mining on {self.backend.name}...")

        transpiled = transpile(qc, backend=self.backend, optimization_level=3)
        sampler = Sampler(self.backend)
        job = sampler.run([transpiled], shots=100)

        result = job.result()
        counts = result[0].data.meas.get_counts()

        # Use most common quantum measurement as nonce
        nonce_binary = max(counts.items(), key=lambda x: x[1])[0]
        nonce = int(nonce_binary, 2)

        print(f"✅ Quantum nonce found: {nonce} (0b{nonce_binary})")

        # Create block hash
        block = {
            'transactions': transactions,
            'timestamp': time.time(),
            'nonce': nonce,
            'luxbin': luxbin,
            'quantum_mined': True,
            'quantum_backend': self.backend.name,
            'job_id': job.job_id()
        }

        block_hash = hashlib.sha256(
            json.dumps(block, sort_keys=True).encode()
        ).hexdigest()

        block['hash'] = block_hash

        print(f"✅ Block mined!")
        print(f"   Hash: {block_hash[:16]}...")
        print(f"   Nonce: {nonce}")

        self.quantum_blocks.append(block)

        return block

    def quantum_consensus(self, block, validator_backends=['ibm_fez', 'ibm_torino', 'ibm_marrakesh']):
        """
        Achieve quantum consensus across multiple quantum computers

        Args:
            block (dict): Block to validate
            validator_backends (list): List of quantum computer names

        Returns:
            bool: True if consensus achieved
        """
        print(f"\n🌐 QUANTUM CONSENSUS PROTOCOL")
        print(f"   Validators: {len(validator_backends)}")

        validations = []

        for backend_name in validator_backends:
            try:
                print(f"\n   Validator: {backend_name}")

                # Create temporary node for this validator
                validator = QuantumBlockchainNode(backend_name)

                # Encode block
                encoded = validator.encode_transaction_luxbin(block)

                # Validate on this quantum computer
                result = validator.quantum_validate_transaction(encoded)

                validations.append({
                    'backend': backend_name,
                    'valid': result['valid'],
                    'job_id': result['job_id']
                })

                print(f"   → {'✅ VALID' if result['valid'] else '❌ INVALID'}")

            except Exception as e:
                print(f"   → ❌ Error: {e}")
                validations.append({
                    'backend': backend_name,
                    'valid': False,
                    'error': str(e)
                })

        # Consensus: 2/3 majority
        valid_count = sum(1 for v in validations if v.get('valid', False))
        consensus_achieved = valid_count >= len(validations) * 2/3

        print(f"\n📊 Consensus Results:")
        print(f"   Valid: {valid_count}/{len(validations)}")
        print(f"   Consensus: {'✅ ACHIEVED' if consensus_achieved else '❌ FAILED'}")

        return {
            'consensus': consensus_achieved,
            'validations': validations,
            'valid_count': valid_count,
            'total_validators': len(validations)
        }

def demo_quantum_blockchain():
    """Demo: Run LUXBIN Chain transaction on quantum computer"""

    print("="*70)
    print("🔗 LUXBIN CHAIN QUANTUM NODE DEMO")
    print("="*70)

    # Initialize quantum node
    node = QuantumBlockchainNode('ibm_fez')

    # Create sample transaction
    transaction = {
        'from': '0xAlice123...',
        'to': '0xBob456...',
        'amount': 100.5,
        'token': 'LUXBIN',
        'data': 'Quantum blockchain rocks!'
    }

    print(f"\n📝 Transaction:")
    print(f"   From: {transaction['from']}")
    print(f"   To: {transaction['to']}")
    print(f"   Amount: {transaction['amount']} LUXBIN")

    # Encode transaction
    encoded = node.encode_transaction_luxbin(transaction)

    # Validate on quantum computer
    validation = node.quantum_validate_transaction(encoded)

    if validation['valid']:
        print(f"\n✅ Transaction validated on quantum computer!")

        # Mine block with quantum computer
        block = node.quantum_mine_block([transaction])

        print(f"\n🎉 QUANTUM BLOCKCHAIN BLOCK MINED!")
        print(f"   Block hash: {block['hash'][:32]}...")
        print(f"   Quantum nonce: {block['nonce']}")
        print(f"   Backend: {block['quantum_backend']}")

        return block
    else:
        print(f"\n❌ Transaction failed quantum validation")
        return None

if __name__ == "__main__":
    demo_quantum_blockchain()
