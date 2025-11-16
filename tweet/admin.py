from django.contrib import admin
from .models import (
    Tweet, UserProfile, Comment, Follow, FollowRequest, Hashtag, TweetHashtag,
    TrendingHashtag, Conversation, DirectMessage, Notification, SearchQuery,
    PopularSearch, Mention, Block, Mute
)

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'privacy', 'parent_tweet', 'created_at', 'get_likes_count', 'get_replies_count')
    list_filter = ('created_at', 'privacy', 'user')
    search_fields = ('text', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_likes_count(self, obj):
        return obj.get_likes_count()
    get_likes_count.short_description = 'Likes'
    
    def get_replies_count(self, obj):
        return obj.get_replies_count()
    get_replies_count.short_description = 'Replies'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'tweet', 'text', 'parent_comment', 'created_at', 'get_likes_count')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'user__username', 'tweet__text')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_likes_count(self, obj):
        return obj.get_likes_count()
    get_likes_count.short_description = 'Likes'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'birth_date', 'is_private', 'get_followers_count')
    list_filter = ('birth_date', 'is_private')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    filter_horizontal = ('followers',)
    
    def get_followers_count(self, obj):
        return obj.get_followers_count()
    get_followers_count.short_description = 'Followers'


# Following System Admin
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    readonly_fields = ('created_at',)


@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['accept_requests', 'reject_requests']
    
    def accept_requests(self, request, queryset):
        for follow_request in queryset.filter(status='pending'):
            follow_request.accept()
        self.message_user(request, f"Accepted {queryset.count()} follow requests.")
    accept_requests.short_description = "Accept selected follow requests"
    
    def reject_requests(self, request, queryset):
        for follow_request in queryset.filter(status='pending'):
            follow_request.reject()
        self.message_user(request, f"Rejected {queryset.count()} follow requests.")
    reject_requests.short_description = "Reject selected follow requests"


# Hashtag System Admin
@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name', 'tweet_count', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'tweet_count')
    ordering = ('-tweet_count', '-created_at')


@admin.register(TweetHashtag)
class TweetHashtagAdmin(admin.ModelAdmin):
    list_display = ('tweet', 'hashtag', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tweet__text', 'hashtag__name')
    readonly_fields = ('created_at',)


@admin.register(TrendingHashtag)
class TrendingHashtagAdmin(admin.ModelAdmin):
    list_display = ('hashtag', 'trend_score', 'tweets_last_24h', 'tweets_last_week', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('hashtag__name',)
    readonly_fields = ('last_updated',)
    ordering = ('-trend_score', '-tweets_last_24h')


# Direct Message System Admin
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_group', 'created_at', 'updated_at', 'get_participants_count')
    list_filter = ('is_group', 'created_at')
    search_fields = ('group_name',)
    filter_horizontal = ('participants',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    get_participants_count.short_description = 'Participants'


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'message_type', 'content', 'sent_at', 'is_edited')
    list_filter = ('message_type', 'sent_at', 'is_edited')
    search_fields = ('sender__username', 'content')
    readonly_fields = ('sent_at', 'edited_at')
    filter_horizontal = ('read_by',)


# Notification System Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'message', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'message')
    readonly_fields = ('created_at',)
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"Marked {queryset.count()} notifications as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"Marked {queryset.count()} notifications as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"


# Search System Admin
@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('query', 'search_type', 'user', 'results_count', 'created_at')
    list_filter = ('search_type', 'created_at')
    search_fields = ('query', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = ('query', 'search_count', 'last_searched')
    search_fields = ('query',)
    readonly_fields = ('last_searched',)
    ordering = ('-search_count', '-last_searched')


# Mention System Admin
@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ('mentioned_user', 'tweet', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('mentioned_user__username', 'tweet__text')
    readonly_fields = ('created_at',)


# Block and Mute System Admin
@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('blocker__username', 'blocked__username')
    readonly_fields = ('created_at',)


@admin.register(Mute)
class MuteAdmin(admin.ModelAdmin):
    list_display = ('muter', 'muted', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('muter__username', 'muted__username')
    readonly_fields = ('created_at',)