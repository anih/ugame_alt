import sys
sys.path.append('/home/ugame/web/')
import os
import django.core.handlers.wsgi

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

application = django.core.handlers.wsgi.WSGIHandler()

# mount this application at the webroot
applications = { '/': 'application' }
