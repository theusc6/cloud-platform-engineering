#!/bin/bash
# GlobalProtect VPN Management Script
# This script helps check, start, stop, and restart the GlobalProtect VPN client
# Usage: ./vpn_management.sh [status|start|stop|restart|connect|diagnose]

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Define paths
GP_APP="/Applications/GlobalProtect.app"
GP_DAEMON="/Library/LaunchDaemons/com.paloaltonetworks.gp.pangpsd.plist"
GP_CONFIG="/Library/Application Support/PaloAltoNetworks/GlobalProtect"
GP_LOG="/var/log/globalprotect.log"

# Find the actual client launch agent files
echo -e "${CYAN}Finding GlobalProtect agent files...${NC}"
LAUNCH_AGENTS_DIR="/Library/LaunchAgents"
GP_AGENT_FILES=()

for file in "$LAUNCH_AGENTS_DIR"/com.paloaltonetworks*.plist; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}Found agent file: $file${NC}"
        GP_AGENT_FILES+=("$file")
    fi
done

if [ ${#GP_AGENT_FILES[@]} -eq 0 ]; then
    echo -e "${RED}No GlobalProtect agent files found in $LAUNCH_AGENTS_DIR${NC}"
fi

# Get current logged-in user
CURRENT_USER=$(stat -f "%Su" /dev/console)

# Function to check installation
check_installation() {
    echo -e "${CYAN}Checking GlobalProtect installation...${NC}"
    
    if [ -d "$GP_APP" ]; then
        echo -e "${GREEN}GlobalProtect is installed${NC}"
        if command -v tree &> /dev/null; then
            tree -L 1 "$GP_APP/Contents/"
        else
            ls -la "$GP_APP/Contents/"
        fi
        return 0
    else
        echo -e "${RED}GlobalProtect is not installed at $GP_APP${NC}"
        return 1
    fi
}

# Function to check status
check_status() {
    echo -e "${CYAN}Checking GlobalProtect service status...${NC}"
    
    # Check daemon
    echo -e "${YELLOW}Daemon status:${NC}"
    if launchctl list | grep -q "com.paloaltonetworks.gp.pangpsd"; then
        launchctl list | grep "com.paloaltonetworks.gp.pangpsd"
        echo -e "${GREEN}VPN daemon is running${NC}"
    else
        echo -e "${RED}VPN daemon is not running${NC}"
    fi
    
    # Check all GlobalProtect agents
    echo -e "${YELLOW}Agent status:${NC}"
    
    # First check if pangpa or pangps are in the list
    if launchctl list | grep -q -E "pangpa|pangps"; then
        launchctl list | grep -E "pangpa|pangps"
        echo -e "${GREEN}VPN agents are running${NC}"
    else
        echo -e "${RED}No VPN agents appear to be running${NC}"
    fi

    # Check connection status
    check_connection
}

# Function to check connection status
check_connection() {
    echo -e "${CYAN}Checking VPN connection status...${NC}"
    
    # Check if GlobalProtect processes are running
    if pgrep -f "GlobalProtect" > /dev/null; then
        echo -e "${GREEN}GlobalProtect application is running${NC}"
    else
        echo -e "${RED}GlobalProtect application is not running${NC}"
    fi
    
    # Check connection-specific interface
    if ifconfig | grep -q "gpd0"; then
        echo -e "${GREEN}VPN tunnel interface (gpd0) is active${NC}"
        ifconfig gpd0 | grep "inet " | awk '{print "VPN IP: " $2}'
    else
        echo -e "${RED}No active VPN tunnel interface found${NC}"
    fi
    
    # Check logs for connection status
    if [ -f "$GP_LOG" ]; then
        echo -e "${YELLOW}Recent connection log entries:${NC}"
        grep -i "connect\|establish\|success\|fail\|error" "$GP_LOG" | tail -10
    fi
}

# Function to diagnose connection issues with more focused log collection
diagnose_vpn() {
    echo -e "${CYAN}Diagnosing GlobalProtect VPN issues...${NC}"
    
    # Create a temp directory for log collection
    LOG_DIR=$(mktemp -d /tmp/globalprotect_logs_XXXXXX)
    echo -e "${YELLOW}Collecting logs in: $LOG_DIR${NC}"
    
    # Check installation and status
    check_installation
    check_status
    
    # Collect focused GlobalProtect logs - extract only relevant entries
    echo -e "${YELLOW}Collecting focused GlobalProtect logs...${NC}"
    
    # System logs related to GlobalProtect - only errors and warnings, last 4 hours
    echo -e "${YELLOW}Extracting recent GlobalProtect errors and warnings...${NC}"
    log show --predicate 'process contains "GlobalProtect" OR process contains "PanGPS"' \
        --style syslog --last 4h | grep -i "error\|warn\|fail\|cannot" > "$LOG_DIR/globalprotect_errors.txt"
    
    # Network Extension logs - only errors
    echo -e "${YELLOW}Extracting network extension errors...${NC}"
    log show --predicate 'subsystem contains "com.apple.networkextension"' \
        --last 2h | grep -i "error\|fail" > "$LOG_DIR/network_extension_errors.txt"
    
    # Check for GlobalProtect specific log files
    if [ -d "/var/log/paloaltonetworks" ]; then
        echo -e "${YELLOW}Extracting GlobalProtect service logs...${NC}"
        find "/var/log/paloaltonetworks" -type f -name "*.log" | while read -r logfile; do
            filename=$(basename "$logfile")
            grep -i "error\|fail\|cannot\|denied" "$logfile" > "$LOG_DIR/${filename}_errors.txt"
        done
    fi
    
    # Check for standard GlobalProtect log locations with focused extraction
    if [ -d "$GP_CONFIG" ]; then
        echo -e "${YELLOW}Copying critical GlobalProtect configuration logs...${NC}"
        # Only look for recent or small log files to avoid large file copies
        find "$GP_CONFIG" -name "*.log" -size -5M -exec cp {} "$LOG_DIR/" \;
    fi
    
    # Quick network status checks
    echo -e "${YELLOW}Checking network status...${NC}"
    echo "=== Interface with VPN IP (if present) ===" > "$LOG_DIR/network_summary.txt"
    ifconfig | grep -A2 gpd0 >> "$LOG_DIR/network_summary.txt" 
    echo -e "\n=== Current active interfaces ===" >> "$LOG_DIR/network_summary.txt"
    ifconfig | grep "status: active" -B1 >> "$LOG_DIR/network_summary.txt"
    echo -e "\n=== VPN routes (if any) ===" >> "$LOG_DIR/network_summary.txt"
    netstat -rn | grep -i "gpd\|tunnel" >> "$LOG_DIR/network_summary.txt"
    
    # Connection test to localhost on GlobalProtect daemon port
    echo -e "${YELLOW}Testing local GlobalProtect service connection...${NC}"
    nc -zv localhost 4767 > "$LOG_DIR/local_service_test.txt" 2>&1 || 
        echo "Failed to connect to GlobalProtect service on port 4767" >> "$LOG_DIR/local_service_test.txt"
    
    # Check GlobalProtect processes
    echo -e "${YELLOW}Checking GlobalProtect processes...${NC}"
    ps aux | grep -i "GlobalProtect\|PanGPS\|PanGPA" | grep -v grep > "$LOG_DIR/gp_processes.txt"
    
    # System extensions status
    echo -e "${YELLOW}System extensions status:${NC}"
    systemextensionsctl list | grep -i "palo\|global" > "$LOG_DIR/system_extensions.txt"
    
    # Compress all logs for easy sharing
    echo -e "${YELLOW}Compressing collected logs...${NC}"
    LOG_ARCHIVE="/tmp/globalprotect_logs_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$LOG_ARCHIVE" -C "$(dirname "$LOG_DIR")" "$(basename "$LOG_DIR")"
    
    echo -e "${GREEN}Log collection complete!${NC}"
    echo -e "${GREEN}Logs saved to: $LOG_ARCHIVE${NC}"
    
    # Check for the connection issue you're experiencing
    echo -e "\n${CYAN}=== Analysis of Collected Logs ===${NC}"
    
    # Check for connection refused errors
    if grep -q "error: 61" "$LOG_DIR"/*/PanGPA*.txt 2>/dev/null; then
        echo -e "${RED}Connection to GlobalProtect service is being refused (error 61)${NC}"
        echo -e "${YELLOW}This typically means the GlobalProtect daemon service is not running properly${NC}"
        echo -e "${YELLOW}Recommended action: Try 'sudo ./vpn_diag.sh full_reset' to completely reset the service${NC}"
    fi
    
    # Check for network extension errors
    if grep -q "Could not find app info" "$LOG_DIR"/network_extension_errors.txt 2>/dev/null; then
        echo -e "${RED}Network extension errors detected - extension may not be properly enabled${NC}"
    fi
}

# Function to check for specific GlobalProtect issues
check_gp_connection_issues() {
    echo -e "${CYAN}Checking for common GlobalProtect connection issues...${NC}"
    
    # Check if we can reach the GlobalProtect portal
    echo -e "${YELLOW}Testing VPN portal connectivity:${NC}"
    # Get portal from preferences if possible
    PORTAL=""
    if [ -d "$GP_CONFIG" ]; then
        if [ -f "$GP_CONFIG/global-protect-preferences.json" ]; then
            PORTAL=$(grep -o '"portal":"[^"]*' "$GP_CONFIG/global-protect-preferences.json" | cut -d'"' -f4)
        fi
    fi
    
    if [ -n "$PORTAL" ]; then
        echo -e "${GREEN}Found portal in config: $PORTAL${NC}"
        echo "Testing connectivity to $PORTAL..."
        if ping -c 3 "$PORTAL" &>/dev/null; then
            echo -e "${GREEN}Successfully pinged $PORTAL${NC}"
        else
            echo -e "${RED}Failed to ping $PORTAL - DNS or network connectivity issue${NC}"
        fi
        
        echo "Testing HTTPS connection to portal..."
        if nc -z "$PORTAL" 443 &>/dev/null; then
            echo -e "${GREEN}Successfully connected to $PORTAL:443${NC}"
        else
            echo -e "${RED}Failed to connect to $PORTAL:443 - Possible firewall or proxy issue${NC}"
        fi
    else
        echo -e "${YELLOW}No GlobalProtect portal found in configuration${NC}"
        echo "Please enter your GlobalProtect portal (e.g., vpn.company.com):"
        read -r PORTAL
        if [ -n "$PORTAL" ]; then
            echo "Testing connectivity to $PORTAL..."
            if ping -c 3 "$PORTAL" &>/dev/null; then
                echo -e "${GREEN}Successfully pinged $PORTAL${NC}"
            else
                echo -e "${RED}Failed to ping $PORTAL - DNS or network connectivity issue${NC}"
            fi
        fi
    fi
    
    # Check the credential state
    echo -e "${YELLOW}Checking credential state...${NC}"
    # Look for credential errors in logs
    if [ -f "$GP_LOG" ]; then
        if grep -q -i "credential\|auth failed\|login failed" "$GP_LOG"; then
            echo -e "${RED}Possible credential issues found in logs:${NC}"
            grep -i "credential\|auth failed\|login failed" "$GP_LOG" | tail -5
            echo -e "${YELLOW}You may need to re-enter your credentials in the GlobalProtect app${NC}"
        fi
    fi
    
    # Check for certificate issues
    echo -e "${YELLOW}Checking for certificate issues...${NC}"
    if [ -f "$GP_LOG" ]; then
        if grep -q -i "certificate\|ssl\|tls" "$GP_LOG"; then
            echo -e "${RED}Possible certificate issues found in logs:${NC}"
            grep -i "certificate\|ssl\|tls" "$GP_LOG" | tail -5
        fi
    fi
    
    # Check for connection process
    echo -e "${YELLOW}Checking VPN connection process...${NC}"
    if ps aux | grep -v grep | grep -q "GlobalProtect"; then
        echo -e "${GREEN}GlobalProtect processes running:${NC}"
        ps aux | grep -v grep | grep "GlobalProtect"
    else
        echo -e "${RED}No GlobalProtect processes found running${NC}"
    fi
    
    # Check for network extension framework issues (common in newer macOS)
    echo -e "${YELLOW}Checking Network Extension framework status...${NC}"
    if [ -d "/Library/SystemExtensions" ]; then
        echo "System Extensions:"
        systemextensionsctl list | grep -i "palo\|global"
    fi
    
    # Suggest fixes based on our findings
    echo -e "\n${CYAN}=== Suggested fixes based on analysis ===${NC}"
    echo -e "${YELLOW}1. Try manually connecting through the GlobalProtect UI${NC}"
    echo -e "${YELLOW}2. Check your credentials - they may have expired${NC}"
    echo -e "${YELLOW}3. Make sure your network allows VPN connections (not blocked by firewall)${NC}"
    echo -e "${YELLOW}4. Try rebooting your computer${NC}"
    echo -e "${YELLOW}5. Check with your IT department if VPN access requires additional setup${NC}"
}

# Function to start VPN
start_vpn() {
    echo -e "${CYAN}Starting GlobalProtect services...${NC}"
    
    echo -e "${YELLOW}Current logged-in user: $CURRENT_USER${NC}"
    
    # Start daemon if not already running
    echo -e "${YELLOW}Loading VPN daemon...${NC}"
    if launchctl list | grep -q "com.paloaltonetworks.gp.pangpsd"; then
        echo -e "${GREEN}VPN daemon already running${NC}"
    else
        launchctl load "$GP_DAEMON" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Daemon loaded successfully${NC}"
        else
            echo -e "${RED}Failed to load daemon${NC}"
        fi
    fi
    
    # For loading agents, we need to use a different approach
    echo -e "${YELLOW}Loading agent services using sudo -u $CURRENT_USER...${NC}"
    
    # Check if we have any agent files
    if [ ${#GP_AGENT_FILES[@]} -eq 0 ]; then
        echo -e "${RED}No agent files to load${NC}"
    else
        # Load each agent file
        for agent_file in "${GP_AGENT_FILES[@]}"; do
            echo -e "${YELLOW}Loading $agent_file...${NC}"
            sudo -u $CURRENT_USER launchctl load "$agent_file" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}Successfully loaded: $agent_file${NC}"
            else
                echo -e "${RED}Failed to load: $agent_file${NC}"
            fi
        done
    fi
    
    # Verify services are running
    echo -e "${CYAN}Verifying services...${NC}"
    launchctl list | grep -i "com.paloaltonetworks" || echo -e "${RED}No services found${NC}"
    
    # Launch the GlobalProtect app as the current user
    echo -e "${YELLOW}Launching GlobalProtect application...${NC}"
    sudo -u $CURRENT_USER open -a GlobalProtect
    
    echo -e "${GREEN}GlobalProtect services started${NC}"
    
    # Wait a few seconds and check connection status
    echo -e "${YELLOW}Waiting for connection to initialize...${NC}"
    sleep 5
    check_connection
}

# Function to attempt connection to VPN
connect_vpn() {
    echo -e "${CYAN}Attempting to connect to VPN...${NC}"
    
    # First make sure services are running
    if ! launchctl list | grep -q "com.paloaltonetworks.gp.pangpsd"; then
        echo -e "${YELLOW}Services not running. Starting services first...${NC}"
        start_vpn
        sleep 3
    fi
    
    # Get portal from preferences if possible
    PORTAL=""
    if [ -d "$GP_CONFIG" ]; then
        if [ -f "$GP_CONFIG/global-protect-preferences.json" ];then
            PORTAL=$(grep -o '"portal":"[^"]*' "$GP_CONFIG/global-protect-preferences.json" | cut -d'"' -f4)
            echo -e "${GREEN}Found portal in config: $PORTAL${NC}"
        fi
    fi
    
    # Try multiple connection methods
    echo -e "${YELLOW}Trying connection method 1: UI automation...${NC}"
    # Use AppleScript to simulate clicking the connect button
    sudo -u $CURRENT_USER osascript <<EOF
tell application "GlobalProtect"
    activate
    delay 1
    # Try to press connect button via UI automation
    tell application "System Events"
        tell process "GlobalProtect"
            if exists button "Connect" of window 1 then
                click button "Connect" of window 1
                delay 1
            else
                # Try to find buttons by name or index
                try
                    click button 1 of window 1
                end try
            end if
        end tell
    end tell
end tell
EOF
    
    # Method 2: Try CLI connection if available
    echo -e "${YELLOW}Trying connection method 2: CLI...${NC}"
    GP_CLI="$GP_APP/Contents/MacOS/gpcli"
    if [ -f "$GP_CLI" ]; then
        echo "Found GlobalProtect CLI tool, attempting connection..."
        sudo -u $CURRENT_USER "$GP_CLI" connect || echo "CLI connection attempt failed"
    else
        echo "GlobalProtect CLI tool not found"
    fi
    
    # Check if connection was successful
    echo -e "${YELLOW}Waiting for connection to establish...${NC}"
    sleep 10
    check_connection
    
    # If still not connected, run diagnostics
    if ! ifconfig | grep -q "gpd0"; then
        echo -e "${RED}Connection attempts failed. Running diagnostics...${NC}"
        check_gp_connection_issues
    fi
}

# Function to stop VPN
stop_vpn() {
    echo -e "${CYAN}Stopping GlobalProtect services...${NC}"
    
    # Kill running GlobalProtect application first
    echo -e "${YELLOW}Killing GlobalProtect application processes...${NC}"
    pkill -f "GlobalProtect" || echo -e "${YELLOW}No GlobalProtect processes found${NC}"
    
    # For unloading agents, use sudo as the current user
    if [ ${#GP_AGENT_FILES[@]} -gt 0 ]; then
        for agent_file in "${GP_AGENT_FILES[@]}"; do
            echo -e "${YELLOW}Unloading $agent_file...${NC}"
            sudo -u $CURRENT_USER launchctl unload "$agent_file" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}Successfully unloaded: $agent_file${NC}"
            else
                echo -e "${RED}Failed to unload: $agent_file${NC}"
            fi
        done
    fi
    
    # Verify agents are stopped
    echo -e "${CYAN}Checking if services are stopped...${NC}"
    if launchctl list | grep -q -E "pangpa|pangps"; then
        echo -e "${RED}Some VPN services may still be running${NC}"
        launchctl list | grep -E "pangpa|pangps"
    else
        echo -e "${GREEN}All VPN agents stopped${NC}"
    fi
}

# Function to restart VPN
restart_vpn() {
    echo -e "${CYAN}Restarting GlobalProtect services...${NC}"
    
    # Perform stop and start
    stop_vpn
    sleep 2
    start_vpn
    
    echo -e "${GREEN}GlobalProtect services restarted${NC}"
}

# Function to fix VPN extensions
fix_vpn_extensions() {
    echo -e "${CYAN}Checking and fixing GlobalProtect extensions...${NC}"
    
    # Check if extensions are properly enabled
    EXTENSION_STATUS=$(systemextensionsctl list | grep "GlobalProtect")
    
    if [[ $EXTENSION_STATUS == *"waiting for user"* ]]; then
        echo -e "${RED}GlobalProtect extension is waiting for user approval${NC}"
        echo -e "${YELLOW}Please check System Preferences → Security & Privacy${NC}"
        echo -e "${YELLOW}You may need to approve the GlobalProtect system extension${NC}"
        
        # Open Security & Privacy preferences
        echo -e "${YELLOW}Opening Security & Privacy preferences...${NC}"
        sudo -u $CURRENT_USER open "x-apple.systempreferences:com.apple.preference.security?General"
        
        # Wait for user to approve
        echo -e "${YELLOW}Please approve the GlobalProtect extension when prompted${NC}"
        echo -e "${YELLOW}Press Enter when you have approved the extension...${NC}"
        read -r
    fi
    
    # Check Network settings
    echo -e "${YELLOW}Checking Network settings...${NC}"
    networksetup -listallnetworkservices
    
    # Reset network settings that might interfere with VPN
    echo -e "${YELLOW}Resetting DNS cache...${NC}"
    dscacheutil -flushcache
    killall -HUP mDNSResponder
    
    echo -e "${GREEN}Network cache flushed${NC}"
    
    # Check if there's a DNS resolution issue with the VPN portal
    echo -e "${YELLOW}Adding VPN portal to hosts file as a workaround...${NC}"
    echo "Please enter your VPN portal address (e.g., vpn.company.com):"
    read -r PORTAL_NAME
    
    if [ -n "$PORTAL_NAME" ]; then
        echo "Please enter the IP address for $PORTAL_NAME (leave blank to skip):"
        read -r PORTAL_IP
        
        if [ -n "$PORTAL_IP" ]; then
            # Check if entry already exists in hosts file
            if grep -q "$PORTAL_NAME" /etc/hosts; then
                echo -e "${YELLOW}Updating existing hosts entry for $PORTAL_NAME...${NC}"
                sed -i '' "/$PORTAL_NAME/d" /etc/hosts
            fi
            
            # Add new entry to hosts file
            echo "$PORTAL_IP $PORTAL_NAME" >> /etc/hosts
            echo -e "${GREEN}Added $PORTAL_NAME to hosts file${NC}"
            
            # Test if it resolves now
            echo "Testing DNS resolution:"
            ping -c 3 "$PORTAL_NAME"
        fi
    fi
    
    # Reset global protect completely by removing all config files (more aggressive)
    echo -e "${YELLOW}Would you like to completely reset GlobalProtect? (y/n)${NC}"
    read -r RESET_CHOICE
    
    if [[ $RESET_CHOICE == "y" || $RESET_CHOICE == "Y" ]]; then
        echo -e "${RED}Performing complete reset of GlobalProtect...${NC}"
        
        # Stop services
        stop_vpn
        
        # Backup config
        echo "Backing up configuration..."
        NOW=$(date +%Y%m%d%H%M%S)
        mkdir -p /tmp/gp_backup_complete_$NOW
        
        if [ -d "$GP_CONFIG" ]; then
            cp -r "$GP_CONFIG" /tmp/gp_backup_complete_$NOW/
        fi
        
        # Remove config files
        echo "Removing configuration files..."
        rm -rf "$GP_CONFIG"/* 2>/dev/null
        
        # Remove any GlobalProtect preferences
        sudo -u $CURRENT_USER defaults delete com.paloaltonetworks.GlobalProtect 2>/dev/null || true
        
        # Reset system extensions
        echo "Resetting system extensions..."
        systemextensionsctl reset
        
        echo -e "${GREEN}GlobalProtect has been completely reset${NC}"
        echo -e "${YELLOW}You will need to reconfigure the client${NC}"
        
        # Restart GlobalProtect
        echo "Restarting GlobalProtect..."
        sleep 2
        start_vpn
        
        echo -e "${YELLOW}Please configure GlobalProtect with your portal address: $PORTAL_NAME${NC}"
    fi
}

# Main execution
case "$1" in
    status)
        check_installation
        check_status
        ;;
    start)
        check_installation && start_vpn
        ;;
    stop)
        stop_vpn
        ;;
    restart)
        restart_vpn
        ;;
    connect)
        connect_vpn
        ;;
    diagnose)
        diagnose_vpn
        ;;
    quick_fix)
        echo -e "${CYAN}Attempting quick fix for VPN connection issues...${NC}"
        stop_vpn
        sleep 2
        echo -e "${YELLOW}Clearing GlobalProtect cached data...${NC}"
        if [ -d "$GP_CONFIG" ]; then
            echo "Backing up and clearing state data..."
            NOW=$(date +%Y%m%d%H%M%S)
            mkdir -p /tmp/gp_backup_$NOW
            cp -r "$GP_CONFIG"/* /tmp/gp_backup_$NOW/ 2>/dev/null
            rm -f "$GP_CONFIG"/pangps.db* 2>/dev/null
            rm -f "$GP_CONFIG"/prelogon* 2>/dev/null
            echo -e "${GREEN}Cleared GlobalProtect cached data${NC}"
        fi
        sleep 2
        start_vpn
        sleep 5
        connect_vpn
        ;;
    issues)
        check_gp_connection_issues
        ;;
    fix_extensions)
        fix_vpn_extensions
        ;;
    full_reset)
        echo -e "${RED}WARNING: This will completely reset GlobalProtect configuration.${NC}"
        echo -e "${RED}All settings will be lost. Continue? (y/n)${NC}"
        read -r CONFIRM
        if [[ $CONFIRM == "y" || $CONFIRM == "Y" ]]; then
            stop_vpn
            sleep 1
            echo -e "${YELLOW}Backing up and removing all GlobalProtect configuration...${NC}"
            NOW=$(date +%Y%m%d%H%M%S)
            BACKUP_DIR="/tmp/gp_backup_full_$NOW"
            mkdir -p "$BACKUP_DIR"
            cp -r "$GP_CONFIG" "$BACKUP_DIR/" 2>/dev/null
            rm -rf "$GP_CONFIG"/* 2>/dev/null
            sudo -u $CURRENT_USER defaults delete com.paloaltonetworks.GlobalProtect 2>/dev/null || true
            systemextensionsctl reset
            echo -e "${GREEN}GlobalProtect completely reset${NC}"
            echo -e "${YELLOW}Waiting 5 seconds before restarting...${NC}"
            sleep 5
            start_vpn
            echo -e "${YELLOW}GlobalProtect has been reset. Please reconfigure it with your VPN details.${NC}"
        else
            echo -e "${YELLOW}Full reset cancelled.${NC}"
        fi
        ;;
    *)
        echo -e "${YELLOW}GlobalProtect VPN Management Script${NC}"
        echo -e "Usage: $0 ${GREEN}{status|start|stop|restart|connect|diagnose|quick_fix|issues|fix_extensions|full_reset}${NC}"
        echo ""
        echo -e "  ${GREEN}status${NC}   - Check if GlobalProtect is installed and running"
        echo -e "  ${GREEN}start${NC}    - Start the GlobalProtect VPN services"
        echo -e "  ${GREEN}stop${NC}     - Stop the GlobalProtect VPN client"
        echo -e "  ${GREEN}restart${NC}  - Restart the GlobalProtect VPN client"
        echo -e "  ${GREEN}connect${NC}  - Attempt to establish VPN connection"
        echo -e "  ${GREEN}diagnose${NC} - Run diagnostics on the VPN connection"
        echo -e "  ${GREEN}quick_fix${NC} - Attempt common fixes for connection issues"  
        echo -e "  ${GREEN}issues${NC}    - Check for specific connection issues"
        echo -e "  ${GREEN}fix_extensions${NC} - Fix VPN network extension issues"
        echo -e "  ${GREEN}full_reset${NC}     - Completely reset GlobalProtect (use as last resort)"
        exit 1
esac

exit 0