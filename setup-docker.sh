#!/bin/bash

# AutoMail Agent Docker Setup Script
# This script detects available browsers and creates docker-compose override

echo "🔍 Detecting system environment..."

# Detect if running on WSL
IS_WSL=false
if grep -qEi "(Microsoft|WSL)" /proc/version 2>/dev/null; then
    IS_WSL=true
    echo "✅ WSL environment detected"
    
    # Get Windows username for profile paths
    WINDOWS_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r\n' 2>/dev/null || echo "")
    if [ -n "$WINDOWS_USER" ]; then
        echo "🪟 Windows user: $WINDOWS_USER"
    fi
else
    echo "🐧 Native Linux environment detected"
fi

echo "🔍 Detecting available browsers on host system..."

# Create docker-compose override file
OVERRIDE_FILE="docker-compose.override.yml"

cat > "$OVERRIDE_FILE" << 'EOF'
version: '3.8'

services:
  automail-headless:
    volumes:
      # Data persistence
      - ./data:/home/app/data
      - ./logs:/home/app/logs
      # X11 socket for GUI if needed
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
EOF

# Add WSL-specific network configuration for debug port connectivity
if [ "$IS_WSL" = true ]; then
    cat >> "$OVERRIDE_FILE" << 'EOF'
    ports:
      - "8000:8000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
EOF
fi

# Function to add browser mount if it exists
add_browser_mount() {
    local browser_path="$1"
    local service_name="$2"
    
    if [ -f "$browser_path" ]; then
        echo "✅ Found: $browser_path"
        echo "      - $browser_path:$browser_path:ro" >> "$OVERRIDE_FILE"
        return 0
    else
        echo "❌ Not found: $browser_path"
        return 1
    fi
}

# Function to add profile mount if it exists
add_profile_mount() {
    local profile_path="$1"
    local container_path="$2"
    
    if [ -d "$profile_path" ]; then
        echo "✅ Found profile: $profile_path"
        echo "      - $profile_path:$container_path:ro" >> "$OVERRIDE_FILE"
        return 0
    else
        echo "❌ Profile not found: $profile_path"
        return 1
    fi
}

echo ""
echo "🌐 Checking for browser executables..."

# Check for Linux browsers first
add_browser_mount "/usr/bin/google-chrome" "automail-headless"
add_browser_mount "/usr/bin/google-chrome-stable" "automail-headless"
add_browser_mount "/usr/bin/chromium" "automail-headless"
add_browser_mount "/usr/bin/chromium-browser" "automail-headless"
add_browser_mount "/snap/bin/chromium" "automail-headless"
add_browser_mount "/usr/bin/firefox" "automail-headless"
add_browser_mount "/usr/bin/firefox-esr" "automail-headless"

# If on WSL, also check for Windows browsers
if [ "$IS_WSL" = true ]; then
    echo ""
    echo "🪟 Checking for Windows browsers (WSL)..."
    echo "ℹ️  Note: Windows executables cannot run in Linux containers."
    echo "ℹ️  Using Playwright's Chromium instead, but mounting Windows profiles for data access."
    
    # Common Windows browser paths
    WINDOWS_CHROME_PATHS=(
        "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
        "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"
    )
    
    WINDOWS_FIREFOX_PATHS=(
        "/mnt/c/Program Files/Mozilla Firefox/firefox.exe"
        "/mnt/c/Program Files (x86)/Mozilla Firefox/firefox.exe"
    )
    
    WINDOWS_EDGE_PATHS=(
        "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
    )
    
    # Check Windows Chrome (for informational purposes only)
    for chrome_path in "${WINDOWS_CHROME_PATHS[@]}"; do
        if [ -f "$chrome_path" ]; then
            echo "✅ Found Windows Chrome: $chrome_path (profiles will be mounted)"
            # Note: Not mounting executable as it can't run in Linux container
            # echo "      - $chrome_path:/usr/bin/chrome.exe:ro" >> "$OVERRIDE_FILE"
            break
        fi
    done
    
    # Check Windows Firefox (for informational purposes only)
    for firefox_path in "${WINDOWS_FIREFOX_PATHS[@]}"; do
        if [ -f "$firefox_path" ]; then
            echo "✅ Found Windows Firefox: $firefox_path (profiles will be mounted)"
            # Note: Not mounting executable as it can't run in Linux container
            # echo "      - $firefox_path:/usr/bin/firefox.exe:ro" >> "$OVERRIDE_FILE"
            break
        fi
    done
    
    # Check Windows Edge (for informational purposes only)
    for edge_path in "${WINDOWS_EDGE_PATHS[@]}"; do
        if [ -f "$edge_path" ]; then
            echo "✅ Found Windows Edge: $edge_path (profiles will be mounted)"
            # Note: Not mounting executable as it can't run in Linux container
            # echo "      - $edge_path:/usr/bin/msedge.exe:ro" >> "$OVERRIDE_FILE"
            break
        fi
    done
