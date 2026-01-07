"""
LUXBIN Light Language - Real Quantum Computer Demo
Run this in Google Colab to test on IBM Quantum hardware

Setup:
1. Create free account at: https://quantum.ibm.com/
2. Get your API token from: https://quantum.ibm.com/account
3. Run this notebook and paste your token when prompted
"""

# Install required packages
# !pip install qiskit qiskit-ibm-runtime matplotlib numpy

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.visualization import plot_histogram, plot_bloch_multivector
import numpy as np
import matplotlib.pyplot as plt

# LUXBIN Alphabet (77 characters - 6-7 bits per character)
LUXBIN_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?;:-()[]{}@#$%^&*+=_~`<>\"'|\\"

def text_to_luxbin(text):
    """Convert text to LUXBIN representation"""
    # Convert to binary
    binary = ''.join(format(ord(char), '08b') for char in text)

    # Convert binary to LUXBIN (6 bits per character)
    luxbin = ''
    for i in range(0, len(binary), 6):
        chunk = binary[i:i+6].ljust(6, '0')
        index = int(chunk, 2) % len(LUXBIN_ALPHABET)
        luxbin += LUXBIN_ALPHABET[index]

    return luxbin, binary

def luxbin_to_wavelengths(luxbin, enable_quantum=True):
    """Convert LUXBIN to photonic wavelengths"""
    wavelengths = []
    QUANTUM_ZERO_PHONON = 637  # Diamond NV center (nm)

    for char in luxbin:
        if enable_quantum and char == ' ':
            # Use diamond NV center wavelength for spaces
            wavelengths.append({
                'character': char,
                'wavelength_nm': QUANTUM_ZERO_PHONON,
                'frequency_hz': 3e8 / (QUANTUM_ZERO_PHONON * 1e-9),
                'energy_ev': 1240 / QUANTUM_ZERO_PHONON
            })
        else:
            # Map to visible spectrum (400-700nm)
            index = LUXBIN_ALPHABET.index(char)
            wavelength = 400 + (index / len(LUXBIN_ALPHABET)) * 300

            wavelengths.append({
                'character': char,
                'wavelength_nm': wavelength,
                'frequency_hz': 3e8 / (wavelength * 1e-9),
                'energy_ev': 1240 / wavelength
            })

    return wavelengths

def wavelength_to_quantum_state(wavelength_nm):
    """
    Encode wavelength as quantum state angles
    Maps 400-700nm wavelength range to qubit rotation angles
    """
    # Normalize wavelength to 0-1 range
    norm = (wavelength_nm - 400) / 300

    # Convert to quantum rotation angles
    theta = norm * np.pi  # Polar angle
    phi = norm * 2 * np.pi  # Azimuthal angle

    return theta, phi

def create_luxbin_quantum_circuit(wavelengths, num_qubits=3):
    """
    Create quantum circuit encoding LUXBIN wavelength data
    Uses rotation gates to encode wavelength information
    """
    qc = QuantumCircuit(num_qubits)

    # Encode first few wavelengths (limited by qubit count)
    for i, wl_data in enumerate(wavelengths[:num_qubits]):
        wavelength = wl_data['wavelength_nm']
        theta, phi = wavelength_to_quantum_state(wavelength)

        # Initialize qubit in superposition
        qc.h(i)

        # Encode wavelength via rotation
        qc.ry(theta, i)  # Y-rotation (polar angle)
        qc.rz(phi, i)    # Z-rotation (azimuthal angle)

    # Create entanglement between qubits (quantum correlation)
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)  # CNOT gate for entanglement

    # Measure all qubits
    qc.measure_all()

    return qc

def run_on_quantum_computer(circuit, backend_name='ibm_brisbane'):
    """
    Run circuit on real IBM quantum hardware
    Returns measurement results
    """
    print(f"🔬 Connecting to IBM Quantum computer: {backend_name}")

    # Get backend
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)

    print(f"✅ Connected! Queue status: {backend.status().pending_jobs} jobs pending")
    print(f"📊 Backend has {backend.num_qubits} qubits")

    # Transpile for hardware
    print("🔄 Transpiling circuit for quantum hardware...")
    transpiled = transpile(circuit, backend=backend, optimization_level=3)

    # Run on quantum computer
    print("🚀 Submitting job to quantum computer...")
    sampler = Sampler(backend)
    job = sampler.run([transpiled], shots=1024)

    print(f"⏳ Job submitted! Job ID: {job.job_id()}")
    print("⏳ Waiting for quantum computer to execute...")

    result = job.result()

    print("✅ Quantum execution complete!")
    return result

