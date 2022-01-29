from rest_framework.permissions import BasePermission, SAFE_METHODS


"""class for checking if user is the owner of the wallet"""
class IsWalletOwner(BasePermission):

    message = 'You Must be the owner of The wallet!'

    def has_object_permission(self, request, view, obj):
        safe_method = ['GET', 'PUT']
        if request.method in safe_method and obj.user_id == request.user:
            return True
        return False
