from re import A
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PostForm, ProfileUpdateForm
from .models import Post, Profile, Hashtag,Notificaton,FriendRequest,UserFollowing
from django.views.generic import UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse,HttpResponse
from django.contrib.auth.models import User
import requests
import json 
from django.db.models import  Q
from itertools import chain




def home(request):
    if request.user.is_authenticated:
        form = PostForm(request.POST)
        if request.method == 'POST' and form.is_valid():
            post_content = form.cleaned_data['content']
            f = form.instance
            f.user = request.user
            f.save()
            messages.success(request, _('Post created successfully'))
            return redirect('home')
        ctx = {
            'posts':Post.objects.filter(
                Q(user=request.user)|
                Q(user__profile__only_friends=False)|
                Q(user__profile__only_friends=True,user__in=request.user.profile.friends.all())).order_by('-date_added'),'form':form,'profile':request.user.profile,
            'last_hashtags':Hashtag.objects.all().order_by('-date_added')[:5]
            }
        return render(request, 'home.html',ctx)
    ctx = {
        'posts':Post.objects.all().order_by('-date_added'),
        'last_hashtags':Hashtag.objects.all().order_by('-date_added')[:5]
        }
    return render(request, 'home.html',ctx)

def post_detail(request,pk):
    object_ = get_object_or_404(Post, pk=pk)
    return render(request, 'post-detail.html', {'post':object_})

        
def post_delete(request,pk):
    object_ = get_object_or_404(Post, pk=pk)
    if request.user == object_.user:
        object_.delete()
        messages.success(request, _('Post deleted successfully'))
    return redirect('home')

class PostUpdateView(UpdateView):
    model = Post
    fields = ['content',]
    template_name = 'post_update.html'
    success_url  = '/'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        if user == self.object.user:
            return super().post(request, *args, **kwargs)
        else:
            return redirect('home')

    

def register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f'Account created successfully {request.user.username}')

                return redirect('login')

        else:
            form = UserCreationForm()
        return render(request, 'users/register.html', {'form': form})
    else:
        return redirect('home')

@login_required
def current_user_s_profile(request):
    if request.method == 'POST' and 'delete_email' in request.POST:
        a = Profile.objects.get(user=request.user)
        a.mail = None
        a.save()
        messages.success(request, _('Mail is deleted successfully'))
        return redirect('profile')
    elif request.method == 'POST':
        email_form = ProfileUpdateForm(request.POST or None, instance=Profile.objects.get(user=request.user))
        if email_form.is_valid():
            f = email_form.instance
            f.user = request.user
            
            f.save()
            messages.success(request, _('Mail is updated successfully'))
            return redirect('profile')

    else:
        email_form = ProfileUpdateForm()
    if request.POST.get('operation') == 'add_pp':
        a = Profile.objects.get(user=request.user)
        a.image = request.FILES.get('image')
        print(request.FILES.get('image').name)
        a.save()
        messages.success(request, _('Profile picture is updated successfully'))
        response = {'mesage':'pic is updated'}
        return JsonResponse(response)
    return render(request, 'users/profile.html', {'email_form':email_form})

@login_required
def user_profiles(request,username):
    if request.user.username == username:
        return redirect('profile')
    else:
        aforementioned_user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=aforementioned_user) #The profile that wants to be followed
        if UserFollowing.objects.filter(from_user=request.user,to_user=aforementioned_user): #already followed the profile
            flw_btn = 'Following'
        else:
            flw_btn = 'Follow'
        if profile.friends.filter(id=request.user.id):
            is_friend = True
        else:
            is_friend = False
        if profile.is_private: # Kullanıcı Gizli ise
            if not profile.friends.filter(id=request.user.id): # Arkadaş değilse
                if not FriendRequest.objects.filter(from_user=request.user, to_user=profile): # İstek atmamışsa
                    req_btn = "Send Request"
                else:
                    req_btn = 'Unrequest'
                already_friend = False
                friend_btn = "Add Friend"
            else: # Arkaşsa
                friend_btn = "Friend ✔️"
                already_friend = True
                req_btn = "Friend ✔️"
            ctx = {
            'user':aforementioned_user,
            'follow_btn_text':flw_btn,
            'req_btn':req_btn,
            'already_friend':already_friend,
            'friend_btn':friend_btn,
            'is_friend':is_friend,
            }
        else: # Kullanıcı gizli değilse
            if profile.friends.filter(id=request.user.id):
                friend_btn = "Friend ✔️"
            else:
                friend_btn = 'Add Friend'
            ctx = {
                'user':aforementioned_user,
                'follow_btn_text':flw_btn,
                'friend_btn':friend_btn,
                'is_friend':is_friend,
                }
        return render(request, 'users/user_profile.html',ctx)

