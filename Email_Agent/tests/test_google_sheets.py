"""
Test the Google Sheets integration functionality
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GoogleSheets.sheets_manager import read_contacts_from_sheets, update_sheet_with_contact_info
from Classes.contacts import Contact

@pytest.fixture
def mock_sheets_response():
    """Mock response from Google Sheets API"""
    return {
        'values': [
            # Headers
            ['Match', 'Full Name', 'Job Title', 'Location', 'Company Domain', 'Company Name', 'LinkedIn', 'Work Email', 'draft_email'],
            # Data rows
            ['1', 'John Doe', 'Software Engineer', 'San Francisco', 'example.com', 'Example Inc.', 'https://linkedin.com/in/johndoe', 'john.doe@example.com', ''],
            ['1', 'Jane Smith', 'Product Manager', 'New York', 'testcompany.com', 'Test Company', 'https://linkedin.com/in/janesmith', 'jane.smith@testcompany.com', '']
        ]
    }

@patch('googleapiclient.discovery.build')
@patch('google.oauth2.service_account.Credentials.from_service_account_file')
def test_read_contacts_from_sheets(mock_credentials, mock_build, mock_sheets_response):
    """Test reading contacts from Google Sheets"""
    # Setup mocks
    mock_service = MagicMock()
    mock_sheets = MagicMock()
    mock_values = MagicMock()
    
    mock_build.return_value = mock_service
    mock_service.spreadsheets.return_value = mock_sheets
    mock_sheets.values.return_value = mock_values
    mock_values.get.return_value.execute.return_value = mock_sheets_response
    
    # Call function
    contacts = read_contacts_from_sheets(
        spreadsheet_id="mock_spreadsheet_id",
        range_name="Sheet1!A1:I100"
    )
    
    # Verify results
    assert len(contacts) == 2
    
    # Check first contact
    assert contacts[0].full_name == "John Doe"
    assert contacts[0].job_title == "Software Engineer"
    assert contacts[0].company_name == "Example Inc."
    assert contacts[0].company_domain == "example.com"
    assert contacts[0].work_email == "john.doe@example.com"
    
    # Check second contact
    assert contacts[1].full_name == "Jane Smith"
    assert contacts[1].job_title == "Product Manager"
    assert contacts[1].company_name == "Test Company"

@patch('googleapiclient.discovery.build')
@patch('google.oauth2.service_account.Credentials.from_service_account_file')
def test_update_sheet_with_contact_info(mock_credentials, mock_build, mock_contacts, mock_sheets_response):
    """Test updating Google Sheets with contact information"""
    # Add draft emails to contacts
    mock_contacts[0].draft_email = "Hello John, I'm reaching out to discuss..."
    mock_contacts[1].draft_email = "Hi Jane, I wanted to connect about..."
    
    # Setup mocks
    mock_service = MagicMock()
    mock_sheets = MagicMock()
    mock_values = MagicMock()
    mock_batch_update = MagicMock()
    
    mock_build.return_value = mock_service
    mock_service.spreadsheets.return_value = mock_sheets
    mock_sheets.values.return_value = mock_values
    mock_values.get.return_value.execute.return_value = mock_sheets_response
    mock_sheets.values.return_value.batchUpdate.return_value.execute.return_value = {}
    
    # Call function
    update_sheet_with_contact_info(
        spreadsheet_id="mock_spreadsheet_id",
        range_name="Sheet1!A1:I100",
        contacts=mock_contacts
    )
    
    # Verify batch update was called
    assert mock_sheets.values.return_value.batchUpdate.called

@patch('googleapiclient.discovery.build')
@patch('google.oauth2.service_account.Credentials.from_service_account_file')
def test_read_contacts_empty_sheet(mock_credentials, mock_build):
    """Test reading contacts from an empty Google Sheet"""
    # Setup mocks
    mock_service = MagicMock()
    mock_sheets = MagicMock()
    mock_values = MagicMock()
    
    mock_build.return_value = mock_service
    mock_service.spreadsheets.return_value = mock_sheets
    mock_sheets.values.return_value = mock_values
    mock_values.get.return_value.execute.return_value = {'values': []}
    
    # Call function
    contacts = read_contacts_from_sheets(
        spreadsheet_id="mock_spreadsheet_id",
        range_name="Sheet1!A1:I100"
    )
    
    # Verify results
    assert contacts == []
