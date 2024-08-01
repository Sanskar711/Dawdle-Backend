from django.contrib import admin
from .models import Client, Product, UseCase, Prospect, Meeting

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'client')
    search_fields = ('name', 'client__name')
    filter_horizontal = ('assigned_users',)  # Allow admin to assign users to products

admin.site.register(Client)
admin.site.register(Product, ProductAdmin)
admin.site.register(UseCase)
admin.site.register(Prospect)
admin.site.register(Meeting)
