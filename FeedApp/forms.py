from django import forms

from .models import Post, Profile, Relationship

# Post form (for creating posts)
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description', 'image']   # change this to match your Post model fields
        labels = {'description': 'What would you like to say?'}

# Profile form (for editing profile)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'dob', 'bio']   # match your Profile model
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'dob': 'Date of Birth',
            'bio': 'Bio'
        }


# Relationship form (for follow/unfollow)
class RelationshipForm(forms.ModelForm):
   class Meta:
       model = Relationship
       fields = '__all__'  # user being followed
       labels = {
           'sender': 'Accept friend request from',
           'receiver': 'Send friend request to',
       }
