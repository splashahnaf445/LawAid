from django.urls import path
from .views import RegisterClientView, RegisterLawyerView, CustomTokenObtainPairView, CurrentUserView

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('register/client/', RegisterClientView.as_view(), name='register-client'),
    path('register/lawyer/', RegisterLawyerView.as_view(), name='register-lawyer'),
]
