"""
Test script to send an email to a specific address using the Customer Discovery Bot email functionality.
"""
import sys
from secrets import get_secret
from Classes.contacts import Contact
from Email_Sender.email import send_contacts_email

def main():
    # Check if email credentials are set using get_secret
    sender_email = get_secret('EMAIL_USER')
    sender_password = get_secret('EMAIL_PASS')  # Using EMAIL_PASS as in your .env file
    
    # Print debug information (will mask most of the password)
    print(f"Using email: {sender_email}")
    password_masked = sender_password[:2] + '*' * (len(sender_password) - 4) + sender_password[-2:] if sender_password else None
    print(f"Password: {password_masked}")
    
    if not all([sender_email, sender_password]):
        print("ERROR: Email credentials not found in environment variables.")
        print("Please set EMAIL_USER and EMAIL_PASS in your .env file.")
        return False
    
    # Create test contacts
    test_contacts = [
        Contact({
            'Match': 'Yes',
            'Full Name': 'John Doe',
            'Work Email': 'john.doe@example.com',
            'Company Name': 'Example Inc.',
            'Company Domain': 'example.com',
            'Job Title': 'Software Engineer',
            'LinkedIn': 'https://linkedin.com/in/johndoe',
            'Location': 'San Francisco, CA',
            'draft_email': 'Hello John, I wanted to discuss...'
        }),
        Contact({
            'Match': 'Yes',
            'Full Name': 'Jane Smith',
            'Work Email': 'jane.smith@testcompany.com',
            'Company Name': 'Test Company',
            'Company Domain': 'testcompany.com',
            'Job Title': 'Product Manager',
            'LinkedIn': 'https://linkedin.com/in/janesmith',
            'Location': 'New York, NY',
            'draft_email': 'Hi Jane, I would like to connect regarding...'
        })
    ]
    
    # Set recipient email
    recipient_email = "15237bn@gmail.com"
    
    # Set subject and body
    subject = "Customer Discovery Bot - Test Email"
    body = """Hello,

This is a test email sent from the Customer Discovery Bot email functionality.
The attached CSV contains sample contact information.

Best regards,
Customer Discovery Bot
"""
    
    # Send email
    print(f"Sending test email to {recipient_email}...")
    success = send_contacts_email(
        contacts=test_contacts,
        recipient_email=recipient_email,
        subject=subject,
        body=body
    )
    
    if success:
        print("✅ Email sent successfully!")
    else:
        print("❌ Failed to send email. Check the logs for more information.")
    
    return success

if __name__ == "__main__":
    main()
