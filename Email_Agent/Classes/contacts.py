from datetime import datetime, date
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

class Contact:
    def __init__(self, data):
        self.match = data.get('Match')
        self.full_name = data.get('Full Name')
        self.job_title = data.get('Job Title')
        self.location = data.get('Location')
        self.company_domain = data.get('Company Domain')
        self.company_name = data.get('Company Name')
        self.LinkedIn = data.get('LinkedIn')
        self.work_email = data.get('Work Email')
        self.draft_email = data.get('draft_email')

    def print_properties(self):
        for key, value in self.__dict__.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print('-' * 50)

    def is_valid_contact(self) -> bool:
        """
        Check if this is a valid contact with required fields and no draft email.
        """
        required_fields = ['full_name', 'company_domain', 'work_email']
        
        # Check required fields - must exist AND be non-empty
        has_required = True
        for field in required_fields:
            value = getattr(self, field, None)
            if not value or not str(value).strip():
                has_required = False
                break
        
        # Check draft email status - must NOT have a draft email
        has_draft = bool(self.draft_email and str(self.draft_email).strip())
        
        return has_required and not has_draft
        
    def is_valid(self) -> bool:
        """
        Validate that this contact has all required fields AND has no draft email.
        A valid contact MUST have:
        1. full_name
        2. company_domain
        3. work_email
        4. NO draft_email
        """
        return self.is_valid_contact()
        
    def to_dict(self):
        """
        Convert this Contact object to a dictionary for JSON serialization.
        This is necessary for Flask's jsonify to work properly with Contact objects.
        Also used for easy export.
        """
        return {
            'match': self.match,
            'full_name': self.full_name,
            'job_title': self.job_title,
            'location': self.location,
            'company_domain': self.company_domain,
            'company_name': self.company_name,
            'LinkedIn': self.LinkedIn,
            'work_email': self.work_email,
            'draft_email': self.draft_email
        }

    def to_list(self):
        """
        Convert contact to list format for sheet updates.
        Ensures attributes are in the same order as sheet headers.
        """
        return [
            self.match,
            self.full_name,
            self.job_title,
            self.location,
            self.company_domain,
            self.company_name,
            self.LinkedIn,
            self.work_email,
            self.draft_email
        ]
