# AutoMail Agent

A beautiful web interface for sending emails through Gmail automation using browser sessions.

## Quick Start

### 1. Setup
```bash
# Linux/Mac
./setup.sh

# Windows
setup.bat
```

### 2. Run
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate.bat  # Windows

# Then run the application
python3 -m main
```

Visit `http://localhost:8000` to use the web interface or send API requests.

## Features

- **Web Interface**: Clean, modern UI for sending emails
- **API Endpoints**: RESTful API for programmatic access
- **Browser Automation**: Uses your existing Gmail sessions with Playwright
- **Profile Management**: Automatically detects browser profiles
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

## Browser Profile Detection

Profiles are automatically detected from:
- **Chrome**: `~/.config/google-chrome/` (Linux), `%LOCALAPPDATA%\Google\Chrome\User Data` (Windows)
- **Firefox**: `~/.mozilla/firefox/` (Linux), `%APPDATA%\Mozilla\Firefox\Profiles` (Windows)

## Project Structure

```
automail-agent/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── setup.sh               # Linux/Mac setup script
├── setup.bat              # Windows setup script
├── start.sh               # Linux/Mac start script (created by setup)
├── start.bat              # Windows start script (created by setup)
├── .env.example           # Environment variables template
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Docker image definition
├── src/                   # Source code
│   ├── app.py            # FastAPI application
│   ├── dependencies.py   # Dependency injection
│   ├── routes/           # API endpoints
│   │   ├── email_routes.py
│   │   └── profile_routes.py
│   ├── services/         # Business logic
│   │   ├── email_service.py
│   │   └── profile_service.py
│   ├── browser/          # Browser automation
│   │   ├── lunchers.py   # Browser launcher
│   │   ├── mailer.py     # Gmail automation
│   │   ├── finders.py    # Browser detection
│   │   └── profile_manager.py
│   ├── schemas/          # Data models and configuration
│   │   ├── config.py     # Application configuration
│   │   ├── browser.py    # Browser configuration
│   │   ├── email.py      # Email models
│   │   └── enums.py      # Enumerations
│   ├── static/           # Static files (CSS, JS)
│   ├── templates/        # Jinja2 templates
│   │   └── index.html
│   ├── utils/            # Utilities and logging
│   │   └── logger.py
│   └── agents/           # Agent implementations
├── data/                 # Data storage (created by setup)
├── logs/                 # Application logs (created by setup)
└── venv/                 # Virtual environment (created by setup)
```

## Requirements

- Python 3.8+
- Chrome or Firefox browser
- Gmail account (must be logged in to browser)

## Setup Details

The setup scripts automatically:
- Create a Python virtual environment
- Install all Python dependencies including Playwright
- Set up proper permissions for browser automation
- Create start scripts for easy launching

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
# Activate virtual environment
source venv/bin/activate

# Run the application
python3 -m main
```

## Troubleshooting

### Common Issues

1. **"Module not found"**: Make sure virtual environment is activated (`source venv/bin/activate`)
2. **No profiles found**: Ensure Chrome/Firefox is installed and you're logged into Gmail
3. **Browser timeout**: Check your internet connection and Gmail login status
4. **Permission errors**: Re-run setup script or ensure browser profile directories are readable
5. **Playwright browser not found**: Run `playwright install` in activated virtual environment

### Logs

Check logs for detailed error information in the `logs/` directory.

