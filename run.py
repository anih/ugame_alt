from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

import django.core.handlers.wsgi

sys.path.append('/home/ugame/web/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

application = django.core.handlers.wsgi.WSGIHandler()

# mount this application at the webroot
applications = { '/': 'application' }
