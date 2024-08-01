from django import forms
from .models import User

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'user_type', 'linkedin_id')

class OTPForm(forms.Form):
    code = forms.CharField(max_length=6)
