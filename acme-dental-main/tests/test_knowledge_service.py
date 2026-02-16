"""Unit tests for KnowledgeService."""

import pytest
from src.services.knowledge_service import KnowledgeService


class TestKnowledgeService:
    """Test cases for KnowledgeService."""
    
    @pytest.fixture
    def service(self):
        """Create a KnowledgeService instance."""
        return KnowledgeService()
    
    def test_initialization(self, service):
        """Test service initializes with clinic info."""
        assert service.clinic_info is not None
        assert "location" in service.clinic_info
        assert "price" in service.clinic_info
    
    def test_search_pricing(self, service):
        """Test searching for pricing information."""
        result = service.search_knowledge_base("How much does a checkup cost?")
        assert result["success"] is True
        assert "€60" in result["answer"]
        assert result["category"] == "pricing"
    
    def test_search_duration(self, service):
        """Test searching for duration information."""
        result = service.search_knowledge_base("How long is the appointment?")
        assert result["success"] is True
        assert "30 minutes" in result["answer"]
        assert result["category"] == "duration"
    
    def test_search_what_to_bring(self, service):
        """Test searching for what to bring."""
        result = service.search_knowledge_base("What should I bring?")
        assert result["success"] is True
        assert "photo ID" in result["answer"]
        assert result["category"] == "what_to_bring"
    
    def test_search_cancellation_policy(self, service):
        """Test searching for cancellation policy."""
        result = service.search_knowledge_base("What is the cancellation policy?")
        assert result["success"] is True
        assert "24" in result["answer"]
        assert "€20" in result["answer"]
        assert result["category"] == "cancellation_policy"
    
    def test_search_emergency(self, service):
        """Test searching for emergency information."""
        result = service.search_knowledge_base("Do you offer emergency dental treatment?")
        assert result["success"] is True
        assert "emergency" in result["answer"].lower()
        assert result["category"] == "emergency"
    
    def test_search_fallback(self, service):
        """Test fallback for unknown questions."""
        result = service.search_knowledge_base("what is your favorite color?")
        assert result["success"] is True
        assert result["category"] == "general"
        assert "€60" in result["answer"]  # Should return general info
    
    def test_get_clinic_info(self, service):
        """Test getting full clinic information."""
        result = service.get_clinic_info()
        assert result["success"] is True
        assert "clinic" in result
        assert "formatted" in result
        assert "Dublin" in result["formatted"]
    
    def test_get_contact_info(self, service):
        """Test getting contact information."""
        contact = service.get_contact_info()
        assert "email" in contact
        assert "phone" in contact
        assert "location" in contact
        assert "@" in contact["email"]
