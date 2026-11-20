from django.urls import path

from .views import CourtListView, PracticeAreaListView

urlpatterns = [
    path("courts/", CourtListView.as_view(), name="reference-courts"),
    path("practice-areas/", PracticeAreaListView.as_view(), name="reference-practice-areas"),
]
