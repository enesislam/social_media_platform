from django.urls import path, include
from .import views
import core.urls 
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static  
from django.contrib.auth.decorators import login_required
from .decorators import if_user_logged


urlpatterns =[
    path('',views.home, name='home'),
    path('post-detail/<int:pk>',views.post_detail, name='post-detail'),
    path('post-edit/<int:pk>',views.PostUpdateView.as_view(), name='post-edit'),
    path('post-delete/<int:pk>',views.post_delete, name='post-delete'),
    path('hashtag/<stra>',views.hashtag, name='hashtag'),

    # User Actions
    path('profile/', views.current_user_s_profile, name='profile'),
    path('profile-settings/', views.settings, name='settings'),
    path('profile/<str:username>/', views.user_profiles, name='user_profiles'),
    path('followings/', views.followings_list, name='followings'),
    path('friends/', views.friends_list, name='friends_list'),
    path('follow/', views.follow, name='follow'),
    path('send_friend_request/', views.send_friend_request, name='send_friend_request'),
    path('read_the_notifications/', views.read_the_notifications, name='read_the_notifications'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('delete_all_notifications/', views.delete_all_notifications, name='delete_all_notifications'),
    
    path('read_the_friend_notifications/', views.read_the_friend_notifications, name='read_the_friend_notifications'),
    path('add_friend/', views.add_friend, name='add_friend'),
    path('accept_friend_request/', views.accept_friend_request, name='accept_friend_request'),
    path('delete_friend_request/', views.delete_friend_request, name='delete_friend_request'),
    path('search_results/', views.search_results, name='search_results'),


    #Authentication URLs
    path('register/',views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html',redirect_authenticated_user=True), name='login'),
    path('logout/', if_user_logged(auth_views.LogoutView.as_view(template_name='users/logout.html')), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)