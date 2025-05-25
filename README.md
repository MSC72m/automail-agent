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
# IMPORTANT: Run setup script first to detect your browsers
./setup-docker.sh

# Then start the application
docker-compose up --build

# Development mode  
docker-compose --profile dev up automail-dev

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
# STEP 1: Setup browser detection (required)
./setup-docker.sh

# STEP 2: Start in production mode
docker-compose up --build

# Start in development mode (with live reload)
docker-compose --profile dev up automail-dev
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

### Environment Variables

AutoMail Agent uses a unified configuration system with environment variables. Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

#### Server Configuration
- `HOST` - Server host (default: `0.0.0.0`)
- `PORT` - Server port (default: `8000`)
- `RELOAD` - Enable auto-reload in development (default: `true`)
- `ENVIRONMENT` - Application environment: `development`, `production`, `testing` (default: `development`)

#### Logging Configuration
- `LOG_LEVEL` - Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default: `INFO`)
- `LOG_FORMAT` - Log format string (default: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`)
- `LOG_DATE_FORMAT` - Log date format (default: `%Y-%m-%d %H:%M:%S`)

#### API Configuration
- `API_TITLE` - API title (default: `AutoMail Agent API`)
- `API_DESCRIPTION` - API description
- `API_VERSION` - API version (default: `1.0.0`)

#### Browser Configuration
- `BROWSER_TIMEOUT` - Browser timeout in milliseconds (default: `30000`)
- `HEADLESS` - Run browser in headless mode (default: `false`)

### Browser Profile Detection

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

# Copy and configure environment variables
cp .env.example .env
# Edit .env as needed

python src/main.py
```

## Docker Details

### Why the setup-docker.sh Script?

The `setup-docker.sh` script is **essential** for Docker deployment because:

1. **Dynamic Browser Detection**: Different systems have browsers installed in different locations
   - Some have Chrome at `/usr/bin/google-chrome`
   - Others have Chromium at `/usr/bin/chromium` 
   - Some use Snap packages at `/snap/bin/chromium`
   - Firefox might be at `/usr/bin/firefox` or `/usr/bin/firefox-esr`

2. **Profile Location Variance**: Browser profiles are stored in different paths per user
   - Chrome: `~/.config/google-chrome/` (varies by user)
   - Firefox: `~/.mozilla/firefox/` (varies by user)

3. **Avoiding Mount Errors**: Docker fails if you try to mount files/directories that don't exist
   - Static docker-compose.yml would break on systems missing certain browsers
   - The script only mounts what actually exists on your system

### How setup-docker.sh Works

```bash
./setup-docker.sh
```

The script:
1. **Scans** your system for installed browsers (`google-chrome`, `chromium`, `firefox`, etc.)
2. **Detects** your browser profile directories (`~/.config/google-chrome`, `~/.mozilla/firefox`)
3. **Generates** a `docker-compose.override.yml` file with only the browsers/profiles found
4. **Mounts** your host browsers and profiles into the container so the app can use your existing Gmail sessions

**Example output:**
```
🔍 Detecting available browsers on host system...

🌐 Checking for browser executables...
✅ Found: /usr/bin/google-chrome
❌ Not found: /usr/bin/chromium
✅ Found: /usr/bin/firefox

📁 Checking for browser profiles...
✅ Found profile: /home/user/.config/google-chrome
✅ Found profile: /home/user/.mozilla/firefox

✅ Docker setup complete!
📄 Created: docker-compose.override.yml
```

### Docker Architecture

The Docker setup includes:
- **Multi-stage build** for optimized images
- **Host browser mounting** for using your existing browser sessions
- **Volume persistence** for data
- **Development mode** with live reload
- **Network host mode** to avoid networking issues

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

- **Docker users**: Always run `./setup-docker.sh` before `docker-compose up`
- Firefox support is experimental
- Requires manual Gmail login on first use
- Temporary profiles are cleaned up automatically
- No credentials stored - uses browser session cookies

