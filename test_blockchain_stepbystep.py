"""
Step-by-Step LUXBIN Chain Quantum Blockchain Test
Tests each quantum computer individually, then runs distributed consensus
"""

from luxbin_chain_quantum_node import QuantumBlockchainNode
import json
import time

def test_individual_computer(backend_name, transaction):
    """Test blockchain on a single quantum computer"""
    print(f"\n{'='*70}")
    print(f"🔬 TESTING: {backend_name.upper()}")
    print(f"{'='*70}")

    try:
        # Initialize node
        node = QuantumBlockchainNode(backend_name)

        # Encode transaction
        print(f"\n📝 Encoding transaction...")
        encoded = node.encode_transaction_luxbin(transaction)
        print(f"✅ LUXBIN: {encoded['luxbin'][:50]}...")
        print(f"✅ Wavelengths: {len(encoded['wavelengths'])}")

        # Validate
        print(f"\n⚛️  Running quantum validation...")
        validation = node.quantum_validate_transaction(encoded)

        if validation['valid']:
            print(f"\n✅ {backend_name.upper()} VALIDATION: PASSED")
            print(f"   Job ID: {validation['job_id']}")
            print(f"   State balance: {validation['balance']:.1%}")
        else:
            print(f"\n❌ {backend_name.upper()} VALIDATION: FAILED")

        return {
            'backend': backend_name,
            'success': validation['valid'],
            'job_id': validation['job_id'],
            'validation': validation
        }

    except Exception as e:
        print(f"\n❌ ERROR on {backend_name}: {e}")
        return {
            'backend': backend_name,
            'success': False,
            'error': str(e)
        }

def main():
    print("="*70)
    print("🔗 LUXBIN CHAIN QUANTUM BLOCKCHAIN - STEP BY STEP TEST")
    print("="*70)
    print("\nPhase 1: Test each quantum computer individually")
    print("Phase 2: Run distributed quantum consensus")
    print("="*70)

    # Create transaction
    transaction = {
        'from': '0xAlice123...',
        'to': '0xBob456...',
        'amount': 250.75,
        'token': 'LUXBIN',
        'data': 'Testing distributed quantum blockchain!'
    }

    print(f"\n📝 Transaction:")
    print(f"   From: {transaction['from']}")
    print(f"   To: {transaction['to']}")
    print(f"   Amount: {transaction['amount']} {transaction['token']}")

    # Phase 1: Individual tests
    print(f"\n{'='*70}")
    print(f"🎯 PHASE 1: INDIVIDUAL QUANTUM COMPUTER TESTS")
    print(f"{'='*70}")

    backends = ['ibm_fez', 'ibm_torino', 'ibm_marrakesh']
    results = []

    for backend in backends:
        result = test_individual_computer(backend, transaction)
        results.append(result)
        time.sleep(2)  # Brief pause between tests

    # Summary of individual tests
    print(f"\n{'='*70}")
    print(f"📊 PHASE 1 SUMMARY")
    print(f"{'='*70}")

    successful = [r for r in results if r['success']]
    print(f"\n✅ Successful: {len(successful)}/{len(backends)}")

    for result in results:
        status = '✅' if result['success'] else '❌'
        backend = result['backend'].upper()
        job_id = result.get('job_id', 'N/A')
        print(f"   {status} {backend}: Job {job_id}")

    # Phase 2: Distributed consensus (only if at least 2 passed)
    if len(successful) >= 2:
        print(f"\n{'='*70}")
        print(f"🌐 PHASE 2: DISTRIBUTED QUANTUM CONSENSUS")
        print(f"{'='*70}")
        print(f"\nRunning consensus across {len(backends)} quantum computers...")

        # Use primary node for consensus
        node = QuantumBlockchainNode('ibm_fez')

        print(f"\n⚛️  Running quantum consensus protocol...")
        consensus_result = node.quantum_consensus(
            transaction,
            validator_backends=backends
        )

        if consensus_result['consensus']:
            print(f"\n✅ CONSENSUS ACHIEVED!")
            print(f"   Valid: {consensus_result['valid_count']}/{consensus_result['total_validators']}")

            # Mine block
            print(f"\n⛏️  Mining block with quantum nonce...")
            block = node.quantum_mine_block([transaction])

            print(f"\n🎉 QUANTUM BLOCKCHAIN BLOCK MINED!")
            print(f"   Hash: {block['hash']}")
            print(f"   Nonce: {block['nonce']}")
            print(f"   Backend: {block['quantum_backend']}")

            # Final summary
            print(f"\n{'='*70}")
            print(f"🌟 COMPLETE SUCCESS!")
            print(f"{'='*70}")
            print(f"\n✅ Phase 1: All quantum computers tested individually")
            print(f"✅ Phase 2: Distributed consensus achieved")
            print(f"✅ Phase 3: Block mined with quantum nonce")
            print(f"\n🔗 Your LUXBIN Chain is now running on quantum computers!")

        else:
            print(f"\n❌ CONSENSUS FAILED")
            print(f"   Valid: {consensus_result['valid_count']}/{consensus_result['total_validators']}")
    else:
        print(f"\n⚠️  Insufficient quantum computers passed Phase 1")
        print(f"   Need at least 2 for distributed consensus")

if __name__ == "__main__":
    main()
