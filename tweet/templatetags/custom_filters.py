from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
import re

register = template.Library()

@register.filter
def highlight_hashtags(text):
    """Convert hashtags to clickable links"""
    def replace_hashtag(match):
        hashtag = match.group(1)
        url = reverse('hashtag_detail', kwargs={'hashtag_name': hashtag})
        return f'<a href="{url}" class="text-primary text-decoration-none">#{hashtag}</a>'
    
    return mark_safe(re.sub(r'#(\w+)', replace_hashtag, text))

@register.filter
def highlight_mentions(text):
    """Convert mentions to clickable links"""
    def replace_mention(match):
        username = match.group(1)
        url = reverse('user_profile', kwargs={'username': username})
        return f'<a href="{url}" class="text-info text-decoration-none">@{username}</a>'
    
    return mark_safe(re.sub(r'@(\w+)', replace_mention, text))

@register.filter
def format_tweet_text(text):
    """Apply both hashtag and mention highlighting"""
    text = highlight_hashtags(text)
    text = highlight_mentions(text)
    return text

@register.filter
def unread_notifications_count(user):
    """Get unread notifications count for a user"""
    if not user.is_authenticated:
        return 0
    
    from ..models import Notification
    return Notification.objects.filter(recipient=user, is_read=False).count()

@register.filter
def unread_messages_count(user):
    """Get unread messages count for a user"""
    if not user.is_authenticated:
        return 0
    
    from ..models import DirectMessage
    return DirectMessage.objects.filter(
        conversation__participants=user
    ).exclude(
        sender=user
    ).exclude(
        read_by=user
    ).count()

@register.filter
def is_following(user, target_user):
    """Check if user is following target_user"""
    if not user.is_authenticated:
        return False
    
    from ..models import Follow
    return Follow.objects.filter(follower=user, following=target_user).exists()

@register.filter
def follow_status(user, target_user):
    """Get follow status between users"""
    if not user.is_authenticated or user == target_user:
        return 'self'
    
    from ..models import Follow, FollowRequest
    
    # Check if already following
    if Follow.objects.filter(follower=user, following=target_user).exists():
        return 'following'
    
    # Check if follow request is pending
    if FollowRequest.objects.filter(from_user=user, to_user=target_user, status='pending').exists():
        return 'requested'
    
    return 'not_following'

@register.filter
def is_blocked(user, target_user):
    """Check if user has blocked target_user"""
    if not user.is_authenticated:
        return False
    
    from ..models import Block
    return Block.objects.filter(blocker=user, blocked=target_user).exists()

@register.filter
def is_muted(user, target_user):
    """Check if user has muted target_user"""
    if not user.is_authenticated:
        return False
    
    from ..models import Mute
    return Mute.objects.filter(muter=user, muted=target_user).exists()

@register.simple_tag
def trending_hashtags(limit=5):
    """Get trending hashtags"""
    from ..models import TrendingHashtag
    return TrendingHashtag.objects.select_related('hashtag')[:limit]

@register.simple_tag
def popular_searches(limit=5):
    """Get popular search terms"""
    from ..models import PopularSearch
    return PopularSearch.objects.all()[:limit]

# Badge components removed - using simple_tag versions below

@register.simple_tag
def notification_badge(user):
    """Display notification badge if user has unread notifications"""
    if not user.is_authenticated:
        return ""
    
    try:
        from ..models import Notification
        count = Notification.objects.filter(recipient=user, is_read=False).count()
        if count > 0:
            return mark_safe(f'<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">{count}</span>')
    except Exception:
        pass
    return ""

@register.simple_tag
def message_badge(user):
    """Display message badge if user has unread messages"""
    if not user.is_authenticated:
        return ""
    
    try:
        from ..models import Conversation, DirectMessage
        unread_count = 0
        
        # Get all conversations for the user
        conversations = Conversation.objects.filter(participants=user)
        
        for conversation in conversations:
            # Count unread messages in this conversation
            unread_messages = DirectMessage.objects.filter(
                conversation=conversation
            ).exclude(sender=user).exclude(read_by=user)
            
            if unread_messages.exists():
                unread_count += 1
        
        if unread_count > 0:
            return mark_safe(f'<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">{unread_count}</span>')
    except Exception:
        pass
    
    return ""
