"""
Pytest configuration and shared fixtures for AutoMail Agent tests
"""

import pytest
import asyncio
import sys
import os
from typing import AsyncGenerator
from fastapi.testclient import TestClient

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    from api.app import app
    return TestClient(app)

@pytest.fixture
def sample_email_data():
    """Sample email data for testing."""
    return {
        "to": "test@example.com",
        "subject": "Test Email Subject",
        "body": "This is a test email body with some content.",
        "priority": "normal",
        "profile_name": None,
        "attachments": None
    }

@pytest.fixture
def sample_email_with_attachments():
    """Sample email data with attachments for testing."""
    return {
        "to": "test@example.com",
        "subject": "Test Email with Attachments",
        "body": "This email has attachments.",
        "priority": "high",
        "profile_name": "default",
        "attachments": ["/path/to/file1.pdf", "/path/to/file2.txt"]
    } 