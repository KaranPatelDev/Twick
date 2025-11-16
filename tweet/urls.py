from django.urls import path
from . import views

urlpatterns = [
    # Core Tweet URLs
    path("", views.home, name="home"),
    path("tweets/", views.tweet_list, name="tweet_list"),
    path("create/", views.tweet_create, name="tweet_create"),
    path("tweet/<int:tweet_id>/", views.tweet_detail, name="tweet_detail"),
    path("tweet/<int:tweet_id>/edit/", views.tweet_edit, name="tweet_edit"),
    path("tweet/<int:tweet_id>/delete/", views.tweet_delete, name="tweet_delete"),
    path("tweet/<int:tweet_id>/like/", views.like_tweet, name="like_tweet"),
    path("tweet/<int:tweet_id>/reply/", views.tweet_reply, name="tweet_reply"),
    path("tweet/<int:tweet_id>/comment/", views.add_comment, name="add_comment"),
    
    # Comment URLs
    path("comment/<int:comment_id>/like/", views.like_comment, name="like_comment"),
    path("comment/<int:comment_id>/reply/", views.reply_to_comment, name="reply_to_comment"),
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    
    # User Profile URLs
    path("register/", views.register, name="register"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.user_profile, name="user_profile"),
    path("profile/<str:username>/follow/", views.follow_user, name="follow_user"),
    
    # Enhanced Following System URLs
    path("api/follow/<str:username>/", views.follow_user_new, name="follow_user_new"),
    path("follow-requests/", views.follow_requests, name="follow_requests"),
    path("follow-request/<int:request_id>/handle/", views.handle_follow_request, name="handle_follow_request"),
    path("profile/<str:username>/followers/", views.followers_list, name="followers_list"),
    path("profile/<str:username>/following/", views.following_list, name="following_list"),
    
    # Direct Messaging URLs
    path("messages/", views.conversations_list, name="conversations_list"),
    path("messages/<int:conversation_id>/", views.conversation_detail, name="conversation_detail"),
    path("messages/start/", views.start_conversation, name="start_conversation"),
    
    # Hashtag URLs
    path("hashtag/<str:hashtag_name>/", views.hashtag_detail, name="hashtag_detail"),
    path("trending/", views.trending_hashtags, name="trending_hashtags"),
    
    # Search URLs
    path("search/", views.search, name="search"),
    path("search/advanced/", views.advanced_search, name="advanced_search"),
    
    # Notification URLs
    path("notifications/", views.notifications_list, name="notifications_list"),
    path("api/notifications/<int:notification_id>/read/", views.mark_notification_read, name="mark_notification_read"),
    path("api/notifications/count/", views.notifications_count, name="notifications_count"),
    
    # Block and Mute URLs
    path("api/block/<str:username>/", views.block_user, name="block_user"),
    path("api/unblock/<str:username>/", views.unblock_user, name="unblock_user"),
    path("api/mute/<str:username>/", views.mute_user, name="mute_user"),
    path("api/unmute/<str:username>/", views.unmute_user, name="unmute_user"),
    path("blocked-users/", views.blocked_users_list, name="blocked_users_list"),
    path("muted-users/", views.muted_users_list, name="muted_users_list"),
    
    # Enhanced Feed
    path("feed/", views.personalized_feed, name="personalized_feed"),
    
    # Debug features
    path("debug/", views.debug_features, name="debug_features"),
]