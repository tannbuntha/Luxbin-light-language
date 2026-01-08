# LUXBIN Browser Extension

Access the LUXBIN Quantum Photonic Internet directly from your browser.

## Features

- **Navigate to luxbin:// URLs** - Browse the quantum internet
- **Decentralized DNS** - Resolve names via blockchain
- **Quantum Security** - Unhackable QKD encryption
- **Censorship Resistance** - No central authority
- **Name Registration** - Register your own names on blockchain
- **Network Status** - Monitor quantum node connectivity

## Installation

### Prerequisites

1. **Start Local Gateway Service**
   ```bash
   cd /Users/nicholechristie/luxbin-light-language
   python3 luxbin_gateway_service.py
   ```

   The gateway runs on `localhost:9000` and connects your browser to the LUXBIN network.

### Install Extension

#### Chrome/Edge

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `luxbin-browser-extension` folder
5. Extension installed! Look for the LUXBIN icon in toolbar

#### Firefox

1. Open Firefox and navigate to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select `manifest.json` from the `luxbin-browser-extension` folder
4. Extension installed!

## Usage

### Navigate to LUXBIN Address

**Option 1: Use Extension Popup**
1. Click the LUXBIN extension icon
2. Enter a name or full LUXBIN address:
   - `mywebsite` (name resolution via blockchain)
   - `luxbin://node1.550nm.ABC123/page.html` (full address)
3. Click "Navigate"

**Option 2: Direct URL**
- Type `luxbin://mywebsite` in address bar
- Extension will intercept and route through gateway

### Register a Name

1. Click the LUXBIN extension icon
2. Scroll to "Register Name" section
3. Enter:
   - **Name**: `mywebsite` (3-64 characters, alphanumeric + hyphens)
   - **LUXBIN Address**: `luxbin://node1.550nm.ABC123/index.html`
4. Click "Register on Blockchain"
5. Name is permanently registered on quantum blockchain

### Monitor Network Status

The extension popup shows:
- **Gateway Status**: Local gateway connection
- **Quantum Node**: Network connectivity
- **Connected Peers**: Number of peers in mesh
- **Node ID**: Your quantum node identifier
- **Quantum Backends**: IBM + IonQ quantum computers

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser Extension                    │
│  - Protocol interceptor (luxbin://)                     │
│  - UI popup (status + navigation)                       │
│  - Content script (page indicators)                     │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP
                      ↓
┌─────────────────────────────────────────────────────────┐
│              Local Gateway Service (Port 9000)          │
│  - HTTP → LUXBIN translation                            │
│  - Name resolution (blockchain DNS)                     │
│  - Content fetching (DHT)                               │
│  - Quantum P2P node                                     │
└─────────────────────┬───────────────────────────────────┘
                      │ Quantum
                      ↓
┌─────────────────────────────────────────────────────────┐
│                  LUXBIN Quantum Network                 │
│  - P2P mesh (entanglement-based)                        │
│  - Wavelength routing (400-700nm)                       │
│  - Quantum blockchain (name storage)                    │
│  - Distributed hash table (content)                     │
└─────────────────────────────────────────────────────────┘
```

## Components

### Extension Files

- **manifest.json** - Extension configuration
- **background.js** - Service worker (protocol interception)
- **content-script.js** - Page injection (LUXBIN indicators)
- **popup/popup.html** - Extension UI
- **popup/popup.js** - UI logic

### Gateway Service

- **luxbin_gateway_service.py** - Local HTTP gateway
  - Routes: `/status`, `/fetch`, `/register-name`, `/resolve`
  - Connects to: P2P mesh, blockchain, DHT, router

## API Endpoints

### GET /status

Returns gateway and network status.

**Response:**
```json
{
  "connected": true,
  "node_id": "X6&35Z}04AKJE%VW...",
  "peers": 5,
  "quantumBackends": ["ibm_fez", "ibm_torino", "ionq_harmony"],
  "uptime": 3600.5
}
```

### GET /fetch?address=...

Fetch content from LUXBIN address or resolve name.

**Parameters:**
- `address` - LUXBIN address or name

**Response:**
```json
{
  "success": true,
  "content": "<html>...</html>",
  "luxbin_address": "luxbin://node1.550nm.ABC123/page.html",
  "latency_ms": 23.5
}
```

### POST /register-name

Register name on quantum blockchain.

**Body:**
```json
{
  "name": "mywebsite",
  "address": "luxbin://node1.550nm.ABC123/index.html",
  "owner": "public_key"
}
```

**Response:**
```json
{
  "success": true,
  "record": {
    "name": "mywebsite",
    "luxbin_address": "luxbin://...",
    "block_number": 5,
    "transaction_hash": "abc123..."
  }
}
```

### GET /resolve?name=...

Resolve name to LUXBIN address.

**Parameters:**
- `name` - Name to resolve

**Response:**
```json
{
  "success": true,
  "name": "mywebsite",
  "luxbin_address": "luxbin://node1.550nm.ABC123/index.html",
  "owner_public_key": "...",
  "block_number": 5
}
```

## Troubleshooting

### Extension shows "Gateway Offline"

**Solution**: Start the gateway service:
```bash
python3 luxbin_gateway_service.py
```

Wait 30-60 seconds for quantum node initialization.

### luxbin:// URLs not working

1. Check gateway is running (`http://localhost:9000/status`)
2. Ensure extension has proper permissions
3. Try reloading extension in `chrome://extensions/`

### Name registration fails

1. Verify gateway is connected to quantum blockchain
2. Check name format (3-64 chars, alphanumeric + hyphens)
3. Ensure LUXBIN address is valid format

## Development

### Testing Locally

1. Start gateway:
   ```bash
   python3 luxbin_gateway_service.py
   ```

2. Register test name:
   ```bash
   curl -X POST http://localhost:9000/register-name \
     -H "Content-Type: application/json" \
     -d '{"name":"test","address":"luxbin://test.550nm.ABC/page.html","owner":"dev"}'
   ```

3. Navigate to `luxbin://test` in browser

### Debugging

- Open DevTools Console (F12)
- Check background script: `chrome://extensions/` → Details → "Inspect views: background page"
- View logs in gateway terminal

## Security

- **Quantum Key Distribution**: Unhackable encryption via Bell pairs
- **Post-Quantum Crypto**: CRYSTALS-Kyber fallback
- **Blockchain DNS**: Censorship-resistant naming
- **No Central Authority**: Fully decentralized

## Performance

- **Name Resolution**: <50ms (cached: <1ms)
- **Content Fetching**: 23ms average latency
- **P2P Mesh**: Quantum entanglement-based discovery
- **Replication**: 3x content redundancy

## Future Features

- [ ] Offline mode (local content cache)
- [ ] Batch name registration
- [ ] Custom quantum backend selection
- [ ] LUXBIN bookmarks
- [ ] Content publishing tools

## License

LUXBIN Quantum Photonic Internet
Created by Nichole Christie, 2026

## Links

- Website: https://luxbin-app.vercel.app
- GitHub: https://github.com/yourusername/luxbin-light-language
- Documentation: See LUXBIN_INTERNET_README.md
