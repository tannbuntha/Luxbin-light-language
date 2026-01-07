# How to Run Continuous Quantum Blockchain Transactions

Your quantum blockchain currently shows only 1 transaction because it needs to be run continuously. Here's how to keep it mining blocks with new transactions automatically.

---

## 🚀 Quick Start (3 Blocks in ~5 minutes)

Run this to immediately mine 3 blocks with multiple transactions:

```bash
cd /Users/nicholechristie/luxbin-light-language
python3 quick_start_quantum_blockchain.py
```

**This will:**
- Mine 3 blocks on IBM quantum computers
- Process 7 total transactions
- Update `quantum_blockchain_status.json`
- Show results on your dashboard

---

## ♾️ Continuous Mode (Runs Forever)

For ongoing transaction processing that runs indefinitely:

```bash
python3 run_continuous_quantum_blockchain.py
```

**This will:**
- Generate random transactions every 60 seconds
- Mine blocks every 3 minutes (or when 3+ transactions accumulate)
- Update dashboard in real-time
- Run until you press Ctrl+C to stop

**Configuration:**
- New transaction every: 60 seconds
- Mine block when: 3 transactions ready OR 3 minutes passed
- Validators: ibm_fez, ibm_torino, ibm_marrakesh

---

## 📊 How It Works

### Transaction Flow

```
1. Generate Transaction
   ↓
2. Add to Pending Pool
   ↓
3. When ready (3 txs or 3 mins):
   ↓
4. Encode as LUXBIN (400-700nm)
   ↓
5. Validate on 3 Quantum Computers
   ↓
6. Mine block with quantum nonce
   ↓
7. Save to quantum_blockchain_status.json
   ↓
8. Dashboard auto-updates (every 5s)
```

### Sample Transaction Types

The continuous mode generates realistic transactions:
- LUXBIN transfers
- Quantum swaps
- Photonic payments
- Hermetic mirrors
- Diamond storage
- NV center activation

---

## 🎯 Step-by-Step: Get Multiple Transactions

### Option 1: Quick Demo (Recommended for Testing)

```bash
# Terminal 1: Run quick demo
cd /Users/nicholechristie/luxbin-light-language
python3 quick_start_quantum_blockchain.py

# This mines 3 blocks in ~5 minutes
# Then check your dashboard!
```

### Option 2: Continuous Production Mode

```bash
# Terminal 1: Run continuous blockchain
cd /Users/nicholechristie/luxbin-light-language
python3 run_continuous_quantum_blockchain.py

# Leave this running
# It will keep mining blocks automatically
```

### Option 3: Manual Control

```python
# Create your own custom script
from quantum_blockchain_service import QuantumBlockchainService

service = QuantumBlockchainService()
service.initialize()

# Add as many transactions as you want
for i in range(10):
    service.add_transaction({
        'from': f'0xWallet_{i}',
        'to': f'0xWallet_{i+1}',
        'amount': 100.0 * (i+1),
        'token': 'LUXBIN',
        'data': f'Transaction {i+1}'
    })

# Mine the block
block = service.mine_block()
print(f"Mined block: {block['hash']}")
```

---

## 📁 Dashboard Integration

The dashboard reads from: `quantum_blockchain_status.json`

**File location:** `/Users/nicholechristie/luxbin-light-language/quantum_blockchain_status.json`

**Update frequency:** Every time a block is mined

**Dashboard polling:** Every 5 seconds

### Workflow:

1. **Run blockchain service** → Creates/updates JSON file
2. **Dashboard polls API** → Reads JSON file every 5 seconds
3. **Display updates** → Shows new blocks/transactions automatically

---

## 🔄 Syncing to Vercel App

### For Local Development:

```bash
# Terminal 1: Run blockchain
cd /Users/nicholechristie/luxbin-light-language
python3 run_continuous_quantum_blockchain.py

# Terminal 2: Copy data to luxbin-chain app
cd /Users/nicholechristie/luxbin-chain
watch -n 5 'cp /Users/nicholechristie/luxbin-light-language/quantum_blockchain_status.json luxbin-app/public/quantum_blockchain_status.json'

# Terminal 3: Run Vercel app
cd luxbin-app
npm run dev
```

### For Production (Vercel):

