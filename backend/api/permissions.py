from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrStaffOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff
            or request.method in SAFE_METHODS
            or obj.author == request.user
        )
