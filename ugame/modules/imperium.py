# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.http import HttpResponseRedirect

from ugame.models import send_error_message
from ugame.models.all import Badania
from ugame.models.all import Buildings
from ugame.models.all import Flota
from ugame.models.all import Obrona
from ugame.topnav import Output
from ugame.topnav import topnav_site
from utils.jinja.filters import url

from ..generic.cms_metaclass import CmsMetaclass


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

        planety = self.game.get_all_planets()

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
                self.game.cron_function(p_id)
                planeta = self.game.get_planet(p_id)
                pl = Output()
                pl.planeta = planeta
                pl.budynki = []
                for b in budynki:
                    level = self.game.bud_get_level(planeta, b.pk)
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
                level = self.game.bad_get_level(self.game.user, b.pk)
                if b.pk in razem:
                    razem[b.pk] += level
                else:
                    razem[b.pk] = level
                planets.append(level)

        elif typ == 'flota':
            floty = Flota.objects.all().order_by('id')
            colspan = len(floty)
            for p_id in planety:
                self.game.cron_function(p_id)
                planeta = self.game.get_planet(p_id)
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
                self.game.cron_function(p_id)
                planeta = self.game.get_planet(p_id)
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
                planeta = self.game.get_planet(p_id)
                self.game.cron_function(p_id)
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

        topnav = topnav_site(self.game)
        return {
            'topnav': topnav, "colspan": colspan, "razem": razem,
            "planety": planets, "budynki": budynki, "badania": badania,
            "obrona": obrona, "floty": floty, "typ": typ
        }

    site_main.url = "^ugame/imperium/$"

    def site_change_planets_order(self):
        planety = self.game.get_all_planets()

        for p_id in planety:
            planeta = self.game.get_planet(p_id)
            kolej_str = 'kolej_%s' % (p_id)
            if kolej_str in self.request.POST:
                try:
                    planeta.kolej = int(self.request.POST[kolej_str])
                except:
                    pass
        message='Kolejność planet została uaktualniona'
        send_error_message(user=self.game.user, message=message)

        redirect_url = url(self.urls.main)
        if 'HTTP_REFERER' in self.request.META:
            if len(self.request.META['HTTP_REFERER']) > 3:
                redirect_url = self.request.META['HTTP_REFERER']

        return HttpResponseRedirect(redirect_url)
