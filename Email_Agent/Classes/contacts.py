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
        
        
        # Check required fields and draft email status
        has_required = all(getattr(self, field) for field in required_fields)
        has_draft = bool(self.draft_email and str(self.draft_email).strip())
        
        return has_required and not has_draft

    def to_dict(self):
        """
        Convert contact to dictionary format for easy export.
        """
        return vars(self)

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
