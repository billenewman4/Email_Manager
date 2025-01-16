
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
        self.draft_email = data.get('draft_email', '')

    def print_properties(self):
        for key, value in self.__dict__.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print('-' * 50)

    def is_valid_contact(self) -> bool:
        # Check that we have full name and company domain
        # AND that we don't already have a work email
        return (
            bool(self.full_name) and 
            bool(self.company_domain) and 
            bool(self.work_email) and not self.draft_email
        )
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
