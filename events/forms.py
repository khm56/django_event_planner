from django import forms
from django.contrib.auth.models import User
from .models import Concert


class UserSignup(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email' ,'password']

        widgets={
        'password': forms.PasswordInput(),
        }


class UserLogin(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())


class ConcertForm(forms.ModelForm):
    class Meta:
        model = Concert
        exclude = ['organizer',]

        widgets = {
        	'start_date': forms.DateInput({'type': 'date'}),
        	'start_time': forms.TimeInput({'type': 'time'}),
        	'end_time': forms.TimeInput({'type': 'time'}),
        }


