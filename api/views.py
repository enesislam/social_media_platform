from lib2to3.pgen2.pgen import generate_grammar
from rest_framework import generics,permissions
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view
from core.models import Post,Hashtag,Profile
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .serializers import (
    PostSerializer,
    HashtagSerializer,
    IsOwnerOrReadOnly,
    UserSerializer,
    RegisterSerializer,
    ProfileSerializer
    )
    
@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'Post List':'/api/post-list',
        'Post Detail-Update-Delete':'/api/post/<str:pk>',
        'Post Create':'/api/post-create',

        'Hashtag List':'/api/hashtag-list',
        'Hashtag Create':'/api/hashtag-create',
    }
    return Response(api_urls)

class PostListAPIView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class=PostSerializer
    permission_classes = [permissions.AllowAny]

class PostCreate(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class=PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class  PostRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class=PostSerializer
 

class HashtagListAPIView(generics.ListAPIView):
    queryset = Hashtag.objects.all()
    serializer_class=HashtagSerializer

class HashtagCreate(generics.CreateAPIView):
    queryset = Hashtag.objects.all()
    serializer_class=HashtagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class=PostSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class =  UserSerializer

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class CustomAuthToken(ObtainAuthToken):
    pass
            

class ProfileUpdate(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class=ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]