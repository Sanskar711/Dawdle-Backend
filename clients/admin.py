from django.contrib import admin
from .models import Client, Product, UseCase, Prospect, Meeting, QualifyingQuestion,Resource,IdealCustomerProfile,QualifyingQuestionResponse
from .models import EmailRequest

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'client')
    search_fields = ('name', 'client__name')
    filter_horizontal = ('assigned_users',)  # Allow admin to assign users to products

admin.site.register(Client)
admin.site.register(Product, ProductAdmin)
admin.site.register(UseCase)
admin.site.register(Prospect)
admin.site.register(Meeting)
admin.site.register(QualifyingQuestionResponse)
admin.site.register(Resource)
admin.site.register(QualifyingQuestion)
admin.site.register(IdealCustomerProfile)

@admin.register(EmailRequest)
class EmailRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'prospect', 'poc_email', 'status', 'created_at']
    search_fields = ['poc_email', 'email_subject']
    list_filter = ['status', 'created_at']