fi

echo ""
echo "📁 Checking for browser profiles..."

# Check for Linux browser profiles
add_profile_mount "$HOME/.config/google-chrome" "/home/app/.config/google-chrome"
add_profile_mount "$HOME/.mozilla/firefox" "/home/app/.mozilla/firefox"

# If on WSL, also check for Windows browser profiles
if [ "$IS_WSL" = true ] && [ -n "$WINDOWS_USER" ]; then
    echo ""
    echo "🪟 Checking for Windows browser profiles (WSL)..."
    
    # Windows Chrome profile paths
    WINDOWS_CHROME_PROFILE="/mnt/c/Users/$WINDOWS_USER/AppData/Local/Google/Chrome/User Data"
    if [ -d "$WINDOWS_CHROME_PROFILE" ]; then
        echo "✅ Found Windows Chrome profile: $WINDOWS_CHROME_PROFILE"
        echo "      - $WINDOWS_CHROME_PROFILE:/home/app/.config/google-chrome-windows:ro" >> "$OVERRIDE_FILE"
    fi
    
    # Windows Firefox profile paths
    WINDOWS_FIREFOX_PROFILE="/mnt/c/Users/$WINDOWS_USER/AppData/Roaming/Mozilla/Firefox"
    if [ -d "$WINDOWS_FIREFOX_PROFILE" ]; then
        echo "✅ Found Windows Firefox profile: $WINDOWS_FIREFOX_PROFILE"
        echo "      - $WINDOWS_FIREFOX_PROFILE:/home/app/.mozilla/firefox-windows:ro" >> "$OVERRIDE_FILE"
    fi
fi

# Add environment variables
cat >> "$OVERRIDE_FILE" << EOF
    environment:
      - DISPLAY=\${DISPLAY:-:0}
      - BROWSER_HEADLESS=true
      - PATH=/usr/bin:/usr/local/bin:/bin
      - IS_WSL=$IS_WSL

  automail-dev:
    volumes:
      - .:/app
      - ./data:/app/data
      # X11 socket
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
EOF

# Add WSL-specific configuration for dev service
if [ "$IS_WSL" = true ]; then
    cat >> "$OVERRIDE_FILE" << 'EOF'
    ports:
      - "8000:8000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
EOF
fi

echo "🔄 Adding browser mounts for development service..."

# Re-check browsers for dev service (Linux browsers)
if [ -f "/usr/bin/google-chrome" ]; then
    echo "      - /usr/bin/google-chrome:/usr/bin/google-chrome:ro" >> "$OVERRIDE_FILE"
fi
if [ -f "/usr/bin/google-chrome-stable" ]; then
    echo "      - /usr/bin/google-chrome-stable:/usr/bin/google-chrome-stable:ro" >> "$OVERRIDE_FILE"
fi
if [ -f "/usr/bin/chromium" ]; then
    echo "      - /usr/bin/chromium:/usr/bin/chromium:ro" >> "$OVERRIDE_FILE"
fi
if [ -f "/usr/bin/chromium-browser" ]; then
    echo "      - /usr/bin/chromium-browser:/usr/bin/chromium-browser:ro" >> "$OVERRIDE_FILE"
fi
if [ -f "/snap/bin/chromium" ]; then
    echo "      - /snap/bin/chromium:/snap/bin/chromium:ro" >> "$OVERRIDE_FILE"
fi
if [ -f "/usr/bin/firefox" ]; then
    echo "      - /usr/bin/firefox:/usr/bin/firefox:ro" >> "$OVERRIDE_FILE"
