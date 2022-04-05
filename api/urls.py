from django.urls import path
from .views import (
    apiOverview,
    PostListAPIView,
    PostCreate,
    HashtagListAPIView,
    HashtagCreate,
    UserListView,
    RegisterAPIView,
    CustomAuthToken,
    RetrieveUpdateDestroyAPIView,
    ProfileUpdate,
    SendFriendRequest,
    ReadAllNotificaitons,
    DeleteAllNotifications,
    ReadFriendNotifications,
    ReadTheNotifications,
    AddFriend,
    AcceptFriendRequest,
    RefuseFriendRequest,
    FollowView,
    AddProfilePicture,

    )

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', apiOverview, name= "apiOverview"), #api/
    path('post-list/', PostListAPIView.as_view(), name= "PostListSet"), # Lists all posts
    path('post/', PostCreate.as_view(), name= "PostCreateSet"), # Create a post
    path('post/<int:pk>/', RetrieveUpdateDestroyAPIView.as_view(), name="RetrieveAPIView"), # Retrieve, Update, Delete a post

    path('hashtag-list/', HashtagListAPIView.as_view(), name= "HashtagListAPIView"), # Lists all hashtags
    path('hashtag-create/', HashtagCreate.as_view(), name= "HashtagCreate"), # create a hashtag
    path('send_friend_request/', SendFriendRequest.as_view(), name='send_friend_request'), # Send a friend request
    
    path('read_the_notifications/', ReadTheNotifications.as_view(), name='read_the_notifications'), #Reads follow and other notifications
    path('read_the_friend_notifications/', ReadFriendNotifications.as_view(), name='read_the_friend_notifications'), #Reads friend request notifications 
    path('read_all_notifications/', ReadAllNotificaitons.as_view(), name='read_all_notifications'), #Reads all notifications. Including Friend requests
    path('delete_all_notifications/', DeleteAllNotifications.as_view(), name='delete_all_notifications'), #Deletes all notifications. Including Friend requests
    path('add_friend/', AddFriend.as_view(), name='add_friend'),
    path('accept_friend_request/', AcceptFriendRequest.as_view(), name='accept_friend_request'),
    path('delete_friend_request/', RefuseFriendRequest.as_view(), name='delete_friend_request'),
    path('follow/', FollowView.as_view(), name='follow'),

    path('user-list/', UserListView.as_view(),  name="UserListView"), #Lists all users
    path('register/', RegisterAPIView.as_view(),  name="RegisterView"), #Registers a user
    path('login/', CustomAuthToken.as_view(), name='api_token_auth'),  # Login
    path('profile/<int:pk>', ProfileUpdate.as_view(), name='ProfileUpdate'),  # Updates profile
    path('add_profile_pic/', AddProfilePicture.as_view(), name='AddProfilePicture'),  # Updates profile

]
