# -*- coding: utf-8 -*-
from string import split

from ..generic.cms_metaclass import CmsMetaclass
from ugame.topnav import topnav_site, Output
from ugame.models.all import Buildings, Badania, Flota, Obrona


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        current_planet = self.game.get_current_planet()

        bud = Buildings.objects.all()
        bad = Badania.objects.all()
        flo = Flota.objects.all()
        obr = Obrona.objects.all()

        budynki = []
        for i in bud:
            budynek = Output()
            budynek.id = i.pk
            budynek.nazwa = i.nazwa
            budynek.zal_bud = []
            for zal_b in split(i.w_bud, ";"):
                zbud = split(zal_b, ",")
                if len(zbud) > 1:
                    tmp = Output()
                    tmp.nazwa = Buildings.objects.get(pk=zbud[0]).nazwa
                    tmp.level = zbud[1]
                    level = int(self.game.bud_get_level(current_planet, zbud[0]))
                    if int(zbud[1]) <= level:
                        tmp.spelnione = 1
                    budynek.zal_bud.append(tmp)

            budynek.zal_bad = []
            for zal_b in split(i.w_bad, ";"):
                zbud = split(zal_b, ",")
                if len(zbud) > 1:
                    tmp = Output()
                    tmp.nazwa = Badania.objects.get(pk=zbud[0]).nazwa
                    tmp.level = zbud[1]
                    level = int(self.game.bad_get_level(self.game.user, zbud[0]))
                    if int(zbud[1]) <= level:
                        tmp.spelnione = 1
                    budynek.zal_bad.append(tmp)
            budynki.append(budynek)

        badania = []
        for i in bad:
            badanie = Output()
            badanie.id = i.pk
            badanie.nazwa = i.nazwa
            badanie.zal_bud = []
            for zal_b in split(i.w_bud, ";"):
                zbud = split(zal_b, ",")
                if len(zbud) > 1:
                    tmp = Output()
                    tmp.nazwa = Buildings.objects.get(pk=zbud[0]).nazwa
                    tmp.level = zbud[1]
                    level = int(self.game.bud_get_level(current_planet, zbud[0]))
                    if int(zbud[1]) <= level:
                        tmp.spelnione = 1
                    badanie.zal_bud.append(tmp)

            badanie.zal_bad = []
            for zal_b in split(i.w_bad, ";"):
                zbud = split(zal_b, ",")
                if len(zbud) > 1:
                    tmp = Output()
                    tmp.nazwa = Badania.objects.get(pk=zbud[0]).nazwa
                    tmp.level = zbud[1]
                    level = int(self.game.bad_get_level(self.game.user, zbud[0]))
                    if int(zbud[1]) <= level:
                        tmp.spelnione = 1
                    badanie.zal_bad.append(tmp)
            badania.append(badanie)

        floty = []
        for i in flo:
            flota = Output()
            flota.id = i.pk
            flota.nazwa = i.nazwa
            flota.zal_bud = []
            for zal_b in split(i.w_bud, ";"):
                zbud = split(zal_b, ",")
                if len(zbud) > 1:
                    tmp = Output()
                    tmp.nazwa = Buildings.objects.get(pk=zbud[0]).nazwa
                    tmp.level = zbud[1]
                    level = int(self.game.bud_get_level(current_planet, zbud[0]))
                    if int(zbud[1]) <= level:
                        tmp.spelnione = 1
                    flota.zal_bud.append(tmp)

            flota.zal_bad = []
            for zal_b in split(i.w_bad, ";"):
                zbud = split(zal_b, ",")
                if len(zbud) > 1:
                    tmp = Output()
                    tmp.nazwa = Badania.objects.get(pk=zbud[0]).nazwa
                    tmp.level = zbud[1]
                    level = int(self.game.bad_get_level(self.game.user, zbud[0]))
                    if int(zbud[1]) <= level:
                        tmp.spelnione = 1
                    flota.zal_bad.append(tmp)
            floty.append(flota)

        obronne = []
        for i in obr:
            obrona = Output()
            obrona.id = i.pk
            obrona.nazwa = i.nazwa
            obrona.zal_bud = []
            for zal_b in split(i.w_bud, ";"):
                zbud = split(zal_b, ",")
                if len(zbud) > 1:
                    tmp = Output()
                    tmp.nazwa = Buildings.objects.get(pk=zbud[0]).nazwa
                    tmp.level = zbud[1]
                    level = int(self.game.bud_get_level(current_planet, zbud[0]))
                    if int(zbud[1]) <= level:
                        tmp.spelnione = 1
                    obrona.zal_bud.append(tmp)

            obrona.zal_bad = []
            for zal_b in split(i.w_bad, ";"):
                zbud = split(zal_b, ",")
                if len(zbud) > 1:
                    tmp = Output()
                    tmp.nazwa = Badania.objects.get(pk=zbud[0]).nazwa
                    tmp.level = zbud[1]
                    level = int(self.game.bad_get_level(self.game.user, zbud[0]))
                    if int(zbud[1]) <= level:
                        tmp.spelnione = 1
                    obrona.zal_bad.append(tmp)
            obronne.append(obrona)

        topnav = topnav_site(self.game)
        return {
            "topnav": topnav, "budynki": budynki,
            "badania": badania, "floty": floty, "obronne": obronne,
        }

    site_main.url = "^ugame/technology/$"
