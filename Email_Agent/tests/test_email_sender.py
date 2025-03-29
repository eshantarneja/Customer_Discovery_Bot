"""
Test the email sending functionality
"""
import os
import sys
import pytest
import csv
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Email_Sender.email import send_contacts_email, create_contact_csv

def test_create_contact_csv(mock_contacts, temp_csv_file):
    """Test creating a CSV file with contact information"""
    # Make sure the file doesn't exist before the test
    if os.path.exists(temp_csv_file):
        os.remove(temp_csv_file)
    
    # Add draft emails to contacts for the test
    mock_contacts[0].draft_email = "Hello, this is a test email for John"
    mock_contacts[1].draft_email = "Hello, this is a test email for Jane"
    
    # Call function with mock contacts
    output_path = create_contact_csv(mock_contacts, temp_csv_file)
    
    # Check that the file was created
    assert os.path.exists(output_path)
    
    # Read the file and verify content
    with open(output_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # Verify headers
        assert rows[0][0] == "Name"
        assert "Email Address" in rows[0][1]
        assert "Company" in rows[0][2]
        assert "Job Title" in rows[0][3]
        assert "Email Body" in rows[0][4]
        
        # Verify data for first contact
        assert rows[1][0] == "John Doe"
        assert "john.doe@example.com" in rows[1][1]
        assert "Example Inc." in rows[1][2]

@patch('smtplib.SMTP')
def test_send_contacts_email_success(mock_smtp, mock_contacts, mock_env_variables):
    """Test sending contacts via email successfully"""
    # Setup mock
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    # Call function
    result = send_contacts_email(
        contacts=mock_contacts,
        recipient_email="15237bn@gmail.com",
        subject="Test Email",
        body="This is a test email"
    )
    
    # Verify SMTP was called correctly
    assert mock_smtp.called
    assert mock_server.login.called
    assert mock_server.send_message.called
    assert result is True

@patch('smtplib.SMTP')
def test_send_contacts_email_error(mock_smtp, mock_contacts, mock_env_variables):
    """Test handling SMTP error during email sending"""
    # Setup mock to raise an exception
    mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")
    
    # Call function
    result = send_contacts_email(
        contacts=mock_contacts,
        recipient_email="15237bn@gmail.com"
    )
    
    # Verify result
    assert result is False

def test_send_contacts_email_missing_credentials(mock_contacts, monkeypatch):
    """Test handling missing email credentials"""
    # Unset environment variables
    monkeypatch.delenv("EMAIL_USER", raising=False)
    monkeypatch.delenv("EMAIL_PASSWORD", raising=False)
    
    # Call function
    result = send_contacts_email(
        contacts=mock_contacts,
        recipient_email="15237bn@gmail.com"
    )
    
    # Verify result
    assert result is False
