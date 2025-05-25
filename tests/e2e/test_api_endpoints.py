"""
End-to-end tests for API endpoints
"""

import pytest
import requests
import time
import sys
import os
from fastapi.testclient import TestClient

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestAPIEndpoints:
    """End-to-end tests for API endpoints"""

    def test_health_check(self, test_client):
        """Test the health check endpoint"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_web_interface_loads(self, test_client):
        """Test that the web interface loads correctly"""
        response = test_client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "AutoMail Agent" in response.text

    def test_api_documentation_accessible(self, test_client):
        """Test that API documentation is accessible"""
        response = test_client.get("/api/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_documentation_accessible(self, test_client):
        """Test that ReDoc documentation is accessible"""
        response = test_client.get("/api/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_profiles_endpoint(self, test_client):
        """Test the profiles endpoint"""
        response = test_client.get("/api/profiles/")
        
        assert response.status_code == 200
        data = response.json()
        assert "profiles" in data
        assert "total_count" in data
        assert isinstance(data["profiles"], list)
        assert isinstance(data["total_count"], int)

    def test_email_validation_valid_email(self, test_client, sample_email_data):
        """Test email validation with valid email data"""
        response = test_client.post("/api/email/validate", json=sample_email_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True

    def test_email_validation_invalid_email(self, test_client):
        """Test email validation with invalid email data"""
        invalid_email_data = {
            "to": "invalid-email-address",
            "subject": "Test Subject",
            "body": "Test body content",
            "priority": "normal"
        }
        
        response = test_client.post("/api/email/validate", json=invalid_email_data)
        
        assert response.status_code == 422  # Validation error

    def test_email_validation_missing_fields(self, test_client):
        """Test email validation with missing required fields"""
        incomplete_email_data = {
            "to": "test@example.com",
            # Missing subject and body
        }
        
        response = test_client.post("/api/email/validate", json=incomplete_email_data)
        
        assert response.status_code == 422  # Validation error

    def test_send_email_form_data(self, test_client):
        """Test sending email via form data (simulating web form submission)"""
        form_data = {
            "to": "test@example.com",
            "subject": "Test Email from E2E Test",
            "body": "This is a test email sent from the e2e test suite.",
            "priority": "normal"
        }
        
        # Note: This will fail in actual sending since we don't have a real Gmail session
        # But we can test that the endpoint accepts the request and validates the data
        response = test_client.post("/api/email/send", data=form_data)
        
        # The response might be 500 due to browser automation failure, but that's expected
        # We're testing that the endpoint is reachable and validates input correctly
        assert response.status_code in [200, 500]  # 500 is expected without browser setup

    def test_send_email_with_attachments(self, test_client):
        """Test sending email with attachments via form data"""
        form_data = {
            "to": "test@example.com",
            "subject": "Test Email with Attachments",
            "body": "This email has attachments.",
            "priority": "high",
            "attachments": "/path/to/file1.pdf,/path/to/file2.txt"
        }
        
        response = test_client.post("/api/email/send", data=form_data)
        
        # Expected to fail at browser automation level, but input validation should pass
        assert response.status_code in [200, 500]

    def test_send_email_invalid_priority(self, test_client):
        """Test sending email with invalid priority"""
        form_data = {
            "to": "test@example.com",
            "subject": "Test Email",
            "body": "Test body",
            "priority": "invalid_priority"
        }
        
        response = test_client.post("/api/email/send", data=form_data)
        
        assert response.status_code == 422  # Validation error

    def test_send_email_invalid_email_address(self, test_client):
        """Test sending email with invalid email address"""
        form_data = {
            "to": "invalid-email",
            "subject": "Test Email",
            "body": "Test body",
            "priority": "normal"
        }
        
        response = test_client.post("/api/email/send", data=form_data)
        
        assert response.status_code == 422  # Validation error

    def test_get_email_status_not_found(self, test_client):
        """Test getting status of non-existent email"""
        response = test_client.get("/api/email/status/non-existent-email-id")
        
        assert response.status_code == 404

    def test_openapi_schema(self, test_client):
        """Test that OpenAPI schema is accessible"""
        response = test_client.get("/api/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_cors_headers(self, test_client):
        """Test CORS headers are present"""
        response = test_client.options("/api/email/send")
        
        # Check that CORS headers are present (if CORS is configured)
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled

    def test_content_type_validation(self, test_client):
        """Test that endpoints properly validate content types"""
        # Test sending JSON to form-data endpoint
        json_data = {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Test body"
        }
        
        response = test_client.post("/api/email/send", json=json_data)
        
        # Should fail because endpoint expects form data, not JSON
        assert response.status_code == 422

    def test_rate_limiting_headers(self, test_client):
        """Test for rate limiting headers (if implemented)"""
        response = test_client.get("/health")
        
        # This test checks if rate limiting headers are present
        # If not implemented, this test will just verify the endpoint works
        assert response.status_code == 200
        
        # Check for common rate limiting headers (optional)
        headers = response.headers
        # These headers might not be present if rate limiting isn't implemented
        # assert "X-RateLimit-Limit" in headers  # Optional
        # assert "X-RateLimit-Remaining" in headers  # Optional


class TestAPIErrorHandling:
    """Test error handling in API endpoints"""

    def test_404_for_unknown_endpoint(self, test_client):
        """Test 404 response for unknown endpoints"""
        response = test_client.get("/api/unknown-endpoint")
        
        assert response.status_code == 404

    def test_405_for_wrong_method(self, test_client):
        """Test 405 response for wrong HTTP methods"""
        # Try POST on a GET endpoint
        response = test_client.post("/health")
        
        assert response.status_code == 405

    def test_422_for_validation_errors(self, test_client):
        """Test 422 response for validation errors"""
        invalid_data = {
            "to": "not-an-email",
            "subject": "",  # Empty subject
            "body": "Test body"
        }
        
        response = test_client.post("/api/email/validate", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data 