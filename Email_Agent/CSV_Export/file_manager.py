"""
Module for handling file operations, primarily CSV reading and writing.
"""
import os
import csv
from datetime import datetime
from typing import List, Dict, Any
from Classes.contacts import Contact

def read_contacts_from_csv(file_path, limit=100):
   """
   Read contacts from a CSV file, up to a specified limit.
   
   :param file_path: Path to the CSV file
   :param limit: Maximum number of contacts to read (default: 100)
   :return: List of contact dictionaries
   """
   contacts = []
   try:
       with open(file_path, 'r') as csvfile:
           reader = csv.DictReader(csvfile)
           for i, row in enumerate(reader):
               if i >= limit:
                   break
               if row.get('Work Email') and row.get('Work Email').strip():
                   contact = {
                   'name': row.get('Full Name', ''),
                   'email': row.get('Work Email', ''),
                   'company_domain': row.get('Company Domain', ''),
                   'job_title': row.get('Job Title', ''),
                   'LinkedIn': row.get('LinkedIn Profile', ''),
                   'company': row.get('Company Name', '')
                }
               contacts.append(contact)
   except Exception as e:
       print(f"An error occurred while reading the CSV file: {e}")
   return contacts

def save_email_to_csv(name, email, subject, body):
    """
    Save email details to a CSV file.
    Creates a new file if it doesn't exist, otherwise appends to existing file.
    """
    # Create 'logs' directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create filename with current date
    filename = os.path.join(logs_dir, f'email_log_{datetime.now().strftime("%Y-%m-%d")}.csv')
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(filename)
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Name', 'Email Address', 'Subject', 'Email Body', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write headers if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write email data
            writer.writerow({
                'Name': name,
                'Email Address': email,
                'Subject': subject,
                'Email Body': body,
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
        print(f"Email saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving email to CSV: {str(e)}")
        return False

def save_emails_to_csv(contacts: List[Contact], output_file=None):
    """
    Save multiple email details to a CSV file at once.
    
    :param contacts: List of Contact objects with draft emails
    :param output_file: Optional file path for output (used in testing)
    :return: Path to the created CSV file
    """
    # Create 'logs' directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir) and output_file is None:
        os.makedirs(logs_dir)
    
    # Create filename with current date or use provided output file
    if output_file:
        filename = output_file
    else:
        filename = os.path.join(logs_dir, f'bulk_email_log_{datetime.now().strftime("%Y-%m-%d")}.csv')
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(filename)
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Name', 'Email Address', 'Company', 'Job Title', 'Email Body', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write headers if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write all emails
            for contact in contacts:
                if contact.draft_email:
                    writer.writerow({
                        'Name': contact.full_name,
                        'Email Address': contact.work_email,
                        'Company': contact.company_name,
                        'Job Title': contact.job_title,
                        'Email Body': contact.draft_email,
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
        print(f"All emails saved to {filename}")
        return filename
    except Exception as e:
        print(f"Error saving emails to CSV: {str(e)}")
        return None
