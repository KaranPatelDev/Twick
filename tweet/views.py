from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Tweet, UserProfile, Comment
from .forms import TweetForm, CustomUserCreationForm, UserProfileForm, ReplyForm, CommentForm

def home(request):
    """Home page showing recent tweets"""
    if request.user.is_authenticated:
        # Show public tweets and user's own tweets
        tweets = Tweet.objects.filter(
            Q(privacy='public') | Q(user=request.user)
        ).filter(parent_tweet__isnull=True)[:10]  # Latest 10 parent tweets
    else:
        tweets = Tweet.objects.filter(privacy='public', parent_tweet__isnull=True)[:10]
    
    return render(request, "home.html", {"tweets": tweets})

def tweet_list(request):
    """List all tweets with search functionality"""
    search_query = request.GET.get('search', '')
    
    # Base queryset - only show public tweets and user's own tweets
    if request.user.is_authenticated:
        tweets = Tweet.objects.filter(
            Q(privacy='public') | Q(user=request.user)
        ).filter(parent_tweet__isnull=True)  # Only show parent tweets, not replies
    else:
        tweets = Tweet.objects.filter(privacy='public', parent_tweet__isnull=True)
    
    if search_query:
        tweets = tweets.filter(
            Q(text__icontains=search_query) |
            Q(user__username__icontains=search_query)
        ).order_by("-created_at")
    else:
        tweets = tweets.order_by("-created_at")
    
    return render(request, "tweet_list.html", {
        "tweets": tweets, 
        "search_query": search_query
    })

@login_required
def tweet_create(request):
    """Create a new tweet"""
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, 'Tweet created successfully!')
            return redirect("tweet_list")
    else:
        form = TweetForm()
    return render(request, "tweet_form.html", {"form": form})

@login_required
def tweet_edit(request, tweet_id):
    """Edit a tweet"""
    tweet = get_object_or_404(Tweet, id=tweet_id, user=request.user)
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tweet updated successfully!')
            return redirect("tweet_list")
    else:
        form = TweetForm(instance=tweet)
    return render(request, "tweet_form.html", {"form": form, "tweet": tweet})

@login_required
def tweet_delete(request, tweet_id):
    """Delete a tweet"""
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == "POST":
        tweet.delete()
        messages.success(request, 'Tweet deleted successfully!')
        return redirect("tweet_list")
    return render(request, "tweet_confirm_delete.html", {"tweet": tweet})

@login_required
def like_tweet(request, tweet_id):
    """Like/unlike a tweet via AJAX"""
    tweet = get_object_or_404(Tweet, id=tweet_id)
    
    if request.user in tweet.likes.all():
        tweet.likes.remove(request.user)
        liked = False
    else:
        tweet.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': tweet.get_likes_count()
    })

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserProfile is automatically created by signals
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_profile(request, username):
    """Enhanced user profile page with advanced features"""
    profile_user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=profile_user)
    
    # Increment profile views (but not for the profile owner)
    if request.user != profile_user and request.user.is_authenticated:
        profile.increment_profile_views()
    
    # Get user's tweets with privacy filtering
    if request.user.is_authenticated:
        if request.user == profile_user or not profile.is_private or request.user in profile.followers.all():
            tweets = Tweet.objects.filter(user=profile_user, parent_tweet__isnull=True).order_by('-created_at')
        else:
            tweets = Tweet.objects.filter(user=profile_user, privacy='public', parent_tweet__isnull=True).order_by('-created_at')
    else:
        tweets = Tweet.objects.filter(user=profile_user, privacy='public', parent_tweet__isnull=True).order_by('-created_at')
    
    # Get stats
    total_likes = sum(tweet.get_likes_count() for tweet in Tweet.objects.filter(user=profile_user))
    total_replies = Tweet.objects.filter(user=profile_user, parent_tweet__isnull=False).count()
    
    # Check if current user is following this profile
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = request.user in profile.followers.all()
    
    # Get recent followers (for display)
    recent_followers = profile.followers.all()[:6]
    
    # Get mutual followers (if viewing someone else's profile)
    mutual_followers = []
    if request.user.is_authenticated and request.user != profile_user:
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        mutual_followers = profile.followers.filter(id__in=user_profile.followers.all())[:3]
    
    # Profile completion for profile owner
    show_completion = request.user == profile_user
    
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'tweets': tweets,
        'total_likes': total_likes,
        'total_replies': total_replies,
        'is_following': is_following,
        'recent_followers': recent_followers,
        'mutual_followers': mutual_followers,
        'show_completion': show_completion,
        'can_view_private_content': (
            request.user == profile_user or 
            not profile.is_private or 
            (request.user.is_authenticated and request.user in profile.followers.all())
        )
    }
    
    return render(request, 'user_profile.html', context)

