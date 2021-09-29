from django.db import models

class MSCBase(models.Model):
    created = models.DateTimeField(auto_now_add=True,
                                   help_text="Date and time this object was created.")
    modified = models.DateTimeField(auto_now=True,
                                    help_text="Date and time this object was last modified.")

    class Meta:
        abstract = True