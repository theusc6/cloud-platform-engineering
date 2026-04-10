# GlobalProtect VPN Management Script

This documentation provides an overview of the VPN Management Script, a comprehensive tool designed to manage, diagnose, and troubleshoot GlobalProtect VPN connections on macOS systems.

## Overview

The VPN Management Script simplifies the process of starting, stopping, troubleshooting, and resetting GlobalProtect VPN connections on macOS. It automates several complex tasks that would otherwise require manual intervention through different interfaces.

## Features

- **Service Management**: Start, stop, and restart GlobalProtect services
- **Connection Diagnostics**: Diagnose common VPN connection issues
- **Network Extension Management**: Fix issues with macOS network extensions
- **Configuration Reset**: Clean up corrupted configurations
- **Connection Utilities**: Automated connection attempts using multiple methods
- **Detailed Status Information**: Comprehensive status reports for all VPN components

## Prerequisites

- macOS 10.15 (Catalina) or newer
- GlobalProtect VPN client installed
- Administrative (sudo) privileges

## Usage

### Basic Commands

```bash
# Check VPN status
sudo ./vpn_diag.sh status

# Start GlobalProtect services and application
sudo ./vpn_diag.sh start

# Stop GlobalProtect services
sudo ./vpn_diag.sh stop

# Restart GlobalProtect services
sudo ./vpn_diag.sh restart

# Attempt to establish VPN connection
sudo ./vpn_diag.sh connect

```

### Advanced Troubleshooting Commands

```bash
# Run comprehensive diagnostics
sudo ./vpn_diag.sh diagnose

# Check for specific connection issues
sudo ./vpn_diag.sh issues

# Try quick fixes for common problems
sudo ./vpn_diag.sh quick_fix

# Fix VPN network extension issues
sudo ./vpn_diag.sh fix_extensions

# Complete reset of GlobalProtect configuration (last resort)
sudo ./vpn_diag.sh full_reset
```

## Troubleshooting Guide

### Common Issues and Solutions

#### No VPN Interface (gpd0) Created

If the script reports "No active VPN tunnel interface found":

1. Check network extension approval:

```bash
sudo ./vpn_diag.sh fix_extensions
```

2. Ensure DNS resolution to your VPN portal:

```bash
for i in cb ny; do host amer-$i-vpn.example.com; ping -c4 amer-$i-vpn.example.com; done
```

3. If unresolvable, add an entry to your hosts file using:

```bash
sudo ./vpn_diag.sh fix_extensions
```

- Follow the prompts to add your portal details

---

### Authentication Failures

If you're having login issues:

1.Check credential state:

```bash
sudo ./vpn_diag.sh issues
```

2. Clear cached credentials:

```bash
sudo ./vpn_diag.sh quick_fix
```

### Complete Reset

As a last resort for persistent issues:

```bash
sudo ./vpn_diag.sh full_reset
```

**Warning**: This will remove all VPN settings and require reconfiguration.

### Technical Details

The script manages the following GlobalProtect components:

- Daemon processes (com.paloaltonetworks.gp.pangpsd)
- Agent processes (com.paloaltonetworks.gp.pangpa and com.paloaltonetworks.gp.pangps)
- Network extensions and system extensions
- Configuration files in /Library/Application Support/PaloAltoNetworks/GlobalProtect
- DNS cache and network settings that might affect VPN connectivity

### Best Practices

- Always start with the status command to understand the current state
- Use diagnose or issues before attempting fixes
- Try the least invasive fixes first (connect, restart)
- Only use full_reset when other methods have failed
- After major macOS updates, you may need to reapprove network extensions

### Support

If persistent issues remain after using this script, contact your IT department with the diagnostic information gathered from:

```bash
sudo ./vpn_diag.sh diagnose > vpn_diagnostics.txt
```

This file will contain valuable information for troubleshooting.
