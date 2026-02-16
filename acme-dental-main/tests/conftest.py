"""Pytest configuration and fixtures."""

import os
import pytest


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for all tests."""
    # Set dummy API keys to prevent validation errors during tests
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("CALENDLY_API_TOKEN", "test-token")
    monkeypatch.setenv("CALENDLY_URL", "https://calendly.com/test")
