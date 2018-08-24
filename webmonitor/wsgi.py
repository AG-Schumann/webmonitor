"""
WSGI config for webmonitor project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/scratch/webmonitor')
sys.path.append('/scratch/anaconda3/envs/webmonitor/lib/python3.7/site-packages')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webmonitor.settings')

application = get_wsgi_application()
