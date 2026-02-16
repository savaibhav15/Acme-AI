"""Unit tests for BookingService."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from src.services.booking_service import BookingService
from src.api.exceptions import CalendlyAPIError, CalendlyAuthenticationError


class TestBookingService:
    """Test cases for BookingService."""
    
    @pytest.fixture
    def mock_api(self):
        """Create a mock CalendlyAPI."""
        api = Mock()
        api.get_event_types.return_value = [{"uri": "test-event-type-uri"}]
        return api
    
    @pytest.fixture
    def service(self, mock_api):
        """Create a BookingService with mocked API."""
        return BookingService(api_client=mock_api)
    
    def test_initialization_with_api(self, mock_api):
        """Test service initializes with API client."""
        service = BookingService(api_client=mock_api)
        assert service.api is not None
    
    def test_initialization_handles_auth_error(self):
        """Test service handles authentication errors gracefully."""
        mock_api = Mock()
        mock_api.side_effect = CalendlyAuthenticationError("Auth failed")
        service = BookingService()
        # Service should still be created, but with no API
        assert service is not None
    
    def test_get_available_times_invalid_date(self, service):
        """Test validation rejects invalid date format."""
        result = service.get_available_times("18th feb")
        assert result["success"] is False
        assert "validation_error" in result
        assert result["times"] == []
    
    def test_get_available_times_past_date(self, service):
        """Test validation rejects past dates."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        result = service.get_available_times(yesterday)
        assert result["success"] is False
        assert "past" in result["message"].lower()
    
    def test_get_available_times_success(self, service, mock_api):
        """Test getting available times successfully."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        mock_api.get_available_times.return_value = [
            {"start_time": "2026-02-20T09:00:00Z"},
            {"start_time": "2026-02-20T10:00:00Z"}
        ]
        
        result = service.get_available_times(tomorrow)
        assert result["success"] is True
        assert len(result["times"]) > 0
    
    def test_create_booking_invalid_email(self, service):
        """Test validation rejects invalid email."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = service.create_booking("John Doe", "invalid#email", tomorrow, "2:00 PM")
        assert result["success"] is False
        assert "validation_error" in result
        assert "email" in result["message"].lower()
    
    def test_create_booking_invalid_date(self, service):
        """Test validation rejects invalid date."""
        result = service.create_booking("John Doe", "john@example.com", "18th feb", "2:00 PM")
        assert result["success"] is False
        assert "validation_error" in result
    
    def test_create_booking_empty_name(self, service):
        """Test validation rejects empty name."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = service.create_booking("", "john@example.com", tomorrow, "2:00 PM")
        assert result["success"] is False
        assert "Name is required" in result["message"]
    
    def test_create_booking_success(self, service, mock_api):
        """Test successful booking creation."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        mock_api.create_invitee.return_value = {"uri": "booking-uri"}
        
        result = service.create_booking("John Doe", "john@example.com", tomorrow, "2:00 PM")
        assert result["success"] is True
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
    
    def test_find_user_bookings_invalid_email(self, service):
        """Test validation rejects invalid email."""
        result = service.find_user_bookings("invalid#email")
        assert result["success"] is False
        assert "validation_error" in result
    
    def test_find_user_bookings_no_appointments(self, service, mock_api):
        """Test finding bookings when none exist."""
        mock_api.get_scheduled_events.return_value = []
        
        result = service.find_user_bookings("test@example.com")
        assert result["success"] is True
        assert result["count"] == 0
        assert len(result["appointments"]) == 0
    
    def test_cancel_appointment_invalid_email(self, service):
        """Test validation rejects invalid email."""
        result = service.cancel_appointment("invalid#email")
        assert result["success"] is False
        assert "validation_error" in result
    
    def test_cancel_appointment_not_found(self, service, mock_api):
        """Test cancelling when no appointment exists."""
        mock_api.get_scheduled_events.return_value = []
        
        result = service.cancel_appointment("test@example.com")
        assert result["success"] is False
        assert "No upcoming appointments" in result["message"]
    
    def test_reschedule_appointment_invalid_email(self, service):
        """Test validation rejects invalid email."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = service.reschedule_appointment("invalid#email", tomorrow)
        assert result["success"] is False
        assert "validation_error" in result
    
    def test_reschedule_appointment_invalid_date(self, service):
        """Test validation rejects invalid date."""
        result = service.reschedule_appointment("test@example.com", "18th feb")
        assert result["success"] is False
        assert "validation_error" in result
