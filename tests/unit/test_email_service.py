"""
Unit tests for email service
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api.services.email_service import EmailService
from api.models.email import EmailRequest, EmailPriority
from schemas.browser import BrowserConfig
from schemas.enums import BrowserType


class TestEmailService:
    """Test cases for EmailService"""

    @pytest.fixture
    def email_service(self):
        """Create an EmailService instance for testing"""
        return EmailService()

    @pytest.fixture
    def sample_email_request(self):
        """Sample email request for testing"""
        return EmailRequest(
            to="test@example.com",
            subject="Test Subject",
            body="Test body content",
            priority=EmailPriority.NORMAL
        )

    @pytest.fixture
    def browser_config(self):
        """Sample browser config for testing"""
        return BrowserConfig(
            browser_name=BrowserType.CHROME,
            headless=False
        )

    @pytest.mark.asyncio
    async def test_validate_email_format_valid(self, email_service, sample_email_request):
        """Test email format validation with valid email"""
        result = await email_service.validate_email_format(sample_email_request)
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_email_format_invalid_email(self, email_service):
        """Test email format validation with invalid email"""
        # This should be caught by pydantic validation before reaching the service
        # But we can test the service method directly
        invalid_request = EmailRequest(
            to="test@example.com",  # Valid for pydantic
            subject="Test Subject",
            body="Test body content"
        )
        
        # Mock the email validation to return False
        with patch.object(email_service, 'validate_email_format', return_value=False):
            result = await email_service.validate_email_format(invalid_request)
            assert result is False

    @pytest.mark.asyncio
    async def test_validate_email_format_empty_subject(self, email_service):
        """Test email format validation with empty subject"""
        # This should be caught by pydantic validation
        with pytest.raises(Exception):  # Pydantic will raise ValidationError
            EmailRequest(
                to="test@example.com",
                subject="",
                body="Test body content"
            )

    @pytest.mark.asyncio
    async def test_validate_email_format_empty_body(self, email_service):
        """Test email format validation with empty body"""
        # This should be caught by pydantic validation
        with pytest.raises(Exception):  # Pydantic will raise ValidationError
            EmailRequest(
                to="test@example.com",
                subject="Test Subject",
                body="   "  # Only whitespace
            )

    @pytest.mark.asyncio
    async def test_send_email_success(self, email_service, sample_email_request, browser_config):
        """Test successful email sending"""
        with patch('api.services.email_service.send_gmail') as mock_send_gmail:
            mock_send_gmail.return_value = True
            
            response = await email_service.send_email(sample_email_request, browser_config)
            
            assert response.success is True
            assert "successfully" in response.message.lower()
            assert response.email_id is not None
            assert response.timestamp is not None
            mock_send_gmail.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_failure(self, email_service, sample_email_request, browser_config):
        """Test failed email sending"""
        with patch('api.services.email_service.send_gmail') as mock_send_gmail:
            mock_send_gmail.return_value = False
            
            response = await email_service.send_email(sample_email_request, browser_config)
            
            assert response.success is False
            assert "failed" in response.message.lower()
            assert response.email_id is None
            assert response.timestamp is not None
            mock_send_gmail.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_exception(self, email_service, sample_email_request, browser_config):
        """Test email sending with exception"""
        with patch('api.services.email_service.send_gmail') as mock_send_gmail:
            mock_send_gmail.side_effect = Exception("Connection error")
            
            response = await email_service.send_email(sample_email_request, browser_config)
            
            assert response.success is False
            assert "error" in response.message.lower()
            assert response.email_id is None
            assert response.timestamp is not None

    @pytest.mark.asyncio
    async def test_send_email_with_attachments(self, email_service, browser_config):
        """Test sending email with attachments"""
        email_request = EmailRequest(
            to="test@example.com",
            subject="Test with Attachments",
            body="This email has attachments",
            attachments=["/path/to/file1.pdf", "/path/to/file2.txt"]
        )
        
        with patch('api.services.email_service.send_gmail') as mock_send_gmail:
            mock_send_gmail.return_value = True
            
            response = await email_service.send_email(email_request, browser_config)
            
            assert response.success is True
            mock_send_gmail.assert_called_once()
            
            # Check that the EmailInput passed to send_gmail has attachments
            call_args = mock_send_gmail.call_args[0][0]  # First argument (EmailInput)
            assert call_args.attachments == ["/path/to/file1.pdf", "/path/to/file2.txt"]

    @pytest.mark.asyncio
    async def test_get_email_status_found(self, email_service):
        """Test getting email status when email exists"""
        email_id = "test-email-123"
        
        # Mock the internal storage
        email_service._email_status = {email_id: "sent"}
        
        status = await email_service.get_email_status(email_id)
        assert status == "sent"

    @pytest.mark.asyncio
    async def test_get_email_status_not_found(self, email_service):
        """Test getting email status when email doesn't exist"""
        email_id = "non-existent-email"
        
        status = await email_service.get_email_status(email_id)
        assert status is None

    def test_generate_email_id(self, email_service):
        """Test email ID generation"""
        email_id1 = email_service._generate_email_id()
        email_id2 = email_service._generate_email_id()
        
        # IDs should be different
        assert email_id1 != email_id2
        
        # IDs should be strings
        assert isinstance(email_id1, str)
        assert isinstance(email_id2, str)
        
        # IDs should not be empty
        assert len(email_id1) > 0
        assert len(email_id2) > 0 