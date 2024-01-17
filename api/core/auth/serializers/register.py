from rest_framework import serializers

from core.user.serializers import UserSerializer
from core.user.models import User


class RegisterSerializer(UserSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True, required=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = '__all__'
        extra_kwargs = {
            'estacion': {'read_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
