# LUXBIN on macOS Setup Guide

## Quick Install (macOS)

```bash
# Clone repository
git clone https://github.com/mermaidnicheboutique-code/Luxbin-light-language.git
cd Luxbin-light-language

# Install dependencies (macOS compatible)
pip install -r requirements.txt

# Run on IBM Quantum (works on macOS!)
python luxbin_quantum_computer.py
```

## What Works on macOS ✅

1. **IBM Quantum** - Full support
   ```bash
   python luxbin_quantum_computer.py
   ```

2. **Web App** - Full support
   ```bash
   cd luxbin-app
   npm install
   npm run dev
   ```

3. **Quantum Simulator** - Full GPU support
   ```bash
   python luxbin_quantum_computer.py
   # Choose simulator option (no IBM account needed)
   ```

4. **All visualizations and tools**

## What Requires Linux/Google Colab ⚠️

1. **Origin Quantum** (Chinese quantum computers)
   - PyQPanda doesn't support macOS
   - **Solution**: Use Google Colab (free!)

2. **Some advanced GPU features**
   - CUDA requires NVIDIA GPU (Macs use Apple Silicon/AMD)
   - **Solution**: Metal Performance Shaders or Colab

## workaround: Use Google Colab for Origin Quantum

Since Origin Quantum doesn't work on macOS, use Colab:

### Step 1: Open Colab
Go to: https://colab.research.google.com/

### Step 2: Create New Notebook

### Step 3: Run This Code
```python
# Install Origin Quantum on Linux (Colab is Linux-based)
!pip install pyqpanda

# Clone LUXBIN
!git clone https://github.com/mermaidnicheboutique-code/Luxbin-light-language.git
%cd Luxbin-light-language

# Run Origin Quantum script
!python luxbin_origin_quantum.py
```

### Step 4: Test Chinese Quantum Computer
```python
# You'll be prompted for:
# 1. Text to translate
# 2. Origin Quantum API token (from https://qcloud.originqc.com.cn/en/)
# 3. It runs on Chinese quantum hardware!
```

## macOS-Specific Features

### Apple Silicon (M1/M2/M3) Optimization

```bash
# Install with Apple Silicon optimizations
pip install --upgrade pip
pip install numpy matplotlib qiskit qiskit-aer qiskit-ibm-runtime

# Verify installation
python -c "import qiskit; print(qiskit.__version__)"
```

### Using Metal Performance Shaders

```python
# macOS uses Metal instead of CUDA for GPU acceleration
# Qiskit-Aer automatically uses Metal on macOS

from qiskit_aer import AerSimulator

# This will use Metal GPU acceleration on M1/M2/M3 Macs
simulator = AerSimulator(method='statevector', device='GPU')
```

## Complete macOS Workflow

### For IBM Quantum (works perfectly on macOS)

```bash
# 1. Install
pip install qiskit qiskit-ibm-runtime qiskit-aer numpy matplotlib

# 2. Run
python luxbin_quantum_computer.py

# 3. When prompted:
# - Enter text: "Hello World"
# - Choose IBM Quantum backend or simulator
# - If choosing real quantum computer, paste IBM API token
# - Get results from real quantum hardware!
```

### For Origin Quantum (use Colab)

```bash
# Can't run locally on macOS, but Colab is just as good:
# 1. Open https://colab.research.google.com/
# 2. Paste the install code above
# 3. Run on Chinese quantum computers from your Mac!
```

## Testing LUXBIN Features on macOS

### Test 1: Quantum Simulator (Local)
```bash
python luxbin_quantum_computer.py
# Choose option 3: Local Simulator
# Runs instantly on your Mac!
```

### Test 2: IBM Quantum (Real Hardware)
```bash
python luxbin_quantum_computer.py
# Choose option 1 or 2: IBM backend
# Sign up: https://quantum.ibm.com/
# Paste API token
# Runs on real quantum computer in USA!
```

### Test 3: Web App (Local Development)
```bash
cd luxbin-app
npm install
npm run dev
# Open http://localhost:3000
# Full LUXBIN visualizer in your browser!
```

### Test 4: Quantum Network (IBM only)
```bash
python luxbin_quantum_network.py
# Connects to IBM Quantum only on macOS
# For full network including Origin, use Colab
```

## Platform Compatibility Matrix

| Feature | macOS | Windows | Linux | Colab |
|---------|-------|---------|-------|-------|
| IBM Quantum | ✅ | ✅ | ✅ | ✅ |
| Origin Quantum | ❌ | ✅ | ✅ | ✅ |
| Qiskit | ✅ | ✅ | ✅ | ✅ |
| PyQPanda | ❌ | ✅ | ✅ | ✅ |
| Web App | ✅ | ✅ | ✅ | ✅ |
| GPU Sim (Metal) | ✅ | ✅* | ✅ | ✅ |
| Quantum Network | ✅* | ✅ | ✅ | ✅ |

*Limited features on macOS, full features on Linux/Colab

## Recommended Setup for macOS Users

**Best Setup:**
1. **Local (macOS)**: Web app + IBM Quantum + Simulation
2. **Colab (Free)**: Origin Quantum + Full quantum network

This gives you access to EVERYTHING while using macOS!

## Troubleshooting

### Error: "No module named 'pyqpanda'"
**Solution**: PyQPanda doesn't support macOS. Use Google Colab or remove Origin Quantum features.

```bash
# Just use IBM Quantum instead:
python luxbin_quantum_computer.py  # Works on macOS!
```

### Error: "GPU not available"
**Solution**: macOS uses Metal, not CUDA. Qiskit-Aer will automatically use Metal on M1/M2/M3.

```python
# Check GPU availability:
from qiskit_aer import AerSimulator
simulator = AerSimulator(method='statevector', device='GPU')
print("GPU available!" if simulator.available_devices() else "Using CPU")
```

### Error: "Could not find a version that satisfies..."
**Solution**: Make sure you're using Python 3.9-3.12

```bash
# Check Python version:
python --version  # Should be 3.9, 3.10, 3.11, or 3.12

# If not, install correct version:
brew install python@3.11
```

## Summary for macOS Users

✅ **You CAN use:**
- IBM Quantum (real quantum computers in USA)
- All quantum simulators
- Full web app
- All LUXBIN encoding/decoding
- Quantum network (IBM portion)
- GPU acceleration (via Metal)

❌ **You NEED Colab for:**
- Origin Quantum (Chinese quantum computers)
- Full quantum network (all computers)
- PyQPanda-specific features

**Bottom line:** macOS works great for 90% of LUXBIN features. Use free Google Colab for the Chinese quantum computer access!

## Quick Start (macOS)

```bash
# Terminal:
git clone https://github.com/mermaidnicheboutique-code/Luxbin-light-language.git
cd Luxbin-light-language
pip install -r requirements.txt
python luxbin_quantum_computer.py
```

**Done!** You're running LUXBIN on your Mac! 🍎💎✨
