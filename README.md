# AutoMail Agent

Browser automation for Gmail email sending. Uses Playwright to control Chrome/Firefox and send emails through Gmail's web interface.

## What it does

- Automates Gmail through browser automation (no SMTP)
- Creates temporary browser profiles for each session
- Supports Chrome and Firefox on Windows/Linux
- Provides REST API and web interface
- Handles browser profile management automatically

## Quick Setup

**Linux/macOS:**
```bash
git clone <repo-url> automail-agent
cd automail-agent
chmod +x setup.sh && ./setup.sh
```

**Windows:**
```cmd
git clone <repo-url> automail-agent
cd automail-agent
setup.bat
```

The setup script handles everything: virtual environment, dependencies, Playwright browsers.

## Usage

### Start the server
```bash
./start.sh          # Linux/macOS
start.bat           # Windows
```

### Send email via API
```bash
curl -X POST "http://localhost:8000/api/v1/email/send" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "test@example.com",
    "subject": "Test",
    "body": "Hello world"
  }'
```

### Web interface
- **App**: http://localhost:8000
- **API docs**: http://localhost:8000/api/docs

## How it works

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
playwright install
python src/main.py
```

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

