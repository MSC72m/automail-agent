# AutoMail Agent

A beautiful web interface for sending emails through Gmail automation using your existing browser sessions via **Chrome DevTools Protocol (CDP)**.

## ⚡ Quick Start

### Native Setup
```bash
# Linux/Mac
./setup.sh

# Windows
setup.bat
```

### Docker Setup
```bash
# Essential: Detects your browsers and profiles
./setup-docker.sh

# Start application
docker-compose up --build
```

### Run
```bash
# Activate environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate.bat  # Windows

# Start application
python3 -m main
```

Visit `http://localhost:8000` for the web interface.

## 🎯 How It Works

### Chrome DevTools Protocol (CDP)
AutoMail Agent uses **CDP** to communicate with your browser instances. CDP is a debugging protocol that allows external applications to:
- Connect to running browser instances
- Control page navigation and interactions
- Execute JavaScript and DOM manipulation
- Reuse existing authentication sessions

This eliminates the need for storing Gmail credentials - we simply reuse your existing logged-in browser sessions.

### Detailed Process Flow
1. **System Detection**: Scans system for browser executables and profile directories
2. **Profile Isolation**: Creates temporary profile copies to avoid corrupting active sessions
3. **Browser Launch**: Starts browser with CDP debugging enabled (`--remote-debugging-port=9222`)
4. **Security Bypass**: Disables browser security features that block automation
5. **CDP Connection**: Playwright connects to the debug port for browser control
6. **Session Authentication**: Leverages existing Gmail cookies and session data
7. **DOM Navigation**: Automated interaction with Gmail's web interface
8. **Email Composition**: Fills recipient, subject, and body fields programmatically
9. **Send Execution**: Triggers Gmail's send mechanism via JavaScript
10. **Clean Termination**: Closes browser, cleans temporary profiles, releases ports

## 📋 Platform Support

| Platform | Chrome | Firefox | Docker | Notes |
|----------|--------|---------|--------|-------|
| **Linux** | ✅ Full | ⚠️ Basic | ✅ Recommended | Best support |
| **Windows** | ❌ Broken | ❌ Broken | ❌ Limited | **Does not work yet** |
| **WSL** | ⚠️ Limited | ❌ Basic | ⚠️ Complex | Use Docker with caution |

### Known Limitations
- **Windows**: Native Windows support is **completely broken** due to incomplete subprocess method implementations for process management
- **Firefox**: Basic support only - not fully tested across all email scenarios
- **Docker**: Incomplete implementation, overly complicated setup process
- **WSL Users**: Docker setup is **especially difficult** - Chrome support very limited
- **Attachments**: Not currently supported

## 🛠️ Setup Methods

### `setup-docker.sh` - Essential but Complex

The Docker setup script performs critical system detection but has limitations:

```bash
./setup-docker.sh
```

**What it does:**
- **Dynamic Browser Detection**: Finds installed browsers (Chrome, Firefox, Edge)
- **Profile Path Discovery**: Locates your browser profiles for session reuse
- **Creates `docker-compose.override.yml`**: Dynamically generates Docker volume mounts
- **Cross-Platform Compatibility**: Handles Linux, WSL, and Docker environments
- **WSL Integration**: Attempts to detect Windows browsers (with limited success)

**Docker Limitations:**
- **Incomplete Implementation**: Many features don't work properly in containers
- **Complex Setup**: Requires manual intervention for WSL environments
- **Chrome Restrictions**: Limited Chrome functionality in Docker, especially on WSL
- **Profile Mounting Issues**: Browser profiles often have permission conflicts in containers

**Without this script**, Docker containers can't access your browser profiles or executables, making email automation impossible.

### Standard Setup Scripts
- `setup.sh` / `setup.bat`: Creates virtual environment and installs dependencies
- **Linux recommended**: Works best on native Linux installations
- **Windows users**: Currently no working solution available

## 🚧 Technical Challenges

### Browser Instance Control
- **Process Hijacking**: Taking control of running browser instances without disrupting user sessions
- **Port Conflicts**: Managing CDP debug ports when multiple browser instances exist
- **Profile Locking**: Browsers lock profile directories, requiring careful copying/isolation
- **Instance Detection**: Identifying which browser processes belong to which profiles

### Security Circumvention
- **Same-Origin Policy**: Bypassing browser security to inject automation scripts
- **CSRF Protection**: Working around Gmail's CSRF tokens and security headers
- **Automation Detection**: Evading Gmail's bot detection mechanisms
- **Headless Limitations**: Many security features break in headless mode, forcing visible browser use

### Process Management
- **Windows Subprocess**: Windows process creation flags completely different from Unix
- **Browser Lifecycle**: Properly starting, monitoring, and terminating browser processes
- **Zombie Processes**: Preventing orphaned browser processes from consuming resources
- **Signal Handling**: Cross-platform process termination requires different approaches

### Profile Handling
- **Permission Issues**: Browser profiles have strict file system permissions
- **Session Corruption**: Risk of corrupting active user sessions during profile copying
- **Database Locks**: Chrome/Firefox use SQLite databases that can't be copied while locked
- **Cross-Platform Paths**: Profile locations vary dramatically between operating systems

### Browser Compatibility
- **Firefox CDP**: Firefox's CDP implementation is incomplete compared to Chrome
- **Version Compatibility**: Different browser versions have varying CDP feature support
- **Extension Conflicts**: Browser extensions can interfere with automation scripts
- **Update Interference**: Browser auto-updates can break automation compatibility

## 🚀 Features

- **Web Interface**: Clean, modern UI for composing emails
- **API Endpoints**: RESTful API for programmatic access
- **Profile Management**: Automatic browser profile detection
- **Session Reuse**: No credential storage needed
- **Cross-Platform**: Linux support only (Windows planned but broken)

## 📁 Project Structure

```
automail-agent/
├── src/
│   ├── browser/          # Browser automation core
│   │   ├── lunchers.py   # CDP connection & process management
│   │   ├── mailer.py     # Gmail interface automation
│   │   ├── finders.py    # Browser detection
│   │   └── profile_manager.py
│   ├── routes/           # FastAPI endpoints
│   ├── services/         # Business logic
│   ├── schemas/          # Data models
│   └── static/           # Web UI assets
├── setup.sh / setup.bat  # Native setup
├── setup-docker.sh      # Docker environment setup
└── docker-compose.yml   # Container orchestration
```

## 🔧 API Usage

### Send Email
```bash
curl -X POST http://localhost:8000/send-email \
  -F "to=recipient@example.com" \
  -F "subject=Test Email" \
  -F "body=Hello from AutoMail!" \
  -F "headless=true" \
  -F "browser_name=chrome"
```

### Get Profiles
```bash
curl http://localhost:8000/profiles/chrome
```

## 🐳 Docker Development

```bash
# Development with live reload
docker-compose --profile dev up automail-dev

# Production mode
docker-compose up automail-headless
```

**Note**: Docker implementation is incomplete and especially problematic for WSL users.

## ⚠️ Troubleshooting

- **"No profiles found"**: Ensure you're logged into Gmail in your browser
- **"Browser timeout"**: Check internet connection and Gmail login status  
- **"Permission errors"**: Re-run setup scripts or check profile directory permissions
- **"CDP connection failed"**: Verify no other applications are using the debug port
- **WSL Docker issues**: Consider using native Linux instead of WSL + Docker

---

**Requirements**: Python 3.8+, Chrome browser (Linux only), Gmail account (logged in)  
**Status**: ⚠️ **Linux only** - Windows support broken, Docker incomplete

