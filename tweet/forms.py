from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Tweet, UserProfile, Comment, DirectMessage, Conversation, DirectMessage, Conversation

class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['text', 'image', 'privacy']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "What's happening?",
                'rows': 3,
                'maxlength': 280
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'privacy': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text or not text.strip():
            raise forms.ValidationError("Tweet text cannot be empty.")
        if len(text) > 280:
            raise forms.ValidationError("Tweet must be 280 characters or less.")
        return text.strip()
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Only validate newly uploaded files, not existing ImageFieldFile objects
            if hasattr(image, 'content_type'):
                # Check file size (limit to 5MB)
                if image.size > 5 * 1024 * 1024:
                    raise forms.ValidationError("Image file too large. Please keep it under 5MB.")
                # Check file type
                if not image.content_type.startswith('image/'):
                    raise forms.ValidationError("Please upload a valid image file.")
        return image


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['text', 'image']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "Tweet your reply...",
                'rows': 2,
                'maxlength': 280
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text or not text.strip():
            raise forms.ValidationError("Reply text cannot be empty.")
        if len(text) > 280:
            raise forms.ValidationError("Reply must be 280 characters or less.")
        return text.strip()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "Write a comment...",
                'rows': 2,
                'maxlength': 280
            })
        }
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text or not text.strip():
            raise forms.ValidationError("Comment text cannot be empty.")
        if len(text) > 280:
            raise forms.ValidationError("Comment must be 280 characters or less.")
        return text.strip()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'avatar', 'cover_photo', 'birth_date', 'location', 'website',
            'twitter_handle', 'github_username', 'linkedin_profile',
            'job_title', 'company', 'theme_color', 'show_birth_date', 'show_email', 'is_private'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': 160,
                'placeholder': 'Tell us about yourself... (160 characters max)'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'cover_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'twitter_handle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'your_twitter_handle'
            }),
            'github_username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'your-github-username'
            }),
            'linkedin_profile': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/your-profile'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Software Developer, Designer, etc.'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name'
            }),
            'theme_color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'show_birth_date': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'bio': 'Bio',
            'avatar': 'Profile Picture',
            'cover_photo': 'Cover Photo',
            'birth_date': 'Birth Date',
            'location': 'Location',
            'website': 'Website',
            'twitter_handle': 'Twitter Handle',
            'github_username': 'GitHub Username',
            'linkedin_profile': 'LinkedIn Profile',
            'job_title': 'Job Title',
            'company': 'Company',
            'theme_color': 'Theme Color',
            'show_birth_date': 'Show Birth Date Publicly',
            'show_email': 'Show Email Publicly',
            'is_private': 'Private Profile',
        }
        help_texts = {
            'avatar': 'Square images work best (max 2MB)',
            'cover_photo': 'Recommended size: 1500x500 pixels (max 5MB)',
            'birth_date': 'Used to calculate your age',
            'twitter_handle': 'Without the @ symbol',
            'github_username': 'Your GitHub username',
            'theme_color': 'Choose your profile theme color',
            'show_birth_date': 'Display your age on your profile',
            'show_email': 'Make your email visible to other users',
            'is_private': 'Only followers can see your tweets when private',
        }
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Only validate newly uploaded files, not existing ImageFieldFile objects
            if hasattr(avatar, 'content_type'):
                if avatar.size > 2 * 1024 * 1024:  # 2MB
                    raise forms.ValidationError("Avatar image too large. Please keep it under 2MB.")
                if not avatar.content_type.startswith('image/'):
                    raise forms.ValidationError("Please upload a valid image file.")
        return avatar
    
    def clean_cover_photo(self):
        cover_photo = self.cleaned_data.get('cover_photo')
        if cover_photo:
            # Only validate newly uploaded files, not existing ImageFieldFile objects
            if hasattr(cover_photo, 'content_type'):
                if cover_photo.size > 5 * 1024 * 1024:  # 5MB
                    raise forms.ValidationError("Cover photo too large. Please keep it under 5MB.")
                if not cover_photo.content_type.startswith('image/'):
                    raise forms.ValidationError("Please upload a valid image file.")
        return cover_photo
    
    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if bio and len(bio) > 160:
            raise forms.ValidationError("Bio must be 160 characters or less.")
        return bio
    
    def clean_twitter_handle(self):
        handle = self.cleaned_data.get('twitter_handle')
        if handle:
            # Remove @ if user includes it
            handle = handle.lstrip('@')
            if not handle.replace('_', '').replace('-', '').isalnum():
                raise forms.ValidationError("Twitter handle can only contain letters, numbers, underscores, and hyphens.")
        return handle
    
    def clean_github_username(self):
        username = self.cleaned_data.get('github_username')
        if username:
            if not username.replace('-', '').replace('_', '').isalnum():
                raise forms.ValidationError("GitHub username can only contain letters, numbers, underscores, and hyphens.")
        return username


