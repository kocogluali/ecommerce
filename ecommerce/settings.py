"""
Django settings for ecommerce project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%48=@tatd69=o@sjc3(^4mdx6x4rt8r2ov)x!9!j1ng33atht1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # My Apps
    'account',
    'ayarlar',
    'comment',
    'faq',
    'home',
    'campaings',
    'product',
    'blog',
    # 3.Party Apps
    'ckeditor',
    'smart_selects',
    'social_django',
    # 'django_filters',
    'sorl.thumbnail',
    'iyzipay',
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
MIDDLEWARE_CLASSES = [
    'social_django.middleware.SocialAuthExceptionMiddleware',  # <--
]
ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',  # <--
                'social_django.context_processors.login_redirect',  # <--
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'tr'

TIME_ZONE = 'Europe/Istanbul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/staticfiles/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  ## For Server
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'staticfiles')  ## For localhost
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CKEDITOR_CONFIGS = {
    'default': {
        'height': '500px',
        'width': '1200px',
        'toolbar': 'full',
        'toolbarCanCollapse': False,
    },
}
# SESSION_COOKIE_SECURE = False
# SESSION_COOKIE_DOMAIN = "http://127.0.0.1:8000"


# email settings

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # mail service smtp
EMAIL_HOST_USER = 'legohabercom@gmail.com'  # email id
EMAIL_HOST_PASSWORD = '141277kk'  # password
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# django auth login social app
AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)
# social auth
LOGIN_URL = '/kullanici/giris'
LOGOUT_URL = '/kullanici/cikis-yap'
LOGIN_REDIRECT_URL = '/kullanici/giris'

SOCIAL_AUTH_GITHUB_KEY = '846a4f16ce064ad60f38'
SOCIAL_AUTH_GITHUB_SECRET = '7c0aa4d57e6273e6e6b17fa6a877c864aa95a9d5'

SOCIAL_AUTH_LOGIN_ERROR_URL = '/kullanici/giris'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/kullanici/giris'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

SOCIAL_AUTH_FACEBOOK_KEY = '1976602399053819'  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = 'ebf69d6155fad8585c9e9a9db287b2ad'  # App Secret
