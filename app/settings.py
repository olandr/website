import os
from app.variables import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "6_$8zsh&07=@+j-q%#e^h22ht_@+q^g+l)xd(&wwf)$gu5lgr^"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("PROD_MODE", "false").lower() == "false"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "phonenumber_field",
    "djmoney",
    "bootstrap4",
    "user",
    "event",
    "application",
    "job",
    "app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'app.utils.variables_processor',
            ]
        },
    }
]

WSGI_APPLICATION = "app.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

if (
    os.environ.get("PG_NAME", None)
    and os.environ.get("PG_USER", None)
    and os.environ.get("PG_PWD", None)
):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.environ.get("PG_NAME"),
            "USER": os.environ.get("PG_USER"),
            "PASSWORD": os.environ.get("PG_PWD"),
            "HOST": os.environ.get("PG_HOST", "localhost"),
            "PORT": "5432",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = HACKATHON_TIMEZONE

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR + "/staticfiles"
STATICFILES_DIRS = [os.path.join(BASE_DIR, os.path.join("app", "static"))]
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# File upload configuration

MEDIA_URL = "/files/"
MEDIA_ROOT = BASE_DIR + "/files"

# Sendgrid API key

SG_KEY = os.environ.get("SG_KEY", None)
EMAIL_BACKEND = "sgbackend.SendGridBackend"

# Set up custom authenthication

AUTH_USER_MODEL = "user.User"
LOGIN_URL = "user_login"
PASSWORD_RESET_TIMEOUT_DAYS = 1

# Add domain to allowed hosts

ALLOWED_HOSTS.append(HACKATHON_DOMAIN)

# Deployment configurations for proxy pass and CSRF

CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Maximum file upload size for forms

MAX_UPLOAD_SIZE = 5242880

# Phone number format

PHONENUMBER_DB_FORMAT = "INTERNATIONAL"
