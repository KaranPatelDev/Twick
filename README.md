# 🚀 **Twick — A Modern Social Interaction Platform Built with Django**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1-darkgreen?logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow?logo=open-source-initiative)

<!-- Project badges -->
![Repo Size](https://img.shields.io/github/repo-size/KaranPatelDev/Twick?color=orange&logo=github)
![Last Commit](https://img.shields.io/github/last-commit/KaranPatelDev/Twick?color=blue)
![Contributors](https://img.shields.io/github/contributors/KaranPatelDev/Twick?color=purple)
![Docker Pulls](https://img.shields.io/docker/pulls/library/python?label=Docker%20Pulls%20(Base%20Image))
![CI/CD](https://img.shields.io/github/actions/workflow/status/KaranPatelDev/Twick/ci.yml?label=CI%2FCD&logo=github-actions&color=brightgreen)

---

# 🎥 **Live Demo Preview**

> Replace the GIF once you generate your project preview.

![Demo GIF](https://raw.githubusercontent.com/yourusername/yourrepo/main/demo.gif)

---

# 🏗️ **System Architecture**

```mermaid
flowchart TD

    A[Client Browser] --> B[Nginx / Reverse Proxy]
    B --> C[Gunicorn]
    C --> D[Django Application - Twick]

    D --> E[Authentication Module]
    D --> F[Tweet Engine]
    D --> G[Notifications System]
    D --> H[Direct Messaging]
    D --> I[Search & Hashtag Engine]

    D --> J[(PostgreSQL / SQLite Database)]
    D --> K[(Static Files / Media Storage)]
```

---

# 🗄️ **Database Schema Diagram**

```mermaid
erDiagram

    USER {
        int id PK
        string username
        string email
        string password
        string bio
        string profile_photo
        string cover_photo
        boolean is_private
    }

    TWEET {
        int id PK
        text content
        datetime created_at
        int author_id FK
        int parent_tweet_id FK
        string image
        string privacy
    }

    LIKE {
        int id PK
        int tweet_id FK
        int user_id FK
        datetime created_at
    }

    FOLLOW {
        int id PK
        int follower_id FK
        int following_id FK
        boolean approved
    }

    MESSAGE {
        int id PK
        int sender_id FK
        int receiver_id FK
        text message
        datetime timestamp
    }

    HASHTAG {
        int id PK
        string tag
    }

    TWEET_HASHTAG {
        int id PK
        int tweet_id FK
        int hashtag_id FK
    }

    USER ||--o{ TWEET : "creates"
    USER ||--o{ LIKE : "likes"
    USER ||--o{ FOLLOW : "follows"
    USER ||--o{ MESSAGE : "sends"
    TWEET ||--o{ LIKE : "liked by"
    TWEET ||--o{ TWEET_HASHTAG : "tagged with"
    HASHTAG ||--o{ TWEET_HASHTAG : "belongs to"
```

---

# 🗺️ **Feature Roadmap**

| Status | Category | Feature | Description |
|--------|----------|----------|-------------|
| ✅ Done | Core | Tweet System | Create, like, retweet, reply, delete |
| ✅ Done | User | Profile + Cover Photo | Bio, company, links, profession |
| ✅ Done | Social | Follow System | Requests, approval, follow suggestions |
| ⏳ In Progress | Chat | Direct Messaging | Real-time UI, conversation list |
| ⏳ In Progress | Feed | Personalized Feed | Intelligent ranking-based timeline |
| ⏳ In Progress | Explore | Trending & Hashtags | Find hashtags, popular tweets |
| 🟦 Planned | AI | Toxicity Detection | ML-based comment moderation |
| 🟦 Planned | AI | Tweet Recommendations | Personalized recommendations |
| 🟦 Planned | Media | Video & Audio Tweets | Upload & playback support |
| 🟦 Planned | Admin | Moderation Dashboard | Analytics + content review |
| 🟦 Planned | DevOps | Full CI/CD Pipeline | Auto-deploy with GitHub Actions |

---

# 📝 **Description**

Twick is a full-scale Django-powered micro-social platform designed with modularity, scalability, and developer extensibility in mind.  
It provides a tweet-driven communication network with hashtags, notifications, messaging, privacy settings, and a fully containerized environment.

This makes Twick ideal for:

- Social platform experiments  
- Academic / portfolio projects  
- AI-enhanced microblogging research  
- Real production deployment with Docker  

---

# ⚙️ **Tech Stack**

### **Backend**
- Python 3.10+
- Django 5.1
- Gunicorn (production)

### **Frontend**
- Django Templates
- Custom CSS
- Vanilla JS

### **DevOps**
- Docker & Docker Compose
- Nginx reverse proxy (planned)
- GitHub Actions CI/CD (planned)
- Shell scripts for automation

---

# 📦 **Dependencies**

```
asgiref: 3.8.1
Django: 5.1.1
pillow: 10.2.0
sqlparse: 0.5.1
gunicorn: 21.2.0
```

---

# 📁 **Project Structure**

```
Twick/
├── Dockerfile
├── Dockerfile.prod
├── docker-compose.yml
├── docker-compose.prod.yml
├── documentation_site/
│   ├── assets/
│   ├── home.html
│   ├── index.html
│   └── pages/
├── extras/
│   ├── cleanup_trash_files.py
│   ├── start.sh
├── static/
│   ├── css/
│   └── images/
├── templates/
│   ├── components/
│   ├── layout.html
│   ├── home.html
│   └── registration/
├── tweet/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── utils.py
│   └── templates/
└── twick/
    ├── settings.py
    ├── production.py
    └── wsgi.py
```

---

# 🛠️ **Development Setup**

```bash
git clone https://github.com/KaranPatelDev/Twick.git
cd Twick
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

# 🐳 **Docker Setup**

### Development
```bash
docker-compose up --build
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up --build
```

---

# 📚 **Documentation**

Open the offline docs:

```
documentation_site/index.html
```

---

# 🤝 **Contributing**

Pull requests and feature proposals are welcome!

---

# 📄 **License**
MIT License  