# DIRECT MESSAGING FORMS
class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['content', 'image', 'video', 'audio', 'file', 'reply_to']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your message...',
                'rows': 2,
                'maxlength': 1000,
                'style': 'border-radius: 25px; resize: none;'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
            'audio': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'reply_to': forms.HiddenInput()
        }
    
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        audio = cleaned_data.get('audio')
        file_upload = cleaned_data.get('file')
        
        # At least one field must be filled
        if not any([content, image, video, audio, file_upload]):
            raise forms.ValidationError("Please provide a message or attach a file.")
        
        return cleaned_data
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content and len(content) > 1000:
            raise forms.ValidationError("Message must be 1000 characters or less.")
        return content
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if hasattr(image, 'content_type'):
                if image.size > 10 * 1024 * 1024:  # 10MB
                    raise forms.ValidationError("Image file too large. Please keep it under 10MB.")
                if not image.content_type.startswith('image/'):
                    raise forms.ValidationError("Please upload a valid image file.")
        return image
    
    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            if hasattr(video, 'content_type'):
                if video.size > 100 * 1024 * 1024:  # 100MB
                    raise forms.ValidationError("Video file too large. Please keep it under 100MB.")
                allowed_types = ['video/mp4', 'video/webm', 'video/avi', 'video/mov']
                if video.content_type not in allowed_types:
                    raise forms.ValidationError("Please upload a valid video file (MP4, WebM, AVI, MOV).")
        return video
    
    def clean_audio(self):
        audio = self.cleaned_data.get('audio')
        if audio:
            if hasattr(audio, 'content_type'):
                if audio.size > 50 * 1024 * 1024:  # 50MB
                    raise forms.ValidationError("Audio file too large. Please keep it under 50MB.")
                allowed_types = ['audio/mp3', 'audio/wav', 'audio/ogg', 'audio/m4a']
                if audio.content_type not in allowed_types:
                    raise forms.ValidationError("Please upload a valid audio file (MP3, WAV, OGG, M4A).")
        return audio
    
    def clean_file(self):
        file_upload = self.cleaned_data.get('file')
        if file_upload:
            if hasattr(file_upload, 'size'):
                if file_upload.size > 25 * 1024 * 1024:  # 25MB
                    raise forms.ValidationError("File too large. Please keep it under 25MB.")
        return file_upload


class ConversationForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.MultipleHiddenInput(),  # We'll handle this manually in template
        required=True
    )
    
    class Meta:
        model = Conversation
        fields = ['group_name', 'group_avatar', 'participants']
        widgets = {
            'group_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter group name...'
            }),
            'group_avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        if current_user:
            # Exclude current user from participants list
            self.fields['participants'].queryset = User.objects.exclude(id=current_user.id)
    
    def clean_participants(self):
        participants = self.cleaned_data.get('participants')
        if len(participants) < 1:
            raise forms.ValidationError("Please select at least one participant.")
        if len(participants) > 50:  # Limit group size
            raise forms.ValidationError("Group cannot have more than 50 participants.")
        return participants


# SEARCH FORMS
class SearchForm(forms.Form):
    SEARCH_TYPE_CHOICES = [
        ('general', 'All'),
        ('users', 'Users'),
        ('tweets', 'Tweets'),
        ('hashtags', 'Hashtags'),
    ]
    
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for tweets, users, hashtags...',
            'autocomplete': 'off'
        })
    )
    
    search_type = forms.ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    def clean_query(self):
        query = self.cleaned_data.get('query')
        if not query or not query.strip():
            raise forms.ValidationError("Please enter a search term.")
        if len(query) < 2:
            raise forms.ValidationError("Search term must be at least 2 characters long.")
        return query.strip()


class AdvancedSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter keywords...'
        })
    )
    
    from_user = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    
    hashtag = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'hashtag (without #)'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    has_media = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    min_likes = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        query = cleaned_data.get('query')
        from_user = cleaned_data.get('from_user')
        hashtag = cleaned_data.get('hashtag')
        
        # At least one search criteria must be provided
        if not any([query, from_user, hashtag]):
            raise forms.ValidationError("Please provide at least one search criteria.")
        
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("'From' date cannot be later than 'To' date.")
        
        return cleaned_data


# FOLLOW REQUEST FORMS
class FollowRequestResponseForm(forms.Form):
    ACTION_CHOICES = [
        ('accept', 'Accept'),
        ('reject', 'Reject'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES)
    request_id = forms.IntegerField(widget=forms.HiddenInput())


# NOTIFICATION PREFERENCES FORM
class NotificationPreferencesForm(forms.Form):
    email_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Email notifications"
    )
    
    likes_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Likes on your tweets"
    )
    
    comments_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Comments on your tweets"
    )
    
    follow_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="New followers"
    )
    
    mention_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Mentions"
    )
    
    dm_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Direct messages"
    )