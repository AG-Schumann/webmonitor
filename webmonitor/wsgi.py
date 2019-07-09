"""
WSGI config for webmonitor project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/software/webmonitor')
sys.path.append('/software/anaconda3/envs/server/lib/python3.7/site-packages')

python_home = '/software/anaconda3/envs/server'
activate_this = python_home + '/bin/activate_this.py'
with open(activate_this) as file_:
    #print(file_.read())
    exec(file_.read(), dict(__file__=activate_this))
    #print(os.environ['DJANGO_SECRET_KEY'])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webmonitor.settings')

application = get_wsgi_application()
