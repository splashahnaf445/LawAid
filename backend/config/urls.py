from django.urls import include, path

urlpatterns = [
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/reference/", include("lawyers.urls")),
]