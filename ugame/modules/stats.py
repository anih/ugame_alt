# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import ceil

from django.core.paginator import InvalidPage
from django.core.paginator import Paginator

from settings import STATS_PERPAGE
from ugame.klasy.BaseGame import Output
from ugame.models.all import UserProfile
from ugame.topnav import topnav_site

from ..generic.cms_metaclass import CmsMetaclass


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_show(self, page=0):
        try:
            page = int(page)
            if page <= 0:
                page = 1
        except:
            page = 1
        zaznaczony_user = None
        if self.request.method == 'POST' and self.request.POST.has_key('user'):
            try:
                punkty = UserProfile.objects.filter(user__username=self.request.POST['user'])
            except:
                punkty = UserProfile.objects.filter(user__username__icontains=self.request.POST['user'])
            if punkty.count() > 0:
                zaznaczony_user = punkty[0].user
                punkty = punkty[0].points

                start = ceil((UserProfile.objects.filter(points__gt=punkty).order_by("-points",
                                                                                     "user").count() + 1) /
                             STATS_PERPAGE)
                page = start + 1
        paginator = Paginator(UserProfile.objects.all().order_by("-points", "user"), STATS_PERPAGE,
                              allow_empty_first_page=True)

        try:
            p = paginator.page(page)
        except InvalidPage:
            page = 1
            p = paginator.page(1)

        stats_tmp = p.object_list
        od = int((page - 1) * STATS_PERPAGE)
        stats = []
        count = 1
        for s in stats_tmp:
            st = Output()
            st.user = s
            st.miejsce = count + od
            count += 1
            stats.append(st)

        topnav = topnav_site(self.game)
        return {"topnav": topnav, "stats": stats, "paginator": paginator, "page": page, "p": p,
                "zaznaczony_user": zaznaczony_user}
