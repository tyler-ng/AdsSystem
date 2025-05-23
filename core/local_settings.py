# Local settings for development
# PostgreSQL Docker configuration

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ads_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',  # Connect to Docker container
        'PORT': '5432',       # Default PostgreSQL port
    }
}

# Use local memory cache instead of Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Debug settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1'] 