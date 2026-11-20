"""
Usama (SYS-18): public reference data for the registration forms.
Mounted at /api/reference/ in config/urls.py (the paths his frontend calls).
"""
from django.urls import path

from .views import CourtListView, PracticeAreaListView

urlpatterns = [
    path("courts/", CourtListView.as_view(), name="reference-courts"),
    path("practice-areas/", PracticeAreaListView.as_view(), name="reference-practice-areas"),
]
