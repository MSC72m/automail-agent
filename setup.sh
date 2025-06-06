#!/bin/bash

# AutoMail Agent - Simple Setup Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    print_error "Python is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

print_success "Python found"

# Check if we're in project directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run this script from the project directory."
    exit 1
fi

print_info "Setting up virtual environment..."
if [ -d "venv" ]; then
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
source venv/bin/activate
print_success "Virtual environment created"

print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"


# Set up basic permissions
print_info "Setting up permissions..."
if [ -d "$HOME/.cache/ms-playwright" ]; then
    chmod -R 755 "$HOME/.cache/ms-playwright" 2>/dev/null || true
fi

# Allow X11 access if display exists
if [ -n "$DISPLAY" ]; then
    xhost +local: >/dev/null 2>&1 || true
fi

print_success "Permissions configured"

# Create simple start script
cat > start.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python3 -m main
EOF
chmod +x start.sh

print_success "Setup complete!"
echo "Run: ./start.sh or python3 -m main (after activating venv)" 