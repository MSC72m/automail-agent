# AutoMail Agent

A web application for automated email sending through Gmail using browser automation. Features a clean web interface and API for sending emails without storing credentials.

## Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/MSC72m/automail-agent.git
cd automail-agent
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env if needed (defaults work for most cases)
```

### 3. Run
```bash
python src/main.py
```

Visit `http://localhost:8000` to use the web interface or send API requests.

## Features

- **Web Interface**: Clean, modern UI for sending emails
- **API Endpoints**: RESTful API for programmatic access
- **Browser Automation**: Uses your existing Gmail sessions
- **Profile Management**: Automatically detects browser profiles
- **Configuration**: Unified config system with environment variables
- **No Credentials**: Leverages existing browser sessions

## How It Works

1. **Profile Detection**: Automatically finds your Chrome/Firefox profiles
2. **Session Reuse**: Uses your existing Gmail login sessions
3. **Browser Automation**: Launches browser with Playwright, navigates Gmail
4. **Email Sending**: Fills compose form and sends email
5. **Clean Isolation**: Each operation uses temporary profiles

## Web Interface

Access the web interface at `http://localhost:8000`:

- **Send Email**: Simple form to compose and send emails
- **Profile Selection**: Choose from detected browser profiles
- **Headless Mode**: Option to run browser in background
- **Real-time Feedback**: Status updates and error messages

## API Usage

### Send Email
```bash
curl -X POST http://localhost:8000/send-email \
  -F "to=recipient@example.com" \
  -F "subject=Test Email" \
  -F "body=Hello from AutoMail Agent!" \
  -F "headless=true" \
  -F "browser_name=chrome" \
  -F "profile_name=Profile 1"
```

### Get Browser Profiles
```bash
curl http://localhost:8000/profiles/chrome
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Configuration

The application uses a unified configuration system. All settings can be configured via environment variables in `.env`:

### Application Settings
```env
# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# Application
APP_TITLE=AutoMail Agent
APP_DESCRIPTION=Automated email sending through Gmail

# Browser
BROWSER_TIMEOUT=30000
HEADLESS=false

# Logging
LOG_LEVEL=INFO
```

### Browser Profile Detection

Profiles are automatically detected from:
- **Chrome**: `~/.config/google-chrome/` (Linux), `%LOCALAPPDATA%\Google\Chrome\User Data` (Windows)
- **Firefox**: `~/.mozilla/firefox/` (Linux), `%APPDATA%\Mozilla\Firefox\Profiles` (Windows)

## Project Structure

```
src/
├── main.py              # Application entry point
├── api/                 # Web interface and API
│   ├── app.py          # FastAPI application
│   ├── routes/         # API endpoints
│   ├── services/       # Business logic
│   └── templates/      # Jinja2 templates
├── browser/            # Browser automation
├── schemas/            # Data models and configuration
├── utils/              # Utilities and logging
└── config/             # Configuration management
```

## Requirements

- Python 3.8+
- Chrome or Firefox browser
- Gmail account (must be logged in to browser)

## Docker Support

### Quick Docker Setup
```bash
# Setup browser detection (required)
./setup-docker.sh

# Start application
docker-compose up --build

# Development mode with live reload
docker-compose --profile dev up automail-dev
```

### Why setup-docker.sh?

The setup script is essential because:
- **Dynamic Detection**: Finds browsers installed on your system
- **Profile Mounting**: Locates your browser profiles for session reuse
- **Compatibility**: Works across different Linux distributions and setups
- **Error Prevention**: Only mounts what exists, preventing Docker errors

## Development

### Running in Development Mode
```bash
# With auto-reload
ENVIRONMENT=development python src/main.py

# Or with Docker
docker-compose --profile dev up automail-dev
```

### Environment Variables
- `ENVIRONMENT=development` enables auto-reload and debug logging
- `LOG_LEVEL=DEBUG` for detailed logging
- `HEADLESS=false` to see browser automation

## Troubleshooting

### Common Issues

1. **"Static file not found"**: Restart the application, conflicting routes have been fixed
2. **No profiles found**: Ensure Chrome/Firefox is installed and you're logged into Gmail
3. **Browser timeout**: Increase `BROWSER_TIMEOUT` in `.env`
4. **Permission errors**: Ensure browser profile directories are readable

### Logs

Check logs for detailed error information:
```bash
# Application logs show browser automation steps
# Set LOG_LEVEL=DEBUG for verbose output
```

