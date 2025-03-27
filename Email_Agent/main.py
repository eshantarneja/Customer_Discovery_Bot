"""\nMain entry point for the Customer Discovery Email Bot application.\n"""
import os
import asyncio
from typing import List

from Classes.contacts import Contact
from Graph.email_agent import EmailAgent
from CSV_Export.file_manager import save_emails_to_csv
from GoogleSheets.sheets_manager import read_contacts_from_sheets, update_sheet_with_contact_info
from Helper.contact_processor import process_all_contacts
from Web.web_search import search_web

# Global variables
SPREADSHEET_ID = '1xyGHQBRn5dfFG3utdAifs2ubMJtolVK9Qoy9YJGoheg'
RANGE_NAME = 'Sheet1!A1:I'

async def main():
    try:
        SPREADSHEET_ID = '1xyGHQBRn5dfFG3utdAifs2ubMJtolVK9Qoy9YJGoheg'
        
        # Get user inputs
        is_test = input("Is this a test run? (y/n): ").lower() == 'y'
        batch_size = int(input("Enter batch size (default 5): ") or 5)
        contact_limit = int(input("Enter number of contacts to process (default 100): ") or 100)
        
        # Ask if user wants to use a custom email template
        use_custom_template = input("Do you want to use a custom email template? (y/n): ").lower() == 'y'
        email_template = None
        
        if use_custom_template:
            print("\nEnter your custom email template below.")
            print("Include placeholders like [Insert First Name], [Insert specific information], etc.")
            print("Type 'END' on a new line when you're finished.\n")
            
            lines = []
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            
            email_template = "\n".join(lines)
        
        print(f"\nRunning in {'TEST' if is_test else 'PRODUCTION'} mode")
        print(f"Batch size: {batch_size}")
        print(f"Contact limit: {contact_limit}")
        
        # Read contacts with limit
        contacts = read_contacts_from_sheets(SPREADSHEET_ID, RANGE_NAME, limit=contact_limit)
        
        print("\nContacts loaded:")
        for i, contact in enumerate(contacts, 1):
            print(f"\nContact {i}:")
            print(f"Name: {contact.full_name}")
            print(f"Email: {contact.work_email}")
            print(f"Company: {contact.company_domain}")
            print(f"Job Title: {contact.job_title}")
            print(f"LinkedIn: {contact.LinkedIn}")
        
        if contacts:
            print("\nProcessing contacts...")
            # Pass batch_size and email template to process_all_contacts
            processed_contacts = await process_all_contacts(contacts, batch_size, email_template)
            
            if processed_contacts:
                # Export to CSV
                print("\nExporting contacts to CSV...")
                save_emails_to_csv(processed_contacts)

                # Update Google Sheet only if not a test run
                if not is_test:
                    print("\nUpdating Google Sheet...")
                    update_sheet_with_contact_info(SPREADSHEET_ID, RANGE_NAME, processed_contacts)
                else:
                    print("\nTest run - skipping Google Sheet update")
                
                print("\nProcess complete! Updated contacts:")
                for contact in processed_contacts:
                    print(f"\nContact: {contact.full_name}")
                    print(f"Company Context Length: {len(contact.context) if contact.context else 0}")
                    print(f"Draft Email Length: {len(contact.draft_email) if contact.draft_email else 0}")
            else:
                print("No contacts were successfully processed")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    # Normal execution
    asyncio.run(main())
    