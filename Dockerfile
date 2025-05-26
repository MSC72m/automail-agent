# Multi-stage build for AutoMail Agent
FROM python:3.11-bookworm as base

# Set working directory
WORKDIR /app

# Install system dependencies for running browsers from host
RUN apt-get update && apt-get install -y \
    curl \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libgconf-2-4 \
    libxfixes3 \
    libxinerama1 \
    libxrandr2 \
    libasound2-dev \
    libpangocairo-1.0-0 \
    libatk1.0-dev \
    libcairo-gobject2 \
    libgtk-3-dev \
    libgdk-pixbuf2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (these will be used if host browsers aren't available)
RUN playwright install chromium

# Production stage
FROM base as production

# Copy application code
COPY src/ ./src/
COPY main.py ./

# Create non-root user
RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "main.py"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir watchdog

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Start with reload for development
CMD ["python", "main.py", "--reload"] 