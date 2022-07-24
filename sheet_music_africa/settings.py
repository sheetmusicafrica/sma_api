"""
Django settings for sheet_music_africa project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import sys
import dj_database_url

from pathlib import Path

from datetime import timedelta

from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key()) 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "True") == "True"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")


CORS_ALLOWED_ORIGINS = [
    "https://www.sheetmusicafrica.com",
    "http://localhost:3000"
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',

    'musicStore',
    'composer',
    'help_center',
    'password',
    'payout',

    'storages',

    'rest_framework_simplejwt.token_blacklist',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sheet_music_africa.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sheet_music_africa.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if DEVELOPMENT_MODE is True:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
    }



# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


# aws settings
AWS_S3_REGION_NAME = 'us-east-1'
AWS_ACCESS_KEY_ID = os.getenv("aws_access_key")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secrete_key")
AWS_STORAGE_BUCKET_NAME = os.getenv("bucket_name")
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)


# s3 public media settings
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'sheet_music_africa.storage_backends.PublicMediaStorage'


# s3 private media settings
PRIVATE_MEDIA_LOCATION = 'private'
PRIVATE_FILE_STORAGE = 'sheet_music_africa.storage_backends.PrivateMediaStorage'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ]
}

# Email configurations
EMAIL_HOST = os.getenv("email_host")
EMAIL_HOST_USER = os.getenv("email_host_user")
EMAIL_HOST_PASSWORD = os.getenv("email_password")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = ""
FROM_EMAIL = os.getenv("from_email")
MAIN_ADDRESS = os.getenv("site_address")



# price Values

MINIMUM_SCORE_PRICE = float(os.getenv("min_price","5.0"))

PAYMENT_LANDMARK = 100
PAYMENT_LANDMARK_CURRENCY = "USD"
PAYOUT_DAY = 25
PAYOUT_LANDMARK = 10000

# Sheet Music Africa Payout info
ACCOUNT_NAME = "SHEET_MUSIC_AFRICA"
ACCOUNT_EMAIL = ""
BANK_NAME = ""
BANK_CODE = ""
ACCOUNT_NUMBER = ""

# Flutter Info
FLUTTER_URL = "https://api.flutterwave.com/v3/"
FLUTTER_WAVE_COUNTRIES = ['NIGERIA', 'GHANA', 'KENYA', 'UGANDA', 'TANZANIA', 'SOUTH AFRICA', 'ZAMBIA', 'IVORY COAST', 'CAMEROON',
                          'IVORY COAST', 'SIERRA LEONE', 'BURKINA FASO', 'GUINEA BISSAU', 'MALI', 'SENEGAL', 'RWANDA', 'TUNISIA', 'GUINEA CONAKRY']


PAYMENT_SECRET_KEY = os.getenv('FLUTTER_WAVE_KEY',"")



LOGO_URL = os.getenv("logo_url","")


BOTREGEX = os.getenv('BOTREGEX')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

MAIN_SITE_ADDRESS = "https://www.sheetmusicafrica.com"
