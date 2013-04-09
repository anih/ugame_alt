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
        try:
            typ = self.request.REQUEST['typ']
        except:
            typ = None

        GraObject = BaseGame(self)
        planety = GraObject.get_all_planets()

        planets = []
        budynki = None
        badania = None
        floty = None
        obrona = None
        razem = {}
        colspan = 0
        if typ == 'budynki':
            budynki = Buildings.objects.all().order_by('id')
            colspan = len(budynki)
            for p_id in planety:
                GraObject.cron_function(p_id)
                planeta = GraObject.get_planet(p_id)
                pl = Output()
                pl.planeta = planeta
                pl.budynki = []
                for b in budynki:
                    level = GraObject.bud_get_level(planeta, b.pk)
                    if b.pk in razem:
                        razem[b.pk] += level
                    else:
                        razem[b.pk] = level
                    pl.budynki.append(level)
                # pl.planeta.powierzchnia_max =  planeta.powierzchnia_max
                planets.append(pl)
        elif typ == 'badania':
            badania = Badania.objects.all().order_by('id')
            colspan = len(badania)
            for b in badania:
                level = GraObject.bad_get_level(GraObject.user, b.pk)
                if b.pk in razem:
                    razem[b.pk] += level
                else:
                    razem[b.pk] = level
                planets.append(level)

        elif typ == 'flota':
            floty = Flota.objects.all().order_by('id')
            colspan = len(floty)
            for p_id in planety:
                GraObject.cron_function(p_id)
                planeta = GraObject.get_planet(p_id)
                pl = Output()
                pl.planeta = planeta
                pl.floty = []
                for f in floty:
                    try:
                        ilosc = planeta.flota_p_set.get(budynek=f).ilosc
                    except:
                        ilosc = 0
                    if f.pk in razem:
                        razem[f.pk] += ilosc
                    else:
                        razem[f.pk] = ilosc
                    pl.floty.append(ilosc)
                planets.append(pl)
        elif typ == 'obrona':
            obrona = Obrona.objects.all().order_by('id')
            colspan = len(obrona)
            for p_id in planety:
                GraObject.cron_function(p_id)
                planeta = GraObject.get_planet(p_id)
                pl = Output()
                pl.planeta = planeta
                pl.obrona = []
                for f in obrona:
                    try:
                        ilosc = planeta.obrona_p_set.get(budynek=f).ilosc
                    except:
                        ilosc = 0
                    if f.pk in razem:
                        razem[f.pk] += ilosc
                    else:
                        razem[f.pk] = ilosc
                    pl.obrona.append(ilosc)
                planets.append(pl)
        else:
            typ = 'surowce'
            razem['met'] = 0
            razem['cry'] = 0
            razem['deu'] = 0
            razem['ene_used'] = 0
            razem['ene_max'] = 0
            for p_id in planety:
                planeta = GraObject.get_planet(p_id)
                GraObject.cron_function(p_id)
                pl = Output()
                pl.planeta = planeta
                razem['met'] += planeta.metal
                razem['cry'] += planeta.crystal
                razem['deu'] += planeta.deuter
                razem['ene_used'] += planeta.energy_used
                razem['ene_max'] += planeta.energy_max
                pl.planeta.powierzchnia_max = planeta.powierzchnia_max
                planets.append(pl)
        colspan += 5

        topnav = topnav_site(GraObject)
        return {
                'topnav': topnav, "colspan": colspan, "razem": razem,
                "planety": planets, "budynki": budynki, "badania": badania,
                "obrona": obrona, "floty": floty, "typ": typ
                }
    site_main.url = "^ugame/imperium/$"

    def site_change_planets_order(self):
        GraObject = BaseGame(self)
        planety = GraObject.get_all_planets()

        for p_id in planety:
            planeta = GraObject.get_planet(p_id)
            kolej_str = 'kolej_%s' % (p_id)
            if kolej_str in self.request.POST:
                try:
                    planeta.kolej = int(self.request.POST[kolej_str])
                except:
                    pass
        GraObject.user.message_set.create(message='Kolejność planet została uaktualniona')

        redirect_url = url(self.urls.main)
        if 'HTTP_REFERER' in self.request.META:
            if len(self.request.META['HTTP_REFERER']) > 3:
                redirect_url = self.request.META['HTTP_REFERER']

        return HttpResponseRedirect(redirect_url)