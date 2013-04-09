# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from settings import DEBUG, MEDIA_ROOT

urlpatterns = patterns('',
    # Example:
    # (r'^ewd/', include('ewd.foo.urls')),

    # Uncomment this for admin:
    (r'^wiadomosci_przeslane/$', 'cms.views.wiadomosci_przeslane'),
    (r'^wiadomosc_przeslana/(?P<id>[0-9]*)/$', 'cms.views.wiadomosc_przeslana'),
    (r'^login_other/(?P<user_id>[0-9]*)/$', 'cms.views.login_other'),
    )
