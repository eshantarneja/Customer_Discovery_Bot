import os
import re

def fix_api_flask():
    # Path to the file
    file_path = 'Email_Agent/api_flask.py'
    
    # Read the file
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Define the replacement for contact creation in POST requests
    old_pattern = r"contacts = \[Contact\(c\) for c in data\['contacts'\]\]"
    new_code = """# Map the incoming fields to what Contact class expects
                    contact_list = []
                    for c in data['contacts']:
                        # Create properly formatted contact dictionary
                        contact_dict = {
                            'Full Name': c.get('name', ''),
                            'Work Email': c.get('email', ''),
                            'Company Name': c.get('company', ''),
                            'Job Title': c.get('position', ''),
                            'LinkedIn': c.get('linkedin', ''),
                            'Company Domain': c.get('company_domain', '')
                        }
                        contact_list.append(Contact(contact_dict))
                    
                    contacts = contact_list"""
    
    # Replace all occurrences
    modified_content = re.sub(old_pattern, new_code, content)
    
    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(modified_content)
    
    print("Modified api_flask.py to fix contact mapping")

if __name__ == "__main__":
    fix_api_flask()
