'''
Author: AugustTheodor
Date: 2021-12-09 16:03:27
LastEditors: AugustTheodor
LastEditTime: 2022-01-25 15:45:35
Description: Aurora-Backend
'''
"""Aurora_Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls import url
from django.views import static

urlpatterns = [
    path('aurora/',include("aurora_main.urls")),
    #url(r'^(?P<path>.*)$',static.serve, {'document_root': 'static/'}),#这个貌似与静态文件有关
]
