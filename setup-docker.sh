#!/bin/bash

# AutoMail Agent Docker Setup Script
# This script detects available browsers and creates docker-compose override

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

# Check for Chrome/Chromium browsers
add_browser_mount "/usr/bin/google-chrome" "automail-headless"
add_browser_mount "/usr/bin/google-chrome-stable" "automail-headless"
add_browser_mount "/usr/bin/chromium" "automail-headless"
add_browser_mount "/usr/bin/chromium-browser" "automail-headless"
add_browser_mount "/snap/bin/chromium" "automail-headless"

# Check for Firefox
add_browser_mount "/usr/bin/firefox" "automail-headless"
add_browser_mount "/usr/bin/firefox-esr" "automail-headless"

echo ""
echo "📁 Checking for browser profiles..."

# Check for browser profiles
add_profile_mount "$HOME/.config/google-chrome" "/home/app/.config/google-chrome"
add_profile_mount "$HOME/.mozilla/firefox" "/home/app/.mozilla/firefox"

# Add environment variables
cat >> "$OVERRIDE_FILE" << EOF
    environment:
      - DISPLAY=\${DISPLAY:-:0}
      - BROWSER_HEADLESS=true
      - PATH=/usr/bin:/usr/local/bin:/bin

  automail-dev:
    volumes:
      - .:/app
      - ./data:/app/data
      # X11 socket
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
EOF

# Add the same browser mounts for dev service
echo "🔄 Adding browser mounts for development service..."

# Re-check browsers for dev service
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

# Add profiles for dev service
if [ -d "$HOME/.config/google-chrome" ]; then
    echo "      - $HOME/.config/google-chrome:/home/app/.config/google-chrome:ro" >> "$OVERRIDE_FILE"
fi
if [ -d "$HOME/.mozilla/firefox" ]; then
    echo "      - $HOME/.mozilla/firefox:/home/app/.mozilla/firefox:ro" >> "$OVERRIDE_FILE"
fi

# Add environment for dev service
cat >> "$OVERRIDE_FILE" << EOF
    environment:
      - PYTHONUNBUFFERED=1
      - FLASK_ENV=development
      - DISPLAY=\${DISPLAY:-:0}
      - PATH=/usr/bin:/usr/local/bin:/bin
EOF

echo ""
echo "✅ Docker setup complete!"
echo "📄 Created: $OVERRIDE_FILE"
echo ""
echo "🚀 You can now run:"
echo "   docker-compose up --build"
echo ""
echo "💡 The override file will automatically mount only the browsers and profiles"
echo "   that exist on your system." 