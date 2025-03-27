"""
Module for handling Google Sheets operations.
"""
import os
from typing import List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from Classes.contacts import Contact

def read_contacts_from_sheets(spreadsheet_id: str, range_name: str, limit: int = 100) -> List[Contact]:
    """
    Read contacts from Google Sheets and return as Contact objects.
    
    :param spreadsheet_id: The ID of the Google Sheet
    :param range_name: The range to read (e.g., 'Sheet1!A2:G100')
    :param limit: Maximum number of contacts to read
    :return: List of Contact objects
    """
    try:
        # Setup Google Sheets credentials
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        SERVICE_ACCOUNT_FILE = 'customeroutreach-440901-18943c7c0e95.json'
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # Build the Google Sheets service
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        
        # Request data from Google Sheets
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print('No data found in sheet.')
            return []
            
        # Get headers from first row
        headers = values[0]
        
        # Define expected headers based on Contact object
        expected_headers = [
            'Match', 'Full Name', 'Job Title', 'Location', 
            'Company Domain', 'Company Name', 'LinkedIn', 
            'Work Email', 'draft_email'
        ]
        
        # Check if headers match expected headers
        if headers != expected_headers:
            raise ValueError(f"Header mismatch: Expected {expected_headers}, but got {headers}")
        
        # Convert rows to Contact objects
        contacts = []
        processed = 0
        row_index = 1  # Start after header

        while processed < limit and row_index < len(values):
            row = values[row_index]
            # Pad the row with empty strings if needed
            padded_row = row + [''] * (len(headers) - len(row))
            
            # Create dictionary with header keys and row values
            row_data = dict(zip(headers, padded_row))
            
            # Create Contact object
            contact = Contact(row_data)
            
            # Only add valid contacts and increment counter when we actually append
            if contact.is_valid_contact():
                contacts.append(contact)
                processed += 1
            
            row_index += 1
        
        print(f"Successfully read {len(contacts)} contacts from Google Sheets")
        return contacts
        
    except Exception as e:
        print(f"Error reading from Google Sheets: {str(e)}")
        return []

def update_sheet_with_contact_info(spreadsheet_id: str, range_name: str, contacts: List[Contact]):
    """
    Update specific rows in Google Sheet with processed contact information.
    Only updates rows where we find a matching contact and only updates changed fields.
    
    :param spreadsheet_id: The ID of the Google Sheet
    :param range_name: The range to update (e.g., 'Sheet1!A2:G100')
    :param contacts: List of Contact objects with updated information
    """
    try:
        # Setup the Sheets API with write permissions
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'customeroutreach-440901-18943c7c0e95.json'
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        
        # First, get the entire sheet to find row numbers for our contacts
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print('No data found in sheet. Cannot update.')
            return
        
        # Create a map of work emails to row indices
        email_to_row = {}
        for i, row in enumerate(values):
            if i == 0:  # Skip header row
                continue
            
            if len(row) >= 8:  # Make sure the row has enough columns for the email
                email = row[7]  # Work Email is the 8th column (index 7)
                if email and email.strip():
                    email_to_row[email.strip()] = i
        
        # For each contact, update its row if found
        update_count = 0
        for contact in contacts:
            if not contact.work_email or not contact.work_email.strip():
                continue
                
            # Find the row index for this contact
            row_index = email_to_row.get(contact.work_email.strip())
            if row_index is None:
                print(f"Contact with email {contact.work_email} not found in sheet")
                continue
            
            # Convert row index to A1 notation for the range to update
            range_to_update = f"{range_name.split('!')[0]}!A{row_index+1}:I{row_index+1}"
            
            # Get existing row data to compare
            existing_row = values[row_index] if row_index < len(values) else []
            new_row = contact.to_list()  # Get new data as list
            
            # Pad existing row with empty strings if needed
            existing_row = existing_row + [''] * (len(new_row) - len(existing_row))
            
            # Check if anything has changed
            if existing_row == new_row:
                print(f"No changes for {contact.work_email}, skipping update")
                continue
            
            # Prepare the update request
            body = {
                'values': [new_row]
            }
            
            # Execute the update request
            try:
                result = sheet.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_to_update,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                update_count += 1
                updated_cells = result.get('updatedCells', 0)
                print(f"Updated {updated_cells} cells for contact: {contact.full_name}")
                
            except Exception as update_error:
                print(f"Error updating row {row_index+1} for {contact.work_email}: {str(update_error)}")
        
        print(f"Successfully updated {update_count} contacts in Google Sheets")
        
    except Exception as e:
        print(f"Error updating sheet: {str(e)}")
