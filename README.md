# Twick

![Python](https://img.shields.io/badge/-Python-blue?logo=python&logoColor=white)

## 📝 Description

Twick is a Python-based project designed to [describe the project's purpose or problem it solves]. While the original description is brief, Twick leverages the versatility of Python to offer [mention key features]. Further development is planned to include [mention potential future features or improvements], solidifying Twick as a [describe the intended impact or user benefit].

## 🛠️ Tech Stack

- 🐍 Python


## 📦 Key Dependencies

```
asgiref: 3.8.1
Django: 5.1.1
pillow: 10.2.0
sqlparse: 0.5.1
gunicorn: 21.2.0
```

## 📁 Project Structure

```
.
├── Dockerfile
├── Dockerfile.prod
├── Project_Report.md
├── docker-compose.prod.yml
├── docker-compose.yml
├── documentation_site
│   ├── assets
│   │   ├── css
│   │   │   ├── style.css
│   │   │   └── styles.css
│   │   └── js
│   │       ├── main.js
│   │       └── script.js
│   ├── home.html
│   ├── index.html
│   └── pages
│       ├── api-reference.html
│       ├── architecture.html
│       ├── changelog.html
│       ├── containerization.html
│       ├── contributing.html
│       ├── deployment-guide.html
│       ├── deployment.html
│       ├── features.html
│       ├── getting-started.html
│       ├── system-architecture.html
│       └── troubleshooting.html
├── extras
│   ├── cleanup_trash_files.py
│   ├── generate_user_manual_pdf.py
│   ├── project_framework.md
│   ├── start.sh
│   └── start_with_debug.bat
├── manage.py
├── requirements.txt
├── static
│   ├── css
│   │   └── custom.css
│   └── images
│       └── favicon.svg
├── templates
│   ├── components
│   │   └── twick_logo.html
│   ├── edit_profile.html
│   ├── home.html
│   ├── layout.html
│   ├── registration
│   │   ├── logged_out.html
│   │   ├── login.html
│   │   ├── password_change_form.html
│   │   └── register.html
│   └── user_profile.html
├── tweet
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── management
│   │   ├── __init__.py
│   │   └── commands
│   │       └── __init__.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_alter_tweet_options_tweet_likes_userprofile.py
│   │   ├── 0003_auto_20250706_0833.py
│   │   ├── 0004_tweet_parent_tweet_tweet_privacy_and_more.py
│   │   ├── 0005_userprofile_company_userprofile_cover_photo_and_more.py
│   │   ├── 0006_hashtag_popularsearch_conversation_directmessage_and_more.py
│   │   └── __init__.py
│   ├── models.py
│   ├── signals.py
│   ├── templates
│   │   ├── components
│   │   │   ├── message_badge.html
│   │   │   ├── notification_badge.html
│   │   │   └── tweet_card.html
│   │   ├── conversation_detail.html
│   │   ├── conversations_list.html
│   │   ├── follow_requests.html
│   │   ├── hashtag_detail.html
│   │   ├── index.html
│   │   ├── notifications_list.html
│   │   ├── personalized_feed.html
│   │   ├── search_results.html
│   │   ├── start_conversation.html
│   │   ├── trending_hashtags.html
│   │   ├── tweet_confirm_delete.html
│   │   ├── tweet_detail.html
│   │   ├── tweet_form.html
│   │   ├── tweet_list.html
│   │   └── tweet_reply.html
│   ├── templatetags
│   │   ├── __init__.py
│   │   └── custom_filters.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
└── twick
    ├── __init__.py
    ├── asgi.py
    ├── production.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

## 🛠️ Development Setup

### Python Setup
1. Install Python (v3.8+ recommended)
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`


## 👥 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/KaranPatelDev/Twick.git`
3. **Create** a new branch: `git checkout -b feature/your-feature`
4. **Commit** your changes: `git commit -am 'Add some feature'`
5. **Push** to your branch: `git push origin feature/your-feature`
6. **Open** a pull request

Please ensure your code follows the project's style guidelines and includes tests where applicable.

