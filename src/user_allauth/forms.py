from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import password_validation
from django import forms
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm
import re
from django.utils.translation import gettext_lazy as _

from .models import User


class LoginForm(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)



def validate_phone_number(value):
    # Check if the input is a valid phone number format
    if not re.match(r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$', value):
        raise forms.ValidationError('Please enter a valid phone number (e.g. +12 1234567890).')

class RegistrationForm(forms.ModelForm):
	
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True  # Explicitly making sure the field is required
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    phone = forms.CharField(label='Phone Number', validators=[validate_phone_number], required=True)

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "autofocus": True}
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        try:
            password_validation.validate_password(password2)
        except ValidationError as error:
            self.add_error("password2", error)
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user

    class Meta:
        model = User
        fields = [
			'first_name', 'last_name','email', 'phone', 'password1', 'password2',
			]
        


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    phone = forms.CharField(max_length=64, required=False)
    

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.save()
        return user
    
    
class UsernameForm(forms.Form):
    username = forms.CharField()
    
class OTPForm(forms.Form):
    otp_code = forms.CharField()