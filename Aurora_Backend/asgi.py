"""
ASGI config for Aurora_Backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""


import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Aurora_Backend.settings')
django.setup()

import os

from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Aurora_Backend.settings')

application = get_default_application()