fi
if [ -f "/usr/bin/firefox-esr" ]; then
    echo "      - /usr/bin/firefox-esr:/usr/bin/firefox-esr:ro" >> "$OVERRIDE_FILE"
fi

# Add Windows browsers for dev service if on WSL
if [ "$IS_WSL" = true ]; then
    # Note: Windows executables cannot run in Linux containers
    # Using Playwright's Chromium instead, but keeping profile mounts
    
    # Windows Chrome (commented out - can't run in Linux container)
    # for chrome_path in "${WINDOWS_CHROME_PATHS[@]}"; do
    #     if [ -f "$chrome_path" ]; then
    #         echo "      - $chrome_path:/usr/bin/chrome.exe:ro" >> "$OVERRIDE_FILE"
    #         break
    #     fi
    # done
    
    # Windows Firefox (commented out - can't run in Linux container)
    # for firefox_path in "${WINDOWS_FIREFOX_PATHS[@]}"; do
    #     if [ -f "$firefox_path" ]; then
    #         echo "      - $firefox_path:/usr/bin/firefox.exe:ro" >> "$OVERRIDE_FILE"
    #         break
    #     fi
    # done
    
    # Windows Edge (commented out - can't run in Linux container)
    # for edge_path in "${WINDOWS_EDGE_PATHS[@]}"; do
    #     if [ -f "$edge_path" ]; then
    #         echo "      - $edge_path:/usr/bin/msedge.exe:ro" >> "$OVERRIDE_FILE"
    #         break
    #     fi
    # done
    
    echo "ℹ️  Windows browser executables skipped (using Playwright Chromium instead)"
fi

# Add Linux profiles for dev service
if [ -d "$HOME/.config/google-chrome" ]; then
    echo "      - $HOME/.config/google-chrome:/home/app/.config/google-chrome:ro" >> "$OVERRIDE_FILE"
fi
if [ -d "$HOME/.mozilla/firefox" ]; then
    echo "      - $HOME/.mozilla/firefox:/home/app/.mozilla/firefox:ro" >> "$OVERRIDE_FILE"
fi

# Add Windows profiles for dev service if on WSL
if [ "$IS_WSL" = true ] && [ -n "$WINDOWS_USER" ]; then
    WINDOWS_CHROME_PROFILE="/mnt/c/Users/$WINDOWS_USER/AppData/Local/Google/Chrome/User Data"
    if [ -d "$WINDOWS_CHROME_PROFILE" ]; then
        echo "      - $WINDOWS_CHROME_PROFILE:/home/app/.config/google-chrome-windows:ro" >> "$OVERRIDE_FILE"
    fi
    
    WINDOWS_FIREFOX_PROFILE="/mnt/c/Users/$WINDOWS_USER/AppData/Roaming/Mozilla/Firefox"
    if [ -d "$WINDOWS_FIREFOX_PROFILE" ]; then
        echo "      - $WINDOWS_FIREFOX_PROFILE:/home/app/.mozilla/firefox-windows:ro" >> "$OVERRIDE_FILE"
    fi
fi

# Add environment for dev service
cat >> "$OVERRIDE_FILE" << EOF
    environment:
      - PYTHONUNBUFFERED=1
      - FLASK_ENV=development
      - DISPLAY=\${DISPLAY:-:0}
      - PATH=/usr/bin:/usr/local/bin:/bin
      - IS_WSL=$IS_WSL
EOF

echo ""
echo "✅ Docker setup complete!"
echo "📄 Created: $OVERRIDE_FILE"

if [ "$IS_WSL" = true ]; then
    echo ""
    echo "🪟 WSL-specific configuration applied:"
    echo "   • Port 8000 explicitly mapped for Windows host access"
    echo "   • Windows browsers and profiles detected and mounted"
    echo "   • Network configuration optimized for WSL"
    echo ""
    echo "🌐 Access the application from Windows at:"
    echo "   http://localhost:8000"
    echo "   http://127.0.0.1:8000"
fi

echo ""
echo "🚀 You can now run:"
echo "   docker-compose up --build"
echo ""
echo "💡 The override file will automatically mount only the browsers and profiles"
echo "   that exist on your system." 