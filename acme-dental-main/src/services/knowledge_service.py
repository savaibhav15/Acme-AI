"""Knowledge service for managing FAQ and clinic information."""

from typing import Dict, Any


class KnowledgeService:
    """Service for handling knowledge base queries and clinic information."""
    
    def __init__(self):
        """Initialize the knowledge service with clinic data."""
        self.clinic_info = {
            "location": "123 Main Street, Dublin, Ireland",
            "hours": "Monday-Friday, 9:00 AM - 5:00 PM",
            "service": "Dental checkups",
            "duration": "30 minutes",
            "price": "€60",
            "contact_email": "info@acmedental.ie",
            "contact_phone": "+353 1 234 5678",
            "staff": "One experienced dentist",
            "description": "Comprehensive oral examinations"
        }
        
        # Knowledge base mapping for efficient lookups
        self.kb_categories = {
            "pricing": self._get_pricing_info,
            "services": self._get_services_info,
            "duration": self._get_duration_info,
            "what_to_bring": self._get_what_to_bring,
            "arrival": self._get_arrival_info,
            "late_arrival": self._get_late_arrival_info,
            "cancellation_policy": self._get_cancellation_policy,
            "payment": self._get_payment_info,
            "insurance": self._get_insurance_info,
            "discounts": self._get_discounts_info,
            "emergency": self._get_emergency_info,
            "walk_ins": self._get_walk_in_info,
            "dentist": self._get_dentist_info,
            "account": self._get_account_info,
            "confirmation": self._get_confirmation_info,
            "privacy": self._get_privacy_info,
            "x_ray": self._get_xray_info,
            "included": self._get_included_info,
            "booking_others": self._get_booking_others_info,
            "no_show": self._get_no_show_info,
            "receipt": self._get_receipt_info,
            "follow_up": self._get_follow_up_info
        }
    
    def _get_pricing_info(self) -> str:
        """Get pricing information."""
        return ("€60 standard checkup. Student (ID required): €50. Senior 65+: €50. "
                "Cannot combine discounts. No deposit required to book.")
    
    def _get_services_info(self) -> str:
        """Get services information."""
        return ("Acme Dental currently offers routine dental checkups only. "
                "Check-up includes oral examination and general health assessment.")
    
    def _get_duration_info(self) -> str:
        """Get appointment duration information."""
        return "Each checkup is 30 minutes."
    
    def _get_what_to_bring(self) -> str:
        """Get information about what to bring."""
        return ("Bring: valid photo ID, medical information (if applicable), "
                "insurance details (if you have them).")
    
    def _get_arrival_info(self) -> str:
        """Get arrival time information."""
        return "Arrive 5-10 minutes early to settle in."
    
    def _get_late_arrival_info(self) -> str:
        """Get late arrival policy."""
        return ("If running late, message us ASAP. We'll try to accommodate but may need to "
                "reschedule if we can't complete the 30-minute checkup.")
    
    def _get_cancellation_policy(self) -> str:
        """Get cancellation policy."""
        return ("Free cancellation 24+ hours before. Less than 24hrs: €20 late cancellation fee. "
                "No-show: €20 fee.")
    
    def _get_payment_info(self) -> str:
        """Get payment information."""
        return ("Payment options: card (in-clinic), contactless, or cash (exact amount preferred). "
                "No deposit required to book.")
    
    def _get_insurance_info(self) -> str:
        """Get insurance information."""
        return ("We provide receipts for insurance claims. We don't process claims directly - "
                "submit receipt to your insurance provider yourself.")
    
    def _get_discounts_info(self) -> str:
        """Get discount information."""
        return ("Student discount (valid ID required): €50. Senior 65+ discount: €50. "
                "Discounts cannot be combined.")
    
    def _get_emergency_info(self) -> str:
        """Get emergency service information."""
        return ("We don't offer emergency treatment. For severe pain, swelling, or bleeding, "
                "contact emergency dental services in your area.")
    
    def _get_walk_in_info(self) -> str:
        """Get walk-in policy."""
        return "No walk-ins accepted. All appointments must be booked in advance through this assistant."
    
    def _get_dentist_info(self) -> str:
        """Get dentist information."""
        return ("Acme Dental has one dentist who handles all checkup appointments. "
                "Every booking is automatically with them.")
    
    def _get_account_info(self) -> str:
        """Get account requirement information."""
        return "No account required to book. We only need your full name and email address."
    
    def _get_confirmation_info(self) -> str:
        """Get confirmation email information."""
        return ("Check your spam/junk folder first. If still not there, tell me "
                "'I didn't get my confirmation email' and I'll help verify your booking details.")
    
    def _get_privacy_info(self) -> str:
        """Get privacy and data security information."""
        return ("We only collect minimum details needed (name + email) and use them solely for "
                "scheduling and confirmations. Your information is secure.")
    
    def _get_xray_info(self) -> str:
        """Get X-ray information."""
        return ("X-rays are NOT included in the €60 checkup. If X-rays are needed, "
                "the dentist will explain next steps and options.")
    
    def _get_included_info(self) -> str:
        """Get information about what's included in checkup."""
        return ("Checkup includes: full oral examination, gum health check, concern review, "
                "recommendations. Duration: 30 minutes. X-rays NOT included - dentist will "
                "explain if needed.")
    
    def _get_booking_others_info(self) -> str:
        """Get information about booking for others."""
        return ("Yes, you can book for someone else. Just provide their full name and "
                "email address when asked.")
    
    def _get_no_show_info(self) -> str:
        """Get no-show policy information."""
        return ("No-shows may incur €20 fee. You can still rebook through the assistant afterward.")
    
    def _get_receipt_info(self) -> str:
        """Get receipt/invoice information."""
        return ("Yes, we provide receipts for all appointments. For invoices with specific details, "
                "ask at reception during your visit.")
    
    def _get_follow_up_info(self) -> str:
        """Get follow-up appointment information."""
        return ("Yes! Just tell me 'Book another checkup appointment' and I'll show you "
                "available times.")
    
    def search_knowledge_base(self, question: str) -> Dict[str, Any]:
        """Search the knowledge base for answers to user questions.
        
        Args:
            question: The user's question
        
        Returns:
            Dictionary with answer and category information
        """
        q = question.lower()
        
        # Keyword matching for different categories
        category_keywords = {
            "pricing": ['cost', 'price', 'how much', 'fee', 'charge'],
            "included": ['included', 'include', 'what do'],
            "duration": ['long', 'duration', 'minutes', 'how many'],
            "what_to_bring": ['bring', 'need to bring', 'should i bring'],
            "arrival": ['early', 'arrive', 'arrival', 'when should i come'],
            "late_arrival": ['late', 'running late', 'arrive late'],
            "cancellation_policy": ['cancel', 'policy', 'cancellation fee'],
            "no_show": ['no-show', 'miss', "didn't attend", 'no show'],
            "payment": ['pay', 'payment', 'card', 'cash'],
            "insurance": ['insurance'],
            "receipt": ['receipt', 'invoice'],
            "discounts": ['discount', 'cheaper', 'student', 'senior'],
            "emergency": ['emergency', 'urgent', 'pain'],
            "walk_ins": ['walk', 'walk-in', 'without appointment'],
            "dentist": ['dentist', 'doctor', 'specific dentist'],
            "account": ['account', 'sign up', 'register'],
            "booking_others": ['someone else', 'for another', 'on behalf'],
            "confirmation": ['confirmation', 'email', "didn't receive", 'not received'],
            "follow_up": ['follow-up', 'another appointment', 'book again'],
            "x_ray": ['x-ray', 'xray'],
            "privacy": ['privacy', 'secure', 'personal information', 'data'],
            "services": ['services', 'what do you offer']
        }
        
        # Find matching category
        matched_category = None
        for category, keywords in category_keywords.items():
            if any(keyword in q for keyword in keywords):
                matched_category = category
                break
        
        # Get answer from category
        if matched_category and matched_category in self.kb_categories:
            answer = self.kb_categories[matched_category]()
            return {
                "success": True,
                "category": matched_category,
                "answer": answer,
                "source": "knowledge_base"
            }
        
        # General fallback
        return {
            "success": True,
            "category": "general",
            "answer": (
                "Acme Dental: €60 checkups (30 min), one dentist. Student/Senior: €50. "
                "Checkup includes: oral exam, gum check, concern review. X-rays NOT included. "
                "Free cancel 24hrs+, €20 fee if less. Payment: card/contactless/cash. "
                "Bring: ID, medical info, insurance details. Arrive 5-10min early. "
                "No account needed - just name & email."
            ),
            "source": "knowledge_base"
        }
    
    def get_clinic_info(self) -> Dict[str, Any]:
        """Get comprehensive clinic information.
        
        Returns:
            Dictionary containing all clinic information
        """
        return {
            "success": True,
            "clinic": self.clinic_info,
            "formatted": (
                f"**Acme Dental Clinic Information:**\n"
                f"- Location: {self.clinic_info['location']}\n"
                f"- Hours: {self.clinic_info['hours']}\n"
                f"- Services: {self.clinic_info['service']} ({self.clinic_info['duration']}, {self.clinic_info['price']})\n"
                f"- Contact: {self.clinic_info['contact_email']} | {self.clinic_info['contact_phone']}\n"
                f"- Staff: {self.clinic_info['staff']}\n"
                f"- Description: {self.clinic_info['description']}"
            )
        }
    
    def get_contact_info(self) -> Dict[str, str]:
        """Get clinic contact information.
        
        Returns:
            Dictionary with contact details
        """
        return {
            "email": self.clinic_info["contact_email"],
            "phone": self.clinic_info["contact_phone"],
            "location": self.clinic_info["location"]
        }
