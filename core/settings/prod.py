import os

from .base import *


DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

RENDER_EXTERNAL_HOSTNAME = (
    os.environ.get("RENDER_EXTERNAL_HOSTNAME")
)

if RENDER_EXTERNAL_HOSTNAME:
   ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': int(os.environ['POSTGRES_PORT']),
    }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True