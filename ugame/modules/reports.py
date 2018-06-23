# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect

from ..generic.cms_metaclass import CmsMetaclass
from ugame.topnav import topnav_site
from ugame.models.all import Raporty
from utils.jinja.filters import url


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_list(self):
        self.game.userprofile.nowe_raporty = 0

        typ = self.request.REQUEST.get('typ', None)

        if self.request.POST.has_key('zaznaczone'):
            zaznaczone = self.request.POST.getlist('zaznaczone')
            if self.request.POST.has_key('del'):
                Raporty.objects.filter(user=self.game.user, pk__in=zaznaczone).delete()

        if typ == 'powrot':
            raporty = Raporty.objects.filter(user=self.game.user, typ='B').order_by("-id")
        elif typ == 'kolonizacja':
            raporty = Raporty.objects.filter(user=self.game.user, typ='K').order_by("-id")
        elif typ == 'przeslij':
            raporty = Raporty.objects.filter(user=self.game.user, typ='P').order_by("-id")
        elif typ == 'transport':
            raporty = Raporty.objects.filter(user=self.game.user, typ='T').order_by("-id")
        elif typ == 'atak':
            raporty = Raporty.objects.filter(user=self.game.user, typ='A').order_by("-id")
        elif typ == 'zlom':
            raporty = Raporty.objects.filter(user=self.game.user, typ='Z').order_by("-id")
        elif typ == 'szpieg':
            raporty = Raporty.objects.filter(user=self.game.user, typ='S').order_by("-id")
        elif typ == 'all':
            raporty = Raporty.objects.filter(user=self.game.user).order_by("-id")
        else:
            raporty = Raporty.objects.filter(user=self.game.user).exclude(typ='B').order_by("-id")

        topnav = topnav_site(self.game)
        return {"raporty": raporty, "topnav": topnav}

    def site_show(self, object_id):
        topnav = topnav_site(self.game)
        raport = Raporty.objects.get(pk=object_id, user=self.game.user)
        if self.request.REQUEST.get('delete', None):
            raport.delete()
            return HttpResponseRedirect(url(self.urls.list))

        return {"raport": raport, "topnav": topnav}
