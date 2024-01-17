from rest_framework import serializers

from core.user.models import User, Permission
from core.stationdata.models import Estacion

class UserSerializer(serializers.ModelSerializer):
    estacion = serializers.PrimaryKeyRelatedField(queryset=Estacion.objects.all())

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user 

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'