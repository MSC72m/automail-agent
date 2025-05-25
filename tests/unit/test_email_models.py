"""
Unit tests for email models and validation
"""

import pytest
from pydantic import ValidationError
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api.models.email import EmailRequest, EmailResponse, EmailPriority


class TestEmailRequest:
    """Test cases for EmailRequest model"""

    def test_valid_email_request(self):
        """Test creating a valid email request"""
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "body": "Test body content"
        }
        
        email_request = EmailRequest(**email_data)
        
        assert email_request.to == "test@example.com"
        assert email_request.subject == "Test Subject"
        assert email_request.body == "Test body content"
        assert email_request.priority == EmailPriority.NORMAL
        assert email_request.profile_name is None
        assert email_request.attachments is None

    def test_email_request_with_all_fields(self):
        """Test creating an email request with all fields"""
        email_data = {
            "to": "user@domain.com",
            "subject": "Important Meeting",
            "body": "Please attend the meeting tomorrow.",
            "priority": "high",
            "profile_name": "work_profile",
            "attachments": ["/path/to/document.pdf", "/path/to/image.jpg"]
        }
        
        email_request = EmailRequest(**email_data)
        
        assert email_request.to == "user@domain.com"
        assert email_request.subject == "Important Meeting"
        assert email_request.body == "Please attend the meeting tomorrow."
        assert email_request.priority == EmailPriority.HIGH
        assert email_request.profile_name == "work_profile"
        assert email_request.attachments == ["/path/to/document.pdf", "/path/to/image.jpg"]

    def test_invalid_email_address(self):
        """Test validation with invalid email address"""
        email_data = {
            "to": "invalid-email",
            "subject": "Test Subject",
            "body": "Test body content"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EmailRequest(**email_data)
        
        assert "value is not a valid email address" in str(exc_info.value)

    def test_empty_subject(self):
        """Test validation with empty subject"""
        email_data = {
            "to": "test@example.com",
            "subject": "",
            "body": "Test body content"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EmailRequest(**email_data)
        
        assert "ensure this value has at least 1 characters" in str(exc_info.value)

    def test_empty_body(self):
        """Test validation with empty body"""
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "body": "   "  # Only whitespace
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EmailRequest(**email_data)
        
        assert "Email body cannot be empty" in str(exc_info.value)

    def test_invalid_priority(self):
        """Test validation with invalid priority"""
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "body": "Test body content",
            "priority": "invalid_priority"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EmailRequest(**email_data)
        
        assert "value is not a valid enumeration member" in str(exc_info.value)

    def test_invalid_attachments(self):
        """Test validation with invalid attachments"""
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "body": "Test body content",
            "attachments": ["", "  "]  # Empty strings
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EmailRequest(**email_data)
        
        assert "Attachment paths must be non-empty strings" in str(exc_info.value)

    def test_subject_too_long(self):
        """Test validation with subject that's too long"""
        email_data = {
            "to": "test@example.com",
            "subject": "x" * 201,  # Exceeds 200 character limit
            "body": "Test body content"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EmailRequest(**email_data)
        
        assert "ensure this value has at most 200 characters" in str(exc_info.value)


class TestEmailResponse:
    """Test cases for EmailResponse model"""

    def test_valid_email_response(self):
        """Test creating a valid email response"""
        response_data = {
            "success": True,
            "message": "Email sent successfully",
            "email_id": "12345",
            "timestamp": "2023-12-01T10:00:00Z"
        }
        
        email_response = EmailResponse(**response_data)
        
        assert email_response.success is True
        assert email_response.message == "Email sent successfully"
        assert email_response.email_id == "12345"
        assert email_response.timestamp == "2023-12-01T10:00:00Z"

    def test_email_response_without_email_id(self):
        """Test creating an email response without email_id"""
        response_data = {
            "success": False,
            "message": "Failed to send email",
            "timestamp": "2023-12-01T10:00:00Z"
        }
        
        email_response = EmailResponse(**response_data)
        
        assert email_response.success is False
        assert email_response.message == "Failed to send email"
        assert email_response.email_id is None
        assert email_response.timestamp == "2023-12-01T10:00:00Z"


class TestEmailPriority:
    """Test cases for EmailPriority enum"""

    def test_email_priority_values(self):
        """Test EmailPriority enum values"""
        assert EmailPriority.LOW == "low"
        assert EmailPriority.NORMAL == "normal"
        assert EmailPriority.HIGH == "high"

    def test_email_priority_from_string(self):
        """Test creating EmailPriority from string"""
        assert EmailPriority("low") == EmailPriority.LOW
        assert EmailPriority("normal") == EmailPriority.NORMAL
        assert EmailPriority("high") == EmailPriority.HIGH 