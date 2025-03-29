"""
Test options for validating email and CSV exports without sending actual emails.
This gives you multiple ways to test the functionality depending on your needs.
"""
import sys
from secrets import get_secret
from Classes.contacts import Contact
from Email_Sender.email import create_contact_csv
from CSV_Export import file_manager

def create_test_contacts():
    """Create sample test contacts for demonstration"""
    return [
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

def option_1_create_csv():
    """Test creating a CSV file without sending an email"""
    contacts = create_test_contacts()
    
    # Create CSV file
    csv_path = create_contact_csv(contacts)
    
    print(f"✅ CSV file created successfully at: {csv_path}")
    print(f"Sample contents will include {len(contacts)} contacts")
    
    return csv_path

def option_2_test_email_format():
    """Test email attachment creation without sending"""
    contacts = create_test_contacts()
    
    # Use the file_manager directly to create a CSV
    output_file = 'test_email_export.csv'
    result = file_manager.save_emails_to_csv(
        contacts, 
        output_file=output_file
    )
    
    if result:
        print(f"✅ Email CSV attachment created successfully at: {result}")
        print(f"This is the exact format that would be attached to an email")
    else:
        print("❌ Failed to create email CSV attachment")
    
    return result

def check_email_credentials():
    """Check and validate email credentials format"""
    email = get_secret('EMAIL_USER')
    password = get_secret('EMAIL_PASS')
    
    if not email:
        print("❌ EMAIL_USER is not set in your .env file")
        return False
    
    if not password:
        print("❌ EMAIL_PASS is not set in your .env file")
        return False
    
    print(f"Email: {email}")
    
    # Check password format
    password_length = len(password)
    print(f"Password length: {password_length}")
    
    if password_length != 16:
        print("\n⚠️ WARNING: Your app password is not 16 characters long.")
        print("Google App Passwords are typically exactly 16 characters without spaces.")
        print("Current format might not work with Gmail's authentication.")
        print("\nRecommendations:")
        print("1. Go to https://myaccount.google.com/apppasswords")
        print("2. Generate a new app password")
        print("3. Copy it exactly as shown (no spaces)")
        print("4. Update your .env file with the new password")
    else:
        print("✅ App password has the correct length (16 characters)")
    
    return True

def main():
    """Main function to run the test options"""
    print("\n===== Email Testing Options =====\n")
    print("1. Create a CSV file (no email sending)")
    print("2. Test email attachment format (no email sending)")
    print("3. Check email credentials")
    print("q. Quit")
    
    choice = input("\nEnter your choice (1-3, or q): ")
    
    if choice == '1':
        option_1_create_csv()
    elif choice == '2':
        option_2_test_email_format()
    elif choice == '3':
        check_email_credentials()
    elif choice.lower() == 'q':
        print("Exiting...")
        return
    else:
        print("Invalid choice. Please try again.")
    
    # Ask if user wants to continue
    if input("\nRun another test? (y/n): ").lower() == 'y':
        main()

if __name__ == "__main__":
    main()
