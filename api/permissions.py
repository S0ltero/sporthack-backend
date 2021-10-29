from rest_framework import permissions

class IsTrainer(permissions.BasePermission):
    """
    Allows access only to trainer users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_trainer)