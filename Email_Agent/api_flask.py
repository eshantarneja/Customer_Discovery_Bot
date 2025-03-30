import os
import json
import random
import string
from typing import List, Dict, Any
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import tempfile
import asyncio

# Import application modules with correct paths
from Classes.contacts import Contact
from Graph.email_agent import EmailAgent
# Import our custom secrets module with a different name to avoid conflicts
import secrets as custom_secrets
from secrets import get_secret as get_app_secret
from CSV_Export.file_manager import save_emails_to_csv
from GoogleSheets.sheets_manager import read_contacts_from_sheets, update_sheet_with_contact_info
from Helper.contact_processor import process_all_contacts
from Email_Sender.email import send_contacts_email

app = Flask(__name__)

# Global variables
SPREADSHEET_ID = '1xyGHQBRn5dfFG3utdAifs2ubMJtolVK9Qoy9YJGoheg'
RANGE_NAME = 'Sheet1!A1:I'

def initialize_llm():
    openai_api_key = get_secret("OpenAPI_KEY")
    return ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai_api_key)

def search_web(contact):
    context = {}
    context['company_info'] = tavily_context_search(contact.company)
    context['person_info'] = tavily_context_search(contact.name)
    return context

def update_context(email_agent, web_context):
    raw_context = web_context['company_info'] + "\n" + web_context['person_info']
    return email_agent.extract_relevant_content(raw_context)

