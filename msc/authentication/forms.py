from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.contrib.admin import widgets

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    is_admin = forms.BooleanField(required=False, initial=False, label='Add User as organisation Admin')
    send_email = forms.BooleanField(required=False, initial=False, label='Send activation email to user')
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('email', 'organisation', 'password1', 'password2', 'is_admin', 'send_email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.current_user.is_superuser:
            del self.fields['send_email']


    def clean(self):
        if self.cleaned_data['is_admin'] == True and self.cleaned_data['organisation'] is None:
            raise ValidationError('Please select organisation to set user as admin of the organisation')
        return self.cleaned_data


class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    is_admin = forms.BooleanField(required=False, label='Is user an organisation Admin')

    class Meta:
        model = User
        fields = ('email', 'organisation', 'is_active', 'is_admin', 'first_name', 'last_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            is_admin = self.instance.is_admin
            if self.instance.organisation and not self.instance.organisation.parent:
                is_admin = self.instance.is_national
            self.fields['is_admin'].initial = is_admin

    def clean(self):
        if self.cleaned_data['is_admin'] == True and self.cleaned_data['organisation'] is None:
            raise ValidationError('Please select organisation to set user as admin of the organisation')
        return self.cleaned_data