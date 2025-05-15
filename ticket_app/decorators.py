from rest_framework.response import Response
from rest_framework import status

def normal_user_required(func):
    def wrapper(self, request, *args, **kwargs):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_normal_user:
            return Response({"error": "Only normal users can perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return func(self, request, *args, **kwargs)
    return wrapper

def admin_required(func):
    def wrapper(self, request, *args, **kwargs):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        if user.is_normal_user:
            return Response({"error": "Only admin users can perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return func(self, request, *args, **kwargs)
    return wrapper

