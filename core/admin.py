from django.contrib import admin
from .models import (
    Post,
    Hashtag,
    Profile,
    FriendRequest,
    Notificaton,
    UserFollowing,
    Friendship,
    )
# Register your models here.
admin.site.register(Post)
admin.site.register(Hashtag)
admin.site.register(Profile)
admin.site.register(FriendRequest)
admin.site.register(Notificaton)
admin.site.register(UserFollowing)
admin.site.register(Friendship)