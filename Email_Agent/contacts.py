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
        self.linkedin_profile = data.get('Linkedin Profile')
        self.work_email = data.get('Work Email')

    def print_properties(self):
        for key, value in self.__dict__.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print('-' * 50)

    def is_valid_contact(self):
        """
        Check if this is a valid contact with required fields.
        """
        required_fields = ['full_name', 'company_domain']
        return all(getattr(self, field) for field in required_fields)

    def to_dict(self):
        """
        Convert contact to dictionary format for easy export.
        """
        return {
            'Match': self.match,
            'Full Name': self.full_name,
            'Job Title': self.job_title,
            'Location': self.location,
            'Company Domain': self.company_domain,
            'Linkedin Profile': self.linkedin_profile,
            'Work Email': self.work_email
        }
