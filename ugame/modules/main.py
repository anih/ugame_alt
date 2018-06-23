# -*- coding: utf-8 -*-
from ..generic.cms_metaclass import CmsMetaclass
from django.http import HttpResponseRedirect
from utils.jinja.filters import url


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        if self.user and self.user.is_active:
            print self.user
            return HttpResponseRedirect(url(self.all_urls.game.main))
        return {}
    site_main.url = "^$"
    site_main.without_user = True

    def site_regulamin(self):
        return {}
    site_regulamin.without_user = True
