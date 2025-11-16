from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Tweet, Comment
from .utils import create_notification

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created"""
    if created:
        # Use get_or_create to prevent duplicates
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when User is saved"""
    try:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
        else:
            # Only create if it doesn't exist
            UserProfile.objects.get_or_create(user=instance)
    except Exception:
        # If there's any issue, silently pass to prevent crashes
        pass


# Notification signals for likes
@receiver(m2m_changed, sender=Tweet.likes.through)
def tweet_like_notification(sender, instance, action, pk_set, **kwargs):
    """Send notification when someone likes a tweet"""
    if action == 'post_add':
        for user_id in pk_set:
            if user_id != instance.user.id:  # Don't notify self
                try:
                    from django.contrib.auth.models import User
                    liker = User.objects.get(id=user_id)
                    create_notification(
                        recipient=instance.user,
                        sender=liker,
                        notification_type='like',
                        message=f"{liker.username} liked your tweet",
                        tweet=instance
                    )
                except User.DoesNotExist:
                    pass


@receiver(m2m_changed, sender=Comment.likes.through)
def comment_like_notification(sender, instance, action, pk_set, **kwargs):
    """Send notification when someone likes a comment"""
    if action == 'post_add':
        for user_id in pk_set:
            if user_id != instance.user.id:  # Don't notify self
                try:
                    from django.contrib.auth.models import User
                    liker = User.objects.get(id=user_id)
                    create_notification(
                        recipient=instance.user,
                        sender=liker,
                        notification_type='like',
                        message=f"{liker.username} liked your comment",
                        comment=instance
                    )
                except User.DoesNotExist:
                    pass


@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    """Send notification when someone comments on a tweet"""
    if created:
        # Don't notify if user is commenting on their own tweet
        if instance.user != instance.tweet.user:
            create_notification(
                recipient=instance.tweet.user,
                sender=instance.user,
                notification_type='comment',
                message=f"{instance.user.username} commented on your tweet",
                tweet=instance.tweet,
                comment=instance
            )


@receiver(post_save, sender=Tweet)
def reply_notification(sender, instance, created, **kwargs):
    """Send notification when someone replies to a tweet"""
    if created and instance.parent_tweet:
        # Don't notify if user is replying to their own tweet
        if instance.user != instance.parent_tweet.user:
            create_notification(
                recipient=instance.parent_tweet.user,
                sender=instance.user,
                notification_type='reply',
                message=f"{instance.user.username} replied to your tweet",
                tweet=instance.parent_tweet
            )
