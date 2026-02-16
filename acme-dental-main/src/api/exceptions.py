"""Custom exceptions for Calendly API interactions.

This module defines a hierarchy of exceptions for handling various
error scenarios when interacting with the Calendly API.
"""


class CalendlyAPIError(Exception):
    """Base exception for all Calendly API errors.
    
    All Calendly-related exceptions inherit from this base class,
    allowing for broad exception handling when needed.
    """
    pass


class CalendlyAuthenticationError(CalendlyAPIError):
    """Raised when authentication with Calendly API fails.
    
    This typically occurs when:
    - API token is invalid or expired
    - API token is missing
    - Authorization header is malformed
    """
    pass


class CalendlyNotFoundError(CalendlyAPIError):
    """Raised when a requested resource is not found (404).
    
    This can occur when:
    - Event type doesn't exist
    - Scheduled event doesn't exist
    - User URI is invalid
    """
    pass


class CalendlyRateLimitError(CalendlyAPIError):
    """Raised when API rate limit is exceeded (429).
    
    Calendly has rate limits on API requests. This exception
    is raised when those limits are hit.
    """
    pass


class BookingNotFoundError(CalendlyAPIError):
    """Raised when a booking/appointment cannot be found.
    
    This is used specifically when searching for a user's
    appointment by email and no matching booking exists.
    """
    pass


class CalendlyConnectionError(CalendlyAPIError):
    """Raised when connection to Calendly API fails.
    
    This can occur due to:
    - Network connectivity issues
    - Calendly service being down
    - DNS resolution failures
    """
    pass


class CalendlyTimeoutError(CalendlyAPIError):
    """Raised when an API request times out.
    
    This occurs when Calendly doesn't respond within
    the configured timeout period.
    """
    pass


class CalendlyValidationError(CalendlyAPIError):
    """Raised when request data fails validation.
    
    This occurs when:
    - Invalid date/time formats
    - Missing required fields
    - Invalid parameter values
    """
    pass


class CalendlyConflictError(CalendlyAPIError):
    """Raised when there's a conflict (409).
    
    This can occur when:
    - Time slot is no longer available
    - Double booking attempted
    - Resource state conflict
    """
    pass
