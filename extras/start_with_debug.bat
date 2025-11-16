@echo off
echo 🚀 Starting Twick Django Application
echo =====================================

echo.
echo 📊 Checking Django setup...
python manage.py check
if %errorlevel% neq 0 (
    echo ❌ Django check failed!
    pause
    exit /b 1
)

echo.
echo 🗄️ Applying migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ❌ Migration failed!
    pause
    exit /b 1
)

echo.
echo 🧪 Testing notifications and messages...
python manage.py test_notifications

echo.
echo 🔧 Fixing start conversation functionality...
python fix_start_conversation.py

echo.
echo 🌐 Starting development server...
echo.
echo 📝 Available URLs:
echo   - Home: http://127.0.0.1:8000/
echo   - Debug: http://127.0.0.1:8000/debug/
echo   - Admin: http://127.0.0.1:8000/admin/
echo.
echo 👤 Test users created:
echo   - Username: testuser1 / Password: testpassword
echo   - Username: testuser2 / Password: testpassword
echo.
echo 🎯 Test these features:
echo   1. Login with test users
echo   2. Visit /debug/ to check notifications and messages
echo   3. Navigate through Feed, Trending, Messages, Search
echo   4. Create tweets, follow users, send messages
echo.

python manage.py runserver
