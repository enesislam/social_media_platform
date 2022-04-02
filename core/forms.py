from cProfile import label
from this import d
from django import forms
from .models import Post,Profile, Hashtag
from django.utils.translation import gettext_lazy as _
class PostForm(forms.ModelForm):
    content = forms.CharField(label=False ,widget = forms.Textarea( 
	attrs ={
		'class':'form-control', 
		'placeholder':_('Write something here...'),
         } ))

    class Meta:
        model = Post
        fields = ['content']

class ProfileUpdateForm(forms.ModelForm):
    mail = forms.EmailField()

    class Meta:
        model = Profile
        fields = ['mail']
        
