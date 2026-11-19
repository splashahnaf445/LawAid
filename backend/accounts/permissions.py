from rest_framework import permissions

class IsPlatformAdmin(permissions.BasePermission):
    """
    Allows access only to authenticated users with the 'admin' role or staff/superuser privileges.
    SRS: FR-34, FR-38, NFR-4.
    """
    message = "Access restricted to LawAid compliance administrators only."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'admin' or request.user.is_staff or request.user.is_superuser)
        )


class IsLawyerUser(permissions.BasePermission):
    """Allows access to authenticated lawyers."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'lawyer'
        )


class IsAdminOnlyForDocuments(permissions.BasePermission):
    """
    Enforces SRS NFR-4:
    'The system shall never expose a client's or lawyer's uploaded identification documents 
    (NID, Bar Council certificate) to any party other than platform administrators during verification.'
    
    Strictly forbids clients, lawyers, and anonymous users from accessing document endpoints.
    """
    message = "Unauthorized: Verification identification documents are strictly confidential and accessible only to authorized platform administrators (SRS NFR-4)."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(user.role == 'admin' or user.is_staff or user.is_superuser)
