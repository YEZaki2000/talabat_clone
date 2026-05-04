from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Object-level permission om alleen de eigenaar van een bestelling 
    toegang te geven tot de data.
    """
    def has_object_permission(self, request, view, obj):
        # Alleen de klant die de bestelling geplaatst heeft, mag deze inzien/wijzigen
        return obj.customer == request.user
