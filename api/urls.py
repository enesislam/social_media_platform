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
    ProfileUpdate

    )

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', apiOverview, name= "apiOverview"),
    path('post-list/', PostListAPIView.as_view(), name= "PostListSet"),
    path('post/', PostCreate.as_view(), name= "PostCreateSet"),
    path('post/<int:pk>/', RetrieveUpdateDestroyAPIView.as_view(), name="RetrieveAPIView"),

    path('hashtag-list/', HashtagListAPIView.as_view(), name= "HashtagListAPIView"),
    path('hashtag-create/', HashtagCreate.as_view(), name= "HashtagCreate"),
    
    path('user-list/', UserListView.as_view(),  name="UserListView"),
    path('register/', RegisterAPIView.as_view(),  name="RegisterView"),
    path('login/', CustomAuthToken.as_view(), name='api_token_auth'),  # <-- And here
    path('profile/<int:pk>', ProfileUpdate.as_view(), name='ProfileUpdate'),  # <-- And here

]
