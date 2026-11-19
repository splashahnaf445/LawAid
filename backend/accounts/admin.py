from django.contrib import admin
from django.utils.html import format_html
from .models import User, LawyerProfile, LawyerVerificationDocument, ClientProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'role', 'status', 'is_active', 'created_at')
    list_filter = ('role', 'status', 'is_active', 'preferred_language')
    search_fields = ('full_name', 'email', 'phone')
    ordering = ('-created_at',)


class LawyerVerificationDocumentInline(admin.TabularInline):
    model = LawyerVerificationDocument
    extra = 0
    readonly_fields = ('doc_type', 'original_filename', 'mime_type', 'file_size_bytes', 'submitted_at', 'sha256_checksum', 'status')
    can_delete = False


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'get_full_name', 
        'bar_council_no', 
        'district', 
        'specialization', 
        'verification_status_badge', 
        'verified_at', 
        'created_at'
    )
    list_filter = ('verification_status', 'district', 'sos_available', 'offers_free_session')
    search_fields = ('user__full_name', 'user__email', 'bar_council_no', 'bar_association', 'specialization')
    inlines = [LawyerVerificationDocumentInline]
    actions = ['approve_verification', 'reject_verification']

    def get_full_name(self, obj):
        return f"{obj.honorific} {obj.user.full_name}"
    get_full_name.short_description = 'Lawyer Name'

    def verification_status_badge(self, obj):
        color = {
            'approved': 'green',
            'pending': 'orange',
            'rejected': 'red'
        }.get(obj.verification_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_verification_status_display()
        )
    verification_status_badge.short_description = 'Verification Status'

    @admin.action(description="Approve selected lawyers for verification")
    def approve_verification(self, request, queryset):
        for profile in queryset:
            profile.verification_status = 'approved'
            profile.verified_at = admin.utils.timezone.now() if hasattr(admin.utils, 'timezone') else None
            profile.verified_by = request.user
            profile.save()
            profile.verification_documents.all().update(status='approved', reviewed_by=request.user)

    @admin.action(description="Reject selected lawyers for verification")
    def reject_verification(self, request, queryset):
        queryset.update(verification_status='rejected')
        for profile in queryset:
            profile.verification_documents.all().update(status='rejected', reviewed_by=request.user)


@admin.register(LawyerVerificationDocument)
class LawyerVerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ('lawyer_name', 'doc_type', 'original_filename', 'status', 'submitted_at')
    list_filter = ('doc_type', 'status', 'submitted_at')
    search_fields = ('lawyer__user__full_name', 'original_filename', 'lawyer__bar_council_no')

    def lawyer_name(self, obj):
        return obj.lawyer.user.full_name
    lawyer_name.short_description = 'Lawyer'


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nid_number', 'address', 'created_at')
    search_fields = ('user__full_name', 'user__email', 'nid_number')
