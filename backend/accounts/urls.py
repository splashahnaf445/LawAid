from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view()),
    path("refresh/", views.RefreshView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path("logout-all/", views.LogoutAllView.as_view()),
    path("me/", views.MeView.as_view()),
]
