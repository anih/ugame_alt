# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.http import HttpResponseRedirect

from utils.jinja.filters import url

from ..generic.cms_metaclass import CmsMetaclass


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        if self.user and self.user.is_active:
            return HttpResponseRedirect(url(self.all_urls.game.main))
        return {}
    site_main.url = "^$"
    site_main.without_user = True

    def site_regulamin(self):
        return {}
    site_regulamin.without_user = True
