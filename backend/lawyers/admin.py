from django.contrib import admin
from .models import LawyerProfile, LawyerVerificationDocument, Court, PracticeArea

@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'honorific', 'bar_council_no', 'district', 'verification_status', 'verified_at')
    list_filter = ('verification_status', 'district')
    search_fields = ('user__full_name', 'bar_council_no', 'bar_association')

@admin.register(LawyerVerificationDocument)
class LawyerVerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ('lawyer', 'doc_type', 'original_filename', 'status', 'submitted_at')
    list_filter = ('doc_type', 'status')

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'court_type', 'district')

@admin.register(PracticeArea)
class PracticeAreaAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_bn', 'slug')
