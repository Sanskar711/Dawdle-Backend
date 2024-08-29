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

class UseCaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'get_linked_products')

    def get_linked_products(self, obj):
        return ", ".join([product.name for product in obj.products.all()])
    
    get_linked_products.short_description = 'Linked Products'

# Custom ResourceAdmin to display linked clients and products
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_linked_clients', 'get_linked_products')

    def get_linked_clients(self, obj):
        # Get unique clients linked to the resource via products
        clients = set(product.client.name for product in obj.products.all())
        return ", ".join(clients)
    
    def get_linked_products(self, obj):
        # Get products linked to the resource
        return ", ".join([product.name for product in obj.products.all()])
    
    get_linked_clients.short_description = 'Linked Clients'
    get_linked_products.short_description = 'Linked Products'

admin.site.register(Client)
admin.site.register(Product, ProductAdmin)
admin.site.register(UseCase, UseCaseAdmin)
admin.site.register(Prospect, ProspectAdmin)
admin.site.register(Meeting)
admin.site.register(QualifyingQuestionResponse)
admin.site.register(Resource, ResourceAdmin)  # Register ResourceAdmin with custom columns
admin.site.register(QualifyingQuestion)
admin.site.register(IdealCustomerProfile)

@admin.register(EmailRequest)
class EmailRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'prospect', 'poc_email', 'status', 'created_at']
    search_fields = ['poc_email', 'email_subject']
    list_filter = ['status', 'created_at']
