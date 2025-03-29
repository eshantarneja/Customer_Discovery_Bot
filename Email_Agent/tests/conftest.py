"""
Common test fixtures and configuration for unit tests
"""
import os
import sys
import pytest
import tempfile
from typing import List

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Classes.contacts import Contact

@pytest.fixture
def mock_contacts() -> List[Contact]:
    """Create a list of mock contacts for testing"""
    contacts = []
    # Create sample contacts
    # Create sample contacts with proper data parameter
    contact1_data = {
        'Match': 'Yes',
        'Full Name': 'John Doe',
        'Work Email': 'john.doe@example.com',
        'Company Name': 'Example Inc.',
        'Company Domain': 'example.com',
        'Job Title': 'Software Engineer',
        'LinkedIn': 'https://linkedin.com/in/johndoe',
        'Location': 'San Francisco, CA',
        'draft_email': ''
    }
    
    contact2_data = {
        'Match': 'Yes',
        'Full Name': 'Jane Smith',
        'Work Email': 'jane.smith@testcompany.com',
        'Company Name': 'Test Company',
        'Company Domain': 'testcompany.com',
        'Job Title': 'Product Manager',
        'LinkedIn': 'https://linkedin.com/in/janesmith',
        'Location': 'New York, NY',
        'draft_email': ''
    }
    
    contacts.append(Contact(contact1_data))
    contacts.append(Contact(contact2_data))
    return contacts

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
        yield temp_file.name
    # Clean up after the test
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)

@pytest.fixture
def mock_env_variables(monkeypatch):
    """Set mock environment variables for testing"""
    monkeypatch.setenv("SMTP_SERVER", "smtp.mockserver.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("EMAIL_USER", "test@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "mock_password")
    monkeypatch.setenv("OpenAPI_KEY", "mock-openai-api-key")
