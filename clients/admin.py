from django.contrib import admin
from .models import Client, Product, UseCase, Prospect, Meeting, QualifyingQuestion, Resource, IdealCustomerProfile, QualifyingQuestionResponse, EmailRequest

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'client')
    search_fields = ('name', 'client__name')
    filter_horizontal = ('assigned_users',)

import pandas as pd
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.http import HttpResponse
from django.contrib import messages

class ProspectAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'get_clients', 'get_products', 'is_approved', 'geography', 'status')
    list_filter = ('is_approved', 'status', 'geography')
    search_fields = ('company_name', 'geography')

    # Adding custom admin action for bulk upload
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.upload_excel, name='upload_excel'),
        ]
        return custom_urls + urls

    def upload_excel(self, request):
        if request.method == "POST":
            try:
                excel_file = request.FILES["excel_file"]
                df = pd.read_excel(excel_file)
                for _, row in df.iterrows():
                    client = Client.objects.get(name=row['Client Name'])
                    products = Product.objects.filter(name__in=row['Product Names'].split(','), client=client)
                    prospect = Prospect.objects.create(
                        company_name=row['Company Name'],
                        geography=row['Geography'],
                        status=row['Status'],
                        is_approved=row['Is Approved'],
                        is_visible=row['Is Visible'],
                    )
                    prospect.product_set.add(*products)
                self.message_user(request, "Prospects uploaded successfully.", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Error during upload: {str(e)}", messages.ERROR)
            return redirect("..")
        return HttpResponse('''<form method="post" enctype="multipart/form-data">
                               <input type="file" name="excel_file">
                               <button type="submit">Upload</button>
                               </form>''')
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['upload_excel_url'] = 'upload-excel/'
        return super().changelist_view(request, extra_context=extra_context)
    # Methods to display linked clients and products in the admin list view
    def get_clients(self, obj):
        clients = set(product.client.name for product in obj.product.all())  # Corrected line
        return ", ".join(clients)
    get_clients.short_description = 'Clients'

    def get_products(self, obj):
        return ", ".join([product.name for product in obj.product.all()])  # Corrected line
    get_products.short_description = 'Products'

    # def has_add_permission(self, request):
    #     return False
    
admin.site.register(Prospect, ProspectAdmin)


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
from django import forms
# Custom Form for Product Admin
# class ProductForm(forms.ModelForm):
#     new_prospect = forms.CharField(max_length=255, required=False, help_text="Add a new prospect for this product.")
#     new_qualifying_question = forms.CharField(max_length=255, required=False, help_text="Add a new qualifying question for this product.")
#     new_icp = forms.CharField(max_length=255, required=False, help_text="Add a new ICP for this product.")
#     new_resource = forms.CharField(max_length=255, required=False, help_text="Add a new resource for this product.")

#     class Meta:
#         model = Product
#         fields = '__all__'

#     def save(self, commit=True):
#         instance = super().save(commit=False)

#         # Add new Prospect
#         new_prospect_name = self.cleaned_data.get('new_prospect')
#         if new_prospect_name:
#             prospect = Prospect.objects.create(company_name=new_prospect_name)
#             instance.product_prospects.add(prospect)

#         # Add new Qualifying Question
#         new_qualifying_question_text = self.cleaned_data.get('new_qualifying_question')
#         if new_qualifying_question_text:
#             question = QualifyingQuestion.objects.create(question=new_qualifying_question_text)
#             instance.qualifying_questions.add(question)

#         # Add new ICP
#         new_icp_name = self.cleaned_data.get('new_icp')
#         if new_icp_name:
#             icp = IdealCustomerProfile.objects.create(name=new_icp_name)
#             instance.ideal_customer_profiles.add(icp)

#         # Add new Resource
#         new_resource_name = self.cleaned_data.get('new_resource')
#         if new_resource_name:
#             resource = Resource.objects.create(name=new_resource_name)
#             instance.resources.add(resource)

#         if commit:
#             instance.save()
#             self.save_m2m()
#         return instance
# Create an inline admin descriptor for Prospect model

# class ProductProspectInlineForm(forms.ModelForm):
#     class Meta:
#         model = Product.product_prospects.through
#         fields = '__all__'
#         widgets = {
#             'name': forms.TextInput(attrs={'placeholder': 'Enter prospect name'}),
#         }

# class ProspectInline(admin.StackedInline):
#     model = Product.product_prospects.through  # Use the through model for the many-to-many relationship
#     extra = 1  # Number of empty forms to display
#     can_delete = True
#     verbose_name_plural = 'Prospects'
#     form = ProductProspectInlineForm

#     # def formfield_for_foreignkey(self, db_field, request, **kwargs):
#     #     if db_field.name == "product_prospects":
#     #         product_id = request.resolver_match.kwargs.get('object_id')
#     #         if product_id:
#     #         # This should include all relevant prospects
#     #             kwargs["queryset"] = Prospect.objects.filter(product__id=product_id) | Prospect.objects.filter(product__isnull=True)
#     #         else:
#     #         # In case of new product or no product selected
#     #             kwargs["queryset"] = Prospect.objects.none()
#     #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

#     def save_new(self, form, commit=True):
#         instance = form.save(commit=False)
#         product = Product.objects.get(pk=self.get_object_id(form))
#         if commit:
#             instance.save()
#             product.product_prospects.add(instance)
#         return instance

#     def get_object_id(self, form):
#         return form.instance.pk if form.instance.pk else self.parent_model.objects.latest('pk').pk


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'client')
    search_fields = ('name', 'client__name')
    filter_horizontal = ('assigned_users', 'qualifying_questions', 'ideal_customer_profiles', 'resources','product_rospect','use_cases')
    
    # inlines = [ProspectInline]
    # exclude = ('product_prospects',)
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        product_id = request.resolver_match.kwargs.get('object_id')
        if db_field.name == "qualifying_questions":
            kwargs["queryset"] = QualifyingQuestion.objects.filter(products__id=product_id) if product_id else QualifyingQuestion.objects.all()
        elif db_field.name == "ideal_customer_profiles":
            kwargs["queryset"] = IdealCustomerProfile.objects.filter(products__id=product_id) if product_id else IdealCustomerProfile.objects.all()
        elif db_field.name == "resources":
            kwargs["queryset"] = Resource.objects.filter(products__id=product_id) if product_id else Resource.objects.all()
        elif db_field.name == "product_prospects":
            kwargs["queryset"] = Prospect.objects.filter(product__id=product_id) if product_id else Prospect.objects.all()
        elif db_field.name == "use_cases":
            kwargs["queryset"] = UseCase.objects.filter(products__id=product_id) if product_id else UseCase.objects.all()
        
        return super().formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(Product, ProductAdmin)



