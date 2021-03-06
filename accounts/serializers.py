from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from .models import User



class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id','username', 'email', 'password', 'first_name', 'last_name')
