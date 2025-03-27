"""
Module for processing contacts and generating emails.
"""
import asyncio
from typing import List, Dict, Any
from Classes.contacts import Contact
from Graph.email_agent import EmailAgent
from Web.web_search import search_web

async def process_single_contact(contact: Contact, email_agent: EmailAgent):
    """
    Process a single contact asynchronously
    
    :param contact: Contact object to process
    :param email_agent: EmailAgent instance
    :return: Contact with updated information
    """
    try:
        print(f"\nProcessing contact: {contact.full_name} - {contact.work_email}")
        
        # Convert Contact object to dictionary for web search
        contact_dict = {
            'name': contact.full_name,
            'email': contact.work_email,
            'company': contact.company_name,
            'company_domain': contact.company_domain,
            'job_title': contact.job_title
        }
        
        # Search web for information about the company and person
        search_results = await search_web(contact_dict)
        
        # Store the context information in the contact
        contact.context = (
            f"Company information: {search_results['company_info']}\n\n"
            f"Person information: {search_results['person_info']}"
        )
        
        # Process contact with email agent to generate draft email
        experiences, email_body = await email_agent.process_contact(contact)
        
        print(f"Drafted email for {contact.full_name}")
        return contact
        
    except Exception as e:
        print(f"Error processing contact {contact.full_name}: {str(e)}")
        return contact

async def process_all_contacts(contacts: List[Contact], batch_size: int = 5, email_template: str = None):
    """
    Process contacts concurrently in smaller batches to manage API rate limits
    
    :param contacts: List of Contact objects to process
    :param batch_size: Number of contacts to process in each batch
    :return: List of processed Contact objects
    """
    try:
        print(f"Processing {len(contacts)} contacts in batches of {batch_size}")
        
        processed_contacts = []
        email_agent = EmailAgent(email_template=email_template)
        
        # Process contacts in batches
        for i in range(0, len(contacts), batch_size):
            batch = contacts[i:i+batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} contacts)")
            
            # Create tasks for concurrent processing
            tasks = [
                process_single_contact(contact, email_agent) 
                for contact in batch
            ]
            
            # Await all tasks in the batch
            batch_results = await asyncio.gather(*tasks)
            processed_contacts.extend(batch_results)
            
            print(f"Completed batch {i//batch_size + 1}")
            
            # Add a small delay between batches to avoid rate limits
            if i + batch_size < len(contacts):
                print("Pausing briefly before next batch...")
                await asyncio.sleep(2)
        
        print(f"\nSuccessfully processed {len(processed_contacts)} contacts")
        return processed_contacts
        
    except Exception as e:
        print(f"Error in process_all_contacts: {str(e)}")
        return contacts
