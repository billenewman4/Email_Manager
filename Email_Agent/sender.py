class Sender:
    def __init__(self, resume, career_interest, key_accomplishments):
        self.resume = resume
        self.career_interest = career_interest
        self.key_accomplishments = key_accomplishments

    def print_details(self):
        print("Sender Details:")
        print(f"Resume: {self.resume}")
        print(f"Career Interest: {self.career_interest}")
        print("Key Accomplishments:")
        for accomplishment in self.key_accomplishments:
            print(f"- {accomplishment}")

    def get_summary(self):
        return {
            "resume": self.resume,
            "career_interest": self.career_interest,
            "key_accomplishments": self.key_accomplishments
        }
