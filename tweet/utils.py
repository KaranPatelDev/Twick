from django.contrib.auth.models import User
from django.db import models
from .models import Notification


def create_notification(recipient, sender, notification_type, message, tweet=None, comment=None, direct_message=None):
    """
    Helper function to create notifications
    """
    # Don't create notification if recipient is the same as sender
    if recipient == sender:
        return None
    
    # Don't create notification if recipient has blocked the sender
    from .models import Block
    if Block.objects.filter(blocker=recipient, blocked=sender).exists():
        return None
    
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        message=message,
        tweet=tweet,
        comment=comment,
        direct_message=direct_message
    )
    
    return notification


def get_trending_hashtags(limit=10):
    """
    Get trending hashtags based on recent activity
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import TrendingHashtag
    
    # Update trending scores before returning
    update_trending_hashtags()
    
    return TrendingHashtag.objects.select_related('hashtag')[:limit]


def update_trending_hashtags():
    """
    Update trending hashtag scores based on recent activity
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count
    from .models import Hashtag, TrendingHashtag, TweetHashtag
    
    now = timezone.now()
    twenty_four_hours_ago = now - timedelta(hours=24)
    one_week_ago = now - timedelta(days=7)
    
    # Get hashtags with recent activity
    hashtags_with_activity = Hashtag.objects.annotate(
        tweets_24h=Count(
            'tweet_relations',
            filter=models.Q(tweet_relations__created_at__gte=twenty_four_hours_ago)
        ),
        tweets_week=Count(
            'tweet_relations',
            filter=models.Q(tweet_relations__created_at__gte=one_week_ago)
        )
    ).filter(tweets_24h__gt=0)
    
    for hashtag in hashtags_with_activity:
        # Calculate trend score (weighted by recency)
        trend_score = (hashtag.tweets_24h * 10) + (hashtag.tweets_week * 1)
        
        trending_hashtag, created = TrendingHashtag.objects.get_or_create(
            hashtag=hashtag,
            defaults={
                'trend_score': trend_score,
                'tweets_last_24h': hashtag.tweets_24h,
                'tweets_last_week': hashtag.tweets_week,
            }
        )
        
        if not created:
            trending_hashtag.trend_score = trend_score
            trending_hashtag.tweets_last_24h = hashtag.tweets_24h
            trending_hashtag.tweets_last_week = hashtag.tweets_week
            trending_hashtag.save()


def search_users(query, limit=20):
    """
    Search for users by username, first name, or last name
    """
    from django.db.models import Q
    
    return User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).select_related('userprofile')[:limit]


def search_tweets(query, user=None, limit=50):
    """
    Search for tweets containing the query text
    """
    from django.db.models import Q
    from .models import Tweet, Block
    
    tweets = Tweet.objects.filter(text__icontains=query)
    
    # If user is provided, filter out blocked users and private tweets
    if user:
        # Get blocked users
        blocked_users = Block.objects.filter(blocker=user).values_list('blocked', flat=True)
        blocking_users = Block.objects.filter(blocked=user).values_list('blocker', flat=True)
        
        tweets = tweets.exclude(
            Q(user__in=blocked_users) | Q(user__in=blocking_users)
        )
        
        # Filter private tweets (only show if user follows the author)
        from .models import Follow
        following = Follow.objects.filter(follower=user).values_list('following', flat=True)
        
        tweets = tweets.filter(
            Q(privacy='public') |
            Q(user=user) |  # User's own tweets
            Q(user__in=following, privacy='private')  # Private tweets from followed users
        )
    else:
        # For anonymous users, only show public tweets
        tweets = tweets.filter(privacy='public')
    
    return tweets.select_related('user').prefetch_related('likes')[:limit]


def search_hashtags(query, limit=20):
    """
    Search for hashtags by name
    """
    from .models import Hashtag
    
    return Hashtag.objects.filter(
        name__icontains=query
    ).order_by('-tweet_count')[:limit]


def get_user_feed(user, limit=50):
    """
    Get personalized feed for a user (tweets from followed users)
    """
    from django.db.models import Q
    from .models import Tweet, Follow, Block, Mute
    
    # Get users that this user follows
    following = Follow.objects.filter(follower=user).values_list('following', flat=True)
    
    # Get blocked and muted users to exclude
    blocked_users = Block.objects.filter(blocker=user).values_list('blocked', flat=True)
    muted_users = Mute.objects.filter(muter=user).values_list('muted', flat=True)
    
    # Get tweets from followed users + user's own tweets
    feed_tweets = Tweet.objects.filter(
        Q(user__in=following) | Q(user=user)
    ).exclude(
        Q(user__in=blocked_users) | Q(user__in=muted_users)
    ).filter(
        Q(privacy='public') | Q(user=user) | Q(user__in=following)
    ).select_related('user').prefetch_related('likes', 'hashtag_relations__hashtag')
    
    return feed_tweets[:limit]


def get_unread_notifications_count(user):
    """
    Get count of unread notifications for a user
    """
    return Notification.objects.filter(recipient=user, is_read=False).count()


def mark_all_notifications_read(user):
    """
    Mark all notifications as read for a user
    """
    return Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)


def get_conversation_for_users(user1, user2):
    """
    Get or create a conversation between two users
    """
    from .models import Conversation
    
    # Try to find existing conversation
    conversation = Conversation.objects.filter(
        participants=user1,
        is_group=False
    ).filter(
        participants=user2
    ).first()
    
    if not conversation:
        # Create new conversation
        conversation = Conversation.objects.create(is_group=False)
        conversation.participants.add(user1, user2)
    
    return conversation