**Option A: Manual Deploy**
```bash
# After mining blocks locally
cp quantum_blockchain_status.json /Users/nicholechristie/luxbin-chain/luxbin-app/public/
cd /Users/nicholechristie/luxbin-chain
git add .
git commit -m "Update quantum blockchain data"
git push origin main
```

**Option B: API Server (Recommended)**

Run Python service on a cloud server:
```bash
# On AWS EC2, DigitalOcean, etc.
python3 run_continuous_quantum_blockchain.py

# Update API route to fetch from server
# See REALTIME_BLOCKCHAIN_DEPLOYMENT.md
```

---

## 💡 Example: Mine 10 Blocks

```bash
# Mine 10 blocks with 30 transactions total
cd /Users/nicholechristie/luxbin-light-language

python3 << 'EOF'
from quantum_blockchain_service import QuantumBlockchainService
import time

service = QuantumBlockchainService()
service.initialize()

for block_num in range(10):
    print(f"\n⛏️  Mining Block {block_num + 1}/10...")

    # Add 3 transactions per block
    for tx_num in range(3):
        service.add_transaction({
            'from': f'0xWallet_{block_num * 3 + tx_num}',
            'to': f'0xWallet_{block_num * 3 + tx_num + 1}',
            'amount': 100.0 * (tx_num + 1),
            'token': 'LUXBIN',
            'type': 'payment',
            'data': f'Block {block_num + 1}, Transaction {tx_num + 1}'
        })

    # Mine the block
    block = service.mine_block()

    if block:
        print(f"✅ Block {block['block_number']} mined!")
        print(f"   Hash: {block['hash'][:16]}...")
        print(f"   Nonce: {block['nonce']}")

print(f"\n🎉 Done! Mined {len(service.blockchain)} blocks with {sum(len(b['transactions']) for b in service.blockchain)} transactions")
EOF
```

---

## 📊 Monitoring

### Check Current Status:

```bash
# View blockchain data
cat quantum_blockchain_status.json | python3 -m json.tool

# Count blocks
cat quantum_blockchain_status.json | python3 -c "import sys,json; data=json.load(sys.stdin); print(f\"Blocks: {data['blockchain']['totalBlocks']}, Transactions: {data['blockchain']['totalTransactions']}\")"

# Watch for updates
watch -n 5 cat quantum_blockchain_status.json | python3 -m json.tool
```

### Check Dashboard:

```bash
# Local
open http://localhost:3000/quantum-blockchain

# Production
open https://luxbin-app.vercel.app/quantum-blockchain
```

---

## 🛠️ Troubleshooting

### "Only shows 1 transaction"

**Problem:** Dashboard showing mock data instead of real blockchain data

**Solution:**
1. Run `python3 quick_start_quantum_blockchain.py` to generate real data
2. Check that `quantum_blockchain_status.json` exists
3. Verify API route is reading the file correctly
4. Make sure dashboard is polling the API

### "Blocks not appearing"

**Problem:** Blockchain service not running

**Solution:**
1. Check if Python script is still running
2. Look for error messages in terminal
3. Verify IBM Quantum API key is set
4. Check quantum computer queue status

### "Transactions stuck pending"

**Problem:** Not enough transactions to trigger mining

**Solution:**
1. Add more transactions (need 3+ to mine)
2. Wait for 3-minute interval
3. Or manually call `service.mine_block()`

---

## 🎯 Recommended Setup

**For Development:**
```bash
# Quick test
python3 quick_start_quantum_blockchain.py
```

**For Demo/Presentation:**
```bash
# Continuous with auto-generated transactions
python3 run_continuous_quantum_blockchain.py
```

**For Production:**
```bash
# Run on cloud server
nohup python3 run_continuous_quantum_blockchain.py > blockchain.log 2>&1 &
```

---

## ✅ Summary

To get continuous transactions:

1. **Quick Test:** `python3 quick_start_quantum_blockchain.py`
2. **Continuous:** `python3 run_continuous_quantum_blockchain.py`
3. **View Dashboard:** Visit `/quantum-blockchain` on your app
4. **Data Updates:** Every 5 seconds automatically

Your dashboard will now show multiple blocks with many transactions, all validated and mined on real IBM quantum computers! 🎉