def follow(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        profile = get_object_or_404(Profile, user__username=username) #The profile that wants to be followed
        notif, is_created = Notificaton.objects.get_or_create(from_user=request.user, to_user=profile, notification_type='follow')
        that_user = get_object_or_404(User, username=username)
        if UserFollowing.objects.filter(from_user=request.user,to_user=that_user).exists(): #already followed the profile
            a = UserFollowing.objects.get(from_user=request.user,to_user__username=username) #remove user from followings
            a.delete()
            followed=False
            print('unfollowed')
            notif.delete()
        else:
            UserFollowing.objects.create(from_user=request.user,to_user=that_user)
            followed=True
            print('followed')
    count = UserFollowing.objects.filter(to_user=that_user).count()
    ctx = {'likes_count':count, "followed":followed}
    return JsonResponse(ctx)

def read_the_notifications(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if Notificaton.objects.filter(to_user=profile, is_read=False).exists():
            notif = Notificaton.objects.filter(to_user=profile, is_read=False)
            notif.update(is_read=True)
            there_are_notifications = True
            info = _('Notifications are read')
        else:
            there_are_notifications = False
            info = _('No notifications')
    ctx = {'info': info,'there_are_notifications':there_are_notifications}
    return JsonResponse(ctx)

def search_results(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        if query:
            posts = Post.objects.filter(Q(content__icontains=query))
            hashtags = Hashtag.objects.filter(name__icontains=query)
            users = Profile.objects.filter(user__username__icontains=query)
            search_all = chain(posts, hashtags, users)
            return render(request, 'search_results.html', {'search_all':search_all, 'q':query} )
        else:
            return redirect('homme')
    else:
        return redirect('profile')


def delete_all_notifications(request):
    profile = Profile.objects.get(user=request.user)
    if Notificaton.objects.filter(to_user=profile).exists():
        notif = Notificaton.objects.filter(to_user=profile)
        notif.delete()
        info = _('All notifications are deleted')
        return redirect('notifications_list')
    else:
        return redirect('notifications_list')

def read_the_friend_notifications(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if Notificaton.objects.filter(to_user=profile, notification_type='friend_request', is_read=False).exists():
            notif = Notificaton.objects.filter(to_user=profile, notification_type='friend_request',is_read=False)
            notif.update(is_read=True)
            there_are_friend_notifications = True
            info = _('Notifications are read')
        else:
            there_are_friend_notifications = False
            info = _('No notifications')
    ctx = {'info': info,'there_are_friend_notifications':there_are_friend_notifications}
    return JsonResponse(ctx)

def read_all_notifications(request):
    profile = Profile.objects.get(user=request.user)
    if Notificaton.objects.filter(to_user=profile, is_read=False).exists():
        notif = Notificaton.objects.filter(to_user=profile,is_read=False)
        notif.update(is_read=True)
    else:
        pass

def notifications_list(request):
    profile = Profile.objects.get(user=request.user)
    if Notificaton.objects.filter(to_user=profile).exists():
        notifs = Notificaton.objects.filter(to_user=profile).order_by('-date_added')
    else:
        notifs = 'None'
    read_all_notifications(request)
    return render(request, 'notifications.html', {'notifs':notifs})

#For Private Profiles
def send_friend_request(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        profile = get_object_or_404(Profile, user__username=username) #The profile that wants to be friended
        if FriendRequest.objects.filter(from_user=request.user,to_user=profile).exists(): #already followed the profile
            req = FriendRequest.objects.get(from_user=request.user,to_user=profile) #remove user from followings
            req.delete()
            notif = Notificaton.objects.get(from_user=request.user, to_user=profile, notification_type='friend_request')
            notif.delete()
            status='unrequested'
            print('unrequested')
        else:
            req = FriendRequest(from_user=request.user,to_user=profile)
            req.save()
            status='requested'
            Notificaton.objects.get_or_create(from_user=request.user, to_user=profile, notification_type='friend_request')
            print('requested')
    
    ctx = {"status":status}
    return JsonResponse(ctx)

#Adds to friends if user is not private, otherwise works inside "accept_friend_request" functions
def add_friend(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        that_user = get_object_or_404(User, username=username) #The profile that wants to be friended
        request_profile = get_object_or_404(Profile, user=request.user) #The profile that wants to be friended


        if request_profile.friends.filter(id=that_user.id).exists(): #already friend the profile
            #remove user from friends
            request_profile.friends.remove(that_user)
            
            that_userprofile = that_user.profile
            that_userprofile.friends.remove(request.user)


            if Notificaton.objects.filter(from_user=request.user, to_user=that_userprofile, notification_type='friend_now').exists():
                notif = Notificaton.objects.get(from_user=request.user, to_user=that_userprofile, notification_type='friend_now')
                notif.delete()
            elif Notificaton.objects.filter(from_user=that_user,to_user=request_profile, notification_type='friend_now'):
                notif2 = Notificaton.objects.get(from_user=that_user,to_user=request_profile, notification_type='friend_now')
                notif2.delete()
            status=False
            print('removed')
        else:
            #add user to friends
            request_profile.friends.add(that_user)
            that_userprofile = that_user.profile
            that_userprofile.friends.add(request.user)

            status=True
            Notificaton.objects.get_or_create(from_user=request.user, to_user=that_userprofile, notification_type='friend_now')
            Notificaton.objects.get_or_create(from_user=that_user, to_user=request_profile, notification_type='friend_now')
        # For Accept Function..
        if FriendRequest.objects.filter(from_user=that_user,to_user=request.user.profile).exists():
            req = FriendRequest.objects.get(from_user=that_user,to_user=request.user.profile)
            req.delete()
            notif = Notificaton.objects.get(from_user=that_user,to_user=request.user.profile, notification_type='friend_request')
            notif.delete()
            print('ok')
    
    ctx = {"status":status}
    return JsonResponse(ctx)

def accept_friend_request(request):
    if request.method == 'POST':
        return add_friend(request)
    else:
        return JsonResponse({'status':False})
def delete_friend_request(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        that_user = get_object_or_404(User, username=username)
        if FriendRequest.objects.filter(from_user=that_user,to_user=request.user.profile).exists():
            req = FriendRequest.objects.get(from_user=that_user,to_user=request.user.profile)
            req.delete()
            notif = Notificaton.objects.get(from_user=that_user,to_user=request.user.profile, notification_type='friend_request')
            notif.delete()
            print('deleted')
            return JsonResponse({'status':True})
        else:
            return JsonResponse({'status':False})


def followings_list(request):
    followings_list = UserFollowing.objects.filter(from_user=request.user)
    is_friend = False
    ctx = {'list':followings_list,'is_friend':is_friend}
    return render(request, 'users/followings_list.html',ctx)

def friends_list(request):
    friends_list = request.user.profile.friends.all()
    is_friend = True
    ctx = {'list':friends_list,'is_friend':is_friend}
    return render(request, 'users/friends.html',ctx)


def settings(request):
    if request.user.profile.is_private:is_private = True
    else:is_private = False

    if request.user.profile.hide_is_online:hide_is_online = True
    else:hide_is_online = False

    if request.user.profile.only_friends:only_friends = True
    else:only_friends = False
    ctx = {
            'is_private':is_private,
            'hide_is_online':hide_is_online,
            'only_friends':only_friends,}   
    if request.method =="POST":
        if request.POST.get('is_private', None) == 'on':
            request.user.profile.is_private = True
            request.user.profile.save()
            is_private = True
            message = _('Your profile is now private')
        else:
            request.user.profile.is_private = False
            request.user.profile.save()
            is_private = False
            message = _('Your profile is now public')
        
        if request.POST.get('hide_is_online', None) == 'on':
            request.user.profile.hide_is_online = True
            request.user.profile.save()
            hide_is_online = True
            message = _('You are a ghost now')
        else:
            request.user.profile.hide_is_online = False
            request.user.profile.save()
            hide_is_online = False
            message = _('Your profile is now public')
        
        if request.POST.get('only_friends', None) == 'on':
            request.user.profile.only_friends = True
            request.user.profile.save()
            only_friends = True
            message = _('Your profile is now restricted to friends')
        else:
            request.user.profile.only_friends = False
            request.user.profile.save()
            only_friends = False
            message = _('Your profile is now public')
        ctx = {
            'is_private':is_private,
            'message':message,
            'hide_is_online':hide_is_online,
            'only_friends':only_friends,
        }
        return render(request, 'users/settings.html',ctx)

        
    return render(request, 'users/settings.html',ctx)

def logout(request):
    if request.user in request.session:
        del request.session['user_']
    auth.logout(request)
    return render(request, 'users/logout.html')

def hashtag(request, stra):
    posts = Post.objects.filter(hashtags__name=stra)
    related_posts = Post.objects.filter(hashtags__name__icontains=stra).exclude(hashtags__name=stra)
    if not Post.objects.filter(hashtags__name=stra):
        return redirect('home')
    else:
        ctx = {
            'hash_name':stra,
            'related_posts':related_posts,
            'posts':posts
        }
        return render(request, 'hashtag.html',ctx)
