from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator

class User(AbstractUser):
    username = None  # Remove the username field
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)  # Set email as unique
    phone_number = models.CharField(max_length=10, unique=True, blank=True, null=True, validators=[RegexValidator(
        regex=r"^\d{10}$", message="Phone number must be 10 digits only."
    )])
    user_type = models.CharField(max_length=12, choices=[('Individual', 'Individual'), ('Organization', 'Organization')])
    linkedin_id = models.CharField(max_length=50, null=True, blank=True)
    designation=models.CharField(max_length=50,default="abc")
    isverified = models.BooleanField(default=False)
    company_name = models.CharField(max_length=50,default="abc")
    USERNAME_FIELD = 'email'  # Use email to log in
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'user_type']  # Required fields for creating a user

    def __str__(self):
        return self.email
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        verbose_name=('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text=('Specific permissions for this user.'),
        verbose_name=('user permissions'),
    )
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return self.created_at >= timezone.now() - timedelta(minutes=5) and not self.is_used
