# -*- coding: utf-8 -*-
from ..generic.cms_metaclass import CmsMetaclass
from ugame.klasy.BaseGame import BaseGame
from ugame.topnav import topnav_site, Output
from ugame.models.all import Buildings, Badania, Flota, Obrona
from utils.jinja.filters import url
from django.http import HttpResponseRedirect


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        GraObject = BaseGame(self)
        sojusz_uzytkownika = GraObject.get_sojusz()
        if sojusz_uzytkownika:
            return HttpResponseRedirect(url(self.urls.my))

        topnav = topnav_site(GraObject)
        zaproszenia = GraObject.user.zaproszenia_set.order_by("data")
        return {
                "topnav": topnav,
                "zaproszenia": zaproszenia,
                }
    site_main.url = "^ugame/alliance/$"

    def site_my(self):
        GraObject = BaseGame(self)
        sojusz_uzytkownika = GraObject.get_sojusz()
        if not sojusz_uzytkownika:
            return HttpResponseRedirect(url(self.urls.main))

        topnav = topnav_site(GraObject)
        zaproszenia = GraObject.user.zaproszenia_set.order_by("data")
        return {
                "topnav": topnav, "sojusz": sojusz_uzytkownika,
                "GraObject": GraObject, "zaproszenia": zaproszenia,
                }
