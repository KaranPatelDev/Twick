from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import re

# Create your models here.
class Tweet(models.Model):
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=280)
    image = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_tweets', blank=True)
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')
    
    # Reply functionality
    parent_tweet = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.text[:50]}'
    
    def get_likes_count(self):
        return self.likes.count()
    
    def get_replies_count(self):
        return self.replies.count()
    
    def is_reply(self):
        return self.parent_tweet is not None
    
    def get_thread_tweets(self):
        """Get all tweets in this thread (parent + all replies)"""
        if self.parent_tweet:
            # If this is a reply, get the parent and all its replies
            parent = self.parent_tweet
            return Tweet.objects.filter(
                models.Q(id=parent.id) | models.Q(parent_tweet=parent)
            ).order_by('created_at')
        else:
            # If this is a parent tweet, get it and all its replies
            return Tweet.objects.filter(
                models.Q(id=self.id) | models.Q(parent_tweet=self)
            ).order_by('created_at')
    
    def extract_hashtags(self):
        """Extract hashtags from tweet text"""
        hashtag_pattern = r'#(\w+)'
        return re.findall(hashtag_pattern, self.text, re.IGNORECASE)
    
    def extract_mentions(self):
        """Extract user mentions from tweet text"""
        mention_pattern = r'@(\w+)'
        return re.findall(mention_pattern, self.text, re.IGNORECASE)
    
    def save(self, *args, **kwargs):
        """Override save to handle hashtags and mentions"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Process hashtags
            hashtags = self.extract_hashtags()
            for hashtag_name in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(
                    name=hashtag_name.lower()
                )
                TweetHashtag.objects.get_or_create(
                    tweet=self,
                    hashtag=hashtag
                )
                hashtag.increment_count()
            
            # Process mentions
            mentions = self.extract_mentions()
            for username in mentions:
                try:
                    mentioned_user = User.objects.get(username=username)
                    Mention.objects.get_or_create(
                        tweet=self,
                        mentioned_user=mentioned_user
                    )
                    # Create notification for mention
                    # Import here to avoid circular imports
                    if mentioned_user != self.user:  # Don't notify self
                        # We'll handle this in signals instead
                        pass
                except User.DoesNotExist:
                    pass
    
    def get_hashtags(self):
        """Get all hashtags for this tweet"""
        return [relation.hashtag for relation in self.hashtag_relations.all()]


class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    
    # Reply to comment functionality
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.user.username} commented: {self.text[:30]}'
    
    def get_likes_count(self):
        return self.likes.count()
    
    def is_reply(self):
        return self.parent_comment is not None


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=160, blank=True, help_text="Tell people a little about yourself")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Profile picture")
    cover_photo = models.ImageField(upload_to='covers/', blank=True, null=True, help_text="Cover photo")
    birth_date = models.DateField(blank=True, null=True, help_text="Your birth date")
    location = models.CharField(max_length=50, blank=True, help_text="Where you're from")
    website = models.URLField(blank=True, help_text="Your website or portfolio")
    
    # Social media links
    twitter_handle = models.CharField(max_length=50, blank=True, help_text="Twitter username (without @)")
    github_username = models.CharField(max_length=50, blank=True, help_text="GitHub username")
    linkedin_profile = models.URLField(blank=True, help_text="LinkedIn profile URL")
    
    # Professional info
    job_title = models.CharField(max_length=100, blank=True, help_text="Your current job title")
    company = models.CharField(max_length=100, blank=True, help_text="Company you work for")
    
    # Privacy and verification
    is_private = models.BooleanField(default=False, help_text="Make profile private")
    is_verified = models.BooleanField(default=False, help_text="Verified account")
    
    # Social connections
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    
    # Profile customization
    theme_color = models.CharField(max_length=7, default='#1DA1F2', help_text="Profile theme color")
    show_birth_date = models.BooleanField(default=False, help_text="Show birth date publicly")
    show_email = models.BooleanField(default=False, help_text="Show email publicly")
    
    # Stats
    profile_views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_followers_count(self):
        return self.followers.count()
    
    def get_following_count(self):
        return self.user.following.count()
    
    def get_tweets_count(self):
        return Tweet.objects.filter(user=self.user).count()
    
    def get_total_likes_received(self):
        return sum(tweet.get_likes_count() for tweet in Tweet.objects.filter(user=self.user))
    
    def get_display_name(self):
        return self.user.get_full_name() or self.user.username
    
    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields_to_check = ['bio', 'location', 'website', 'avatar', 'job_title']
        completed_fields = sum(1 for field in fields_to_check if getattr(self, field))
        return int((completed_fields / len(fields_to_check)) * 100)
    
    def increment_profile_views(self):
        """Increment profile view count"""
        self.profile_views = models.F('profile_views') + 1
        self.save(update_fields=['profile_views'])
    
    @property
    def age(self):
        """Calculate age from birth date"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None


# 1. FOLLOWING/FOLLOWERS SYSTEM
class Follow(models.Model):
    """Model to handle follow relationships between users"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class FollowRequest(models.Model):
    """Model for follow requests to private accounts"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_follow_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_follow_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} requests to follow {self.to_user.username}"
    
    def accept(self):
        """Accept the follow request and create follow relationship"""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            Follow.objects.get_or_create(
                follower=self.from_user,
                following=self.to_user
            )
            return True
        return False
    
    def reject(self):
        """Reject the follow request"""
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
            return True
        return False


