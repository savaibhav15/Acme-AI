"""Tools for interacting with booking and knowledge services.

This module provides LangChain tools that wrap around the BookingService 
and KnowledgeService, keeping the tool layer thin and focused on LangChain integration.
"""

from langchain_core.tools import tool
from .services import BookingService, KnowledgeService

# Initialize services as singletons for the module
_booking_service = BookingService()
_knowledge_service = KnowledgeService()


@tool
def get_available_times(date: str) -> str:
    """
    Get available appointment times for a specific date.
    
    Args:
        date: Date in format YYYY-MM-DD
    
    Returns:
        Available time slots formatted as a string
    """
    result = _booking_service.get_available_times(date)
    
    if result["success"] and result["times"]:
        time_list = "\n".join([f"- {t}" for t in result["times"]])
        return f"Available times on {result['date']}:\n{time_list}"
    elif result["times"]:
        # Fallback times
        time_list = "\n".join([f"- {t}" for t in result["times"]])
        return f"Available times on {result['date']}:\n{time_list}"
    else:
        return f"No available slots for {result['date']}. Please try another date."


@tool
def create_booking(name: str, email: str, date: str, time: str) -> str:
    """
    Create a booking via Calendly Scheduling API.
    
    Args:
        name: Patient's full name
        email: Patient's email address
        date: Date in YYYY-MM-DD format
        time: Time like "2:00 PM"
    
    Returns:
        Booking confirmation message
    """
    result = _booking_service.create_booking(name, email, date, time)
    
    if result["success"]:
        return f"""✅ **Booking Confirmed!**

**Patient:** {result['name']}
**Email:** {result['email']}
**Date:** {result['date']}
**Time:** {result['time']}
**Duration:** 30 minutes
**Cost:** €60

Your appointment has been successfully booked! You'll receive a confirmation email shortly with all the details.

**What to bring:**
- Valid photo ID
- Medical information (if applicable)
- Insurance details

**Arrival:** Please arrive 5-10 minutes early.

See you soon! 😊"""
    else:
        # Fallback with booking URL
        booking_url = result.get("booking_url", "")
        return f"""Booking confirmation pending.

Please complete your booking by clicking: {booking_url}

**Appointment Details:**
- Date: {date}
- Time: {time}
- Duration: 30 minutes
- Cost: €60"""


@tool
def find_user_bookings(email: str) -> str:
    """
    Find scheduled appointments for a user by email.
    
    Args:
        email: Patient's email address
    
    Returns:
        List of scheduled appointments
    """
    result = _booking_service.find_user_bookings(email)
    
    if result["success"] and result["count"] > 0:
        appointments = result["appointments"]
        message = f"Found {result['count']} appointment(s) for {email}:\n\n"
        for idx, apt in enumerate(appointments, 1):
            message += f"{idx}. {apt['name']} on {apt['date']} at {apt['time']}\n"
        return message
    elif result["success"]:
        return f"No upcoming appointments found for {email}."
    else:
        return f"Unable to retrieve bookings: {result.get('message', 'Unknown error')}"


@tool
def cancel_appointment(email: str) -> str:
    """
    Cancel an appointment for a patient.
    
    Args:
        email: Patient's email address
    
    Returns:
        Cancellation confirmation message
    """
    result = _booking_service.cancel_appointment(email)
    
    if result["success"]:
        contact = _knowledge_service.get_contact_info()
        return f"""✅ **Appointment Cancelled**

Your appointment on {result['date']} at {result['time']} has been cancelled.

⚠️ Cancellation within 24 hours may incur a €20 fee.

You'll receive a confirmation email shortly."""
    else:
        contact = _knowledge_service.get_contact_info()
        if "no upcoming" in result["message"].lower():
            return f"No upcoming appointments found for {email}. If you have an appointment, please contact us at {contact['phone']}."
        else:
            return f"Unable to cancel via API. Please contact us at {contact['phone']} or {contact['email']}"


@tool
def reschedule_appointment(email: str, new_date: str) -> str:
    """
    Reschedule appointment: cancel old and show new available times.
    
    Args:
        email: Patient's email
        new_date: New date in YYYY-MM-DD format
    
    Returns:
        Rescheduling confirmation and available times
    """
    result = _booking_service.reschedule_appointment(email, new_date)
    
    if result["success"] and result.get("old_cancelled"):
        times = result["available_times"]
        if times:
            time_list = "\n".join([f"- {t}" for t in times])
            return f"""✅ **Old Appointment Cancelled**

Available times on {result['new_date']}:
{time_list}

Please tell me which time you'd like for {result['new_date']}, and I'll create your new booking.

Example: "I'd like 2:00 PM" """
        else:
            return f"""✅ **Old Appointment Cancelled**

No available slots for {result['new_date']}. Please try another date."""
    else:
        contact = _knowledge_service.get_contact_info()
        return f"To reschedule, contact: {contact['phone']} or {contact['email']}"


@tool
def get_clinic_info() -> str:
    """
    Get information about Acme Dental clinic.
    
    Returns:
        Clinic information formatted as a string
    """
    result = _knowledge_service.get_clinic_info()
    return result["formatted"]


@tool
def search_knowledge_base(question: str) -> str:
    """
    Search Acme Dental knowledge base for answers to FAQs.
    
    Args:
        question: The user's question about clinic policies, services, pricing, etc.
    
    Returns:
        Answer from the knowledge base
    """
    result = _knowledge_service.search_knowledge_base(question)
    return result["answer"]
