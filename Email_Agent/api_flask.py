import os
import json
import random
import string
from typing import List, Dict, Any
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import tempfile

# Import application modules with correct paths
from Classes.contacts import Contact
from Graph.email_agent import EmailAgent
from CSV_Export.file_manager import save_emails_to_csv
from GoogleSheets.sheets_manager import read_contacts_from_sheets, update_sheet_with_contact_info
from Helper.contact_processor import process_all_contacts
from Email_Sender.email import send_contacts_email

# Initialize Flask app
app = Flask(__name__)

# Global variables
SPREADSHEET_ID = '1xyGHQBRn5dfFG3utdAifs2ubMJtolVK9Qoy9YJGoheg'
RANGE_NAME = 'Sheet1!A1:I'

# Create a custom JSON encoder to handle Contact objects
class ContactJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Contact):
            contact_dict = {
                'full_name': getattr(obj, 'full_name', ''),
                'work_email': getattr(obj, 'work_email', ''),
                'company_name': getattr(obj, 'company_name', ''),
                'company_domain': getattr(obj, 'company_domain', ''),
                'job_title': getattr(obj, 'job_title', ''),
                'LinkedIn': getattr(obj, 'LinkedIn', '')
            }
            
            # Safely add optional attributes
            if hasattr(obj, 'draft_email'):
                contact_dict['draft_email'] = obj.draft_email
            
            if hasattr(obj, 'context'):
                contact_dict['context_length'] = len(obj.context) if obj.context else 0
                
            return contact_dict
        return super().default(obj)

# Register the custom encoder with Flask
app.json_encoder = ContactJSONEncoder

@app.route('/', methods=['GET'])
def root():
    """Root endpoint for health checks"""
    return jsonify({'status': 'online', 'service': 'Customer Discovery Bot', 'timestamp': datetime.now().isoformat()})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Google Cloud deployment"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/contacts', methods=['GET'])
def get_contacts():
    """Get contacts from Google Sheets"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        contacts = read_contacts_from_sheets(SPREADSHEET_ID, RANGE_NAME, limit=limit)
        return jsonify({
            'status': 'success',
            'count': len(contacts),
            'contacts': contacts
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/process-contacts', methods=['POST'])
def process_contacts():
    """Process contacts and generate emails"""
    try:
        import asyncio
        data = request.json
        
        # Get parameters from request
        is_test = data.get('is_test', True)  # Default to test mode for safety
        batch_size = data.get('batch_size', 5)
        contact_limit = data.get('contact_limit', 100)
        email_template = data.get('email_template')
        
        # Optional: Use provided contacts or fetch from sheets
        provided_contacts = data.get('contacts')
        if provided_contacts:
            # Convert dictionary to Contact objects
            contacts = [Contact(contact_dict) for contact_dict in provided_contacts]
        else:
            # Fetch from Google Sheets
            contacts = read_contacts_from_sheets(SPREADSHEET_ID, RANGE_NAME, limit=contact_limit)
        
        # Process contacts - using asyncio.run to handle async function
        processed_contacts = asyncio.run(process_all_contacts(contacts, batch_size, email_template))
        
        # Save to CSV file
        csv_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        csv_path = csv_file.name
        csv_file.close()  # Close so we can write to it
        
        # Use existing function to create CSV
        output_path = create_contact_csv(processed_contacts, csv_path)
        
        # Update Google Sheet if not in test mode
        if not is_test and processed_contacts:
            update_sheet_with_contact_info(SPREADSHEET_ID, RANGE_NAME, processed_contacts)
        
        return jsonify({
            'status': 'success',
            'mode': 'TEST' if is_test else 'PRODUCTION',
            'processed_count': len(processed_contacts),
            'contacts': processed_contacts,
            'csv_path': output_path
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/process-and-email', methods=['POST'])
def process_and_email():
    """Process contacts and email the results"""
    try:
        import asyncio
        data = request.json
        
        # Get parameters from request
        is_test = data.get('is_test', True)  # Default to test mode for safety
        batch_size = data.get('batch_size', 5)
        contact_limit = data.get('contact_limit', 100)
        email_template = data.get('email_template')
        recipient_email = data.get('recipient_email')
        
        if not recipient_email:
            return jsonify({'status': 'error', 'message': 'Recipient email is required'}), 400
        
        # Fetch contacts from Google Sheets
        contacts = read_contacts_from_sheets(SPREADSHEET_ID, RANGE_NAME, limit=contact_limit)
        
        # Process contacts - using asyncio.run to handle async function
        processed_contacts = asyncio.run(process_all_contacts(contacts, batch_size, email_template))
        
        # Update Google Sheet if not in test mode
        if not is_test and processed_contacts:
            update_sheet_with_contact_info(SPREADSHEET_ID, RANGE_NAME, processed_contacts)
        
        # Send email with processed contacts
        email_sent = send_contacts_email(
            contacts=processed_contacts,
            recipient_email=recipient_email,
            subject=data.get('email_subject'),
            body=data.get('email_body')
        )
        
        return jsonify({
            'status': 'success' if email_sent else 'error',
            'message': 'Email sent successfully' if email_sent else 'Failed to send email',
            'mode': 'TEST' if is_test else 'PRODUCTION',
            'processed_count': len(processed_contacts),
            'contacts': processed_contacts
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/download-csv/<filename>', methods=['GET'])
def download_csv(filename):
    """Download a previously generated CSV file"""
    try:
        logs_dir = 'logs'
        file_path = os.path.join(logs_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
            
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Helper to generate a random string
def generate_random_string(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

# Helper function to create contact CSV
def create_contact_csv(contacts, filename=None):
    """Create a CSV file with contact information"""
    if not filename:
        # Create filename with timestamp
        filename = f"contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Ensure logs directory exists
    logs_dir = 'logs'
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create full path
    if not os.path.isabs(filename):
        path = os.path.join(logs_dir, filename)
    else:
        path = filename
    
    # Save emails to CSV
    save_emails_to_csv(contacts, path)
    
    return path

# Add app.yaml configuration for Google Cloud
def create_app_yaml():
    """Create app.yaml file for Google Cloud deployment"""
    yaml_content = """
# app.yaml for Google Cloud App Engine deployment
runtime: python39
entrypoint: gunicorn -b :$PORT api_flask:app

env_variables:
  PYTHONUNBUFFERED: 1

handlers:
- url: /.*
  script: auto

automatic_scaling:
  min_instances: 1
  max_instances: 5
  min_idle_instances: 1
  max_idle_instances: 1
  min_pending_latency: 30ms
  max_pending_latency: 100ms
  target_cpu_utilization: 0.65
"""
    
    with open('app.yaml', 'w') as f:
        f.write(yaml_content)
    
    print("Created app.yaml file for Google Cloud deployment")
    return yaml_content

# Run the Flask application - this is for both local development and Cloud Run
if __name__ == '__main__':
    # Get port from environment variable or default to 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

# Helper function to create a Contact CSV without sending an email
def create_contact_csv(contacts: List[Contact], output_file: str = None) -> str:
    """Create a CSV file with contact information"""
    # Create 'logs' directory if it doesn't exist and output_file is not specified
    if not output_file:
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        output_file = os.path.join(logs_dir, f'contacts_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    
    try:
        save_emails_to_csv(contacts)  # Use existing function
        return output_file
    except Exception as e:
        print(f"Error creating CSV file: {str(e)}")
        return ""

if __name__ == '__main__':
    # Create deployment files
    create_app_yaml()
    create_requirements_txt()
    
    # Start Flask app
    print("Starting Flask API server on port 5001...")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
