/**
 * LUXBIN Desktop Application - Main Process
 *
 * Features:
 * - Built-in browser for LUXBIN network
 * - Full quantum P2P node
 * - Name registration UI
 * - Network monitoring dashboard
 * - Content publishing tools
 */

const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Configuration
const isDev = process.argv.includes('--dev');
const PYTHON_BACKEND_PORT = 9001;

// Global state
let mainWindow = null;
let pythonBackend = null;
let quantumNodeStatus = {
  connected: false,
  peers: 0,
  node_id: null
};

/**
 * Create main window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'LUXBIN Quantum Internet',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false // Allow luxbin:// protocol
    },
    backgroundColor: '#1a1a2e',
    titleBarStyle: 'hiddenInset'
  });

  // Load main UI
  mainWindow.loadFile(path.join(__dirname, 'src', 'renderer', 'index.html'));

  // Open DevTools in development
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  // Create menu
  createMenu();

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  console.log('✅ Main window created');
}

/**
 * Create application menu
 */
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        { role: 'quit' }
      ]
    },
    {
      label: 'Navigate',
      submenu: [
        {
          label: 'Home',
          accelerator: 'CmdOrCtrl+H',
          click: () => {
            mainWindow.webContents.send('navigate', 'home');
          }
        },
        {
          label: 'Enter LUXBIN Address',
          accelerator: 'CmdOrCtrl+L',
          click: () => {
            mainWindow.webContents.send('focus-address-bar');
          }
        }
      ]
    },
    {
      label: 'Network',
      submenu: [
        {
          label: 'Node Dashboard',
          click: () => {
            mainWindow.webContents.send('show-dashboard');
          }
        },
        {
          label: 'Register Name',
          click: () => {
            mainWindow.webContents.send('show-register');
          }
        },
        {
          label: 'Network Status',
          click: () => {
            mainWindow.webContents.send('show-status');
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { type: 'separator' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: () => {
            require('electron').shell.openExternal('https://luxbin-app.vercel.app');
          }
        },
        {
          label: 'About LUXBIN',
          click: () => {
            mainWindow.webContents.send('show-about');
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

/**
 * Start Python backend (LUXBIN node)
 */
function startPythonBackend() {
  console.log('🚀 Starting LUXBIN quantum node backend...');

  const pythonScript = path.join(__dirname, 'python-backend', 'desktop_node.py');

  pythonBackend = spawn('python3', [pythonScript, '--port', PYTHON_BACKEND_PORT], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: path.join(__dirname, '../') // Parent directory with LUXBIN modules
  });

  pythonBackend.stdout.on('data', (data) => {
    const output = data.toString();
    console.log('[Python Backend]:', output);

    // Send to renderer
    if (mainWindow) {
      mainWindow.webContents.send('backend-log', output);
    }

    // Check for ready signal
    if (output.includes('✅ LUXBIN Node ready')) {
      quantumNodeStatus.connected = true;
      if (mainWindow) {
        mainWindow.webContents.send('node-ready', quantumNodeStatus);
      }
    }
  });

  pythonBackend.stderr.on('data', (data) => {
    console.error('[Python Backend Error]:', data.toString());
  });

  pythonBackend.on('close', (code) => {
    console.log(`Python backend exited with code ${code}`);
    quantumNodeStatus.connected = false;
  });
}

/**
 * IPC Handlers
 */

// Get node status
ipcMain.handle('get-node-status', async () => {
  return quantumNodeStatus;
});

// Navigate to LUXBIN address
ipcMain.handle('navigate-luxbin', async (event, address) => {
  try {
    const response = await fetch(`http://localhost:${PYTHON_BACKEND_PORT}/fetch?address=${encodeURIComponent(address)}`);
    const data = await response.json();

    return {
      success: true,
      content: data.content,
      luxbin_address: data.luxbin_address
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
});

// Register name
ipcMain.handle('register-name', async (event, { name, address, owner }) => {
  try {
    const response = await fetch(`http://localhost:${PYTHON_BACKEND_PORT}/register-name`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, address, owner })
    });

    const data = await response.json();

    return {
      success: true,
      record: data.record
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
});

// Publish content
ipcMain.handle('publish-content', async (event, { content, metadata }) => {
  try {
    const response = await fetch(`http://localhost:${PYTHON_BACKEND_PORT}/publish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, metadata })
    });

    const data = await response.json();

    return {
      success: true,
      luxbin_address: data.luxbin_address
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
});

/**
 * App lifecycle
 */

app.on('ready', () => {
  console.log('🚀 LUXBIN Desktop Application starting...');

  // Start Python backend
  startPythonBackend();

  // Create window
  createWindow();

  console.log('✅ Application ready');
});

app.on('window-all-closed', () => {
  // Kill Python backend
  if (pythonBackend) {
    pythonBackend.kill();
  }

  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('will-quit', () => {
  // Clean up Python backend
  if (pythonBackend) {
    pythonBackend.kill();
  }
});

console.log('✅ LUXBIN Desktop Main Process loaded');
