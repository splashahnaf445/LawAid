from django.urls import path

from .views import RegisterClientView, RegisterLawyerView

urlpatterns = [
    path("register/client/", RegisterClientView.as_view(), name="register-client"),
    path("register/lawyer/", RegisterLawyerView.as_view(), name="register-lawyer"),
]
