from lib2to3.pgen2.pgen import generate_grammar
from urllib import response
from django.shortcuts import get_object_or_404
from rest_framework import generics,permissions
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view
from core.models import Post,Hashtag,Profile,FriendRequest,Notificaton,UserFollowing
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework import views
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .serializers import (
    PostSerializer,
    HashtagSerializer,
    IsOwnerOrReadOnly,
    UserSerializer,
    RegisterSerializer,
    ProfileSerializer
    )
from django.contrib import messages

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



class SendFriendRequest(views.APIView):
    def post(self,request):
        if FriendRequest.objects.filter(from_user=request.user,to_user=Profile.objects.get(user__username=request.POST.get('username', None))).exists():
            FriendRequest.objects.get(from_user=request.user,to_user=Profile.objects.get(user__username=request.POST.get('username', None))).delete() #remove user from followings
            Notificaton.objects.get(from_user=request.user, to_user=Profile.objects.get(user__username=request.POST.get('username', None)), notification_type='friend_request').delete()
            return Response({'message':'requested','status':'unrequested'})
        FriendRequest(from_user=request.user,to_user=Profile.objects.get(user__username=request.POST.get('username', None))).save()
        Notificaton.objects.get_or_create(from_user=request.user, to_user=Profile.objects.get(user__username=request.POST.get('username', None)), notification_type='friend_request')
        print('requested')
        return Response({'message':'requested','status':'requested'})
    
class ReadAllNotificaitons(views.APIView):
    def post(request):
        if Notificaton.objects.filter(to_user=request.user.profile, is_read=False).exists():
            Notificaton.objects.filter(to_user=request.user.profile, is_read=False).update(is_read=True)
            there_are_notifications = True
            info = ('Notifications are read')
        else:
            there_are_notifications = False
            info = ('No notifications')
        ctx = {'info': info,'there_are_notifications':there_are_notifications}
        return Response(ctx)

class ReadFriendNotifications(views.APIView):
    def post(self,request):
        is_there = False
        info = ('No notifications')
        if Notificaton.objects.filter(Q(notification_type='friend_request'),to_user=request.user.profile, is_read=False).exists():
            Notificaton.objects.filter(Q(notification_type='friend_request'),to_user=request.user.profile, is_read=False).update(is_read=True)
            is_there = True
            info = ('Notifications are rread')
        ctx = {'info': info,'is_there':is_there}
        return Response(ctx)

class ReadTheNotifications(views.APIView):
    def post(self,request):
        is_there = False
        info = ('No notifications')
        if Notificaton.objects.filter(Q(notification_type='follow') | Q(notification_type='friend_now'),to_user=request.user.profile, is_read=False).exists():
            Notificaton.objects.filter(Q(notification_type='follow') | Q(notification_type='friend_now'),to_user=request.user.profile, is_read=False).update(is_read=True)
            is_there = True
            info = ('Notifications are read')
        ctx = {'info': info,'is_there':is_there}
        return Response(ctx)
class DeleteAllNotifications(views.APIView):
    def delete(self,request):
        info = ('No notifications')
        if Notificaton.objects.filter(to_user=request.user.profile).exists():
            Notificaton.objects.filter(to_user=request.user.profile).delete()
            info = ('Notifications are deleted')
        return Response({'info': info})
#Adds to friends if user is not private, otherwise works inside "accept_friend_request" functions
class AddFriend(views.APIView):
    def post(self,request):
        that_user = get_object_or_404(User, username=request.POST.get('username', None)) #The profile that wants to be friended
        if request.user.profile.friends.filter(id=that_user.id).exists(): #already friend the profile
            request.user.profile.friends.remove(that_user)
            that_user.profile.friends.remove(request.user)
            if Notificaton.objects.filter(from_user=request.user, to_user=that_user.profile, notification_type='friend_now').exists():
                Notificaton.objects.get(from_user=request.user, to_user=that_user.profile, notification_type='friend_now').delete()
                
            elif Notificaton.objects.filter(from_user=that_user,to_user=request.user.profile, notification_type='friend_now'):
                Notificaton.objects.get(from_user=that_user,to_user=request.user.profile, notification_type='friend_now').delete()
            status=False
            print('removed')
        else:
            #add user to friends
            request.user.profile.friends.add(that_user)
            that_user.profile.friends.add(request.user)
            status=True
            Notificaton.objects.get_or_create(from_user=request.user, to_user=that_user.profile, notification_type='friend_now')
            Notificaton.objects.get_or_create(from_user=that_user, to_user=request.user.profile, notification_type='friend_now')
        # For Accept Function..
        if FriendRequest.objects.filter(from_user=that_user,to_user=request.user.profile).exists():
            req = FriendRequest.objects.get(from_user=that_user,to_user=request.user.profile)
            req.delete()
            notif = Notificaton.objects.get(from_user=that_user,to_user=request.user.profile, notification_type='friend_request')
            notif.delete()
            print('ok')
        ctx = {"status":status}
        return Response(ctx)

class AcceptFriendRequest(views.APIView):
    def post(self,request):
        return AddFriend.post(self,request)

class RefuseFriendRequest(views.APIView):
    def delete(self,request):
        that_user = get_object_or_404(User, username=request.POST.get('username', None)) #The profile that wants to be friended
        if FriendRequest.objects.filter(from_user=that_user,to_user=request.user.profile).exists():
            FriendRequest.objects.get(from_user=that_user,to_user=request.user.profile).delete()
            Notificaton.objects.get(from_user=that_user,to_user=request.user.profile, notification_type='friend_request').delete()
            print('ok')
        return Response({"status":True})

class FollowView(views.APIView):

    def put(self,request):
        return Response({
            "likes_count": UserFollowing.objects.filter(to_user__username=request.POST.get("username", None)).count(), 
            "followed": request.user.profile.follow_toggle(request.POST.get("username", None))
        }) 

def add_pp(request):
    a = Profile.objects.get(user=request.user)
    a.image = request.FILES.get('image')
    a.save()
    messages.success(request, ('Profile picture is updated successfully'))
    response = {'mesage':'pic is updated'}
    return response

class AddProfilePicture(views.APIView):
    def post(self,request):
        return Response(add_pp(request))