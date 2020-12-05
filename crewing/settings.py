"""
Django settings for crewing project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR,'templates')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '4e69455fa510.ngrok.io']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'web_hiring',
    'tgbot',
    'bootstrap4',
    'crispy_forms',
    'widget_tweaks',
    'django_cleanup',
    'django_celery_beat',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crewing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR,],
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

WSGI_APPLICATION = 'crewing.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Celery settings

REDIS_HOST = 'redis'
REDIS_PORT = '6379'
BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

#############################

TELE_TOKEN = config('TELE_TOKEN')

#####  SCRAPER config  ######

START_URL = config('START_URL')

#############################

TITLE_CHOICES = [
        ('', 'Выберите должность'),
        ('Boatswain, Bosun', 'Boatswain, Bosun'),
        ('Seamen (AB, OS)', 'Seamen (AB, OS)'),
        ('Seamen-welder', 'Seamen-welder'),
        ('Motorman (Oiler)', 'Motorman (Oiler)'),
        ('Cook', 'Cook'),
        ('Wiper', 'Wiper'),
        ('Fitter', 'Fitter'),
        ('Messman', 'Messman'),
        ('Cadet', 'Cadet'),
        ('Master', 'Master'),
        ('Chief Officer', 'Chief Officer'),
        ('2nd Officer', '2nd Officer'),
        ('3rd Officer', '3rd Officer'),
        ('Chief Engineer', 'Chief Engineer'),
        ('2nd Engineer', '2nd Engineer'),
        ('3rd и 4th Engineer', '3rd и 4th Engineer'),
        ('Electro Engineer', 'Electro Engineer'),
        ('Другое', 'Другое')
        ]
FLEET_CHOICES = [
        ('', 'Выберите тип флота'),
        ('Merchant fleet', 'Merchant fleet'),
        ('Offshore fleet', 'Offshore fleet'),
        ('Fishing fleet', 'Fishing fleet'),
        ('Passenger fleet', 'Passenger fleet'),
        ('Tanker fleet', 'Tanker fleet')
        ]
VESSEL_CHOICES = [
        ('','Выберите тип судна'),
        ('Accommodation Barge', 'Accommodation Barge'),
        ('Anchor Handling Tug Supply', 'Anchor Handling Tug Supply'),
        ('ASD Tug (Azimuth Stern Drive Tug)', 'ASD Tug (Azimuth Stern Drive Tug)'),
        ('Bulk Carrier', 'Bulk Carrier'),
        ('Bunkering Vessel', 'Bunkering Vessel'),
        ('Cable Laying Vessel', 'Cable Laying Vessel'),
        ('Car Carrier', 'Car Carrier'),
        ('Cement Carrier', 'Cement Carrier'),
        ('Chemical Tanker', 'Chemical Tanker'),
        ('Coaster', 'Coaster'),
        ('Container', 'Container'),
        ('Crew Boat', 'Crew Boat'),
        ('Crude Oil Tanker', 'Crude Oil Tanker'),
        ('Cruise Vessel', 'Cruise Vessel'),
        ('Dredger', 'Dredger'),
        ('Dry Cargo', 'Dry Cargo'),
        ('DSV - Diving Support Vessel', 'DSV - Diving Support Vessel'),
        ('Fishing Vessel', 'Fishing Vessel'),
        ('FPSO (Floating Production Storage and Offloading)', 'FPSO (Floating Production Storage and Offloading)'),
        ('General Cargo', 'General Cargo'),
        ('Heavy Lift Vessel', 'Heavy Lift Vessel'),
        ('LNG Tanker', 'LNG Tanker'),
        ('LPG Tanker', 'LPG Tanker'),
        ('Multi-Purpose Vessel', 'Multi-Purpose Vessel'),
        ('OBO (Oil/Bulk/Ore Carrier)', 'OBO (Oil/Bulk/Ore Carrier)'),
        ('Oil Chemical Tanker', 'Oil Chemical Tanker'),
        ('Oil Product Tanker', 'Oil Product Tanker'),
        ('Oil Tanker', 'Oil Tanker'),
        ('OSV (Offshore Supply Vessel)', 'OSV (Offshore Supply Vessel)'),
        ('Passenger Vessel', 'Passenger Vessel'),
        ('Pollution Control Vessel', 'Pollution Control Vessel'),
        ('PSV (Platform Supply/Support Vessel)', 'PSV (Platform Supply/Support Vessel)'),
        ('Reefer', 'Reefer'),
        ('Research vessel', 'Research vessel'),
        ('Ro-Ro', 'Ro-Ro'),
        ('Self Unloading Bulk Carrier', 'Self Unloading Bulk Carrier'),
        ('Supply Vessel', 'Supply Vessel'),
        ('Tug Boat', 'Tug Boat'),
        ('Utility Boat', 'Utility Boat'),
        ('VLCC (Very Large Crude Oil Carrier)', 'VLCC (Very Large Crude Oil Carrier)'),
        ('VSP Tug (Voith Schneider Propeller Tug)', 'VSP Tug (Voith Schneider Propeller Tug)'),
]
ENGLISH_CHOICES = [
        ('', 'Выберите уровень английского'),
        ('Любой', 'Любой'),
        ('Без знаний', 'Без знаний'),
        ('Хороший', 'Хороший'),
        ('Продвинутый', 'Продвинутый')
        ]
