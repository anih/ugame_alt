# Django settings for ugame project.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

DIR_ROOT = os.path.dirname(__file__)
MEDIA_ROOT = os.path.join(DIR_ROOT, 'media/')
MEDIA_STATIC_ROOT = os.path.join(DIR_ROOT, 'media_static/')
MEDIA_ROOT_HIDDEN = os.path.join(DIR_ROOT, 'media_hidden/')
MEDIA_ROOT2 = os.path.join(DIR_ROOT, 'media2/')

MEDIA_INCLUDER_INPUT_DIR = MEDIA_STATIC_ROOT = os.path.join(DIR_ROOT, 'media_static/')
MEDIA_STATIC_URL = '/media_static/'
MEDIA_URL_HIDDEN = "/media_hidden/"
MEDIA_URL = '/media/'

STATS_PERPAGE = 20
GAME_SPEED = 5000
RES_SPEED = 2500
FS = 5000
FLEET_SPEED = FS / GAME_SPEED
MAX_PLANETA = 15
MAX_SYSTEM = 50
MAX_GALAXY = 50
MNOZNIK_MAGAZYNOW = 30
ILOSC_PLANET = 53

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

URL = 'http://new.ugame.net.pl'

SESSION_KEY = 'userprofile_flash_id'

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'pl-PL'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# MEDIA_ROOT = '/home/ugame/media/'
# MEDIA_ROOT = '/var/www/localhost/htdocs/ugame/'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
# MEDIA_URL = 'http://localhost/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media2/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'm6mc8qq0(ewy5*6e^ai4a&&9m4qzesy!5e3ndk-n*t(s1ns#8y'
# LOGIN_URL =  '/login/'
# LOGIN_REDIRECT_URL = 'http://'
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)


MIDDLEWARE_CLASSES = (
    # 'djangologging.middleware.LoggingMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'utils.eback.threadlocal.ThreadLocals',
    'utils.sql_profile.SQLLogMiddleware',
    'utils.ip.IPAccessMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'utils.trace.TraceMiddleware',
)
# AUTH_PROFILE_MODULE = 'game.UserData'
ROOT_URLCONF = 'urls'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_COOKIE_AGE=1800
MESSAGE_STORAGE = 'ugame.models.messages.DBStorage'

TEMPLATE_DIRS = (
                                  DIR_ROOT + "/jtemplates/",
 )

TEMPLATE_CONTEXT_PROCESSORS = ("django.core.context_processors.request", "django.contrib.auth.context_processors.auth",)

ACCOUNT_ACTIVATION_DAYS = 7

INSTALLED_APPS = (
    'registration',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'ugame',
    'cms',
)

JINJA_GLOBALS = (
		'utils.jinja.filters.url',
		)

JINJA_FILTERS = (
		'utils.jinja.filters.intcomma',
		'utils.jinja.filters.make_int',
		'utils.jinja.filters.sub',
		'utils.jinja.filters.date',
		'utils.jinja.filters.ceilh',
		'utils.jinja.filters.pretty_time',
		'utils.jinja.filters.escapejs',
		'utils.jinja.filters.floatformat',
		'utils.jinja.filters.kk_resources',
		'utils.jinja.filters.thumbnail',
		'utils.jinja.filters.linebreaks',
		'utils.jinja.filters.bbcodes',
		)

JINJA_TESTS = (
	      )