@login_required
def edit_profile(request):
    """Enhanced profile editing with all new features"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '🎉 Profile updated successfully!')
            return redirect('user_profile', username=request.user.username)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'edit_profile.html', {'form': form, 'profile': profile})

@login_required
def follow_user(request, username):
    """Follow/unfollow a user with AJAX support"""
    if request.method == 'POST':
        user_to_follow = get_object_or_404(User, username=username)
        profile_to_follow, _ = UserProfile.objects.get_or_create(user=user_to_follow)
        
        if request.user == user_to_follow:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'You cannot follow yourself'}, status=400)
            messages.error(request, 'You cannot follow yourself.')
            return redirect('user_profile', username=username)
        
        is_following = request.user in profile_to_follow.followers.all()
        
        if is_following:
            profile_to_follow.followers.remove(request.user)
            action = 'unfollowed'
            button_text = 'Follow'
            button_class = 'btn-outline-primary'
        else:
            profile_to_follow.followers.add(request.user)
            action = 'followed'
            button_text = 'Following'
            button_class = 'btn-primary'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'action': action,
                'button_text': button_text,
                'button_class': button_class,
                'followers_count': profile_to_follow.get_followers_count()
            })
        
        messages.success(request, f'You {action} @{username}')
        return redirect('user_profile', username=username)
    
    return redirect('user_profile', username=username)

@login_required
def tweet_reply(request, tweet_id):
    """Reply to a tweet"""
    parent_tweet = get_object_or_404(Tweet, id=tweet_id)
    
    if request.method == "POST":
        form = ReplyForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.parent_tweet = parent_tweet
            reply.privacy = parent_tweet.privacy  # Inherit privacy from parent
            reply.save()
            messages.success(request, 'Reply posted successfully!')
            return redirect("tweet_detail", tweet_id=parent_tweet.id)
    else:
        form = ReplyForm()
    
    return render(request, "tweet_reply.html", {
        "form": form, 
        "parent_tweet": parent_tweet
    })

def tweet_detail(request, tweet_id):
    """Show tweet detail with replies and comments"""
    tweet = get_object_or_404(Tweet, id=tweet_id)
    
    # Check if user can view this tweet
    if tweet.privacy == 'private' and not request.user.is_authenticated:
        messages.error(request, 'This tweet is private.')
        return redirect('tweet_list')
    
    if tweet.privacy == 'private' and request.user != tweet.user:
        # Check if user follows the tweet author
        profile = getattr(tweet.user, 'userprofile', None)
        if not profile or request.user not in profile.followers.all():
            messages.error(request, 'This tweet is private.')
            return redirect('tweet_list')
    
    # Get all tweets in this thread
    thread_tweets = tweet.get_thread_tweets()
    
    # Get comments for this tweet
    comments = Comment.objects.filter(tweet=tweet, parent_comment__isnull=True)
    
    # Forms for replies and comments
    reply_form = ReplyForm() if request.user.is_authenticated else None
    comment_form = CommentForm() if request.user.is_authenticated else None
    
    return render(request, "tweet_detail.html", {
        "tweet": tweet,
        "thread_tweets": thread_tweets,
        "comments": comments,
        "reply_form": reply_form,
        "comment_form": comment_form
    })

@login_required
def add_comment(request, tweet_id):
    """Add a comment to a tweet"""
    tweet = get_object_or_404(Tweet, id=tweet_id)
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.tweet = tweet
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect("tweet_detail", tweet_id=tweet_id)

@login_required
def reply_to_comment(request, comment_id):
    """Reply to a comment"""
    parent_comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.tweet = parent_comment.tweet
            reply.user = request.user
            reply.parent_comment = parent_comment
            reply.save()
            messages.success(request, 'Reply added successfully!')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect("tweet_detail", tweet_id=parent_comment.tweet.id)

@login_required
def like_comment(request, comment_id):
    """Like/unlike a comment via AJAX"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': comment.get_likes_count()
    })

