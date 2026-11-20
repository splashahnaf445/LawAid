from django.urls import path

from .views import CurrentUserView, CustomTokenObtainPairView, RegisterClientView, RegisterLawyerView

urlpatterns = [
    # Ahnaf (SYS-21/22)
    path("login/", CustomTokenObtainPairView.as_view(), name="auth-login"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    # Usama (SYS-18) - same paths and names in both branches
    path("register/client/", RegisterClientView.as_view(), name="register-client"),
    path("register/lawyer/", RegisterLawyerView.as_view(), name="register-lawyer"),
]
