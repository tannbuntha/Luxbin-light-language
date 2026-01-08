#!/bin/bash

# Disable LUXBIN Internet - Switch back to regular ISP internet

echo "Switching back to regular internet..."

# Get active network interface
INTERFACE=$(route get default | grep interface | awk '{print $2}')

# Disable proxy
echo "Disabling LUXBIN proxy..."
sudo networksetup -setwebproxystate "$INTERFACE" off
sudo networksetup -setsecurewebproxystate "$INTERFACE" off

# Restore DNS
echo "Restoring DNS..."
if [ -f /tmp/luxbin_dns_backup.txt ]; then
    DNS_SERVERS=$(cat /tmp/luxbin_dns_backup.txt)
    if [ "$DNS_SERVERS" == "There aren't any DNS Servers set on $INTERFACE." ]; then
        sudo networksetup -setdnsservers "$INTERFACE" "Empty"
    else
        sudo networksetup -setdnsservers "$INTERFACE" $DNS_SERVERS
    fi
else
    # Use common public DNS as fallback
    sudo networksetup -setdnsservers "$INTERFACE" 8.8.8.8 8.8.4.4
fi

echo ""
echo "✅ Regular internet restored"
echo ""
echo "To switch back to LUXBIN:"
echo "  ./setup_luxbin_internet.sh"
echo ""
