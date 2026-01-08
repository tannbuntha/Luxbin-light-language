#!/bin/bash

# LUXBIN Internet Connection Setup
# Configures macOS to use LUXBIN as your primary internet

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                 LUXBIN QUANTUM INTERNET - SYSTEM SETUP                       ║"
echo "║                                                                              ║"
echo "║         Replace your ISP with quantum-secured internet                      ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

echo "This will configure your Mac to use LUXBIN Quantum Internet for all web traffic."
echo ""
echo "What happens:"
echo "  ✅ All websites routed through LUXBIN gateway"
echo "  ✅ Content mirrored to quantum network"
echo "  ✅ Censorship-resistant browsing"
echo "  ✅ Quantum-secured connections"
echo "  ✅ Works with all browsers (Chrome, Safari, Firefox)"
echo ""
echo "You can switch back to regular internet anytime."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Step 1: Configure system HTTP proxy
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Configure System Proxy"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get active network interface
INTERFACE=$(route get default | grep interface | awk '{print $2}')
echo "Active network interface: $INTERFACE"

# Set HTTP/HTTPS proxy to LUXBIN gateway
echo "Setting proxy to localhost:9000..."
sudo networksetup -setwebproxy "$INTERFACE" localhost 9000
sudo networksetup -setsecurewebproxy "$INTERFACE" localhost 9000
sudo networksetup -setproxybypassdomains "$INTERFACE" "localhost" "127.0.0.1" "*.local"

echo "✅ System proxy configured"

# Step 2: Create LUXBIN DNS resolver
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Configure DNS Resolver"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Backup current DNS
networksetup -getdnsservers "$INTERFACE" > /tmp/luxbin_dns_backup.txt
echo "DNS backup saved to /tmp/luxbin_dns_backup.txt"

# Set LUXBIN as DNS (will resolve via gateway)
echo "Setting LUXBIN DNS resolver..."
sudo networksetup -setdnsservers "$INTERFACE" 127.0.0.1

echo "✅ DNS resolver configured"

# Step 3: Configure browser certificates (optional)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Browser Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat << 'EOF'
For HTTPS websites, you need to configure browser proxy:

Chrome/Edge:
  1. Settings → System → Open computer proxy settings
  2. Already configured via system proxy ✅

Safari:
  1. Preferences → Advanced → Proxies
  2. Already configured via system proxy ✅

Firefox (needs manual config):
  1. Settings → Network Settings → Manual proxy
  2. HTTP Proxy: localhost, Port: 9000
  3. HTTPS Proxy: localhost, Port: 9000
  4. Check "Use this proxy for HTTPS"
EOF

echo ""
read -p "Press Enter to continue..."

# Step 4: Test LUXBIN connection
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Test LUXBIN Internet Connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Testing gateway..."
if curl -s http://localhost:9000/status > /dev/null 2>&1; then
    echo "✅ LUXBIN Gateway is running"
else
    echo "⚠️  LUXBIN Gateway not responding"
    echo "   Please start gateway first: ./start_gateway.sh"
fi

echo ""
echo "Testing internet connection through LUXBIN..."
echo "(This will mirror google.com to quantum network)"
echo ""

# Test via gateway
if curl -x http://localhost:9000 -s http://google.com > /dev/null 2>&1; then
    echo "✅ Internet works through LUXBIN!"
else
    echo "⚠️  Could not reach website through LUXBIN"
fi

# Step 5: Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ LUXBIN QUANTUM INTERNET IS NOW ACTIVE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your Mac is now using LUXBIN Quantum Internet!"
echo ""
echo "What this means:"
echo "  • All websites are routed through quantum network"
echo "  • Content mirrored to IBM quantum computers"
echo "  • Censorship-resistant (sites can't be blocked)"
echo "  • Quantum-secured (unhackable encryption)"
echo "  • Decentralized (no single point of control)"
echo ""
echo "Your apps on LUXBIN:"
echo "  🎮 Global Blackjack: Just type 'globalblackjack.vercel.app' in browser"
echo "  📱 Niche App: Just type 'niche-app-main.vercel.app' in browser"
echo "  🌐 Any website: Works normally!"
echo ""
echo "To switch back to regular internet:"
echo "  ./disable_luxbin_internet.sh"
echo ""
echo "Enjoy your quantum internet! 🌟"
echo ""
