# LUXBIN Node Operator Guide

Complete guide for running production LUXBIN bootstrap nodes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Docker)](#quick-start-docker)
3. [Manual Installation](#manual-installation)
4. [Configuration](#configuration)
5. [Monitoring](#monitoring)
6. [Maintenance](#maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Security](#security)

## Prerequisites

### Hardware Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB SSD
- Network: 100 Mbps up/down

**Recommended:**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50+ GB NVMe SSD
- Network: 1 Gbps up/down

### Software Requirements

- **OS**: Ubuntu 22.04 LTS (recommended) or similar Linux
- **Python**: 3.10+
- **Docker**: 24.0+ (for Docker deployment)
- **Ports**: 8080 (HTTP API), outbound HTTPS for quantum backends

### API Keys

- **IonQ API Key** (required): Get from https://ionq.com
- **IBM Quantum** (optional): Already configured

## Quick Start (Docker)

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Log out and back in for group changes to take effect.

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/luxbin-light-language.git
cd luxbin-light-language
```

### 3. Set Environment Variables

```bash
export IONQ_API_KEY='your_ionq_api_key_here'
```

### 4. Deploy Network

```bash
cd deployment/scripts
chmod +x deploy.sh
./deploy.sh deploy
```

This will start:
- 3 bootstrap nodes (US East, EU West, Asia Pacific)
- 1 network monitor

### 5. Check Status

```bash
./deploy.sh status
```

### 6. View Dashboard

Open http://localhost:3000 in your browser.

## Manual Installation

### 1. Create User

```bash
sudo useradd -r -s /bin/bash -d /opt/luxbin luxbin
sudo mkdir -p /opt/luxbin
sudo chown luxbin:luxbin /opt/luxbin
```

### 2. Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip git

# Install Python packages
cd /opt/luxbin
pip3 install -r requirements.txt
```

### 3. Copy Files

```bash
sudo -u luxbin git clone https://github.com/yourusername/luxbin-light-language.git /opt/luxbin
```

### 4. Configure Service

```bash
sudo cp deployment/systemd/luxbin-bootstrap.service /etc/systemd/system/

# Edit service file with your configuration
sudo nano /etc/systemd/system/luxbin-bootstrap.service

# Update these variables:
# - IONQ_API_KEY
# - NODE_NAME
# - REGION
# - PORT
```

### 5. Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable luxbin-bootstrap
sudo systemctl start luxbin-bootstrap
```

### 6. Check Status

```bash
sudo systemctl status luxbin-bootstrap
journalctl -u luxbin-bootstrap -f
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `IONQ_API_KEY` | IonQ API key | — | Yes |
| `NODE_NAME` | Bootstrap node name | bootstrap-1 | No |
| `REGION` | Geographic region | us-east | No |
| `PORT` | HTTP API port | 8080 | No |

### Regions

Choose region based on your server location:
- `us-east` - US East Coast
- `us-west` - US West Coast
- `eu-west` - Europe (West)
- `eu-central` - Europe (Central)
- `asia-pacific` - Asia Pacific
- `asia-east` - Asia (East)

### Firewall Configuration

```bash
# Allow HTTP API port
sudo ufw allow 8080/tcp

# Allow SSH (if not already allowed)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

## Monitoring

### Health Check

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "healthy": true,
  "checks": {
    "node_running": true,
    "peers_connected": true,
    "blockchain_synced": true,
    "uptime_ok": true
  },
  "timestamp": 1234567890.0
}
```

### Metrics

```bash
curl http://localhost:8080/status | jq
```

### Network Dashboard

Access the network monitor dashboard:
```
http://localhost:3000
```

Shows:
- Bootstrap node health
- Network-wide statistics
- Peer connectivity
- Performance graphs

### Logs

**Docker:**
```bash
docker-compose logs -f bootstrap-us-east
```

**Systemd:**
```bash
journalctl -u luxbin-bootstrap -f
```

## Maintenance

### Update Node

**Docker:**
```bash
cd luxbin-light-language
git pull
cd deployment/docker
docker-compose build
docker-compose up -d
```

**Systemd:**
```bash
cd /opt/luxbin
sudo -u luxbin git pull
sudo systemctl restart luxbin-bootstrap
```

### Backup

Important data to backup:
- Configuration files
- Blockchain data (if storing locally)
- API keys

```bash
# Backup configuration
sudo tar -czf luxbin-backup-$(date +%Y%m%d).tar.gz \
    /opt/luxbin/*.py \
    /etc/systemd/system/luxbin-bootstrap.service
```

### Restart Node

**Docker:**
```bash
./deploy.sh restart
```

**Systemd:**
```bash
sudo systemctl restart luxbin-bootstrap
```

## Troubleshooting

### Node Won't Start

**Check logs:**
```bash
journalctl -u luxbin-bootstrap -n 100
```

**Common issues:**
- Missing IonQ API key
- Port already in use
- Missing Python dependencies

**Solutions:**
```bash
# Check API key
grep IONQ_API_KEY /etc/systemd/system/luxbin-bootstrap.service

# Check port
sudo lsof -i :8080

# Reinstall dependencies
pip3 install -r /opt/luxbin/requirements.txt
```

### No Peers Connected

**Wait 1-2 minutes** - Quantum initialization takes time.

**Check quantum backends:**
```bash
curl http://localhost:8080/status | jq '.metrics.quantum_backends'
```

**Restart if stuck:**
```bash
sudo systemctl restart luxbin-bootstrap
```

### Health Check Failing

**Check individual health components:**
```bash
curl http://localhost:8080/health | jq '.checks'
```

**Fix issues:**
- `node_running: false` - Node not initialized
- `peers_connected: false` - Wait for bootstrap
- `blockchain_synced: false` - Blockchain issue
- `uptime_ok: false` - Just started (normal)

### High Memory Usage

**Check current usage:**
```bash
docker stats  # Docker
systemctl status luxbin-bootstrap  # Systemd
```

**Limit memory:**
```bash
# Add to systemd service:
MemoryLimit=2G

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart luxbin-bootstrap
```

## Security

### Best Practices

1. **API Keys**
   - Never commit API keys to version control
   - Use environment variables or secrets management
   - Rotate keys periodically

2. **Firewall**
   - Only expose necessary ports (8080)
   - Use UFW or iptables
   - Consider VPN for monitoring

3. **Updates**
   - Keep system packages updated
   - Update LUXBIN software regularly
   - Monitor security advisories

4. **Access Control**
   - Run as dedicated user (luxbin)
   - Use SSH keys (not passwords)
   - Enable fail2ban

5. **Monitoring**
   - Set up alerts for downtime
   - Monitor resource usage
   - Track peer count

### Hardening

```bash
# Disable password authentication
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Enable automatic security updates
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Install fail2ban
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
```

## Production Checklist

Before going live:

- [ ] Hardware meets recommended specs
- [ ] IonQ API key configured
- [ ] Firewall configured
- [ ] Health checks passing
- [ ] Peers connecting
- [ ] Monitoring dashboard accessible
- [ ] Logs being collected
- [ ] Backup strategy in place
- [ ] Security hardening applied
- [ ] Documentation reviewed

## Support

- **Documentation**: See LUXBIN_INTERNET_README.md
- **Issues**: GitHub Issues
- **Network Monitor**: http://localhost:3000
- **API Docs**: http://localhost:8080/status

## Performance Targets

### Uptime

- **Target**: 99.9% (8.76 hours/year downtime)
- **Acceptable**: 99.5% (43.8 hours/year downtime)

### Response Times

- **Health Check**: <1 second
- **Peer Discovery**: <5 seconds
- **API Requests**: <2 seconds

### Resource Usage

- **CPU**: <50% average
- **RAM**: <4 GB
- **Network**: <100 Mbps
- **Disk I/O**: <50 MB/s

## Advanced Topics

### Multiple Nodes

Run multiple bootstrap nodes on the same machine:

```bash
# Node 1 on port 8080
NODE_NAME=bootstrap-1 PORT=8080 python3 luxbin_bootstrap_node.py

# Node 2 on port 8081
NODE_NAME=bootstrap-2 PORT=8081 python3 luxbin_bootstrap_node.py
```

### Load Balancing

Use nginx for load balancing across bootstrap nodes:

```nginx
upstream luxbin_bootstrap {
    server localhost:8080;
    server localhost:8081;
    server localhost:8082;
}

server {
    listen 80;
    location / {
        proxy_pass http://luxbin_bootstrap;
    }
}
```

### Kubernetes Deployment

See `deployment/kubernetes/` for Kubernetes manifests.

## License

LUXBIN Quantum Photonic Internet
Created by Nichole Christie, 2026
