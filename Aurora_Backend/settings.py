'''
Author: AugustTheodor
Date: 2021-12-09 16:03:27
LastEditors: AugustTheodor
LastEditTime: 2022-01-25 17:25:22
Description: Aurora_Backend
'''
"""
Django settings for Aurora_Backend project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8y$ax0aaxx4)n^fqs_%u+a7__pu$y5**o_oidmn3x+%(o#@b5e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

#不是交互网页只是后端，不需要额外的插件
INSTALLED_APPS = [
    'channels',
    'aurora_socket.apps.AuroraSocketConfig',
    'aurora_main.apps.AuroraMainConfig',
    'django.contrib.sessions', #session插件
    'django_extensions', #runscript
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

ASGI_APPLICATION = 'Aurora_Backend.asgi_routing.application' #指定ASGI路由

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db' #session引擎
SESSION_COOKIE_NAME='SessionID' 
SESSION_COOKIE_AGE=5184000 #登陆两个月失效

ROOT_URLCONF = 'Aurora_Backend.urls'

TEMPLATES = [#配置模版加载的路径
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'Aurora_Backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': { #正式环境为twe87u2ihwjldhasuiocjxl9-w
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'aurora',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': 'root' ,
        'OPTIONS': {'charset': 'utf8mb4'}, #设置字符集
    }
}


# Password validation
#不需要这玩意，被删了


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# 配置邮箱
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'AugustTheodor@163.com'
#授权码
EMAIL_HOST_PASSWORD = 'HTJILORRTHBNLJBB'
EMAIL_FROM = '<破晓的Augustine>'
#URL
DOMAIN="http://1.116.250.29"
LATEST_VERSION="0_2_0"
APP_LATEST_DOWNLOAD="/aurora/file/app/Aurora{0}.apk".format(LATEST_VERSION)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_ROOT=os.path.join(BASE_DIR,"")
STATIC_URL = '/aurora/image/'
IMAGE_DIR=STATIC_ROOT.replace("\\\\","\\")+"static\\"
STATICFILES_DIRS= (os.path.join(BASE_DIR, "static"),) #共同的静态文件路径
