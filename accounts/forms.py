from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    phone_number = forms.CharField(max_length=10, required=True)
    # removes help text from form
    # what to include in the form from the built-in user model
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2",)

    

class LoginForm(forms.Form):
    username = forms.CharField(max_length=200, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class BankForm(forms.Form):
    bank_name = forms.CharField(max_length=200, required=True)
    bank_accountID = forms.CharField(max_length=50, required =True)
    bank_customerId = forms.CharField(max_length=50, required =True)

class ChatBotInput(forms.Form):
    message = forms.CharField()