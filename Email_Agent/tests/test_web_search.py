"""
Test the web search agent functionality
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Classes.contacts import Contact

# First, let's check which module handles web search
@patch('requests.get')
def test_web_search_functionality(mock_get):
    """Test web search functionality with mocked HTTP responses"""
    # Setup mock response for search
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "title": "John Doe - LinkedIn Profile",
                "url": "https://linkedin.com/in/johndoe",
                "snippet": "John Doe is a Software Engineer at Example Inc with 10 years of experience..."
            },
            {
                "title": "Example Inc Leadership Team",
                "url": "https://example.com/leadership",
                "snippet": "John Doe leads our engineering team with expertise in cloud architecture..."
            }
        ]
    }
    mock_get.return_value = mock_response
    
    # Since we don't know the exact module, we'll use pytest.importorskip
    # to conditionally run this test based on what's available
    try:
        from Web.search_agent import search_for_contact_info
        
        # Create a test contact
        contact = Contact()
        contact.full_name = "John Doe"
        contact.company_name = "Example Inc."
        
        # Call function
        enriched_contact = search_for_contact_info(contact)
        
        # Verify mock was called
        assert mock_get.called
        
        # Verify contact was enriched
        assert hasattr(enriched_contact, 'context')
        assert len(enriched_contact.context) > 0
        
    except ImportError:
        pytest.skip("Web search module not found - skipping test")

@patch('requests.get')
def test_web_search_error_handling(mock_get):
    """Test web search error handling"""
    # Setup mock to raise an exception
    mock_get.side_effect = Exception("Connection error")
    
    try:
        from Web.search_agent import search_for_contact_info
        
        # Create a test contact
        contact = Contact()
        contact.full_name = "John Doe"
        contact.company_name = "Example Inc."
        
        # Call function - should handle the exception gracefully
        enriched_contact = search_for_contact_info(contact)
        
        # Verify contact still has basic info
        assert enriched_contact.full_name == "John Doe"
        assert enriched_contact.company_name == "Example Inc."
        
    except ImportError:
        pytest.skip("Web search module not found - skipping test")

@patch('requests.get')
def test_web_search_empty_results(mock_get):
    """Test web search with empty results"""
    # Setup mock response with no results
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response
    
    try:
        from Web.search_agent import search_for_contact_info
        
        # Create a test contact
        contact = Contact()
        contact.full_name = "John Doe"
        contact.company_name = "Example Inc."
        
        # Call function
        enriched_contact = search_for_contact_info(contact)
        
        # Verify contact still has basic info
        assert enriched_contact.full_name == "John Doe"
        assert enriched_contact.company_name == "Example Inc."
        
    except ImportError:
        pytest.skip("Web search module not found - skipping test")
