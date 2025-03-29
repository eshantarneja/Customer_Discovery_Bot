"""
Test the CSV export functionality
"""
import os
import sys
import csv
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from CSV_Export.file_manager import save_emails_to_csv

def test_save_emails_to_csv(mock_contacts, temp_csv_file):
    """Test saving contact emails to CSV"""
    # Make sure the file doesn't exist before the test
    if os.path.exists(temp_csv_file):
        os.remove(temp_csv_file)

    # Add draft emails to sample contacts
    mock_contacts[0].draft_email = "Hello John, I'm reaching out to discuss..."
    mock_contacts[1].draft_email = "Hi Jane, I wanted to connect about..."
    
    # Call function
    output_path = save_emails_to_csv(mock_contacts, output_file=temp_csv_file)
    
    # Verify file exists
    assert os.path.exists(output_path)
    
    # Read the file and verify content
    with open(output_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # File should have a header row and two data rows
        assert len(rows) == 3
        
        # Verify headers (first row)
        assert rows[0][0] == "Name"
        assert "Email Address" in rows[0][1]
        assert "Email Body" in rows[0][4]
        
        # Verify data
        assert rows[1][0] == "John Doe"
        assert "john.doe@example.com" in rows[1]
        assert "Hello John" in ''.join(rows[1])
        
        assert rows[2][0] == "Jane Smith"
        assert "jane.smith@testcompany.com" in rows[2]
        assert "Hi Jane" in ''.join(rows[2])

def test_save_emails_to_csv_no_drafts(mock_contacts, temp_csv_file):
    """Test saving contact emails to CSV when no draft emails exist"""
    # Make sure the file doesn't exist before the test
    if os.path.exists(temp_csv_file):
        os.remove(temp_csv_file)
        
    # Ensure contacts have the draft_email attribute but it's empty
    mock_contacts[0].draft_email = ""
    mock_contacts[1].draft_email = ""
    
    # Call function
    output_path = save_emails_to_csv(mock_contacts, output_file=temp_csv_file)
    
    # Since the function skips contacts without draft_email, the file should only have headers
    with open(output_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # Verify only the header row exists (no data rows)
        assert len(rows) == 1
        
        # Verify header fields
        assert rows[0][0] == "Name"
        assert "Email Address" in rows[0][1]
        assert "Company" in rows[0][2]

def test_save_emails_to_csv_default_filename():
    """Test CSV export with default filename generation"""
    # Setup
    test_contacts = []
    contact = MagicMock()
    contact.full_name = "Test User"
    contact.work_email = "test@example.com"
    contact.company_name = "Test Company"
    contact.job_title = "Test Title"
    contact.draft_email = "Test draft"
    test_contacts.append(contact)
    
    # Get current date for filename check
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Call function with default filename
    output_path = save_emails_to_csv(test_contacts)
    
    try:
        # Verify file exists and contains date
        assert os.path.exists(output_path)
        assert current_date in output_path
        assert "bulk_email_log" in output_path
        
        # Read the file and verify content
        with open(output_path, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Verify headers and data
            assert rows[0][0] == "Name"
            assert "Email Address" in rows[0]
            assert "Email Body" in rows[0]
            assert rows[1][0] == "Test User"
            assert "Test draft" in ''.join(rows[1])
    finally:
        # Clean up test file
        if os.path.exists(output_path):
            os.remove(output_path)
