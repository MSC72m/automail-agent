# AutoMail Agent

An intelligent email automation system that uses browser automation to send emails through Gmail's web interface. Supports Chrome and Firefox browsers on Windows and Linux.

## Features

- 🌐 **Web-based Email Sending** - Uses browser automation to send emails through Gmail
- 🔧 **Multi-browser Support** - Works with Chrome and Firefox
- 🖥️ **Cross-platform** - Supports Windows and Linux
- 🔒 **Smart Profile Management** - Handles browser profiles with automatic filtering
- 🗂️ **Temporary Automation Profiles** - Creates unique temporary profiles for each session
- 🎯 **Smart Selectors** - Adapts to different Gmail interface languages
- 📊 **API Interface** - RESTful API for integration with other systems
- 🔍 **Comprehensive Logging** - Detailed logging for debugging and monitoring

## Profile Management

### Automatic Profile Filtering
- Filters out system profiles like "Default Profile", "System Profile", and "Guest Profile"
- Shows only user-created profiles in the dropdown
- Always includes "Default" option for basic usage

### Temporary Automation Profiles
- Creates unique temporary directories for each browser session using `tempfile.mkdtemp()`
- Automatically cleans up after browser sessions
- No manual directory management required
- Copies essential login data from selected source profile

### Headless Mode Restrictions
- Default profile cannot be used in headless mode (GUI required for login)
- Headless toggle is automatically disabled when Default profile is selected
- Specific user profiles can be used in both headless and non-headless modes

## Quick Start

### Prerequisites

- Python 3.8+
- Chrome or Firefox browser installed
- Gmail account

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd automail-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

### Basic Usage

#### Using the API

1. Start the API server:
```bash
python -m uvicorn src.api.app:app --reload
```

2. Send an email via API:
```bash
curl -X POST "http://localhost:8000/api/v1/email/send" \
     -H "Content-Type: application/json" \
     -d '{
       "recipient": "recipient@example.com",
       "subject": "Test Email",
       "body": "This is a test email sent via AutoMail Agent"
     }'
```

#### Direct Usage

```python
import asyncio
from src.browser.mailer import GmailMailer
from src.schemas.email import EmailInput
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType

async def send_email():
    email_data = EmailInput(
        recipient="recipient@example.com",
        subject="Test Email",
        body="Hello from AutoMail Agent!"
    )
    
    browser_config = BrowserConfig(
        browser_name=BrowserType.CHROME,
        headless=False,
        profile_name="Profile 1"  # Use specific profile
    )
    
    async with GmailMailer(browser_config) as mailer:
        await mailer.connect_to_gmail()
        success = await mailer.send_email(email_data)
        print(f"Email sent: {success}")

asyncio.run(send_email())
```

## API Documentation

### Send Email
- **Endpoint**: `POST /api/v1/email/send`
- **Body**: 
  ```json
  {
    "recipient": "email@example.com",
    "subject": "Email Subject",
    "body": "Email content",
    "profile_name": "Profile 1",
    "headless": false
  }
  ```

### Get Available Profiles
- **Endpoint**: `GET /api/v1/profiles/available`
- **Response**: List of available browser profiles (filtered)

### Health Check
- **Endpoint**: `GET /health`
- **Response**: System health status

## Configuration

The system supports various configuration options:

### Browser Configuration
- **Browser Type**: Chrome or Firefox
- **Headless Mode**: Run with or without GUI (restricted for Default profile)
- **Profile Management**: Use specific browser profiles with automatic filtering

### Supported Platforms
- **Windows**: Full support for Chrome and Firefox
- **Linux**: Full support for Chrome and Firefox

## Architecture

The system is built with a modular architecture:

- **Browser Module**: Handles browser automation and profile management
- **API Module**: Provides RESTful endpoints for email operations
- **Schemas**: Data validation and type definitions
- **Services**: Business logic for email and profile operations

## Technical Details

### Profile System
- Uses `tempfile.mkdtemp()` for automatic temporary directory creation
- Copies essential browser data (cookies, login data, preferences) from source profiles
- Automatically filters out system and unwanted profiles
- No manual cleanup required - OS handles temporary directory cleanup

### Browser Support
- Chrome: Supports all user profiles, filters out system profiles
- Firefox: Reads from `profiles.ini`, supports custom profiles
- Both browsers create isolated automation profiles in temp directories
**Note that FireFox is not fully tested and isn't ready to be used**

## Troubleshooting

### Common Issues

1. **Browser not found**: Ensure Chrome or Firefox is installed and accessible
2. **Profile issues**: Check browser profile permissions and paths
3. **Gmail login**: Manual login may be required on first use
4. **Headless restrictions**: Use specific profiles for headless mode, not Default

