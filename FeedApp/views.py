from urllib import request

from django.shortcuts import render, redirect
from .forms import PostForm,ProfileForm#, RelationshipForm
from .models import Post, Comment, Like, Profile, Relationship
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import Http404


# Create your views here.

# When a URL request matches the pattern we just defined, 
# Django looks for a function called index() in the views.py file. 

def index(request):
    """The home page for Learning Log."""
    return render(request, 'FeedApp/index.html')


@login_required
def profile(request):
    profile = Profile.objects.filter(user=request.user)
    if not profile.exists():
        Profile.objects.create(user=request.user)
    profile = Profile.objects.get(user=request.user)

    if request.method != 'POST':
        form = ProfileForm(instance=profile)
    else:
        form = ProfileForm(instance=profile, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('FeedApp:profile')
        
    context = {'form': form}
    return render(request, 'FeedApp/profile.html', context)


@login_required
def myfeed(request):
    comment_count_list = []
    like_count_list = []

    posts = Post.objects.filter(username=request.user).order_by('-date_posted')

    for post in posts:
        c_count = Comment.objects.filter(post=post).count()
        l_count = Like.objects.filter(post=post).count()
        
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    
    zipped_list = zip(posts, comment_count_list, like_count_list)
    
    context = {'posts': posts, 'zipped_list': zipped_list}
    return render(request, 'FeedApp/myfeed.html', context)
        

@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
    else:
        form = PostForm(request.POST,request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.username = request.user
            new_post.save()
            return redirect('FeedApp:myfeed')
        
    context = {'form': form}
    return render(request, 'FeedApp/new_post.html', context)


@login_required
def friendfeed(request):
    comment_count_list = []
    like_count_list = []
    profile, created = Profile.objects.get_or_create(user=request.user)
    friends = profile.friends.all()
    posts = Post.objects.filter(username__in=friends).order_by('-date_posted')

    for post in posts:
        c_count = Comment.objects.filter(post=post).count()
        l_count = Like.objects.filter(post=post).count()
        
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    
    zipped_list = zip(posts, comment_count_list, like_count_list)
    
    if request.method == 'POST' and request.POST.get("like"):
        post_to_like = request.POST.get("like")
        print(post_to_like)
        like_already_exists = Like.objects.filter(post_id=post_to_like, username=request.user)
        if not like_already_exists.exists():
            Like.objects.create(post_id=post_to_like, username=request.user)
            return redirect('FeedApp:friendfeed')

    context = {'posts': posts, 'zipped_list': zipped_list}
    return render(request, 'FeedApp/friendfeed.html', context)
        

@login_required
def comments(request, post_id):
    post = post = Post.objects.get(id=post_id)
    
    if request.method == 'POST' and request.POST.get("btnl"):
        comment = request.POST.get("comment")
        
        if comment:
            Comment.objects.create(post_id=post_id, username=request.user, text=comment, date_added=date.today())             
        
        return redirect('FeedApp:comments', post_id=post_id)
    
    comments = Comment.objects.filter(post_id=post_id)
        
    context = {'post': post, 'comments': comments}
        
    return render(request, 'FeedApp/comments.html', context)


@login_required
def friends(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    user_friends = user_profile.friends.all()
    user_friends_profiles = Profile.objects.filter(user__in=user_friends)

    user_relationships = Relationship.objects.filter(sender=request.user, status='sent')
    request_sent_users = user_relationships.values_list('receiver', flat=True)

    all_profiles = (
        Profile.objects
        .exclude(user=request.user)
        .exclude(user__in=user_friends)
        .exclude(user__in=request_sent_users)
    )

    request_received_profiles = Relationship.objects.filter(
        receiver=request.user,
        status='sent'
    )

    if request.method == 'POST' and request.POST.get("submit_requests"):
        receivers = request.POST.getlist("send_requests")

        for receiver in receivers:
            receiver_profile = Profile.objects.get(id=receiver)

            Relationship.objects.get_or_create(
                sender=request.user,
                receiver=receiver_profile.user,
                defaults={'status': 'sent'}
            )

        return redirect('FeedApp:friends')

    if request.method == 'POST' and request.POST.get("accept_requests"):
        request_ids = request.POST.getlist("friend_requests")

        for request_id in request_ids:
            relationship_obj = Relationship.objects.get(id=request_id)

            relationship_obj.status = 'accepted'
            relationship_obj.save()

            user_profile.friends.add(relationship_obj.sender)

            sender_profile = Profile.objects.get(user=relationship_obj.sender)
            sender_profile.friends.add(request.user)

        return redirect('FeedApp:friends')

    context = {
        'user_friends_profiles': user_friends_profiles,
        'user_relationships': user_relationships,
        'all_profiles': all_profiles,
        'request_received_profiles': request_received_profiles,
    }

    return render(request, 'FeedApp/friends.html', context)
    


