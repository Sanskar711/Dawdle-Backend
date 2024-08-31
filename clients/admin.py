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

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_linked_clients', 'get_linked_products')

    def get_linked_clients(self, obj):
        clients = set(product.client.name for product in obj.products.all())
        return ", ".join(clients)
    
    def get_linked_products(self, obj):
        return ", ".join([product.name for product in obj.products.all()])
    
    get_linked_clients.short_description = 'Linked Clients'
    get_linked_products.short_description = 'Linked Products'

# Custom QualifyingQuestionResponseAdmin to show linked meeting, product, and client
class QualifyingQuestionResponseAdmin(admin.ModelAdmin):
    list_display = ('response', 'get_linked_meeting', 'get_linked_product', 'get_linked_client')

    def get_linked_meeting(self, obj):
        return ", ".join([meeting.prospect.company_name for meeting in obj.meetings.all()])
    
    def get_linked_product(self, obj):
        products = set(meeting.product.name for meeting in obj.meetings.all())
        return ", ".join(products)
    
    def get_linked_client(self, obj):
        clients = set(meeting.product.client.name for meeting in obj.meetings.all())
        return ", ".join(clients)

    get_linked_meeting.short_description = 'Linked Meeting'
    get_linked_product.short_description = 'Linked Product'
    get_linked_client.short_description = 'Linked Client'

# Custom QualifyingQuestionAdmin to show linked product and client
class QualifyingQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'get_linked_products', 'get_linked_clients')

    def get_linked_products(self, obj):
        products = obj.products.all()
        return ", ".join([product.name for product in products])
    
    def get_linked_clients(self, obj):
        clients = set(product.client.name for product in obj.products.all())
        return ", ".join(clients)
    search_fields = ('qualifying_question__question', 'response')
    get_linked_products.short_description = 'Linked Products'
    get_linked_clients.short_description = 'Linked Clients'

admin.site.register(Client)
admin.site.register(Product, ProductAdmin)
admin.site.register(UseCase, UseCaseAdmin)
admin.site.register(Prospect, ProspectAdmin)
admin.site.register(QualifyingQuestionResponse, QualifyingQuestionResponseAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(QualifyingQuestion, QualifyingQuestionAdmin)
admin.site.register(IdealCustomerProfile)

@admin.register(EmailRequest)
class EmailRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'prospect', 'poc_email', 'status', 'created_at']
    search_fields = ['poc_email', 'email_subject']
    list_filter = ['status', 'created_at']

from django.db.models import Prefetch

class MeetingAdmin(admin.ModelAdmin):
    list_display = ('prospect', 'get_client_name', 'get_prospect_geography', 'scheduled_at', 'status')
    readonly_fields = ('get_client_name', 'get_prospect_geography', 'get_meeting_qualifying_question_responses', 'get_meeting_use_cases')
    
    def get_client_name(self, obj):
        return obj.product.client.name if obj.product else None
    get_client_name.short_description = 'Client Name'

    def get_prospect_geography(self, obj):
        return obj.prospect.geography if obj.prospect else None
    get_prospect_geography.short_description = 'Prospect Geography'
    
    def get_meeting_qualifying_question_responses(self, obj):
        return ", ".join([response.response for response in obj.qualifying_question_responses.all()])
    get_meeting_qualifying_question_responses.short_description = 'Qualifying Question Responses'
    
    def get_meeting_use_cases(self, obj):
        return ", ".join([use_case.title for use_case in obj.use_cases.all()])
    get_meeting_use_cases.short_description = 'Linked Use Cases'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product__client', 'prospect').prefetch_related(
            'use_cases',
            Prefetch('qualifying_question_responses')
        )

    def has_add_permission(self, request, obj=None):
        return False  # Disable adding new use cases directly from the meeting admin

admin.site.register(Meeting, MeetingAdmin)