@login_required
def delete_comment(request, comment_id):
    """Delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    tweet_id = comment.tweet.id
    
    if request.method == "POST":
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
    
    return redirect("tweet_detail", tweet_id=tweet_id)


# ====================
# FOLLOWING/FOLLOWERS SYSTEM VIEWS
# ====================

@login_required
def follow_user_new(request, username):
    """Enhanced follow system with follow requests for private accounts"""
    if request.method == 'POST':
        user_to_follow = get_object_or_404(User, username=username)
        
        if request.user == user_to_follow:
            return JsonResponse({'error': 'You cannot follow yourself'}, status=400)
        
        from .models import Follow, FollowRequest, Block
        from .utils import create_notification
        
        # Check if user is blocked
        if Block.objects.filter(blocker=user_to_follow, blocked=request.user).exists():
            return JsonResponse({'error': 'You cannot follow this user'}, status=400)
        
        profile_to_follow = get_object_or_404(UserProfile, user=user_to_follow)
        
        # Check if already following
        existing_follow = Follow.objects.filter(follower=request.user, following=user_to_follow).first()
        
        if existing_follow:
            # Unfollow
            existing_follow.delete()
            return JsonResponse({
                'action': 'unfollowed',
                'button_text': 'Follow',
                'followers_count': Follow.objects.filter(following=user_to_follow).count()
            })
        else:
            if profile_to_follow.is_private:
                # Create follow request
                follow_request, created = FollowRequest.objects.get_or_create(
                    from_user=request.user,
                    to_user=user_to_follow,
                    defaults={'status': 'pending'}
                )
                
                if created:
                    # Send notification
                    create_notification(
                        recipient=user_to_follow,
                        sender=request.user,
                        notification_type='follow_request',
                        message=f"{request.user.username} requested to follow you"
                    )
                
                return JsonResponse({
                    'action': 'requested',
                    'button_text': 'Requested',
                    'followers_count': Follow.objects.filter(following=user_to_follow).count()
                })
            else:
                # Follow directly
                Follow.objects.create(follower=request.user, following=user_to_follow)
                
                # Send notification
                create_notification(
                    recipient=user_to_follow,
                    sender=request.user,
                    notification_type='follow',
                    message=f"{request.user.username} started following you"
                )
                
                return JsonResponse({
                    'action': 'followed',
                    'button_text': 'Following',
                    'followers_count': Follow.objects.filter(following=user_to_follow).count()
                })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def follow_requests(request):
    """View and manage follow requests"""
    from .models import FollowRequest
    
    pending_requests = FollowRequest.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('from_user')
    
    return render(request, 'follow_requests.html', {
        'pending_requests': pending_requests
    })


@login_required
def handle_follow_request(request, request_id):
    """Accept or reject follow request"""
    if request.method == 'POST':
        from .models import FollowRequest
        from .utils import create_notification
        
        follow_request = get_object_or_404(
            FollowRequest,
            id=request_id,
            to_user=request.user,
            status='pending'
        )
        
        action = request.POST.get('action')
        
        if action == 'accept':
            if follow_request.accept():
                create_notification(
                    recipient=follow_request.from_user,
                    sender=request.user,
                    notification_type='follow',
                    message=f"{request.user.username} accepted your follow request"
                )
                messages.success(request, f'You accepted {follow_request.from_user.username}\'s follow request.')
        elif action == 'reject':
            if follow_request.reject():
                messages.success(request, f'You rejected {follow_request.from_user.username}\'s follow request.')
    
    return redirect('follow_requests')


@login_required
def followers_list(request, username):
    """List followers of a user"""
    user = get_object_or_404(User, username=username)
    from .models import Follow
    
    followers = Follow.objects.filter(following=user).select_related('follower')
    
    return render(request, 'followers_list.html', {
        'user': user,
        'followers': followers
    })


@login_required
def following_list(request, username):
    """List users that a user is following"""
    user = get_object_or_404(User, username=username)
    from .models import Follow
    
    following = Follow.objects.filter(follower=user).select_related('following')
    
    return render(request, 'following_list.html', {
        'user': user,
        'following': following
    })


# ====================
# DIRECT MESSAGING VIEWS
# ====================

@login_required
def conversations_list(request):
    """List all conversations for the user"""
    from .models import Conversation
    
    conversations = request.user.conversations.all().prefetch_related('participants')
    
    return render(request, 'conversations_list.html', {
        'conversations': conversations
    })


@login_required
def conversation_detail(request, conversation_id):
    """View conversation and send messages"""
    from .models import Conversation, DirectMessage
    from .forms import DirectMessageForm
    
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )
    
    # Mark messages as read
    unread_messages = conversation.messages.exclude(sender=request.user).exclude(read_by=request.user)
    for message in unread_messages:
        message.mark_as_read(request.user)
    
    messages_list = conversation.messages.all().select_related('sender').prefetch_related('read_by')
    
    if request.method == 'POST':
        form = DirectMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            
            # Determine message type
            if message.image:
                message.message_type = 'image'
            elif message.video:
                message.message_type = 'video'
            elif message.audio:
                message.message_type = 'audio'
            elif message.file:
                message.message_type = 'file'
            else:
                message.message_type = 'text'
            
            message.save()
            
            # Update conversation timestamp
            conversation.save()
            
            # Send notifications to other participants
            from .utils import create_notification
            for participant in conversation.participants.exclude(id=request.user.id):
                create_notification(
                    recipient=participant,
                    sender=request.user,
                    notification_type='direct_message',
                    message=f"{request.user.username} sent you a message",
                    direct_message=message
                )
            
            return redirect('conversation_detail', conversation_id=conversation.id)
    else:
        form = DirectMessageForm()
    
    return render(request, 'conversation_detail.html', {
        'conversation': conversation,
        'messages': messages_list,
        'form': form
    })


@login_required
def start_conversation(request):
    """Start a new conversation"""
    from .forms import ConversationForm
    from .utils import get_conversation_for_users
    from .models import Conversation
    
    if request.method == 'POST':
        try:
            # Get participants from form data
            participant_ids = request.POST.getlist('participants')
            
            if not participant_ids:
                messages.error(request, "Please select at least one participant.")
                return render(request, 'start_conversation.html', {
                    'form': ConversationForm(current_user=request.user)
                })
            
            # Get participant users
            participants = User.objects.filter(id__in=participant_ids)
            
            if len(participants) == 1:
                # One-on-one conversation
                conversation = get_conversation_for_users(request.user, participants[0])
            else:
                # Group conversation
                conversation = Conversation.objects.create(
                    is_group=True,
                    group_name=request.POST.get('group_name', '')
                )
                
                # Add participants
                conversation.participants.add(request.user)
                conversation.participants.add(*participants)
            
            return redirect('conversation_detail', conversation_id=conversation.id)
            
        except Exception as e:
            messages.error(request, f"Error creating conversation: {str(e)}")
    
    # GET request or error - show form
    form = ConversationForm(current_user=request.user)
    return render(request, 'start_conversation.html', {'form': form})


# ====================
# HASHTAG AND TRENDING VIEWS
# ====================

def hashtag_detail(request, hashtag_name):
    """View tweets with a specific hashtag"""
    from .models import Hashtag, TweetHashtag
    
    hashtag = get_object_or_404(Hashtag, name=hashtag_name.lower())
    
    # Get tweets with this hashtag
    tweet_relations = TweetHashtag.objects.filter(hashtag=hashtag).select_related('tweet__user')
    tweets = [relation.tweet for relation in tweet_relations]
    
    # Filter based on privacy and user permissions
    if request.user.is_authenticated:
        from .models import Follow, Block
        following = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        blocked_users = Block.objects.filter(blocker=request.user).values_list('blocked', flat=True)
        
        filtered_tweets = []
        for tweet in tweets:
            if tweet.user in blocked_users:
                continue
            if tweet.privacy == 'public' or tweet.user == request.user or tweet.user in following:
                filtered_tweets.append(tweet)
        tweets = filtered_tweets
    else:
        tweets = [tweet for tweet in tweets if tweet.privacy == 'public']
    
    return render(request, 'hashtag_detail.html', {
        'hashtag': hashtag,
        'tweets': tweets
    })


def trending_hashtags(request):
    """View trending hashtags"""
    from .utils import get_trending_hashtags
    
    trending = get_trending_hashtags(limit=20)
    
    return render(request, 'trending_hashtags.html', {
        'trending_hashtags': trending
    })


# ====================
# SEARCH VIEWS
# ====================

def search(request):
    """Main search view"""
    from .forms import SearchForm
    from .utils import search_users, search_tweets, search_hashtags
    
    form = SearchForm(request.GET or None)
    results = {
        'users': [],
        'tweets': [],
        'hashtags': [],
        'query': ''
    }
    
    if form.is_valid():
        query = form.cleaned_data['query']
        search_type = form.cleaned_data.get('search_type', 'general')
        
        results['query'] = query
        
        # Log search query
        from .models import SearchQuery, PopularSearch
        SearchQuery.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query=query,
            search_type=search_type
        )
        
        # Update popular searches
        popular_search, created = PopularSearch.objects.get_or_create(
            query=query,
            defaults={'search_count': 1}
        )
        if not created:
            popular_search.increment_count()
        
        if search_type == 'general' or search_type == 'users':
            results['users'] = search_users(query, limit=10)
        
        if search_type == 'general' or search_type == 'tweets':
            results['tweets'] = search_tweets(query, user=request.user, limit=20)
        
        if search_type == 'general' or search_type == 'hashtags':
            results['hashtags'] = search_hashtags(query, limit=10)
    
    return render(request, 'search_results.html', {
        'form': form,
        'results': results
    })


def advanced_search(request):
    """Advanced search with filters"""
    from .forms import AdvancedSearchForm
    from django.db.models import Q
    
    form = AdvancedSearchForm(request.GET or None)
    tweets = []
    
    if form.is_valid():
        query_filters = Q()
        
        # Text search
        if form.cleaned_data.get('query'):
            query_filters &= Q(text__icontains=form.cleaned_data['query'])
        
        # User search
        if form.cleaned_data.get('from_user'):
            query_filters &= Q(user__username__icontains=form.cleaned_data['from_user'])
        
        # Hashtag search
        if form.cleaned_data.get('hashtag'):
            hashtag_name = form.cleaned_data['hashtag'].lower()
            from .models import TweetHashtag
            hashtag_tweets = TweetHashtag.objects.filter(
                hashtag__name=hashtag_name
            ).values_list('tweet', flat=True)
            query_filters &= Q(id__in=hashtag_tweets)
        
        # Date filters
        if form.cleaned_data.get('date_from'):
            query_filters &= Q(created_at__date__gte=form.cleaned_data['date_from'])
        
        if form.cleaned_data.get('date_to'):
            query_filters &= Q(created_at__date__lte=form.cleaned_data['date_to'])
        
        # Media filter
        if form.cleaned_data.get('has_media'):
            query_filters &= ~Q(image='')
        
        # Minimum likes filter
        if form.cleaned_data.get('min_likes'):
            from django.db.models import Count
            tweets_with_likes = Tweet.objects.annotate(
                likes_count=Count('likes')
            ).filter(likes_count__gte=form.cleaned_data['min_likes']).values_list('id', flat=True)
            query_filters &= Q(id__in=tweets_with_likes)
        
        # Apply filters
        tweets = Tweet.objects.filter(query_filters)
        
        # Apply privacy filters
        if request.user.is_authenticated:
            from .models import Follow, Block
            following = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
            blocked_users = Block.objects.filter(blocker=request.user).values_list('blocked', flat=True)
            
            tweets = tweets.filter(
                Q(privacy='public') |
                Q(user=request.user) |
                Q(user__in=following, privacy='private')
            ).exclude(user__in=blocked_users)
        else:
            tweets = tweets.filter(privacy='public')
        
        tweets = tweets.select_related('user').prefetch_related('likes')[:50]
    
    return render(request, 'advanced_search.html', {
        'form': form,
        'tweets': tweets
    })


# ====================
# NOTIFICATION VIEWS
# ====================

@login_required
def notifications_list(request):
    """List all notifications for the user"""
    from .models import Notification
    
    # Get all notifications first (without slicing)
    all_notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'tweet__user', 'comment__user').order_by('-created_at')
    
    # Mark unread notifications as read BEFORE slicing
    unread_notifications = all_notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    # Now slice to get the first 50 notifications
    notifications = all_notifications[:50]
    
    return render(request, 'notifications_list.html', {
        'notifications': notifications
    })


@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    if request.method == 'POST':
        from .models import Notification
        
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )
        
        notification.mark_as_read()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def notifications_count(request):
    """Get unread notifications count (AJAX)"""
    from .utils import get_unread_notifications_count
    
    count = get_unread_notifications_count(request.user)
    
    return JsonResponse({'count': count})


# ====================
# BLOCK AND MUTE VIEWS
# ====================

@login_required
def block_user(request, username):
    """Block a user"""
    if request.method == 'POST':
        user_to_block = get_object_or_404(User, username=username)
        
        if request.user == user_to_block:
            return JsonResponse({'error': 'You cannot block yourself'}, status=400)
        
        from .models import Block, Follow
        
        # Create block relationship
        Block.objects.get_or_create(blocker=request.user, blocked=user_to_block)
        
        # Remove any follow relationships
        Follow.objects.filter(
            Q(follower=request.user, following=user_to_block) |
            Q(follower=user_to_block, following=request.user)
        ).delete()
        
        return JsonResponse({'success': True, 'message': f'You blocked {username}'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def unblock_user(request, username):
    """Unblock a user"""
    if request.method == 'POST':
        user_to_unblock = get_object_or_404(User, username=username)
        
        from .models import Block
        
        Block.objects.filter(blocker=request.user, blocked=user_to_unblock).delete()
        
        return JsonResponse({'success': True, 'message': f'You unblocked {username}'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def mute_user(request, username):
    """Mute a user"""
    if request.method == 'POST':
        user_to_mute = get_object_or_404(User, username=username)
        
        if request.user == user_to_mute:
            return JsonResponse({'error': 'You cannot mute yourself'}, status=400)
        
        from .models import Mute
        
        Mute.objects.get_or_create(muter=request.user, muted=user_to_mute)
        
        return JsonResponse({'success': True, 'message': f'You muted {username}'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def unmute_user(request, username):
    """Unmute a user"""
    if request.method == 'POST':
        user_to_unmute = get_object_or_404(User, username=username)
        
        from .models import Mute
        
        Mute.objects.filter(muter=request.user, muted=user_to_unmute).delete()
        
        return JsonResponse({'success': True, 'message': f'You unmuted {username}'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def blocked_users_list(request):
    """List blocked users"""
    from .models import Block
    
    blocked_users = Block.objects.filter(blocker=request.user).select_related('blocked')
    
    return render(request, 'blocked_users.html', {
        'blocked_users': blocked_users
    })


@login_required
def muted_users_list(request):
    """List muted users"""
    from .models import Mute
    
    muted_users = Mute.objects.filter(muter=request.user).select_related('muted')
    
    return render(request, 'muted_users.html', {
        'muted_users': muted_users
    })


# ====================
# ENHANCED FEED VIEW
# ====================

@login_required
def personalized_feed(request):
    """Enhanced personalized feed with better filtering"""
    from .utils import get_user_feed
    
    tweets = get_user_feed(request.user, limit=50)
    
    return render(request, 'personalized_feed.html', {
        'tweets': tweets
    })

def debug_features(request):
    """Debug view to test notifications and messages"""
    if not request.user.is_authenticated:
        return HttpResponse("Please log in first.")
    
    from .models import Notification, Conversation, DirectMessage
    from .templatetags.custom_filters import notification_badge, message_badge
    
    # Get counts
    notif_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    conv_count = Conversation.objects.filter(participants=request.user).count()
    
    # Get badge HTML
    notif_badge_html = notification_badge(request.user)
    msg_badge_html = message_badge(request.user)
    
    # Create test notification if none exist
    if notif_count == 0:
        from .utils import create_notification
        create_notification(
            recipient=request.user,
            sender=request.user,  # Self-notification for testing
            notification_type='test',
            message='Test notification created for debugging'
        )
        notif_count = 1
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Features - Twick</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>🔍 Debug Features - User: {request.user.username}</h1>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h3>🔔 Notifications</h3>
                        </div>
                        <div class="card-body">
                            <p><strong>Unread Count:</strong> {notif_count}</p>
                            <p><strong>Badge HTML:</strong> <code>{notif_badge_html}</code></p>
                            <p><strong>Visual Badge:</strong> 
                                <span class="position-relative">
                                    Notifications {notif_badge_html}
                                </span>
                            </p>
                            <a href="/notifications/" class="btn btn-primary">View Notifications</a>
                            <a href="/messages/start/" class="btn btn-outline-primary ms-2">Test Start Conversation</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h3>💬 Messages</h3>
                        </div>
                        <div class="card-body">
                            <p><strong>Conversation Count:</strong> {conv_count}</p>
                            <p><strong>Badge HTML:</strong> <code>{msg_badge_html}</code></p>
                            <p><strong>Visual Badge:</strong> 
                                <span class="position-relative">
                                    Messages {msg_badge_html}
                                </span>
                            </p>
                            <a href="/messages/" class="btn btn-primary">View Messages</a>
                            <a href="/messages/start/" class="btn btn-outline-primary ms-2">Test Start Conversation</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h3>🔗 Quick Links</h3>
                        </div>
                        <div class="card-body">
                            <a href="/" class="btn btn-outline-primary me-2">Home</a>
                            <a href="/feed/" class="btn btn-outline-primary me-2">Feed</a>
                            <a href="/trending/" class="btn btn-outline-primary me-2">Trending</a>
                            <a href="/search/" class="btn btn-outline-primary me-2">Search</a>
                            <a href="/notifications/" class="btn btn-outline-primary me-2">Notifications</a>
                            <a href="/messages/" class="btn btn-outline-primary me-2">Messages</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html)
