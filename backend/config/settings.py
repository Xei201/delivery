import os
import sys

import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


DEBUG = env.bool("DEBUG")
SECRET_KEY = env.str("SECRET_KEY")
TIME_ZONE = env.str("TIME_ZONE", "Europe/Moscow")

LANGUAGE_CODE = "ru"
USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "users.apps.UsersConfig",
    "core.apps.CoreConfig",
    "api.apps.ApiConfig",
]

if DEBUG and "test" not in sys.argv:
    INSTALLED_APPS.extend(["django_extensions", "debug_toolbar"])

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


if DEBUG and "test" not in sys.argv:
    MIDDLEWARE.extend(["debug_toolbar.middleware.DebugToolbarMiddleware"])

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR + "/db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

STATIC_ROOT = env.path("DJANGO_STATIC_ROOT", "./static")
STATIC_URL = "/static/"

MEDIA_ROOT = env.path("DJANGO_MEDIA_ROOT", "./media")
MEDIA_URL = "/media/"


ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "backend"])


def origins_generator():
    """
    Генератор для создания списка допустимых источников (origins) для CORS.

    Этот генератор проходит по списку разрешенных хостов (ALLOWED_HOSTS) и
    создает URL-адреса с протоколами HTTP и HTTPS для каждого хоста.

    Yields:
        str: URL-адрес с протоколом HTTP или HTTPS для каждого разрешенного хоста.
    """
    for _host in ALLOWED_HOSTS:
        yield f"http://{_host}"
        yield f"https://{_host}"


CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = list(origins_generator())
CSRF_TRUSTED_ORIGINS = list(origins_generator())


AUTH_USER_MODEL = "users.CustomUser"

URL_REDIS = env.str("URL_REDIS", "redis://localhost:6379/1")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": URL_REDIS,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# PROD ONLY
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True

