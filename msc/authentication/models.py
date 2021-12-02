from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from django.conf import settings

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from msc.questionnaire.base import MSCBase


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        max_length=255,
        unique=False,
        null=True, blank=True
    )
    organisation = models.ForeignKey(
        "organisation.Organisation", on_delete=models.CASCADE,
        null=True, blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

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
        return self.groups.filter(
            name="SuperAdmin"
        ).exists() or (self.organisation and self.organisation.parent == None)

    @property
    def is_provincial(self):
        if self.organisation and self.organisation.parent:
            parent = self.organisation.parent
            return parent.parent == None
        return False


share_objects = models.Q(app_label='questionnaire', model='questionnaire')
sharer_objects = models.Q(app_label='authentication', model='user') | models.Q(app_label='organisation', model='organisation')
class Share(MSCBase):
    target_content_type = models.ForeignKey(ContentType, limit_choices_to=share_objects, on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_content_type', 'target_object_id')
    sharer_content_type = models.ForeignKey(ContentType, limit_choices_to=sharer_objects, related_name="%(app_label)s_sharer_%(class)s_related", on_delete=models.CASCADE)
    sharer_object_id = models.PositiveIntegerField()
    sharer = GenericForeignKey('sharer_content_type', 'sharer_object_id')
    relationship = models.CharField(choices=settings.SHARER_RELATIONSHIP_TYPES, max_length=32)
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.pk is None:

            share = Share.objects.filter(
                target_content_type=self.target_content_type,
                target_object_id = self.target_object_id,
                sharer_content_type=self.sharer_content_type,
                sharer_object_id = self.sharer_object_id,
            ).first()
            if share is not None:
                return share
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return "%s -> %s -> %s" % (self.sharer, self.relationship, self.target)

    def clean(self):
        if hasattr(self, 'target_content_type') and not self.target:
            raise ValidationError(str(self.target_content_type) + ' with id '+ str(self.target_object_id) + " does not exist!")

        elif hasattr(self, 'sharer_content_type') and not self.sharer:
            raise ValidationError(str(self.sharer_content_type) + ' with id '+ str(self.sharer_object_id) + " does not exist!")
