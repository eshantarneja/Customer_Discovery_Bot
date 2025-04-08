"""  
Module for sending emails with contact information as a CSV attachment.  
"""  
import os
import csv  
import smtplib  
import tempfile  
from datetime import datetime  
from email import encoders  
from email.mime.base import MIMEBase  
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from typing import List  
  
# Import Contact class and get_secret function
from Classes.contacts import Contact
from Helper.get_secrets import get_secret
  
def send_contacts_email(contacts: List[Contact], recipient_email: str, subject: str = None, body: str = None) -> bool:  
    """  
    Send an email with contacts information as a CSV attachment.  
      
    :param contacts: List of Contact objects to include in the CSV  
    :param recipient_email: Email address of the recipient  
    :param subject: Subject of the email (default: 'Contact Information CSV')  
    :param body: Body of the email (default: generic message)  
    :return: True if email was sent successfully, False otherwise  
    """  
    # Get email configuration using get_secret function
    smtp_server = get_secret('SMTP_SERVER') or 'smtp.gmail.com'
    smtp_port = int(get_secret('SMTP_PORT') or 587)
    sender_email = get_secret('EMAIL_USER')
    sender_password = get_secret('EMAIL_PASS')  # Using EMAIL_PASS as in your .env file
    
    # Validate email credentials  
    if not all([sender_email, sender_password]):  
        print("ERROR: Email credentials not found in environment variables.")  
        print("Please set EMAIL_USER and EMAIL_PASS in your .env file.")  
        return False  
    
    # Set default subject and body if not provided  
    if not subject:  
        subject = f"Contact Information CSV - {datetime.now().strftime('%Y-%m-%d')}"  
    
    if not body:  
        body = f"""Hello,  
        
Attached is the CSV file containing contact information as requested.  
        
The file contains {len(contacts)} contacts with their names, email addresses, companies, job titles, and draft emails.  
        
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
        
Regards,  
Customer Discovery Bot  
"""  
    
    # Create message container  
    msg = MIMEMultipart()  
    msg['From'] = sender_email  
    msg['To'] = recipient_email  
    msg['Subject'] = subject  
    
    # Add body to email  
    msg.attach(MIMEText(body, 'plain'))  
    
    try:  
        # Create a temporary CSV file  
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv', newline='', encoding='utf-8') as temp_file:  
            csv_filename = temp_file.name  
            
            # Define CSV fields to match the format in CSV_Export/file_manager.py  
            fieldnames = ['Name', 'Email Address', 'Company', 'Job Title', 'Email Body', 'Timestamp']  
            writer = csv.DictWriter(temp_file, fieldnames=fieldnames)  
            
            # Write header  
            writer.writeheader()  
            
            # Write contact data  
            for contact in contacts:  
                if hasattr(contact, 'draft_email') and contact.draft_email:  
                    writer.writerow({  
                        'Name': contact.full_name,  
                        'Email Address': contact.work_email,  
                        'Company': contact.company_name,  
                        'Job Title': contact.job_title,  
                        'Email Body': contact.draft_email,  
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                    })  
        
        # Attach the CSV file  
        attachment_filename = f"contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"  
        
        with open(csv_filename, 'rb') as attachment:  
            part = MIMEBase('application', 'octet-stream')  
            part.set_payload(attachment.read())  
            
            # Encode file in ASCII characters to send by email  
            encoders.encode_base64(part)  
            
            # Add header as key/value pair to attachment part  
            part.add_header(  
                'Content-Disposition',  
                f'attachment; filename= {attachment_filename}',  
            )  
            
            # Add attachment to message  
            msg.attach(part)  
        
        # Connect to server and send email
        print(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")  
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:  
                server.set_debuglevel(1)  # Enable verbose debug output
                print("Starting TLS...")  
                server.starttls()  # Secure the connection  
                print(f"Logging in as {sender_email}...")  
                
                try:
                    server.login(sender_email, sender_password)  
                except smtplib.SMTPAuthenticationError as auth_err:
                    error_msg = str(auth_err)
                    if "Application-specific password required" in error_msg:
                        print("ERROR: Gmail requires an application-specific password for this account")
                        print("Please generate one at: https://myaccount.google.com/apppasswords")
                        print("Then update EMAIL_PASS in your .env.yaml file with the new app password")
                        raise Exception("Gmail requires an application-specific password. See logs for details.")
                    else:
                        print(f"Authentication error: {error_msg}")
                        raise Exception(f"Email authentication failed: {error_msg}")
                        
                print("Sending email message...")  
                server.send_message(msg)  
            
            print(f"Email sent successfully to {recipient_email} with {len(contacts)} contacts attached.")  
        except smtplib.SMTPException as smtp_err:
            print(f"SMTP Error: {str(smtp_err)}")
            raise Exception(f"SMTP Error: {str(smtp_err)}")
        
        # Clean up the temporary file  
        os.unlink(csv_filename)  
        
        return True  
        
    except Exception as e:  
        print(f"Error sending email: {str(e)}")  
        return False


def create_contact_csv(contacts: List[Contact], output_file: str = None) -> str:
    """
    Create a CSV file with contact information without sending an email.
    
    :param contacts: List of Contact objects to include in the CSV
    :param output_file: Path to save the CSV file (default: creates a file in 'logs' directory)
    :return: Path to the created CSV file
    """
    # Create 'logs' directory if it doesn't exist and output_file is not specified
    if not output_file:
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        output_file = os.path.join(logs_dir, f'contacts_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Define CSV fields to match the format in CSV_Export/file_manager.py
            fieldnames = ['Name', 'Email Address', 'Company', 'Job Title', 'Email Body', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write contact data
            for contact in contacts:
                if hasattr(contact, 'draft_email') and contact.draft_email:
                    writer.writerow({
                        'Name': contact.full_name,
                        'Email Address': contact.work_email,
                        'Company': contact.company_name,
                        'Job Title': contact.job_title,
                        'Email Body': contact.draft_email,
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        print(f"CSV file created successfully: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error creating CSV file: {str(e)}")
        return ""

