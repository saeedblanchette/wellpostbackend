"""
Django settings for willpostbackend project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from datetime import timedelta

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-uj1*a1!%lb5&*&&!+wr)(90_!v48_twp7r0wu3e=cw37wf1abl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = 'willpostbackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        # 'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 'loaders': [
            #     (


            #         'django.template.loaders.app_directories.Loader',
            #         'django.template.loaders.filesystem.Loader',


            #     ),
            # ]
        },
    },
]


WSGI_APPLICATION = 'willpostbackend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'willpost.User'
REST_USE_JWT = True
JWT_AUTH_COOKIE = 'jwt-auth'
INSTALLED_APPS += [
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'willpost',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    "corsheaders",
    'dj_rest_auth.registration',
    'django_q',

]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',

    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'willpost.permissions.TwoAuthFactorPermission',
    ]
}


JWT_AUTH_COOKIE = 'jwt-cookie'
JWT_AUTH_REFRESH_COOKIE = 'jwt-refresh-token'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USERNAME_REQUIRED = False


ACCOUNT_ADAPTER = 'willpost.adapter.DefaultAccountAdapterCustom'

REST_AUTH_SERIALIZERS = {
    'PASSWORD_RESET_SERIALIZER': 'willpost.serializers.CustomPasswordResetSerializer',
    'PASSWORD_RESET_CONFIRM_SERIALIZER': 'willpost.serializers.CustomPasswordResetConfirmSerializer',
    'USER_DETAILS_SERIALIZER': 'willpost.serializers.UserDetailsSerializer',
    'LOGIN_SERIALIZER': 'willpost.serializers.LoginSerializer',
    'REST_AUTH_REGISTER_SERIALIZERS': 'willpost.serializers.RegisterSerializer'
}
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'willpost.serializers.RegisterSerializer'
}
# ACCOUNT_FORMS = {

#     # 'change_password': 'allauth.account.forms.ChangePasswordForm',
#     # 'set_password': 'allauth.account.forms.SetPasswordForm',
#     'reset_password': 'willpost.forms.ResetPasswordForm',
#     'reset_password_from_key': 'willpost.forms.ResetPasswordKeyForm',
#     # 'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
# }


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=45),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1), }
CORS_ALLOW_ALL_ORIGINS = True
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
LOGIN_VERIFICATION_LIFETIME = timedelta(days=1)
MEDIA_URL = 'mediafiles/'
DATA_UPLOAD_MAX_MEMORY_SIZE = None
FILE_UPLOAD_MAX_MEMORY_SIZE = 262144000
FILE_UPLOAD_HANDLERS = ['willpost.fileUploadHandler.MyFileUploadHandler',
                        'django.core.files.uploadhandler.MemoryFileUploadHandler',
                        'django.core.files.uploadhandler.TemporaryFileUploadHandler']

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'my_log_handler': {
#             'level': 'DEBUG' if DEBUG else 'INFO',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'django.log'),
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['my_log_handler'],
#             'level': 'DEBUG' if DEBUG else 'INFO',
#             'propagate': True,
#         },
#     },
# }

Q_CLUSTER = {
    'name': 'DjangORMWillpost',
    'workers': 4,
    'timeout': 90,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default'
}
ip_addr = 'http://34.77.63.151/'

ALLOWED_HOSTS = []
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
# email settings
if DEBUG == True:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = False
    EMAIL_HOST = '0.0.0.0'
    EMAIL_PORT = 1025
    EMAIL_HOST_PASSWORD = 'bchjxiojdpfpagle'
    EMAIL_HOST_USER = ''
    DEFAULT_FROM_EMAIL = 'willpost@noreplay.com'

else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_PASSWORD = 'bchjxiojdpfpagle'
    EMAIL_HOST_USER = 'saidblanchette.emaildev@gmail.com'
    DEFAULT_FROM_EMAIL = 'saidblanchette.emaildev@gmail.com'
# front end settings
SITE_NAME = 'Willpost'
URL_FRONT = 'localhost:3000'
FRONEND_CONFIRMATION_URL = 'http://localhost:3000/confirmation/'

FRONEND_VOTE_URL = 'http://localhost:3000/post/'

SITE_ID = 1
