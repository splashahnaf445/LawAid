from django.contrib import admin
from .models import User, ClientProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'role', 'status', 'is_active', 'created_at')
    list_filter = ('role', 'status')
    search_fields = ('full_name', 'email', 'phone')

    @admin.display(boolean=True, description='Active')
    def is_active(self, obj):
        return obj.is_active


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nid_number', 'address', 'created_at')