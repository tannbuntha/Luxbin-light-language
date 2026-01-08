/**
 * LUXBIN Browser Extension - Popup UI
 */

// UI Elements
const gatewayIndicator = document.getElementById('gateway-indicator');
const gatewayStatus = document.getElementById('gateway-status');
const nodeStatus = document.getElementById('node-status');
const peerCount = document.getElementById('peer-count');
const nodeId = document.getElementById('node-id');
const backendList = document.getElementById('backend-list');
const messageArea = document.getElementById('message-area');

const navigateBtn = document.getElementById('navigate-btn');
const luxbinAddressInput = document.getElementById('luxbin-address');

const registerBtn = document.getElementById('register-btn');
const registerNameInput = document.getElementById('register-name');
const registerAddressInput = document.getElementById('register-address');

/**
 * Update UI with status
 */
function updateStatus(status) {
  if (status.gatewayConnected) {
    gatewayIndicator.classList.add('connected');
    gatewayStatus.textContent = 'Online';

    const nodeData = status.quantumNodeStatus;

    if (nodeData.connected) {
      nodeStatus.textContent = 'Connected';
      peerCount.textContent = nodeData.peers || 0;
      nodeId.textContent = nodeData.node_id ? nodeData.node_id.substring(0, 16) + '...' : '—';

      // Update quantum backends
      if (nodeData.quantumBackends && nodeData.quantumBackends.length > 0) {
        backendList.innerHTML = nodeData.quantumBackends
          .map(backend => `<span class="backend-chip">${backend}</span>`)
          .join('');
      }
    } else {
      nodeStatus.textContent = 'Initializing...';
    }
  } else {
    gatewayIndicator.classList.remove('connected');
    gatewayStatus.textContent = 'Offline';
    nodeStatus.textContent = 'Offline';
    peerCount.textContent = '0';
    nodeId.textContent = '—';
    backendList.innerHTML = '<span class="backend-chip">Gateway not running</span>';

    showError('Gateway not running. Start with: python3 luxbin_gateway_service.py');
  }
}

/**
 * Show error message
 */
function showError(message) {
  messageArea.innerHTML = `<div class="error-message">❌ ${message}</div>`;
  setTimeout(() => {
    messageArea.innerHTML = '';
  }, 5000);
}

/**
 * Show success message
 */
function showSuccess(message) {
  messageArea.innerHTML = `<div class="success-message">✅ ${message}</div>`;
  setTimeout(() => {
    messageArea.innerHTML = '';
  }, 3000);
}

/**
 * Navigate to LUXBIN address
 */
navigateBtn.addEventListener('click', async () => {
  const address = luxbinAddressInput.value.trim();

  if (!address) {
    showError('Please enter a LUXBIN address or name');
    return;
  }

  // Add protocol if not present
  let fullAddress = address;
  if (!address.startsWith('luxbin://')) {
    // Assume it's a name, resolve it
    fullAddress = `luxbin://${address}`;
  }

  try {
    // Open in new tab
    chrome.tabs.create({ url: fullAddress });
    showSuccess('Opening ' + address);
  } catch (error) {
    showError('Failed to navigate: ' + error.message);
  }
});

/**
 * Register name on blockchain
 */
registerBtn.addEventListener('click', async () => {
  const name = registerNameInput.value.trim();
  const address = registerAddressInput.value.trim();

  if (!name || !address) {
    showError('Please enter both name and address');
    return;
  }

  registerBtn.disabled = true;
  registerBtn.textContent = 'Registering...';

  try {
    // Send message to background script
    const response = await chrome.runtime.sendMessage({
      type: 'REGISTER_NAME',
      name: name,
      address: address,
      owner: 'extension_user' // In production, use actual keypair
    });

    if (response.success) {
      showSuccess(`Name "${name}" registered successfully!`);
      registerNameInput.value = '';
      registerAddressInput.value = '';
    } else {
      showError('Registration failed: ' + response.error);
    }
  } catch (error) {
    showError('Registration error: ' + error.message);
  } finally {
    registerBtn.disabled = false;
    registerBtn.textContent = 'Register on Blockchain';
  }
});

/**
 * Load status on popup open
 */
async function loadStatus() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_STATUS' });
    updateStatus(response);
  } catch (error) {
    console.error('Failed to load status:', error);
    showError('Failed to load gateway status');
  }
}

/**
 * Refresh status
 */
async function refreshStatus() {
  try {
    await chrome.runtime.sendMessage({ type: 'CHECK_GATEWAY' });
    await loadStatus();
  } catch (error) {
    console.error('Failed to refresh status:', error);
  }
}

// Initialize
loadStatus();

// Refresh every 5 seconds
setInterval(loadStatus, 5000);

console.log('✅ LUXBIN Popup loaded');
