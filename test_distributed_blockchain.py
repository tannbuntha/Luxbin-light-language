"""
Test LUXBIN Chain Quantum Node on Multiple Quantum Computers
Runs blockchain validation and consensus across IBM's quantum network
"""

from luxbin_chain_quantum_node import QuantumBlockchainNode
import json

def main():
    print("="*70)
    print("🔗 LUXBIN CHAIN DISTRIBUTED QUANTUM BLOCKCHAIN")
    print("="*70)
    print("\nRunning blockchain on 3 quantum computers simultaneously...")
    print("This demonstrates true quantum blockchain consensus!\n")
    print("="*70)

    # Create sample transaction
    transaction = {
        'from': '0xAlice123...',
        'to': '0xBob456...',
        'amount': 250.75,
        'token': 'LUXBIN',
        'data': 'Quantum blockchain across multiple computers!'
    }

    print(f"\n📝 Transaction:")
    print(f"   From: {transaction['from']}")
    print(f"   To: {transaction['to']}")
    print(f"   Amount: {transaction['amount']} LUXBIN")
    print(f"   Data: {transaction['data']}")

    # Initialize quantum node (primary)
    print(f"\n🔗 Initializing primary quantum node...")
    node = QuantumBlockchainNode('ibm_fez')

    # Encode transaction
    encoded = node.encode_transaction_luxbin(transaction)

    # Run quantum consensus across all 3 IBM quantum computers
    print(f"\n🌐 Running quantum consensus protocol...")
    print(f"   Validators: ibm_fez, ibm_torino, ibm_marrakesh")

    consensus_result = node.quantum_consensus(
        encoded['original'],
        validator_backends=['ibm_fez', 'ibm_torino', 'ibm_marrakesh']
    )

    # If consensus achieved, mine the block
    if consensus_result['consensus']:
        print(f"\n✅ CONSENSUS ACHIEVED!")
        print(f"\n⛏️  Mining block with quantum computer...")

        block = node.quantum_mine_block([transaction])

        print(f"\n🎉 QUANTUM BLOCKCHAIN BLOCK MINED!")
        print(f"   Block hash: {block['hash']}")
        print(f"   Quantum nonce: {block['nonce']}")
        print(f"   Mining backend: {block['quantum_backend']}")
        print(f"   Job ID: {block['job_id']}")

        # Show consensus details
        print(f"\n📊 Distributed Quantum Consensus:")
        print(f"   Total validators: {consensus_result['total_validators']}")
        print(f"   Valid confirmations: {consensus_result['valid_count']}/{consensus_result['total_validators']}")
        print(f"\n   Validator Results:")
        for validation in consensus_result['validations']:
            status = '✅ VALID' if validation.get('valid', False) else '❌ INVALID'
            backend = validation['backend'].upper()
            job_id = validation.get('job_id', 'N/A')
            print(f"   • {backend}: {status} (Job: {job_id})")

        print(f"\n🌟 SUCCESS! Transaction validated and mined across quantum network!")
        return block
    else:
        print(f"\n❌ CONSENSUS FAILED")
        print(f"   Valid: {consensus_result['valid_count']}/{consensus_result['total_validators']}")
        print(f"   Need 2/3 majority for consensus")
        return None

if __name__ == "__main__":
    main()
