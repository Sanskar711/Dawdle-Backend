from django.db import models
from users.models import User


class Client(models.Model):
    name = models.CharField(max_length=255)
    company_profile = models.TextField()
    calendly_link = models.URLField()
    

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    client = models.ForeignKey(Client, related_name='products', on_delete=models.CASCADE)
    use_cases = models.ManyToManyField('UseCase', related_name='products')
    assigned_users = models.ManyToManyField(User, related_name='assigned_clients')
    def __str__(self):
        return self.name

class UseCase(models.Model):
    description = models.TextField()

    def __str__(self):
        return self.description

class Prospect(models.Model):
    product = models.ForeignKey(Product, related_name='prospects', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    use_cases = models.TextField()
    poc_first_name = models.CharField(max_length=255)
    poc_last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    designation = models.CharField(max_length=255)
    linkedin_id = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company_name} - {self.poc_first_name} {self.poc_last_name}"
    


class Meeting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    completed = models.BooleanField(default=False)
    is_successful = models.BooleanField(default=False)

    def __str__(self):
        return f"Meeting with {self.prospect.company_name} scheduled at {self.scheduled_at}"
