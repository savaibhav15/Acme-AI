"""Booking service for managing Calendly API interactions.

This service provides business logic for booking operations,
using the CalendlyAPI client for all API communications.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from ..api import (
    CalendlyAPI,
    CalendlyAPIError,
    CalendlyAuthenticationError,
    CalendlyRateLimitError
)
from ..utils import EmailValidator, DateValidator


class BookingService:
    """Service for handling all booking-related operations.
    
    This service encapsulates business logic for booking operations,
    delegating API calls to the CalendlyAPI client.
    """
    
    def __init__(self, api_client: Optional[CalendlyAPI] = None):
        """Initialize the booking service.
        
        Args:
            api_client: CalendlyAPI instance (creates new one if not provided)
        """
        try:
            self.api = api_client or CalendlyAPI()
        except CalendlyAuthenticationError:
            # Service can still operate in fallback mode
            self.api = None
        
        self.calendly_url = os.getenv("CALENDLY_URL", "")
        self._event_type_uri_cache: Optional[str] = None
    
    def _get_event_type_uri(self) -> Optional[str]:
        """Get the event type URI for scheduling with caching.
        
        Returns:
            Event type URI string or None if not available
        """
        if self._event_type_uri_cache:
            return self._event_type_uri_cache
        
        if not self.api:
            return None
        
        try:
            event_types = self.api.get_event_types()
            if event_types:
                self._event_type_uri_cache = event_types[0]["uri"]
                return self._event_type_uri_cache
        except CalendlyAPIError:
            pass
        
        return None
    
    def get_available_times(self, date: str) -> Dict[str, Any]:
        """Get available appointment times for a specific date.
        
        Args:
            date: Date in format YYYY-MM-DD
        
        Returns:
            Dictionary with success status, times list, and message
        """
        # Validate date format first
        is_valid, message = DateValidator.validate(date)
        if not is_valid:
            return {
                "success": False,
                "times": [],
                "date": date,
                "message": message,
                "validation_error": True
            }
        
        # Fallback times for any error scenario
        fallback_times = ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"]
        
        if not self.api:
            return {
                "success": False,
                "times": fallback_times,
                "date": date,
                "message": "API not available - using fallback times",
                "fallback": True
            }
        
        try:
            event_type_uri = self._get_event_type_uri()
            
            if not event_type_uri:
                return {
                    "success": False,
                    "times": fallback_times,
                    "date": date,
                    "message": "Event type not found - using fallback times",
                    "fallback": True
                }
            
            # Calculate time range for the date
            target_date = datetime.strptime(date, "%Y-%m-%d")
            min_time = target_date.isoformat()
            max_time = (target_date + timedelta(days=1)).isoformat()
            
            # Get available times from API
            times = self.api.get_available_times(event_type_uri, min_time, max_time)
            
            if times:
                time_list = [
                    datetime.fromisoformat(slot["start_time"].replace("Z", "+00:00")).strftime("%I:%M %p")
                    for slot in times[:10]
                ]
                return {
                    "success": True,
                    "times": time_list,
                    "date": date,
                    "message": f"Found {len(time_list)} available slots"
                }
            else:
                return {
                    "success": True,
                    "times": [],
                    "date": date,
                    "message": f"No available slots for {date}"
                }
        
        except CalendlyRateLimitError:
            return {
                "success": False,
                "times": fallback_times,
                "date": date,
                "message": "Rate limit exceeded - using fallback times",
                "fallback": True
            }
        except CalendlyAPIError as e:
            return {
                "success": False,
                "times": fallback_times,
                "date": date,
                "message": f"API error - using fallback times",
                "fallback": True,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "times": fallback_times,
                "date": date,
                "message": "Unexpected error - using fallback times",
                "fallback": True,
                "error": str(e)
            }
    
    def create_booking(self, name: str, email: str, date: str, time: str) -> Dict[str, Any]:
        """Create a booking via Calendly API.
        
        Args:
            name: Patient's full name
            email: Patient's email address
            date: Date in YYYY-MM-DD format
            time: Time like "2:00 PM"
        
        Returns:
            Dictionary with success status, booking details, and message
        """
        # Validate email format
        is_valid_email, email_message = EmailValidator.validate(email)
        if not is_valid_email:
            return {
                "success": False,
                "message": email_message,
                "validation_error": True
            }
        
        # Validate date format
        is_valid_date, date_message = DateValidator.validate(date)
        if not is_valid_date:
            return {
                "success": False,
                "message": date_message,
                "validation_error": True
            }
        
        # Validate name (basic check)
        if not name or not name.strip():
            return {
                "success": False,
                "message": "Name is required",
                "validation_error": True
            }
        
        booking_url = f"{self.calendly_url}?name={name}&email={email}&date={date}"
        
        if not self.api:
            return {
                "success": False,
                "booking_url": booking_url,
                "message": "API not available - please use booking URL"
            }
        
        try:
            event_type_uri = self._get_event_type_uri()
            
            if not event_type_uri:
                return {
                    "success": False,
                    "booking_url": booking_url,
                    "message": "Event type not found - please use booking URL"
                }
            
            # Parse date and time to UTC
            time_24h = datetime.strptime(time, "%I:%M %p").strftime("%H:%M")
            start_datetime = f"{date}T{time_24h}:00"
            start_utc = datetime.fromisoformat(start_datetime).isoformat() + "Z"
            
            # Create invitee booking via API
            invitee_data = self.api.create_invitee(
                event_type_uri=event_type_uri,
                start_time=start_utc,
                email=email,
                name=name
            )
            
            return {
                "success": True,
                "name": name,
                "email": email,
                "date": date,
                "time": time,
                "event_uri": invitee_data.get("uri", ""),
                "message": "Booking confirmed successfully"
            }
        
        except CalendlyAuthenticationError:
            return {
                "success": False,
                "booking_url": booking_url,
                "message": "Authentication failed - please use booking URL",
                "error": "Authentication error"
            }
        except CalendlyRateLimitError:
            return {
                "success": False,
                "booking_url": booking_url,
                "message": "Service busy - please try again or use booking URL",
                "error": "Rate limit exceeded"
            }
        except CalendlyAPIError as e:
            return {
                "success": False,
                "booking_url": booking_url,
                "message": "Booking failed - please use booking URL",
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "booking_url": booking_url,
                "message": "Unexpected error - please use booking URL",
                "error": str(e)
            }
    
    def find_user_bookings(self, email: str) -> Dict[str, Any]:
        """Find scheduled appointments for a user by email.
        
        Args:
            email: Patient's email address
        
        Returns:
            Dictionary with success status and list of appointments
        """
        # Validate email format
        is_valid, message = EmailValidator.validate(email)
        if not is_valid:
            return {
                "success": False,
                "email": email,
                "appointments": [],
                "message": message,
                "validation_error": True
            }
        
        if not self.api:
            return {
                "success": False,
                "email": email,
                "appointments": [],
                "message": "API not available"
            }
        
        try:
            # Get scheduled events
            events = self.api.get_scheduled_events(
                min_start_time=datetime.now().isoformat()
            )
            
            # Filter by invitee email
            user_events = []
            for event in events:
                event_uuid = event['uri'].split('/')[-1]
                
                try:
                    invitees = self.api.get_event_invitees(event_uuid)
                    
                    for invitee in invitees:
                        if invitee.get("email", "").lower() == email.lower():
                            start_time = datetime.fromisoformat(event["start_time"].replace("Z", "+00:00"))
                            user_events.append({
                                "uri": event["uri"],
                                "date": start_time.strftime("%Y-%m-%d"),
                                "time": start_time.strftime("%I:%M %p"),
                                "name": event.get("name", "Dental Checkup")
                            })
                            break
                except CalendlyAPIError:
                    # Skip this event if we can't get invitees
                    continue
            
            return {
                "success": True,
                "email": email,
                "appointments": user_events,
                "count": len(user_events)
            }
        
        except CalendlyAPIError as e:
            return {
                "success": False,
                "email": email,
                "appointments": [],
                "error": str(e),
                "message": "Unable to retrieve bookings"
            }
        except Exception as e:
            return {
                "success": False,
                "email": email,
                "appointments": [],
                "error": str(e),
                "message": "Unexpected error retrieving bookings"
            }
    
    def cancel_appointment(self, email: str) -> Dict[str, Any]:
        """Cancel an appointment for a patient.
        
        Args:
            email: Patient's email address
        
        Returns:
            Dictionary with success status and cancellation details
        """
        # Validate email format
        is_valid, message = EmailValidator.validate(email)
        if not is_valid:
            return {
                "success": False,
                "email": email,
                "message": message,
                "validation_error": True
            }
        
        if not self.api:
            return {
                "success": False,
                "email": email,
                "message": "API not available"
            }
        
        try:
            # Find the user's events
            events = self.api.get_scheduled_events(
                min_start_time=datetime.now().isoformat()
            )
            
            # Find event for this email
            event_to_cancel = None
            for event in events:
                event_uuid = event['uri'].split('/')[-1]
                
                try:
                    invitees = self.api.get_event_invitees(event_uuid)
                    
                    for invitee in invitees:
                        if invitee.get("email", "").lower() == email.lower():
                            event_to_cancel = event
                            break
                    
                    if event_to_cancel:
                        break
                except CalendlyAPIError:
                    continue
            
            if not event_to_cancel:
                return {
                    "success": False,
                    "email": email,
                    "message": "No upcoming appointments found"
                }
            
            # Cancel the event
            event_uuid = event_to_cancel['uri'].split('/')[-1]
            self.api.cancel_event(event_uuid, reason="Cancelled by patient")
            
            start_time = datetime.fromisoformat(event_to_cancel["start_time"].replace("Z", "+00:00"))
            return {
                "success": True,
                "email": email,
                "date": start_time.strftime("%B %d, %Y"),
                "time": start_time.strftime("%I:%M %p"),
                "message": "Appointment cancelled successfully"
            }
        
        except CalendlyAPIError as e:
            return {
                "success": False,
                "email": email,
                "error": str(e),
                "message": "Unable to cancel via API"
            }
        except Exception as e:
            return {
                "success": False,
                "email": email,
                "error": str(e),
                "message": "Unexpected error cancelling appointment"
            }
    
    def reschedule_appointment(self, email: str, new_date: str) -> Dict[str, Any]:
        """Reschedule appointment by cancelling old and preparing for new booking.
        
        Args:
            email: Patient's email
            new_date: New date in YYYY-MM-DD format
        
        Returns:
            Dictionary with cancellation and availability info
        """
        # Validate email format
        is_valid_email, email_message = EmailValidator.validate(email)
        if not is_valid_email:
            return {
                "success": False,
                "message": email_message,
                "validation_error": True
            }
        
        # Validate date format
        is_valid_date, date_message = DateValidator.validate(new_date)
        if not is_valid_date:
            return {
                "success": False,
                "message": date_message,
                "validation_error": True
            }
        
        # Cancel the old appointment
        cancel_result = self.cancel_appointment(email)
        
        if not cancel_result["success"]:
            return cancel_result
        
        # Get available times for new date
        availability = self.get_available_times(new_date)
        
        return {
            "success": True,
            "email": email,
            "old_cancelled": True,
            "new_date": new_date,
            "available_times": availability["times"],
            "message": "Old appointment cancelled. Select new time."
        }
