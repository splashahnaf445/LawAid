from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import CustomTokenObtainPairView

def api_root(request):
    return JsonResponse({
        "system": "LawAid Backend Judicial API",
        "version": "2.0.0",
        "modules": {
            "auth": "/api/auth/",
            "lawyers": "/api/lawyers/",
        },
        "status": "online"
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),

    # JWT Authentication
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Modular Domain Apps
    path('api/auth/', include('accounts.urls')),
    path('api/lawyers/', include('lawyers.urls')),
    # Usama (SYS-18): courts / practice areas for the registration forms
    path('api/reference/', include('lawyers.reference_urls')),
]