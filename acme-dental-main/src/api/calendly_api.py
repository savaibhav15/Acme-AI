"""Calendly API client with comprehensive error handling.

This module provides a clean interface to the Calendly API, handling all HTTP
requests, authentication, and error scenarios in a centralized location.
"""

import os
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from requests.exceptions import (
    RequestException,
    HTTPError,
    ConnectionError,
    Timeout,
    JSONDecodeError
)
from .exceptions import (
    CalendlyAPIError,
    CalendlyAuthenticationError,
    CalendlyNotFoundError,
    CalendlyRateLimitError,
    CalendlyConnectionError,
    CalendlyTimeoutError
)


class CalendlyAPI:
    """Client for interacting with Calendly API.
    
    This class handles all HTTP communication with Calendly, including
    authentication, error handling, and response parsing.
    """
    
    def __init__(self, api_token: Optional[str] = None, timeout: int = 10):
        """Initialize the Calendly API client.
        
        Args:
            api_token: Calendly API token (defaults to env variable)
            timeout: Request timeout in seconds
        """
        self.api_token = api_token or os.getenv("CALENDLY_API_TOKEN")
        self.api_base = "https://api.calendly.com"
        self.timeout = timeout
        self._user_uri_cache: Optional[str] = None
        
        if not self.api_token:
            raise CalendlyAuthenticationError("Calendly API token not provided")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests.
        
        Returns:
            Dictionary with authorization and content-type headers
        """
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions.
        
        Args:
            response: Response object from requests
            
        Returns:
            Parsed JSON response
            
        Raises:
            CalendlyAuthenticationError: For 401 errors
            CalendlyNotFoundError: For 404 errors
            CalendlyRateLimitError: For 429 errors
            CalendlyAPIError: For other errors
        """
        try:
            if response.status_code == 401:
                raise CalendlyAuthenticationError("Invalid or expired API token")
            elif response.status_code == 404:
                raise CalendlyNotFoundError("Resource not found")
            elif response.status_code == 429:
                raise CalendlyRateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                error_msg = f"API error {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('message', 'Unknown error')}"
                except JSONDecodeError:
                    pass
                raise CalendlyAPIError(error_msg)
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except JSONDecodeError as e:
            raise CalendlyAPIError(f"Invalid JSON response: {str(e)}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to Calendly API with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON request body
            
        Returns:
            Parsed JSON response
            
        Raises:
            CalendlyAPIError: For various API errors
        """
        url = f"{self.api_base}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=self.timeout
            )
            return self._handle_response(response)
            
        except Timeout:
            raise CalendlyTimeoutError("Request timed out - Calendly may be slow or unavailable")
        except ConnectionError:
            raise CalendlyConnectionError("Connection failed - check internet connection")
        except HTTPError as e:
            raise CalendlyAPIError(f"HTTP error: {str(e)}")
        except RequestException as e:
            raise CalendlyAPIError(f"Request failed: {str(e)}")
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get the current user's information.
        
        Returns:
            User data including URI
            
        Raises:
            CalendlyAPIError: If request fails
        """
        try:
            data = self._make_request("GET", "/users/me")
            return data.get("resource", {})
        except CalendlyAPIError:
            raise
    
    def get_user_uri(self) -> str:
        """Get the current user's URI with caching.
        
        Returns:
            User URI string
            
        Raises:
            CalendlyAPIError: If request fails
        """
        if self._user_uri_cache:
            return self._user_uri_cache
        
        user_data = self.get_current_user()
        self._user_uri_cache = user_data.get("uri", "")
        
        if not self._user_uri_cache:
            raise CalendlyAPIError("User URI not found in response")
        
        return self._user_uri_cache
    
    def get_event_types(self, user_uri: Optional[str] = None, active: bool = True) -> List[Dict[str, Any]]:
        """Get event types for a user.
        
        Args:
            user_uri: User URI (defaults to current user)
            active: Filter for active event types only
            
        Returns:
            List of event type objects
            
        Raises:
            CalendlyAPIError: If request fails
        """
        if not user_uri:
            user_uri = self.get_user_uri()
        
        params = {
            "user": user_uri,
            "active": "true" if active else "false"
        }
        
        data = self._make_request("GET", "/event_types", params=params)
        return data.get("collection", [])
    
    def get_available_times(
        self,
        event_type_uri: str,
        start_time: str,
        end_time: str
    ) -> List[Dict[str, Any]]:
        """Get available time slots for an event type.
        
        Args:
            event_type_uri: Event type URI
            start_time: Start time in ISO format
            end_time: End time in ISO format
            
        Returns:
            List of available time slots
            
        Raises:
            CalendlyAPIError: If request fails
        """
        params = {
            "event_type": event_type_uri,
            "start_time": start_time,
            "end_time": end_time
        }
        
        data = self._make_request("GET", "/event_type_available_times", params=params)
        return data.get("collection", [])
    
    def create_invitee(
        self,
        event_type_uri: str,
        start_time: str,
        email: str,
        name: str
    ) -> Dict[str, Any]:
        """Create a booking by adding an invitee.
        
        Args:
            event_type_uri: Event type URI
            start_time: Start time in ISO format
            email: Invitee email
            name: Invitee name
            
        Returns:
            Created invitee data
            
        Raises:
            CalendlyAPIError: If request fails
        """
        payload = {
            "event_type_uri": event_type_uri,
            "start_time": start_time,
            "invitee": {
                "email": email,
                "name": name
            }
        }
        
        data = self._make_request("POST", "/scheduling/invitees", json_data=payload)
        return data.get("resource", {})
    
    def get_scheduled_events(
        self,
        user_uri: Optional[str] = None,
        status: str = "active",
        min_start_time: Optional[str] = None,
        count: int = 100
    ) -> List[Dict[str, Any]]:
        """Get scheduled events for a user.
        
        Args:
            user_uri: User URI (defaults to current user)
            status: Event status filter
            min_start_time: Minimum start time filter
            count: Maximum number of events to return
            
        Returns:
            List of scheduled events
            
        Raises:
            CalendlyAPIError: If request fails
        """
        if not user_uri:
            user_uri = self.get_user_uri()
        
        params = {
            "user": user_uri,
            "status": status,
            "count": count
        }
        
        if min_start_time:
            params["min_start_time"] = min_start_time
        
        data = self._make_request("GET", "/scheduled_events", params=params)
        return data.get("collection", [])
    
    def get_event_invitees(self, event_uuid: str) -> List[Dict[str, Any]]:
        """Get invitees for a scheduled event.
        
        Args:
            event_uuid: Event UUID (from event URI)
            
        Returns:
            List of invitee objects
            
        Raises:
            CalendlyAPIError: If request fails
        """
        endpoint = f"/scheduled_events/{event_uuid}/invitees"
        data = self._make_request("GET", endpoint)
        return data.get("collection", [])
    
    def cancel_event(self, event_uuid: str, reason: str = "Cancelled by patient") -> Dict[str, Any]:
        """Cancel a scheduled event.
        
        Args:
            event_uuid: Event UUID (from event URI)
            reason: Cancellation reason
            
        Returns:
            Cancellation response data
            
        Raises:
            CalendlyAPIError: If request fails
        """
        endpoint = f"/scheduled_events/{event_uuid}/cancellation"
        payload = {"reason": reason}
        
        return self._make_request("POST", endpoint, json_data=payload)
