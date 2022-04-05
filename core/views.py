from re import A
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PostForm, ProfileUpdateForm,ProfileSettingsForm
from .models import Post, Profile, Hashtag,Notificaton,FriendRequest,UserFollowing
from django.views.generic import UpdateView, DeleteView, DetailView,ListView
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse,HttpResponse,Http404
from django.contrib.auth.models import User
import requests
import json 
from django.db.models import  Q
from itertools import chain
from api.views import ReadAllNotificaitons,AddProfilePicture,add_pp

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

class PostDetailView(DetailView):
    model = Post
    template_name = 'post-detail.html'
    context_object_name = 'post'

class IsOwnerOnlyMixin:
    def has_object_permission(self, request, obj):
        return super().has_object_permission(request, obj) and obj.user == request.user

class PostDeleteView(IsOwnerOnlyMixin, DeleteView):
    model = Post
    success_url = "/"
    def get(self,request,*args,**kwargs):
        messages.success(request, _('Post deleted successfully'))
        return super().post(request,*args,**kwargs)

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
        AddProfilePicture.as_view().post(request)
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



def notifications_list(request):
    profile = Profile.objects.get(user=request.user)
    if Notificaton.objects.filter(to_user=profile).exists():
        notifs = Notificaton.objects.filter(to_user=profile).order_by('-date_added')
    else:
        notifs = 'None'
    ReadAllNotificaitons.post(request) #API view
    return render(request, 'notifications.html', {'notifs':notifs})




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
    form = ProfileSettingsForm(request.POST or None, instance=request.user.profile)
    if form.is_valid():
        form.save()
    return render(request, "users/settings.html", {"form": form})

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
