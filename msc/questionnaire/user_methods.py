from django.contrib.auth.models import User

def initials(self):
    if self.first_name and self.last_name:
        return (self.first_name[0] + self.last_name[0]).upper()
    else:
        return (self.username[0] + self.username[1]).upper()

def display_name(self):
    if self.first_name and self.last_name:
        return self.first_name + ' ' + self.last_name
    else:
        return self.username

User.add_to_class('initials', initials)
User.add_to_class('display_name', display_name)