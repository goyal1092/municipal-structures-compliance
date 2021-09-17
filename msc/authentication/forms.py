from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    is_admin = forms.BooleanField(required=False, initial=False, label='Add User as organisation Admin')
    
    class Meta:
        model = User
        fields = ('email', 'organisation', 'password1', 'password2', 'is_admin',)


class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    is_admin = forms.BooleanField(required=False, label='Is user an organisation Admin')

    class Meta:
        model = User
        fields = ('email', 'password', 'organisation', 'is_active', 'is_admin', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            is_admin = self.instance.is_admin
            if not self.instance.organisation.parent:
                is_admin = self.instance.is_national
            self.fields['is_admin'].initial = is_admin