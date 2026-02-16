"""Validation utilities for user input."""

import re
from datetime import datetime
from typing import Tuple


class EmailValidator:
    """Validator for email addresses."""
    
    # RFC 5322 compliant email regex (simplified for practical use)
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @classmethod
    def is_valid(cls, email: str) -> bool:
        """Check if email format is valid.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        email = email.strip()
        return bool(cls.EMAIL_PATTERN.match(email))
    
    @classmethod
    def validate(cls, email: str) -> Tuple[bool, str]:
        """Validate email and return result with message.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not email:
            return False, "Email is required"
        
        if not isinstance(email, str):
            return False, "Email must be a string"
        
        email = email.strip()
        
        if not cls.EMAIL_PATTERN.match(email):
            return False, "Invalid email format. Please provide a valid email address (e.g., john@example.com)"
        
        return True, "Valid email"


class DateValidator:
    """Validator for date strings."""
    
    @classmethod
    def is_valid_format(cls, date_str: str, format_str: str = "%Y-%m-%d") -> bool:
        """Check if date string matches the expected format.
        
        Args:
            date_str: Date string to validate
            format_str: Expected format (default: YYYY-MM-DD)
            
        Returns:
            True if valid format, False otherwise
        """
        if not date_str or not isinstance(date_str, str):
            return False
        
        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False
    
    @classmethod
    def validate(cls, date_str: str, format_str: str = "%Y-%m-%d") -> Tuple[bool, str]:
        """Validate date string and return result with message.
        
        Args:
            date_str: Date string to validate
            format_str: Expected format (default: YYYY-MM-DD)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not date_str:
            return False, "Date is required"
        
        if not isinstance(date_str, str):
            return False, "Date must be a string"
        
        try:
            parsed_date = datetime.strptime(date_str, format_str)
            
            # Check if date is in the past
            if parsed_date.date() < datetime.now().date():
                return False, "Date cannot be in the past"
            
            return True, "Valid date"
        except ValueError:
            return False, f"Invalid date format. Please use {format_str} format (e.g., 2026-02-20)"
