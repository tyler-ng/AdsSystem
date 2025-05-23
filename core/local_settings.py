# Local settings for development
# PostgreSQL Docker configuration

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ads_system',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',  # Connect to local Docker container
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