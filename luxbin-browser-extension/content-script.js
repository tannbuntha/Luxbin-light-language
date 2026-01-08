/**
 * LUXBIN Browser Extension - Content Script
 *
 * Injected into all pages to:
 * - Detect luxbin:// links
 * - Add visual indicators
 * - Handle in-page LUXBIN content
 */

// Add LUXBIN indicator to page
function addLuxbinIndicator() {
  // Check if page is served from LUXBIN
  if (window.location.href.includes('localhost:9000/fetch')) {
    const indicator = document.createElement('div');
    indicator.id = 'luxbin-indicator';
    indicator.innerHTML = `
      <div style="
        position: fixed;
        top: 10px;
        right: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 12px;
        font-weight: 600;
        z-index: 999999;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        gap: 8px;
      ">
        <span style="
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #00ff00;
          animation: luxbin-pulse 2s infinite;
        "></span>
        <span>LUXBIN Quantum Network</span>
      </div>
      <style>
        @keyframes luxbin-pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      </style>
    `;

    document.body.appendChild(indicator);
  }
}

// Highlight luxbin:// links
function highlightLuxbinLinks() {
  const links = document.querySelectorAll('a[href^="luxbin://"]');

  links.forEach(link => {
    if (!link.classList.contains('luxbin-link-highlighted')) {
      link.classList.add('luxbin-link-highlighted');
      link.style.cssText = `
        color: #667eea !important;
        text-decoration: underline !important;
        font-weight: 600 !important;
        position: relative !important;
      `;

      // Add quantum icon
      const icon = document.createElement('span');
      icon.innerHTML = ' ⚛️';
      icon.style.cssText = 'font-size: 0.9em;';
      link.appendChild(icon);
    }
  });
}

// Initialize
function initialize() {
  console.log('✅ LUXBIN Content Script loaded');

  // Add indicator if on LUXBIN page
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addLuxbinIndicator);
  } else {
    addLuxbinIndicator();
  }

  // Highlight links
  highlightLuxbinLinks();

  // Watch for new links
  const observer = new MutationObserver(() => {
    highlightLuxbinLinks();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

// Start
initialize();
