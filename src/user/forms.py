from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from .models import User

class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
        "first_name",
        "last_name",
        "phone",
        "email",
        "address",
        "email_confirmed",
        "is_active",
        "is_superuser",
        "is_staff",
    ]
        
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("ایمیل وارد شده از قبل وجود دارد.")
        return email
    


class LoginForm(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)

class UsernameForm(forms.Form):
    username = forms.CharField()

class OTPForm(forms.Form):
    otp_code = forms.CharField()

class ChangeEmailForm(forms.Form):
      new_email = forms.EmailField()
      

class ChangePhoneRequestForm(forms.Form):
      new_phone = forms.CharField(validators=[RegexValidator(regex='^[1-9]{1}[0-9]{9}$', message='این مقدار باید  یک شماره همراه و بدون صفر وارد شود.')])
      
class ChangePhoneForm(forms.Form):
    token = forms.CharField(max_length=4)