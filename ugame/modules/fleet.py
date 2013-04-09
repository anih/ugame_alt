# -*- coding: utf-8 -*-
from ..generic.cms_metaclass import CmsMetaclass
from ugame.klasy.BaseGame import BaseGame
from ugame.topnav import topnav_site
from ugame.models.all import Flota_p, Planets
from django.core.paginator import Paginator
from ugame.funkcje import zawroc, get_speed, get_flota
from django.http import HttpResponseRedirect


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        GraObject = BaseGame(self)
        GraObject.userprofile_podglad_flota()
        current_planet = GraObject.get_current_planet()

        if "fast_fleet_del" in self.request.REQUEST:
            GraObject.userprofile.fast_fleet.remove(self.request.REQUEST['fast_fleet_del'])
        if "fast_fleet_add" in self.request.REQUEST:
            try:
                fast_planet = Planets.objects.get(pk=self.request.REQUEST['fast_fleet_add'])
                GraObject.userprofile.fast_fleet.add(fast_planet)
            except:
                pass

        try:
            page = int(self.request.REQUEST['page'])
            if not page > 0:
                page = 1
        except:
            page = 1
        paginator = Paginator(GraObject.userprofile.fast_fleet.all(), 20, allow_empty_first_page=True)
        if page > paginator.num_pages:
            page = paginator.num_pages

        p = paginator.page(page)
        fast_fleet = p.object_list

        if "fs_zawroc" in self.request.REQUEST:
            GraObject.user.message_set.create(message="Flotę zawrócono")
            zawroc(self.request.REQUEST['fs_zawroc'], GraObject.user)

        if "g" in self.request.REQUEST and "s" in self.request.REQUEST and "p" in self.request.REQUEST and "typ" in self.request.REQUEST:
            try:
                g = int(self.request.REQUEST['g'])
                s = int(self.request.REQUEST['s'])
                p = int(self.request.REQUEST['p'])
                if self.request.REQUEST['typ'] == 'a':
                    return HttpResponseRedirect("/game/fs/atak/?g=%d&s=%d&p=%d" % (g, s, p))
                elif self.request.REQUEST['typ'] == 'k':
                    return HttpResponseRedirect("/game/fs/kolonizuj/?g=%d&s=%d&p=%d" % (g, s, p))
                elif self.request.REQUEST['typ'] == 'p':
                    return HttpResponseRedirect("/game/fs/przeslij/?g=%d&s=%d&p=%d" % (g, s, p))
                elif self.request.REQUEST['typ'] == 't':
                    return HttpResponseRedirect("/game/fs/surowce/?g=%d&s=%d&p=%d" % (g, s, p))
                elif self.request.REQUEST['typ'] == 'z':
                    return HttpResponseRedirect("/game/fs/zlom/?g=%d&s=%d&p=%d" % (g, s, p))
                elif self.request.REQUEST['typ'] == 's':
                    return HttpResponseRedirect("/game/fs/spy/?g=%d&s=%d&p=%d" % (g, s, p))
            except:
                GraObject.user.message_set.create(message="Wprowadź poprawne dane do ataku")
                pass

        dostepne_statki_tmp = Flota_p.objects.filter(planeta=current_planet, budynek__lata__gt=0, ilosc__gt=0).order_by("budynek")
        dostepne_statki = []
        for i in dostepne_statki_tmp:
            d = i
            d.speed = int(get_speed(GraObject, i.budynek, GraObject.user))
            dostepne_statki.append(d)

        # userprofile.fast_fleet.add(planeta)

        floty_own, floty_obce, _ = get_flota(GraObject)
        topnav = topnav_site(GraObject)
        return {
                "paginator": paginator, "fast_fleet": fast_fleet,
                "floty_own": floty_own, "floty_obce": floty_obce,
                'topnav': topnav, "dostepne_statki": dostepne_statki
                }

    site_main.url = "^ugame/fleet/$"
