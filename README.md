# 🚀 AutoMail Agent

A FastAPI web application for automating Gmail through browser automation. Send emails programmatically with a beautiful web interface and REST API.

## ✨ Features

- 🌐 **Beautiful Web Interface** - Modern, responsive UI for sending emails
- 📧 **Gmail Automation** - Send emails through Gmail web interface using browser automation
- 🔌 **REST API** - Full API for programmatic email sending
- 📚 **Auto-generated Documentation** - Interactive API docs with Swagger UI
- 🎯 **Email Validation** - Built-in email format and content validation
- 📎 **Attachment Support** - Send emails with file attachments
- 🔧 **Browser Profile Management** - Use different browser profiles
- ⚡ **Fast & Reliable** - Built with FastAPI for high performance

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Chrome browser
- Gmail account

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd automail-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install browser support**
   ```bash
   playwright install
   ```

4. **Start the application**
   ```bash
   python main.py
   ```

5. **Open your browser**
   Navigate to: http://localhost:8000

## 🌐 Available URLs

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Alternative API Docs**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

## 📧 Usage

### Web Interface
1. Fill out the email form with recipient, subject, and body
2. Choose priority level (Low, Normal, High)
3. Optionally select a browser profile
4. Add file attachments if needed
5. Click "Send Email"
6. Login to Gmail if prompted
7. Watch your email get sent automatically!

### API Usage

**Send Email**
```bash
curl -X POST "http://localhost:8000/api/email/send" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "to=recipient@example.com&subject=Hello&body=Test message&priority=normal"
```

**Validate Email**
```bash
curl -X POST "http://localhost:8000/api/email/validate" \
  -H "Content-Type: application/json" \
  -d '{"to":"test@example.com","subject":"Test","body":"Hello World","priority":"normal"}'
```

**Get Profiles**
```bash
curl "http://localhost:8000/api/profiles/"
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only e2e tests
pytest tests/e2e/

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_email_models.py
```

## 📁 Project Structure

```
automail-agent/
├── src/                    # Source code
│   ├── api/               # FastAPI application
│   │   ├── models/        # Pydantic models
│   │   ├── routes/        # API routes
│   │   ├── services/      # Business logic
│   │   └── templates/     # HTML templates
│   ├── browser/           # Browser automation
│   └── schemas/           # Data schemas
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── e2e/              # End-to-end tests
│   └── conftest.py       # Test configuration
├── main.py               # Application entry point
├── requirements.txt      # Dependencies
└── pytest.ini          # Test configuration
```

## 🔧 Configuration

The application uses environment variables for configuration:

- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)
- `DEBUG`: Debug mode (default: False)

## 🛠️ Development

### Setting up development environment

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run tests:
   ```bash
   pytest
   ```

4. Start development server:
   ```bash
   python main.py
