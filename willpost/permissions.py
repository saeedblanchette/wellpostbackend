from rest_framework import permissions


class TwoAuthFactorPermission(permissions.BasePermission):
    message = 'Not allowed'
    def has_permission(self, request, view):
        return not request.user.is_expired()
def allow_recipients(private_file):
    request = private_file.request
    return True