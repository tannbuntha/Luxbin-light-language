/**
 * LUXBIN Browser Extension - Background Service Worker
 *
 * Handles:
 * - luxbin:// protocol interception
 * - Routing to local gateway service
 * - Network status monitoring
 * - Quantum node connectivity
 */

const GATEWAY_URL = 'http://localhost:9000';

// Extension state
let gatewayConnected = false;
let quantumNodeStatus = {
  connected: false,
  peers: 0,
  quantumBackends: []
};

/**
 * Check if local gateway is running
 */
async function checkGateway() {
  try {
    const response = await fetch(`${GATEWAY_URL}/status`);
    const status = await response.json();

    gatewayConnected = true;
    quantumNodeStatus = status;

    console.log('✅ LUXBIN Gateway connected:', status);
    updateBadge('ON', '#00ff00');

    return true;
  } catch (error) {
    gatewayConnected = false;
    console.log('❌ LUXBIN Gateway not running');
    updateBadge('OFF', '#ff0000');

    return false;
  }
}

/**
 * Update extension badge
 */
function updateBadge(text, color) {
  chrome.action.setBadgeText({ text });
  chrome.action.setBadgeBackgroundColor({ color });
}

/**
 * Handle luxbin:// URL navigation
 */
chrome.webRequest.onBeforeRequest.addListener(
  async (details) => {
    const url = details.url;

    // Check if it's a luxbin:// URL (may be encoded)
    if (url.includes('luxbin://') || url.includes('luxbin%3A%2F%2F')) {
      console.log('🔗 Intercepted LUXBIN URL:', url);

      // Extract luxbin address
      let luxbinAddress = url;
      if (url.includes('luxbin%3A%2F%2F')) {
        luxbinAddress = decodeURIComponent(url.split('luxbin%3A%2F%2F')[1]);
        luxbinAddress = 'luxbin://' + luxbinAddress;
      }

      // Check gateway
      if (!gatewayConnected) {
        await checkGateway();
      }

      if (!gatewayConnected) {
        // Redirect to error page
        return {
          redirectUrl: chrome.runtime.getURL('popup/gateway-error.html')
        };
      }

      // Route through gateway
      const gatewayUrl = `${GATEWAY_URL}/fetch?address=${encodeURIComponent(luxbinAddress)}`;
      console.log('🚀 Routing to gateway:', gatewayUrl);

      return { redirectUrl: gatewayUrl };
    }
  },
  { urls: ["<all_urls>"] },
  ["blocking"]
);

/**
 * Handle messages from popup and content scripts
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('📨 Message received:', message);

  switch (message.type) {
    case 'GET_STATUS':
      sendResponse({
        gatewayConnected,
        quantumNodeStatus
      });
      break;

    case 'CHECK_GATEWAY':
      checkGateway().then(connected => {
        sendResponse({ connected });
      });
      return true; // Keep channel open for async response

    case 'FETCH_LUXBIN':
      fetchLuxbinAddress(message.address).then(response => {
        sendResponse(response);
      });
      return true;

    case 'REGISTER_NAME':
      registerName(message.name, message.address, message.owner).then(result => {
        sendResponse(result);
      });
      return true;

    default:
      sendResponse({ error: 'Unknown message type' });
  }
});

/**
 * Fetch content from LUXBIN address
 */
async function fetchLuxbinAddress(address) {
  try {
    const response = await fetch(`${GATEWAY_URL}/fetch?address=${encodeURIComponent(address)}`);
    const data = await response.json();

    return {
      success: true,
      content: data.content,
      metadata: data.metadata,
      luxbinAddress: data.luxbin_address
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Register name on blockchain
 */
async function registerName(name, address, owner) {
  try {
    const response = await fetch(`${GATEWAY_URL}/register-name`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, address, owner })
    });

    const result = await response.json();

    return {
      success: true,
      record: result.record
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Initialize extension
 */
async function initialize() {
  console.log('🚀 LUXBIN Browser Extension initialized');

  // Check gateway on startup
  await checkGateway();

  // Poll gateway every 30 seconds
  setInterval(checkGateway, 30000);

  // Set initial badge
  updateBadge('...', '#888888');
}

// Start extension
initialize();

console.log('✅ LUXBIN Background Service Worker loaded');
