import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-kakalif-key-paling-aman')

# Set False di produksi Vercel, True hanya untuk debug lokal
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS wajib mencakup domain Vercel dan domain pribadi
ALLOWED_HOSTS = ['.vercel.app', 'sabar.kakalif.my.id', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'monitoring', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Menangani file statis tanpa ribet
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'

# DATABASE STRATEGY
# Menggunakan memory agar tidak error 'ReadOnly File System' di Vercel
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:', 
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Jalur absolut lebih aman
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

# --- GOOGLE SHEETS CONFIG ---
# settings.py
SPREADSHEET_ID = '18knwd2i4FR0XOX0Bb22No66venosWUsma5DbTZ6u9_s'

# Static Files Configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Setting Whitenoise agar tetap jalan meskipun file static belum di-collect
WHITENOISE_MANIFEST_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# Ganti dari CompressedManifestStaticFilesStorage ke ini:
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

TIME_ZONE = 'Asia/Jakarta'
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
