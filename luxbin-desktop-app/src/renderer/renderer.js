/**
 * LUXBIN Desktop - Renderer Process
 */

const { ipcRenderer } = require('electron');

// UI Elements
const addressInput = document.getElementById('address-input');
const navigateBtn = document.getElementById('navigate-btn');
const statusIndicator = document.getElementById('status-indicator');
const browserContent = document.getElementById('browser-content');
const logArea = document.getElementById('log-area');

const navItems = document.querySelectorAll('.nav-item');
const contentSections = document.querySelectorAll('.content-section');

// Node status displays
const nodeIdDisplay = document.getElementById('node-id-display');
const peersDisplay = document.getElementById('peers-display');
const statusDisplay = document.getElementById('status-display');
const uptimeDisplay = document.getElementById('uptime-display');

// Register form
const registerNameInput = document.getElementById('register-name-input');
const registerAddressInput = document.getElementById('register-address-input');
const registerSubmitBtn = document.getElementById('register-submit-btn');
const registerMessage = document.getElementById('register-message');

// Publish form
const publishContentInput = document.getElementById('publish-content-input');
const publishTitleInput = document.getElementById('publish-title-input');
const publishSubmitBtn = document.getElementById('publish-submit-btn');
const publishMessage = document.getElementById('publish-message');

/**
 * Navigation
 */
navItems.forEach(item => {
  item.addEventListener('click', () => {
    const sectionId = item.dataset.section;

    // Update active nav item
    navItems.forEach(nav => nav.classList.remove('active'));
    item.classList.add('active');

    // Show corresponding section
    contentSections.forEach(section => section.classList.remove('active'));
    document.getElementById(`${sectionId}-section`).classList.add('active');
  });
});

/**
 * Navigate to LUXBIN address
 */
async function navigateLuxbin(address) {
  if (!address) return;

  browserContent.innerHTML = '<div style="padding: 40px; text-align: center;">Loading...</div>';

  try {
    const result = await ipcRenderer.invoke('navigate-luxbin', address);

    if (result.success) {
      // Display content
      browserContent.innerHTML = `
        <div style="margin-bottom: 20px; padding: 15px; background: rgba(0, 255, 0, 0.1); border-radius: 8px;">
          <strong>Loaded from:</strong> ${result.luxbin_address}
        </div>
        <div style="background: white; color: black; padding: 20px; border-radius: 8px;">
          ${result.content}
        </div>
      `;
    } else {
      browserContent.innerHTML = `
        <div style="padding: 40px; text-align: center; color: #ff6b6b;">
          <h3>Failed to load content</h3>
          <p>${result.error}</p>
        </div>
      `;
    }
  } catch (error) {
    browserContent.innerHTML = `
      <div style="padding: 40px; text-align: center; color: #ff6b6b;">
        <h3>Error</h3>
        <p>${error.message}</p>
      </div>
    `;
  }
}

navigateBtn.addEventListener('click', () => {
  const address = addressInput.value.trim();
  navigateLuxbin(address);
});

addressInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    const address = addressInput.value.trim();
    navigateLuxbin(address);
  }
});

/**
 * Register name
 */
registerSubmitBtn.addEventListener('click', async () => {
  const name = registerNameInput.value.trim();
  const address = registerAddressInput.value.trim();

  if (!name || !address) {
    registerMessage.innerHTML = '<div class="message error">Please fill in both fields</div>';
    return;
  }

  registerSubmitBtn.disabled = true;
  registerSubmitBtn.textContent = 'Registering...';

  try {
    const result = await ipcRenderer.invoke('register-name', {
      name,
      address,
      owner: 'desktop_user'
    });

    if (result.success) {
      registerMessage.innerHTML = `<div class="message success">✅ Name "${name}" registered successfully!</div>`;
      registerNameInput.value = '';
      registerAddressInput.value = '';
    } else {
      registerMessage.innerHTML = `<div class="message error">❌ Registration failed: ${result.error}</div>`;
    }
  } catch (error) {
    registerMessage.innerHTML = `<div class="message error">❌ Error: ${error.message}</div>`;
  } finally {
    registerSubmitBtn.disabled = false;
    registerSubmitBtn.textContent = 'Register on Quantum Blockchain';
  }
});

/**
 * Publish content
 */
publishSubmitBtn.addEventListener('click', async () => {
  const content = publishContentInput.value.trim();
  const title = publishTitleInput.value.trim();

  if (!content) {
    publishMessage.innerHTML = '<div class="message error">Please enter content to publish</div>';
    return;
  }

  publishSubmitBtn.disabled = true;
  publishSubmitBtn.textContent = 'Publishing...';

  try {
    const result = await ipcRenderer.invoke('publish-content', {
      content,
      metadata: { title, author: 'Desktop User' }
    });

    if (result.success) {
      publishMessage.innerHTML = `
        <div class="message success">
          ✅ Content published successfully!<br>
          <strong>Address:</strong> ${result.luxbin_address}
        </div>
      `;
      publishContentInput.value = '';
      publishTitleInput.value = '';
    } else {
      publishMessage.innerHTML = `<div class="message error">❌ Publishing failed: ${result.error}</div>`;
    }
  } catch (error) {
    publishMessage.innerHTML = `<div class="message error">❌ Error: ${error.message}</div>`;
  } finally {
    publishSubmitBtn.disabled = false;
    publishSubmitBtn.textContent = 'Publish to Network';
  }
});

/**
 * Update node status
 */
async function updateNodeStatus() {
  try {
    const status = await ipcRenderer.invoke('get-node-status');

    if (status.connected) {
      statusIndicator.classList.add('connected');
      statusDisplay.textContent = 'Connected';

      if (status.node_id) {
        nodeIdDisplay.textContent = status.node_id.substring(0, 16) + '...';
      }

      peersDisplay.textContent = status.peers || '0';
    } else {
      statusIndicator.classList.remove('connected');
      statusDisplay.textContent = 'Connecting...';
    }
  } catch (error) {
    console.error('Failed to update status:', error);
  }
}

/**
 * IPC Event Listeners
 */

// Node ready
ipcRenderer.on('node-ready', (event, status) => {
  console.log('✅ Quantum node ready:', status);
  statusIndicator.classList.add('connected');
  updateNodeStatus();
});

// Backend logs
ipcRenderer.on('backend-log', (event, log) => {
  const logLine = document.createElement('div');
  logLine.textContent = log;
  logLine.style.marginBottom = '5px';
  logArea.appendChild(logLine);

  // Auto-scroll
  logArea.scrollTop = logArea.scrollHeight;
});

// Navigation messages
ipcRenderer.on('navigate', (event, destination) => {
  if (destination === 'home') {
    addressInput.value = '';
    browserContent.innerHTML = '<p style="opacity: 0.7; text-align: center; padding: 40px;">Enter a LUXBIN address or name in the address bar above to navigate.</p>';
  }
});

ipcRenderer.on('focus-address-bar', () => {
  addressInput.focus();
  addressInput.select();
});

ipcRenderer.on('show-dashboard', () => {
  document.querySelector('[data-section="dashboard"]').click();
});

ipcRenderer.on('show-register', () => {
  document.querySelector('[data-section="register"]').click();
});

ipcRenderer.on('show-status', () => {
  document.querySelector('[data-section="dashboard"]').click();
});

/**
 * Initialize
 */
function initialize() {
  console.log('✅ LUXBIN Desktop Renderer loaded');

  // Update status every 5 seconds
  updateNodeStatus();
  setInterval(updateNodeStatus, 5000);
}

initialize();
