from gettext import gettext
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, reverse
from django.forms import ValidationError
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from PIL import Image
from django.conf import settings

class Hashtag(models.Model):
    name = models.CharField(help_text=_('Name'),max_length=30,unique=True)
    date_added = models.DateTimeField(help_text=_('Date added'),auto_now_add=True)
    

    def __str__(self):
        return self.name


class Post(models.Model):
    content = models.TextField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE,help_text=_('User of Post'),related_name='posts')
    date_added = models.DateTimeField(help_text=_('Date Added'),auto_now=True)
    hashtags=models.ManyToManyField(Hashtag,related_name='posts',help_text=_('Hashtags'),blank=True)

    def __str__(self):
        return self.content

    def clean(self) -> None:
        for word in self.content.split():
            if word.startswith('#') and len(word) == 1:
                raise  ValidationError('Hashtag yeterli uzunlukta değil')
            elif word.startswith('#') and "#" in word[1:]:
                raise  ValidationError('Hashtag karakteri (#) hashtag olamaz')

        return super().clean()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    image = models.ImageField(default='default.png', upload_to='user_profiles')
    bio = models.CharField(max_length=80, blank=True)
    mail = models.EmailField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    friends = models.ManyToManyField(User, related_name='friends',blank=True)
    followings = models.ManyToManyField(User, related_name='follows', blank=True)
    is_private = models.BooleanField(default=False)
    hide_is_online = models.BooleanField(default=False)
    only_friends = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username
        
    @property
    def pp(self):
        return self.image.url or None
    
    def total_follows(self):
        return self.followings.count()


    def follow(self, user):
        Notificaton.objects.create(from_user=self.user, to_user=user.profile, notification_type='follow')
        UserFollowing.objects.create(from_user=self.user, to_user=user)
        return True

    def unfollow(self,username):
        Notificaton.objects.get(from_user=self.user, to_user__user__username=username, notification_type="follow").delete()
        UserFollowing.objects.get(from_user=self.user, to_user__username=username).delete()
        return False

    def follow_toggle(self, username):
        profile = get_object_or_404(Profile, user__username=username)  # The profile that wants to be followed
        that_user = profile.user
        if self.is_following(username):
            return self.unfollow(username)
        return self.follow(that_user)

    def is_following(self, username):
        return UserFollowing.objects.filter(from_user=self.user, to_user__username=username).exists()

    def total_friends(self):
        return self.friends.count()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 350 or img.width > 450:
            output_size = (350, 450)
            img.thumbnail(output_size)
            img.save(self.image.path)

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user_req')
    to_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='to_user_req')
    date_added = models.DateTimeField(help_text=_('Date Added'),auto_now=True)
    is_accepted = models.BooleanField(default=False)
    def __str__(self):
            return self.from_user.username + ' >>> ' + self.to_user.user.username


class UserFollowing(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_following')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_user')
    date_added = models.DateTimeField(help_text=_('Date Added'),auto_now=True)
    def __str__(self):
        return self.from_user.username + ' >>> ' + self.to_user.username





class Friendship(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user_friend')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user_friend')
    date_added = models.DateTimeField(help_text=_('Date Added'),auto_now=True)

    def __str__(self):
        return self.from_user.username + ' and  ' + self.to_user.username






class Notificaton(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user_notfy')
    to_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='to_user_notfy')
    date_added = models.DateTimeField(help_text=_('Date Added'),auto_now=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, choices=(('follow', 'follow'),('friend_now','friend_now'), ('friend_request', 'friend_request'), ('notification', 'notification')), default='notification')
    
    def __str__(self):
        return self.from_user.username + ' ' + self.to_user.user.username

