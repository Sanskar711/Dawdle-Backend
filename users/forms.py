from django import forms
from .models import User

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'user_type', 'linkedin_id')

class OTPForm(forms.Form):
    code = forms.CharField(max_length=6)
# forms.py
from django import forms
from .models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'linkedin_id', 'designation', 'company_name', 'user_type']

