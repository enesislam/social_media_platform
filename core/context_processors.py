from core.views import hashtag
from .models import Notificaton, Post, Hashtag, Profile, FriendRequest
from django.shortcuts import render
def notifications(request):
    if request.user.is_authenticated:  
        profile = Profile.objects.get(user=request.user)
        friend_req = FriendRequest.objects.filter(to_user=profile, is_accepted=False).order_by('-date_added')
        #In the next edit just the line below is needed: natification_type=all
        follow_notifications = Notificaton.objects.filter(to_user=profile).exclude(notification_type='friend_request').order_by('-date_added')
        friend_req_notifications = Notificaton.objects.filter(to_user=profile,notification_type='friend_request').order_by('-date_added')
        # Follow notifications 
        if follow_notifications.filter(is_read=False).exists():
            new_notifs = True
            new_notifs_count = follow_notifications.filter(is_read=False).count()
        else:
            new_notifs = False
            new_notifs_count = False

        # Friend Request Notifications
        if friend_req_notifications.filter(is_read=False).exists():
            friend_req_new_notifs = True
            friend_req_new_notifs_count = friend_req_notifications.filter(is_read=False).count()
        else:
            friend_req_new_notifs = False
            friend_req_new_notifs_count = False

        return {
            'follow_notifications': follow_notifications,
            'friend_req_notifications': friend_req,
            'new_notifs':new_notifs,
            'new_notifs_count':new_notifs_count,
            'friend_req_new_notifs':friend_req_new_notifs,
            'friend_req_new_notifs_count':friend_req_new_notifs_count,
            }
    else:
        return {}