# 2. HASHTAG SYSTEM
class Hashtag(models.Model):
    """Model for hashtags"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tweet_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-tweet_count', '-created_at']
    
    def __str__(self):
        return f"#{self.name}"
    
    def increment_count(self):
        """Increment tweet count for this hashtag"""
        self.tweet_count = models.F('tweet_count') + 1
        self.save(update_fields=['tweet_count'])
    
    def decrement_count(self):
        """Decrement tweet count for this hashtag"""
        if self.tweet_count > 0:
            self.tweet_count = models.F('tweet_count') - 1
            self.save(update_fields=['tweet_count'])


class TweetHashtag(models.Model):
    """Junction table for tweets and hashtags"""
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='hashtag_relations')
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name='tweet_relations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('tweet', 'hashtag')
    
    def __str__(self):
        return f"{self.tweet.user.username}'s tweet with #{self.hashtag.name}"


class TrendingHashtag(models.Model):
    """Model to track trending hashtags"""
    hashtag = models.OneToOneField(Hashtag, on_delete=models.CASCADE)
    trend_score = models.FloatField(default=0.0)
    tweets_last_24h = models.PositiveIntegerField(default=0)
    tweets_last_week = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-trend_score', '-tweets_last_24h']
    
    def __str__(self):
        return f"Trending: #{self.hashtag.name} (Score: {self.trend_score})"


# 3. DIRECT MESSAGING SYSTEM
class Conversation(models.Model):
    """Model for conversations between users"""
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_group = models.BooleanField(default=False)
    group_name = models.CharField(max_length=100, blank=True, null=True)
    group_avatar = models.ImageField(upload_to='group_avatars/', blank=True, null=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.is_group:
            return f"Group: {self.group_name or 'Unnamed Group'}"
        participants = list(self.participants.all()[:2])
        if len(participants) >= 2:
            return f"Chat: {participants[0].username} & {participants[1].username}"
        return f"Chat: {participants[0].username if participants else 'Empty'}"
    
    def get_last_message(self):
        """Get the last message in this conversation"""
        return self.messages.first()
    
    def get_unread_count(self, user):
        """Get unread message count for a specific user"""
        return self.messages.filter(
            read_by__lt=models.F('id'),
            sender__ne=user
        ).count()


class DirectMessage(models.Model):
    """Model for direct messages"""
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('file', 'File'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(max_length=1000, blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    
    # Media attachments
    image = models.ImageField(upload_to='dm_images/', blank=True, null=True)
    video = models.FileField(upload_to='dm_videos/', blank=True, null=True)
    audio = models.FileField(upload_to='dm_audio/', blank=True, null=True)
    file = models.FileField(upload_to='dm_files/', blank=True, null=True)
    
    # Message status
    sent_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    
    # Reply functionality
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50] if self.content else f'[{self.message_type}]'}"
    
    def mark_as_read(self, user):
        """Mark message as read by a user"""
        self.read_by.add(user)
    
    def is_read_by(self, user):
        """Check if message is read by a user"""
        return self.read_by.filter(id=user.id).exists()


# 4. NOTIFICATION SYSTEM
class Notification(models.Model):
    """Model for real-time notifications"""
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('reply', 'Reply'),
        ('follow', 'Follow'),
        ('follow_request', 'Follow Request'),
        ('mention', 'Mention'),
        ('direct_message', 'Direct Message'),
        ('retweet', 'Retweet'),
        ('quote_tweet', 'Quote Tweet'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField(max_length=200)
    
    # Related objects
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    direct_message = models.ForeignKey(DirectMessage, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:50]}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])


# 5. SEARCH SYSTEM
class SearchQuery(models.Model):
    """Model to track search queries for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    query = models.CharField(max_length=200)
    search_type = models.CharField(max_length=20, choices=[
        ('general', 'General'),
        ('users', 'Users'),
        ('hashtags', 'Hashtags'),
        ('tweets', 'Tweets'),
    ], default='general')
    results_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Search: '{self.query}' by {self.user.username if self.user else 'Anonymous'}"


class PopularSearch(models.Model):
    """Model for popular/trending search terms"""
    query = models.CharField(max_length=200, unique=True)
    search_count = models.PositiveIntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-search_count', '-last_searched']
    
    def __str__(self):
        return f"Popular: '{self.query}' ({self.search_count} searches)"
    
    def increment_count(self):
        """Increment search count"""
        self.search_count = models.F('search_count') + 1
        self.save(update_fields=['search_count', 'last_searched'])


# 6. USER MENTION SYSTEM
class Mention(models.Model):
    """Model for user mentions in tweets"""
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='mentions')
    mentioned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentioned_in')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('tweet', 'mentioned_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"@{self.mentioned_user.username} mentioned in {self.tweet.user.username}'s tweet"


# 7. BLOCK AND MUTE SYSTEM
class Block(models.Model):
    """Model for blocking users"""
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('blocker', 'blocked')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"


class Mute(models.Model):
    """Model for muting users"""
    muter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='muting')
    muted = models.ForeignKey(User, on_delete=models.CASCADE, related_name='muted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('muter', 'muted')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.muter.username} muted {self.muted.username}"