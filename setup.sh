#!/bin/bash

# AutoMail Agent - Linux/macOS Setup Script
# This script will set up the AutoMail Agent project and start the application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
}

# Function to check if browsers are installed
check_browsers() {
    CHROME_FOUND=false
    FIREFOX_FOUND=false
    
    # Check for Chrome
    if command_exists google-chrome || command_exists google-chrome-stable || command_exists chromium-browser; then
        CHROME_FOUND=true
        print_success "Chrome/Chromium browser found"
    fi
    
    # Check for Firefox
    if command_exists firefox; then
        FIREFOX_FOUND=true
        print_success "Firefox browser found"
    fi
    
    if [ "$CHROME_FOUND" = false ] && [ "$FIREFOX_FOUND" = false ]; then
        print_warning "No supported browsers found. Please install Chrome or Firefox."
        print_warning "The application will still start, but browser automation may not work."
    fi
}

# Main setup function
main() {
    echo "🚀 AutoMail Agent Setup Script"
    echo "================================"
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    check_python_version
    check_browsers
    
    # Check if git is installed
    if ! command_exists git; then
        print_error "Git is not installed. Please install Git and try again."
        exit 1
    fi
    print_success "Git found"
    
    echo ""
    
    # Get repository URL if not already in the directory
    if [ ! -f "requirements.txt" ]; then
        print_status "Repository not found in current directory."
        echo -n "Enter the repository URL (or press Enter to skip cloning): "
        read -r REPO_URL
        
        if [ -n "$REPO_URL" ]; then
            print_status "Cloning repository..."
            git clone "$REPO_URL" automail-agent
            cd automail-agent
            print_success "Repository cloned successfully"
        else
            print_error "No repository URL provided and requirements.txt not found in current directory."
            exit 1
        fi
    else
        print_success "Found existing project in current directory"
    fi
    
    # Create virtual environment
    print_status "Creating Python virtual environment..."
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf venv
    fi
    
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Python dependencies installed"
    
    # Install Playwright browsers
    print_status "Installing Playwright browsers (this may take a few minutes)..."
    playwright install
    print_success "Playwright browsers installed"
    
    # Create a simple start script
    print_status "Creating start script..."
    cat > start.sh << 'EOF'
#!/bin/bash
# AutoMail Agent Start Script

# Activate virtual environment
source venv/bin/activate

# Start the application
echo "🚀 Starting AutoMail Agent..."
python src/main.py
EOF
    
    chmod +x start.sh
    print_success "Start script created (start.sh)"
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo "================================"
    echo ""
    echo "📋 Next steps:"
    echo "1. Run the application:"
    echo "   ./start.sh"
    echo ""
    echo "   OR manually:"
    echo "   source venv/bin/activate"
    echo "   python src/main.py"
    echo ""
    echo "2. Open your browser and go to:"
    echo "   🌐 Web Interface: http://localhost:8000"
    echo "   📚 API Documentation: http://localhost:8000/api/docs"
    echo "   🔍 Health Check: http://localhost:8000/health"
    echo ""
    echo "3. For email automation, make sure you're logged into Gmail in your browser"
    echo ""
    
    # Ask if user wants to start the application now
    echo -n "Would you like to start the application now? (y/N): "
    read -r START_NOW
    
    if [ "$START_NOW" = "y" ] || [ "$START_NOW" = "Y" ]; then
        echo ""
        print_status "Starting AutoMail Agent..."
        python src/main.py
    else
        echo ""
        print_success "Setup complete! Run './start.sh' when you're ready to start the application."
    fi
}

# Run main function
main "$@" 