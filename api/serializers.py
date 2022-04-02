from dataclasses import fields
from rest_framework import serializers, permissions
from core.models import Post,Hashtag,Profile
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id','content','user']
        read_only_fields = ['user']

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = '__all__'
        #read_only_fields = ['user']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','last_login','is_active','email')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ( 'id', 'username', 'email', 'password')
        extra_kwargs = {
            "id": {"read_only": True},
            'password': {'write_only':True}
        }
#Has ownership on?
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
        
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id','is_online','mail',)
