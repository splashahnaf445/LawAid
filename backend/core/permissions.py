from rest_framework import permissions

class IsPlatformAdmin(permissions.BasePermission):
    """
    Grants access only to authenticated platform compliance administrators.
    SRS: FR-34, FR-38.
    """
    message = "Access restricted to LawAid compliance administrators only."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and 
            user.is_authenticated and 
            (getattr(user, 'role', '') == 'admin' or user.is_staff or user.is_superuser)
        )


class IsLawyer(permissions.BasePermission):
    """Grants access only to authenticated lawyers."""
    message = "Access restricted to registered LawAid advocates."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'role', '') == 'lawyer')


class IsClient(permissions.BasePermission):
    """Grants access to registered clients."""
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'role', '') == 'client')


class IsAdminOnlyForDocuments(permissions.BasePermission):
    """
    Strictly enforces SRS NFR-4:
    'The system shall never expose a client's or lawyer's uploaded identification documents 
    (NID, Bar Council certificate) to any party other than platform administrators during verification.'
    
    Unauthorized users, clients, and competing lawyers receive a strict 403 Forbidden.
    """
    message = "Unauthorized: Verification identification documents are strictly confidential and accessible only to authorized platform administrators (SRS NFR-4)."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(getattr(user, 'role', '') == 'admin' or user.is_staff or user.is_superuser)
