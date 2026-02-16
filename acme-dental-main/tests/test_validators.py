"""Unit tests for validators."""

import pytest
from datetime import datetime, timedelta
from src.utils.validators import EmailValidator, DateValidator


class TestEmailValidator:
    """Test cases for EmailValidator."""
    
    def test_valid_email(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "firstname.lastname@company.com"
        ]
        for email in valid_emails:
            assert EmailValidator.is_valid(email), f"{email} should be valid"
    
    def test_invalid_email(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "sav3#ff.com",  # Invalid character #
            "invalid",
            "@example.com",
            "user@",
            "user name@example.com",  # Space not allowed
            "",
            None
        ]
        for email in invalid_emails:
            assert not EmailValidator.is_valid(email), f"{email} should be invalid"
    
    def test_validate_with_message(self):
        """Test validate method returns proper tuple."""
        is_valid, message = EmailValidator.validate("test@example.com")
        assert is_valid is True
        assert "Valid" in message
        
        is_valid, message = EmailValidator.validate("invalid#email.com")
        assert is_valid is False
        assert "Invalid email format" in message


class TestDateValidator:
    """Test cases for DateValidator."""
    
    def test_valid_date_format(self):
        """Test valid date formats."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert DateValidator.is_valid_format(tomorrow)
        assert DateValidator.is_valid_format("2026-12-31")
    
    def test_invalid_date_format(self):
        """Test invalid date formats."""
        invalid_dates = [
            "18th feb",  # Natural language
            "2026/02/18",  # Wrong separator
            "18-02-2026",  # Wrong order
            "2026-13-01",  # Invalid month
            "not-a-date"
        ]
        for date_str in invalid_dates:
            assert not DateValidator.is_valid_format(date_str), f"{date_str} should be invalid"
    
    def test_past_date_validation(self):
        """Test that past dates are rejected."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        is_valid, message = DateValidator.validate(yesterday)
        assert is_valid is False
        assert "cannot be in the past" in message
    
    def test_future_date_validation(self):
        """Test that future dates are accepted."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        is_valid, message = DateValidator.validate(tomorrow)
        assert is_valid is True
        assert "Valid" in message
