from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    organisation = models.ForeignKey(
        "organisation.Organisation", on_delete=models.CASCADE,
        null=True, blank=True
    )

    def __str__(self):
        return self.display_name()

    def initials(self):
        if self.first_name and self.last_name:
            return (self.first_name[0] + self.last_name[0]).upper()
        else:
            return (self.email[0] + self.email[1]).upper()

    def display_name(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        else:
            return self.email

    @property
    def is_admin(self):
        return self.groups.filter(name="Admin").exists()

    @property
    def is_national(self):
        return self.groups.filter(name="SuperAdmin").exists()
