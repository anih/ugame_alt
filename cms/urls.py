# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^ewd/', include('ewd.foo.urls')),

    # Uncomment this for admin:
    (r'^wiadomosci_przeslane/$', 'cms.views.wiadomosci_przeslane'),
    (r'^wiadomosc_przeslana/(?P<id>[0-9]*)/$', 'cms.views.wiadomosc_przeslana'),
    (r'^login_other/(?P<user_id>[0-9]*)/$', 'cms.views.login_other'),
    )
