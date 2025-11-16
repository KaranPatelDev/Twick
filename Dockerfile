# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=twick.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        tcl-dev \
        tk-dev \
        python3-tk \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Make start script executable
RUN chmod +x /app/start.sh

# Create directories for media and static files
RUN mkdir -p /app/media/avatars /app/media/covers /app/media/photos \
    && mkdir -p /app/staticfiles

# Set proper permissions
RUN chmod -R 755 /app/media \
    && chmod -R 755 /app/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput

# Run database migrations
RUN python manage.py makemigrations
RUN python manage.py migrate

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' django \
    && chown -R django:django /app
USER django

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python manage.py check || exit 1

# Default command with startup script
CMD ["./start.sh"]
