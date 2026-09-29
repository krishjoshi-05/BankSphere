from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-banksphere-secret-key-2026-xyz'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'banksphere_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'myapp' / 'templates'],
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

WSGI_APPLICATION = 'banksphere_project.wsgi.application'

# ─────────────────────────────────────────────────────────────
#  DATABASE
#  The db.sqlite3 file lives inside the project folder.
#  As long as you DO NOT delete this file, all your signup
#  data, transactions and contact messages are permanently
#  stored and will work across every restart.
# ─────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',   # ← this file = your entire database
    }
}

# Optional MySQL (see banksphere_mysql.sql for setup instructions)
# DATABASES = {
#     'default': {
#         'ENGINE':   'django.db.backends.mysql',
#         'NAME':     'banksphere_db',
#         'USER':     'your_mysql_username',
#         'PASSWORD': 'your_mysql_password',
#         'HOST':     'localhost',
#         'PORT':     '3306',
#         'OPTIONS':  {'charset': 'utf8mb4'},
#     }
# }

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Kolkata'
USE_I18N      = True
USE_TZ        = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'myapp' / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