@app.route('/generate-email', methods=['POST'])
def generate_email():
    try:
        data = request.json
        
        # Initialize LLM
        llm = initialize_llm()
        
        # Create Contact object
        contact_data = data.get('contact')
        if not contact_data:
            return jsonify({"error": "Contact data is required"}), 400
        contact = Contact(contact_data)
        
        # Create Sender object
        sender_data = data.get('sender')
        if not sender_data:
            return jsonify({"error": "Sender data is required"}), 400
            
        sender = Sender(
            name=sender_data.get('name'),
            resume=sender_data.get('resume'),
            career_interest=sender_data.get('career_interest'),
            key_accomplishments=sender_data.get('key_accomplishments', []),
            llm=llm
        )
        
        # Process sender information
        sender.process_relevant_content()
        
        # Create EmailAgent
        email_agent = EmailAgent(contact, sender)
        
        # Search web and process context
        web_context = search_web(contact)
        web_relevant_content = update_context(email_agent, web_context)
        
        # Run email workflow
        final_state = run_email_workflow(
            email_agent=email_agent,
            sender_info=sender.get_relevant_content(),
            context=web_relevant_content
        )
        
        return jsonify({
            "draft": final_state["draft"],
            "critique": final_state["critique"],
            "revision_count": final_state["revision_count"],
            "web_context": web_relevant_content
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process-contacts', methods=['POST', 'GET'])
def process_contacts():
    """Process contacts and optionally send emails"""
    try:
        # Get parameters from query string or form data
        if request.method == 'GET':
            is_test = request.args.get('is_test', 'false').lower() == 'true'
            batch_size = int(request.args.get('batch_size', 5))
            contact_limit = int(request.args.get('contact_limit', 100))
            email_template = request.args.get('email_template', None)
            send_email = request.args.get('send_email', 'false').lower() == 'true'
            recipient_email = request.args.get('recipient_email', None)
        else:  # POST
            data = request.json
            is_test = data.get('is_test', False)
            batch_size = data.get('batch_size', 5)
            contact_limit = data.get('contact_limit', 100)
            email_template = data.get('email_template', None)
            send_email = data.get('send_email', False)
            recipient_email = data.get('recipient_email', None)
            
            # If contacts were provided directly in the POST data, use those
            if 'contacts' in data:
                contacts = [Contact(c) for c in data['contacts']]
            else:
                # Otherwise read from Google Sheets
                contacts = read_contacts_from_sheets(SPREADSHEET_ID, RANGE_NAME, limit=contact_limit)
        
        # If GET or no contacts in POST data, read from Google Sheets
        if request.method == 'GET' or ('contacts' not in data if request.method == 'POST' else True):
            contacts = read_contacts_from_sheets(SPREADSHEET_ID, RANGE_NAME, limit=contact_limit)
        
        # Process the contacts
        processed_contacts = asyncio.run(process_all_contacts(contacts, batch_size, email_template))
        
        # Generate a unique filename for the CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"contacts_{timestamp}.csv"
        
        # Save emails to CSV
        csv_path = save_emails_to_csv(processed_contacts, filename)
        
        # Update Google Sheet if not in test mode
        if not is_test:
            update_sheet_with_contact_info(SPREADSHEET_ID, RANGE_NAME, processed_contacts)
        
        # Prepare the response
        response = {
            "status": "success",
            "mode": "test" if is_test else "production",
            "processed_count": len(processed_contacts),
            "csv_file": filename
        }
        
        # Send email if requested
        if send_email:
            # Default to billenewman4@gmail.com if no recipient specified
            if not recipient_email:
                recipient_email = "billenewman4@gmail.com"
                response["default_email_used"] = True
            
            # Send email with the CSV attached
            email_subject = f"Contact Processing Results - {timestamp}"
            email_body = f"Attached is a CSV file containing {len(processed_contacts)} processed contacts with draft emails."
            
            email_sent = send_contacts_email(
                contacts=processed_contacts,
                recipient_email=recipient_email,
                subject=email_subject,
                body=email_body
            )
            
            response["email_sent"] = email_sent
            response["recipient_email"] = recipient_email
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/process-and-email', methods=['POST', 'GET'])
def process_and_email():
    """Process contacts and email the results"""
    try:
        # Get parameters from query string or form data
        if request.method == 'GET':
            is_test = request.args.get('is_test', 'false').lower() == 'true'
            batch_size = int(request.args.get('batch_size', 5))
            contact_limit = int(request.args.get('contact_limit', 100))
            email_template = request.args.get('email_template', None)
            recipient_email = request.args.get('recipient_email', None)
            email_subject = request.args.get('email_subject', f"Contact Processing Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            email_body = request.args.get('email_body', "Attached is a CSV file containing processed contacts with draft emails.")
        else:  # POST
            data = request.json
            is_test = data.get('is_test', False)
            batch_size = data.get('batch_size', 5)
            contact_limit = data.get('contact_limit', 100)
            email_template = data.get('email_template', None)
            recipient_email = data.get('recipient_email', None)
            email_subject = data.get('email_subject', f"Contact Processing Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            email_body = data.get('email_body', "Attached is a CSV file containing processed contacts with draft emails.")
            
            # If contacts were provided directly in the POST data, use those
            if 'contacts' in data:
                contacts = [Contact(c) for c in data['contacts']]
            else:
                # Otherwise read from Google Sheets
                contacts = read_contacts_from_sheets(SPREADSHEET_ID, RANGE_NAME, limit=contact_limit)
        
        # If GET or no contacts in POST data, read from Google Sheets
        if request.method == 'GET' or ('contacts' not in data if request.method == 'POST' else True):
            contacts = read_contacts_from_sheets(SPREADSHEET_ID, RANGE_NAME, limit=contact_limit)
        
        # Process the contacts
        processed_contacts = asyncio.run(process_all_contacts(contacts, batch_size, email_template))
        
        # Generate a unique filename for the CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"contacts_{timestamp}.csv"
        
        # Save emails to CSV
        csv_path = save_emails_to_csv(processed_contacts, filename)
        
        # Update Google Sheet if not in test mode
        if not is_test:
            update_sheet_with_contact_info(SPREADSHEET_ID, RANGE_NAME, processed_contacts)
        
        # Default to billenewman4@gmail.com if no recipient specified
        if not recipient_email:
            recipient_email = "billenewman4@gmail.com"
        
        # Send email with the CSV attached
        email_sent = send_contacts_email(
            contacts=processed_contacts,
            recipient_email=recipient_email,
            subject=email_subject,
            body=email_body
        )
        
        # Prepare the response
        response = {
            "status": "success" if email_sent else "error",
            "message": "Email sent successfully" if email_sent else "Failed to send email",
            "mode": "test" if is_test else "production",
            "processed_count": len(processed_contacts),
            "recipient_email": recipient_email,
            "csv_file": filename
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Google Cloud deployment"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # Use port 8080 for consistency with the Customer Discovery Bot's expected configuration
    # Disable debug mode to avoid conflicts with Python's built-in secrets module
    app.run(host='0.0.0.0', port=8080, debug=False)
