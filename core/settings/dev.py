from .base import *

DEBUG = True

ALLOWED_HOSTS = []

SECRET_KEY = (
    "django-insecure-nk+gl@3w_wt91qrh66120nv%60(_%k&mjihvtloexv0_h$hz@l"
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
