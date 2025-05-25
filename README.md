# AutoMail Agent

A lightweight web API for automated email sending through Gmail using browser automation. Leverages existing browser sessions to send emails without storing credentials.

## Quick Start

### Linux/macOS
```bash
curl -sSL https://raw.githubusercontent.com/your-repo/automail-agent/main/setup.sh | bash
```

### Windows
```cmd
curl -sSL https://raw.githubusercontent.com/your-repo/automail-agent/main/setup.bat -o setup.bat && setup.bat
```

### Docker
```bash
# Production mode
docker-compose up

# Development mode  
docker-compose --profile dev up automail-agent-dev

# Background
docker-compose up -d

# Stop
docker-compose down
```

## Usage

### Native
```bash
# Start server
./start.sh        # Linux/macOS
start.bat         # Windows

# API available at http://localhost:8000
```

### Docker
```bash
# Start in production mode
docker-compose up

# Start in development mode (with live reload)
docker-compose --profile dev up automail-agent-dev
```

**Send Email:**
```bash
curl -X POST http://localhost:8000/api/v1/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Test Email",
    "body": "Hello from AutoMail Agent!"
  }'
```

## How It Works

1. **Profile Management**: Creates temporary browser profiles, copies login data from your existing browser profiles
2. **Browser Automation**: Launches Chrome/Firefox with remote debugging, connects via Playwright
3. **Gmail Automation**: Navigates Gmail interface, fills compose form, sends email
4. **Session Isolation**: Each run uses a fresh temporary profile

## API Endpoints

```
POST /api/v1/email/send     # Send email
GET  /api/v1/profiles       # List available browser profiles  
GET  /health                # Health check
```

## Configuration

Browser profiles are automatically detected:
- **Chrome**: `~/.config/google-chrome/` (Linux), `%LOCALAPPDATA%\Google\Chrome\User Data` (Windows)
- **Firefox**: `~/.mozilla/firefox/` (Linux), `%APPDATA%\Mozilla\Firefox\Profiles` (Windows)

System profiles are filtered out automatically.

## Requirements

- Python 3.8+
- Chrome or Firefox
- Gmail account (must be logged in)

## Manual Setup

```bash
git clone <repo-url>
cd automail-agent
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python src/main.py
```

## Docker Details

The Docker setup includes:
- **Multi-stage build** for optimized images
- **Volume persistence** for data
- **Development mode** with live reload

Ports:
- `8000`: API server

## Architecture

```
src/
├── api/           # FastAPI routes and services
├── browser/       # Browser automation (launchers, mailer)
├── schemas/       # Pydantic models
└── utils/         # Logging, utilities
```

**Key components:**
- `BrowserLauncher`: Manages browser processes and profiles
- `GmailMailer`: Handles Gmail automation
- `FastAPI app`: REST API interface

## Notes

- Firefox support is experimental
- Requires manual Gmail login on first use
- Temporary profiles are cleaned up automatically
- No credentials stored - uses browser session cookies