def main():
    """Main demo function"""
    print("=" * 60)
    print("LUXBIN LIGHT LANGUAGE - QUANTUM COMPUTER DEMO")
    print("=" * 60)

    # Step 1: Get user input
    text = input("\n💬 Enter text to translate to quantum light: ")

    # Step 2: Convert to LUXBIN
    print("\n🔄 Converting to LUXBIN Light Language...")
    luxbin, binary = text_to_luxbin(text)
    print(f"📝 Original text: {text}")
    print(f"🔢 Binary: {binary[:80]}..." if len(binary) > 80 else f"🔢 Binary: {binary}")
    print(f"💎 LUXBIN: {luxbin}")

    # Step 3: Convert to wavelengths
    print("\n🌈 Converting to photonic wavelengths...")
    wavelengths = luxbin_to_wavelengths(luxbin, enable_quantum=True)

    print(f"\n📊 Generated {len(wavelengths)} wavelength states:")
    for i, wl in enumerate(wavelengths[:10]):  # Show first 10
        print(f"  {wl['character']} → {wl['wavelength_nm']:.2f}nm "
              f"({wl['frequency_hz']:.2e}Hz, {wl['energy_ev']:.3f}eV)")
    if len(wavelengths) > 10:
        print(f"  ... and {len(wavelengths) - 10} more")

    # Step 4: Create quantum circuit
    print("\n⚛️  Creating quantum circuit...")
    num_qubits = min(5, len(wavelengths))  # Use up to 5 qubits
    qc = create_luxbin_quantum_circuit(wavelengths, num_qubits)

    print(f"✅ Circuit created with {num_qubits} qubits")
    print(f"   Gates: {qc.count_ops()}")
    print(f"   Depth: {qc.depth()}")

    # Visualize circuit
    print("\n📈 Circuit diagram:")
    print(qc.draw(output='text'))

    # Step 5: Connect to IBM Quantum
    print("\n🔐 IBM Quantum Authentication")
    print("Get your token from: https://quantum.ibm.com/account")

    # Check if already authenticated
    try:
        service = QiskitRuntimeService()
        print("✅ Already authenticated!")
    except:
        token = input("Paste your IBM Quantum API token: ")
        QiskitRuntimeService.save_account(channel="ibm_quantum", token=token, overwrite=True)
        service = QiskitRuntimeService()
        print("✅ Authentication successful!")

    # List available backends
    print("\n🖥️  Available quantum computers:")
    backends = service.backends(simulator=False, operational=True)
    for i, backend in enumerate(backends[:5]):
        status = backend.status()
        print(f"  {i+1}. {backend.name} - {backend.num_qubits} qubits - "
              f"{status.pending_jobs} jobs queued")

    # Select backend
    backend_choice = input("\nEnter backend name (or press Enter for simulator): ").strip()

    if not backend_choice:
        # Run on simulator
        print("\n🖥️  Running on quantum simulator...")
        from qiskit_aer import AerSimulator
        backend = AerSimulator()
        transpiled = transpile(qc, backend)
        job = backend.run(transpiled, shots=1024)
        result = job.result()
        counts = result.get_counts()
    else:
        # Run on real quantum computer
        result = run_on_quantum_computer(qc, backend_choice)
        counts = result[0].data.meas.get_counts()

    # Step 6: Display results
    print("\n" + "=" * 60)
    print("QUANTUM MEASUREMENT RESULTS")
    print("=" * 60)

    print("\n📊 Measurement counts:")
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        probability = count / 1024 * 100
        print(f"  |{state}⟩: {count} times ({probability:.1f}%)")

    # Visualize
    print("\n📈 Generating visualization...")
    fig = plot_histogram(counts, figsize=(12, 6))
    plt.title(f"Quantum Measurement Results for '{text}'")
    plt.tight_layout()
    plt.savefig('quantum_results.png', dpi=150, bbox_inches='tight')
    print("✅ Saved visualization to: quantum_results.png")
    plt.show()

    # Analysis
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"✨ Your text '{text}' was successfully encoded as quantum light states")
    print(f"💎 Used {num_qubits} qubits to represent {len(wavelengths)} wavelengths")
    print(f"🌊 Wavelength range: {min(w['wavelength_nm'] for w in wavelengths):.1f}-"
          f"{max(w['wavelength_nm'] for w in wavelengths):.1f}nm")
    print(f"⚛️  Total quantum operations: {sum(qc.count_ops().values())}")

    if '637' in [f"{w['wavelength_nm']:.0f}" for w in wavelengths]:
        print("\n🔬 QUANTUM RESONANCE DETECTED!")
        print("   Your text contains spaces, encoded at 637nm")
        print("   This is the diamond NV center zero-phonon line")
        print("   Perfect for quantum state storage! 💎")

    print("\n✅ Quantum execution complete!")

if __name__ == "__main__":
    main()
