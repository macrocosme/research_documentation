"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from alert_web.models import User


FIELDS = ['title', 'first_name', 'last_name', 'email', 'gender', 'institution', 'is_student', 'country',
          'scientific_interests', 'username', ]

WIDGETS = {
            'title': forms.Select(
                attrs={'class': 'form-control', 'tabindex': '1'},
            ),
            'first_name': forms.TextInput(
                attrs={'class': "form-control", 'tabindex': '2'},
            ),
            'last_name': forms.TextInput(
                attrs={'class': "form-control", 'tabindex': '3'},
            ),
            'email': forms.TextInput(
                attrs={'class': "form-control", 'tabindex': '4'},
            ),
            'gender': forms.Select(
                attrs={'class': "form-control", 'tabindex': '5'},
            ),
            'institution': forms.TextInput(
                attrs={'class': "form-control", 'tabindex': '6'},
            ),
            'is_student': forms.CheckboxInput(
                attrs={'tabindex': '7'},
            ),
            'country': forms.Select(
                attrs={'class': "form-control", 'tabindex': '8'},
            ),
            'scientific_interests': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'tabindex': '9'},
            ),
            'username': forms.TextInput(
                attrs={'class': "form-control", 'tabindex': '10'},
            ),
        }

LABELS = {
    'title': _('Title'),
    'first_name': _('First name'),
    'last_name': _('Last name'),
    'email': _('Email'),
    'gender': _('Gender'),
    'institution': _('Institution'),
    'is_student': _('Is student?'),
    'country': _('Country'),
    'scientific_interests': _('Scientific interests'),
    'username': _('Username'),
}

class RegistrationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['country'].initial = 'AU'
        self.fields['username'].help_text = None
        self.fields['username'].widget.attrs.update({'autofocus': False})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'tabindex': '11'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'tabindex': '12'})
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['scientific_interests'].help_text = 'e.g. your area of expertise, how you hope to use the data, ' \
                                                        'team memberships and collaborations'

    class Meta:
        model = get_user_model()
        fields = FIELDS
        labels = LABELS
        widgets = WIDGETS

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'This email address is already taken by some other user.')
        return email

    def save(self, commit=True):
        # Save the user as an inactive user
        user = super(RegistrationForm, self).save(commit=False)
        user.is_active = False
        if commit:
            user.save()
        return user
