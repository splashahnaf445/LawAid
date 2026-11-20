from django.contrib import admin
from .models import User, ClientProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'role', 'status', 'is_active', 'created_at')
    list_filter = ('role', 'status', 'is_active')
    search_fields = ('full_name', 'email', 'phone')

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nid_number', 'address', 'created_at')
