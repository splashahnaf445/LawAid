from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        "system": "LawAid Backend API",
        "version": "1.0.0",
        "modules": {
            "auth": "/api/auth/",
            "verification": "/api/verification/",
            "lawyers": "/api/lawyers/",
        },
        "status": "online"
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    
    # JWT Auth tokens
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Accounts & Verification routes
    path('api/', include('accounts.urls')),
]
