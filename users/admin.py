from django.contrib import admin
from .models import User, OTP

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'isverified')
    list_filter = ('isverified',)
    actions = ['verify_users']

    def verify_users(self, request, queryset):
        queryset.update(isverified=True)
    verify_users.short_description = "Verify selected users"
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ( 'user','code', 'created_at', 'is_used')
    search_fields = ('user',)
    list_filter = ('created_at', 'is_used')
