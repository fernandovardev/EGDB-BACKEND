from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from core.user.serializers import UserSerializer, PermissionSerializer
from core.user.models import User, Permission
from rest_framework.response import Response
from rest_framework import status


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ('patch', 'get')
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.exclude(is_superuser=True)

    def get_object(self):
        id_usuario = self.kwargs.get('pk')
        return get_object_or_404(User, id_usuario=id_usuario)
    
    def update(self, request, *args, **kwargs):
        if not request.user.has_permission('edit_user_profile'):
            return Response({"detail": "You do not have permission to edit user profiles."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned permissions,
        by filtering against a `name` query parameter in the URL.
        """
        queryset = Permission.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset
    
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser

class UserPermissionAssignmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=True, methods=['post'], url_path='assign-permission')
    def assign_permission(self, request, pk=None):
        user = self.get_object()
        permission_name = request.data.get("permission_name")

        try:
            permission = Permission.objects.get(name=permission_name)
        except Permission.DoesNotExist:
            return Response({"detail": "Permission not found."}, status=status.HTTP_404_NOT_FOUND)

        user.custom_permissions.add(permission)
        return Response({"detail": "Permission assigned successfully."}, status=status.HTTP_200_OK)
