from django.contrib import admin
from .models import Client, Product, UseCase, Prospect, Meeting, QualifyingQuestion, Resource, IdealCustomerProfile, QualifyingQuestionResponse, EmailRequest

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'client')
    search_fields = ('name', 'client__name')
    filter_horizontal = ('assigned_users',)

class ProspectAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'is_approved', 'geography', 'status')
    list_filter = ('is_approved', 'status', 'geography')
    search_fields = ('company_name', 'geography')

# Custom UseCaseAdmin to display linked products
class UseCaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'get_linked_products')

    def get_linked_products(self, obj):
        # Join product names into a comma-separated string
        return ", ".join([product.name for product in obj.products.all()])
    
    get_linked_products.short_description = 'Linked Products'

admin.site.register(Client)
admin.site.register(Product, ProductAdmin)
admin.site.register(UseCase, UseCaseAdmin)
admin.site.register(Prospect, ProspectAdmin)
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
