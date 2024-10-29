from datetime import datetime, date
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

class Contact:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.created_time = data.get('createdTime')
        self.last_edited_time = data.get('lastEditedTime')
        self.url = data.get('url')
        self.email = data.get('email')
        self.linkedin_url = data.get('linkedInURL')
        self.date_last_contacted = data.get('dateLastContacted')
        self.status = data.get('status')
        self.next_steps = data.get('nextSteps')
        self.role = data.get('role')
        self.contact_type = data.get('contactType')
        self.meeting_notes = data.get('meetingNotes')
        self.company = data.get('company')
        self.company_info = data.get('companyInfo')

    def print_properties(self):
        for key, value in self.__dict__.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print('-' * 50)

    def is_reach_out_needed(self, status_days_array):
        days_to_next_contact = status_days_array.get(self.status)
        if days_to_next_contact is None:
            print(f"Status '{self.status}' not found in status_days_array, skipping {self.name}")
            return False

        if days_to_next_contact == -1:
            return False

        if not self.date_last_contacted:
            print(f"No last contacted date for {self.name}, considering for follow-up.")
            return True

        try:
            last_contacted_date = parse(self.date_last_contacted).date()
        except ValueError:
            print(f"Error parsing date for {self.name}")
            return False

        days_since_contact = (datetime.now().date() - last_contacted_date).days

        if days_since_contact >= days_to_next_contact:
            return True
        else:
            print(f"{self.name} was contacted {days_since_contact} days ago. No follow-up needed yet.")
            return False
