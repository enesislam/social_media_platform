from django.db.models.signals import post_save, pre_save
from django.conf import settings 
from django.contrib.auth.signals import user_logged_in,user_logged_out
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver
from . models import Profile
from . models import Post, Hashtag,FriendRequest
from django.core.signals import request_finished
from allauth.socialaccount.models import SocialAccount

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance)
    instance.profile.save()

@receiver(user_logged_in)
def user_logged(sender,request,user,**kwargs):
    user.profile.is_online=True
    user.profile.save()

@receiver(user_logged_out)
def user_logged_out(sender,request,user,**kwargs):
    user.profile.is_online=False
    user.profile.save()

@receiver(post_save,sender=Post)
def hashtag_add(sender, instance, *args, **kwargs):
    instance.hashtags.clear()
    for word in instance.content.split():
        if word[0] == '#':
            hashtag , _= Hashtag.objects.get_or_create(name=word)
            instance.hashtags.add(hashtag)

