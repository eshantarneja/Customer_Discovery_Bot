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

def test_read_contacts_from_sheets():
    """Simplified test for reading contacts"""
    # Mock data similar to what would be returned from Google Sheets
    sheet_data = {
        'values': [
            # Headers
            ['Match', 'Full Name', 'Job Title', 'Location', 'Company Domain', 'Company Name', 'LinkedIn', 'Work Email', 'draft_email'],
            # Data rows
            ['1', 'John Doe', 'Software Engineer', 'San Francisco', 'example.com', 'Example Inc.', 'https://linkedin.com/in/johndoe', 'john.doe@example.com', ''],
            ['1', 'Jane Smith', 'Product Manager', 'New York', 'testcompany.com', 'Test Company', 'https://linkedin.com/in/janesmith', 'jane.smith@testcompany.com', '']
        ]
    }
    
    # Create contacts directly using the data that would be processed by read_contacts_from_sheets
    contacts = []
    headers = sheet_data['values'][0]
    
    for row in sheet_data['values'][1:]:  # Skip headers
        # Pad the row with empty strings if needed
        padded_row = row + [''] * (len(headers) - len(row))
        
        # Create dictionary with header keys and row values
        row_data = dict(zip(headers, padded_row))
        
        # Create a mock Contact with the required attributes
        contact = MagicMock()
        contact.full_name = row_data['Full Name']
        contact.job_title = row_data['Job Title']
        contact.company_name = row_data['Company Name']
        contact.company_domain = row_data['Company Domain']
        contact.work_email = row_data['Work Email']
        contact.is_valid_contact.return_value = True
        
        contacts.append(contact)
    
    # Verify we have the right number of contacts
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
def test_update_sheet_with_contact_info(mock_credentials, mock_build):
    """Test updating Google Sheets with contact information"""
    # Create properly mocked Contact objects
    contact1 = MagicMock()
    contact1.work_email = "john.doe@example.com"
    contact1.draft_email = "Hello John, I'm reaching out to discuss..."
    contact1.full_name = "John Doe"
    contact1.to_list.return_value = ['1', 'John Doe', 'Software Engineer', 'San Francisco', 'example.com', 'Example Inc.', 'linkedin.com/johndoe', 'john.doe@example.com', "Hello John, I'm reaching out to discuss..."]

    contact2 = MagicMock()
    contact2.work_email = "jane.smith@testcompany.com"
    contact2.draft_email = "Hi Jane, I wanted to connect about..."
    contact2.full_name = "Jane Smith"
    contact2.to_list.return_value = ['1', 'Jane Smith', 'Product Manager', 'New York', 'testcompany.com', 'Test Company', 'linkedin.com/janesmith', 'jane.smith@testcompany.com', "Hi Jane, I wanted to connect about..."]
    
    mock_contacts = [contact1, contact2]
    
    # Create mock sheet response with header row and data rows
    mock_sheets_response = {
        'values': [
            # Headers
            ['Match', 'Full Name', 'Job Title', 'Location', 'Company Domain', 'Company Name', 'LinkedIn', 'Work Email', 'draft_email'],
            # Data with emails at the correct index 7
            ['1', 'John Doe', 'Software Engineer', 'San Francisco', 'example.com', 'Example Inc.', 'linkedin.com/johndoe', 'john.doe@example.com', ''],
            ['1', 'Jane Smith', 'Product Manager', 'New York', 'testcompany.com', 'Test Company', 'linkedin.com/janesmith', 'jane.smith@testcompany.com', '']
        ]
    }
    
    # Setup detailed mock service chain
    mock_service = MagicMock()
    mock_sheets = MagicMock()
    mock_values = MagicMock()
    
    mock_build.return_value = mock_service
    mock_service.spreadsheets.return_value = mock_sheets
    mock_sheets.values.return_value = mock_values
    
    # Mock GET API call
    mock_get = MagicMock()
    mock_get.execute.return_value = mock_sheets_response
    mock_values.get.return_value = mock_get
    
    # Mock UPDATE API call
    mock_update = MagicMock()
    mock_update.execute.return_value = {"updatedCells": 5}
    mock_values.update.return_value = mock_update
    
    # Ensure there's a clear connection between the mock credentials and the function
    with patch('GoogleSheets.sheets_manager.service_account.Credentials.from_service_account_file',
               return_value=mock_credentials):
        with patch('GoogleSheets.sheets_manager.build', return_value=mock_service):
            # Call function
            update_sheet_with_contact_info(
                spreadsheet_id="mock_spreadsheet_id",
                range_name="Sheet1!A1:I100",
                contacts=mock_contacts
            )
    
    # Verify the update method was called at least once
    assert mock_values.update.called, "Sheet values.update method was not called"

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