admin.site.register(UseCase, UseCaseAdmin)
admin.site.register(QualifyingQuestionResponse, QualifyingQuestionResponseAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(QualifyingQuestion, QualifyingQuestionAdmin)
class IdealCustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('industry', 'geography', 'company_size', 'department', 'get_linked_products', 'get_linked_clients')

    def get_linked_products(self, obj):
        # This assumes a ManyToManyField relationship with Product
        products = obj.products.all()
        return ", ".join([product.name for product in products])
    get_linked_products.short_description = 'Linked Products'

    def get_linked_clients(self, obj):
        # This assumes a relationship through the Product model to the Client
        clients = set(product.client.name for product in obj.products.all())
        return ", ".join(clients)
    get_linked_clients.short_description = 'Linked Clients'

admin.site.register(IdealCustomerProfile, IdealCustomerProfileAdmin)

@admin.register(EmailRequest)
class EmailRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'prospect', 'poc_email', 'status', 'created_at']
    search_fields = ['poc_email', 'email_subject']
    list_filter = ['status', 'created_at']

from django.db.models import Prefetch

class MeetingAdminForm(forms.ModelForm):
    class Meta:
        model = Meeting
        exclude = ('qualifying_question_responses', 'use_cases')
from django.utils.html import format_html, format_html_join

class MeetingAdmin(admin.ModelAdmin):
    form = MeetingAdminForm
    
    list_display = ('prospect', 'get_client_name', 'get_prospect_geography', 'scheduled_at', 'status')
    readonly_fields = (
        'get_client_name',
        'get_prospect_geography',
        'get_meeting_qualifying_question_responses',
        'get_meeting_use_cases',
    )

    def get_client_name(self, obj):
        return obj.product.client.name if obj.product else None
    get_client_name.short_description = 'Client Name'

    def get_prospect_geography(self, obj):
        return obj.prospect.geography if obj.prospect else None
    get_prospect_geography.short_description = 'Prospect Geography'
    
    def get_meeting_qualifying_question_responses(self, obj):
        # Display each qualifying question with its corresponding response
        responses_html = format_html_join(
            '', 
            '<div style="margin-bottom: 10px;"><strong>{}</strong>: {}</div>',
            [(response.qualifying_question.question, response.response) for response in obj.qualifying_question_responses.all()]
        )
        return format_html('<div class="qualifying-questions" style="max-height: 200px; overflow-y: auto;">{}</div>', responses_html)
    get_meeting_qualifying_question_responses.short_description = 'Qualifying Question Responses'

    def get_meeting_use_cases(self, obj):
        # Display the linked use cases in a read-only format
        use_cases = ", ".join([use_case.title for use_case in obj.use_cases.all()])
        return format_html('<div class="use-cases" style="max-height: 200px; overflow-y: auto;">{}</div>', use_cases)
    get_meeting_use_cases.short_description = 'Linked Use Cases'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product__client', 'prospect').prefetch_related(
            'use_cases',
            Prefetch('qualifying_question_responses')
        )

    def has_add_permission(self, request, obj=None):
        # Prevent the addition of new items in the admin interface
        return False  

    def has_change_permission(self, request, obj=None):
        # Allow changing but not adding or removing Use Cases
        return super().has_change_permission(request, obj)

admin.site.register(Meeting, MeetingAdmin)


