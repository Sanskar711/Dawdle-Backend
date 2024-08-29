from django.db import models
from users.models import User
from PIL import Image

class Client(models.Model):
    name = models.CharField(max_length=255)
    company_description = models.TextField(help_text="A brief description of the company.", null=True)
    company_website = models.URLField(help_text="The official website of the company.", null=True)
    calendly_link = models.URLField(help_text="Link to the company's Calendly schedule.", null=True)
    company_logo = models.ImageField(upload_to='company_logos/', help_text="Upload the company logo.", null=True, blank=True)
    email = models.EmailField(unique=True)  # Set email as unique

    def __str__(self):
        return self.name

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator
class OTP(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return self.created_at >= timezone.now() - timedelta(minutes=5) and not self.is_used


# class Product(models.Model):
#     name = models.CharField(max_length=255)
#     client = models.ForeignKey(Client, related_name='products', on_delete=models.CASCADE)
#     use_cases = models.ManyToManyField('UseCase', related_name='products')
#     assigned_users = models.ManyToManyField(User, related_name='assigned_clients')
#     product_prospects=models.ManyToManyField('Prospect', related_name='product')
#     def __str__(self):
#         return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=255)
    client = models.ForeignKey(Client, related_name='products', on_delete=models.CASCADE)
    
    # New Fields
    description = models.TextField(help_text="Brief product description", null=True)
    key_features = models.TextField(help_text="Key product features in bullet points", null=True)
    key_problems_solved = models.TextField(help_text="Key problems solved by the product in bullet points", null=True)
    video_link = models.URLField(help_text="Link to the product video", null=True, blank=True)  # New video link field

    # Relationships
    use_cases = models.ManyToManyField('UseCase', related_name='products', blank=True)
    assigned_users = models.ManyToManyField(User, related_name='assigned_clients', blank=True)
    product_prospects = models.ManyToManyField('Prospect', related_name='product', blank=True)
    qualifying_questions = models.ManyToManyField('QualifyingQuestion', related_name='products', blank=True)
    resources = models.ManyToManyField('Resource', related_name='products')
    ideal_customer_profiles = models.ManyToManyField('IdealCustomerProfile', related_name='products', blank=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    name = models.CharField(max_length=255)
    link = models.URLField(help_text="Link to resources like websites, documents, etc.")

    def __str__(self):
        return self.name

class QualifyingQuestion(models.Model):
    question = models.TextField()

    def __str__(self):
        return self.question

class IdealCustomerProfile(models.Model):
    INDUSTRY_CHOICES = [
        ('Tech', 'Technology'),
        ('Health', 'Healthcare'),
        # Add more choices as needed
    ]
    GEOGRAPHY_CHOICES = [
        ('NA', 'North America'),
        ('EU', 'Europe'),
        # Add more choices as needed
    ]
    COMPANY_SIZE_CHOICES = [
        ('Small', '1-50 employees'),
        ('Medium', '51-200 employees'),
        ('Large', '201+ employees'),
        # Add more choices as needed
    ]
    DEPARTMENT_CHOICES = [
        ('HR', 'Human Resources'),
        ('IT', 'Information Technology'),
        # Add more choices as needed
    ]

    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, help_text="Select the industry")
    geography = models.CharField(max_length=50, choices=GEOGRAPHY_CHOICES, help_text="Select the geographical region")
    company_size = models.CharField(max_length=50, choices=COMPANY_SIZE_CHOICES, help_text="Select the size of the company")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, help_text="Select the department")
    designations = models.TextField(help_text="Comma-separated designations")
    additional_details = models.TextField(blank=True, null=True, help_text="Additional details about the ideal customer profile")

    def __str__(self):
        return f"{self.industry}, {self.geography}, {self.company_size}, {self.department}"

class UseCase(models.Model):
    title = models.CharField(max_length=255, default=1)
    description = models.TextField(help_text="Brief description of the use case",null=True)
    solution = models.TextField(help_text="How the product is solving the problem",null=True)
    target_audience = models.TextField(help_text="Who might be facing the problem?",null=True)
    sample_pitch = models.TextField(help_text="Sample pitch to present the use case",null=True)
    reference_links = models.TextField(help_text="Reference links related to the use case",null=True)

    def __str__(self):
        return self.title




class Prospect(models.Model):
    
    company_name = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=True)
    is_visible= models.BooleanField(default=True)
    geography = models.CharField(max_length=255, help_text="Geographic location of the prospect",default="Undefined")
    STATUS_CHOICES = [
        ('scheduled', 'Meeting Scheduled'),
        ('completed', 'Meeting Completed'),
        ('closed', 'Deal Closed'),
        ('open', 'Open For Meeting'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open', help_text="Current status of the prospect")

    def __str__(self):
        return f"{self.company_name}"
    


from django.db import models

class QualifyingQuestionResponse(models.Model):
    qualifying_question = models.ForeignKey('QualifyingQuestion', on_delete=models.CASCADE)
    response = models.TextField()

    def __str__(self):
        return f"Response to {self.qualifying_question}"

class Meeting(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
        ('pending', 'Pending For Approval'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    prospect = models.ForeignKey('Prospect', on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    
    # New Fields
    qualifying_question_responses = models.ManyToManyField(
        QualifyingQuestionResponse,
        through='MeetingQualifyingQuestionResponse',
        related_name='meetings'
    )
    use_cases = models.ManyToManyField('UseCase', related_name='meetings')
    poc_first_name = models.CharField(max_length=255,null=True)
    poc_last_name = models.CharField(max_length=255,null=True)
    poc_email = models.EmailField(null=True)
    poc_phone_number = models.CharField(max_length=20,null=True)
    poc_designation = models.CharField(max_length=255,null=True)
    other_relevant_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self):
        return f"Meeting with {self.prospect.company_name} scheduled at {self.scheduled_at}"
    
class EmailRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prospect = models.ForeignKey('Prospect', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    poc_first_name = models.CharField(max_length=255)
    poc_last_name = models.CharField(max_length=255)
    poc_email = models.EmailField()
    poc_designation = models.CharField(max_length=255)
    email_subject = models.CharField(max_length=255)
    email_body = models.TextField()
    status = models.CharField(max_length=50, default='pending', choices=[
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email to {self.poc_email} by {self.user.email}"
    
    
    
class MeetingQualifyingQuestionResponse(models.Model):
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE)
    qualifying_question_response = models.ForeignKey('QualifyingQuestionResponse', on_delete=models.CASCADE)


    
