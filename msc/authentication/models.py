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
        return self.email


    @property
    def is_admin(self):
        return self.groups.filter(name="Admin").exists()

    @property
    def is_national(self):
        return self.groups.filter(name="SuperAdmin").exists()
