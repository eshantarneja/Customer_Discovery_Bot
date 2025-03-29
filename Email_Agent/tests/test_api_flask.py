"""
Test the Flask API server functionality
"""
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_flask import app
from Classes.contacts import Contact

@pytest.fixture
def mock_contacts_dict():
    """Create a list of mock contacts as dictionaries for API tests"""
    return [
        {
            'match': 'Yes',
            'full_name': 'John Doe',
            'work_email': 'john.doe@example.com',
            'company_name': 'Example Inc.',
            'company_domain': 'example.com',
            'job_title': 'Software Engineer',
            'linkedin': 'https://linkedin.com/in/johndoe',
            'location': 'San Francisco, CA',
            'draft_email': ''
        },
        {
            'match': 'Yes',
            'full_name': 'Jane Smith',
            'work_email': 'jane.smith@testcompany.com',
            'company_name': 'Test Company',
            'company_domain': 'testcompany.com',
            'job_title': 'Product Manager',
            'linkedin': 'https://linkedin.com/in/janesmith',
            'location': 'New York, NY',
            'draft_email': ''
        }
    ]

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the /health endpoint"""
    response = client.get('/health')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_root_endpoint(client):
    """Test the root (/) endpoint"""
    response = client.get('/')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'online'
    assert data['service'] == 'Customer Discovery Bot'
    assert 'timestamp' in data

@patch('api_flask.read_contacts_from_sheets')
def test_get_contacts_endpoint(mock_read_contacts, client, mock_contacts_dict):
    """Test the /contacts endpoint for retrieving contacts"""
    # Setup mock
    mock_read_contacts.return_value = mock_contacts_dict
    
    # Make request
    response = client.get('/contacts?spreadsheet_id=test_id&range_name=Sheet1!A1:I10&limit=10')
    
    # Print response data for debugging
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['count'] == 2
    assert len(data['contacts']) == 2

@patch('api_flask.process_all_contacts')
def test_process_contacts_endpoint(mock_process, client, mock_contacts_dict):
    """Test the /process endpoint for processing contacts"""
    # Setup mock
    mock_process.return_value = mock_contacts_dict
    
    # Create test data - must be an object, not a list
    test_data = {
        'is_test': True,
        'batch_size': 5,
        'contact_limit': 10,
        'email_template': 'Hi {{name}}, this is a test email',
        'contacts': [
            {
                'full_name': 'John Doe',
                'work_email': 'john.doe@example.com',
                'company_name': 'Example Inc.'
            },
            {
                'full_name': 'Jane Smith',
                'work_email': 'jane.smith@testcompany.com',
                'company_name': 'Test Company'
            }
        ]
    }
    
    # Make request
    response = client.post(
        '/process-contacts',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # Print response data for debugging
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    
    # Check response
    assert response.status_code == 200
    assert mock_process.called

@patch('api_flask.send_contacts_email')
@patch('api_flask.process_all_contacts')
@patch('api_flask.read_contacts_from_sheets')
def test_send_email_endpoint(mock_read_sheets, mock_process, mock_send_email, client, mock_contacts_dict):
    """Test the /process-and-email endpoint"""
    # Setup mocks
    mock_read_sheets.return_value = mock_contacts_dict
    mock_process.return_value = mock_contacts_dict  # Mock async function
    mock_send_email.return_value = True
    
    # Create test data
    test_data = {
        'recipient_email': 'user@example.com',
        'email_subject': 'Test Email',
        'email_body': 'This is a test email',
        'is_test': True,
        'batch_size': 2,
        'contact_limit': 5,
        'email_template': 'Hi {{name}}, this is a test'
    }
    
    # Make request
    response = client.post(
        '/process-and-email',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'message' in data
    
    # Verify all mocks were called with expected args
    mock_read_sheets.assert_called_once()
    mock_process.assert_called_once()
    mock_send_email.assert_called_once()

@patch('api_flask.send_contacts_email')
@patch('api_flask.process_all_contacts')
@patch('api_flask.read_contacts_from_sheets')
def test_send_email_endpoint_failure(mock_read_sheets, mock_process, mock_send_email, client, mock_contacts_dict):
    """Test the /process-and-email endpoint with a failure"""
    # Setup mocks
    mock_read_sheets.return_value = mock_contacts_dict
    mock_process.return_value = mock_contacts_dict
    mock_send_email.return_value = False  # Email sending fails
    
    # Create test data
    test_data = {
        'recipient_email': 'user@example.com',
        'email_subject': 'Test Email',
        'email_body': 'This is a test email',
        'is_test': True,
        'contact_limit': 5
    }
    
    # Make request
    response = client.post(
        '/process-and-email',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # Check response - the response should indicate error in the status but still be a 200 response
    # based on the actual implementation of process-and-email
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'message' in data
    assert 'Failed to send email' in data['message']
