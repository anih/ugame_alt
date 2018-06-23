# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import floor

from django.shortcuts import get_object_or_404

from settings import MNOZNIK_MAGAZYNOW
from ugame.klasy.BaseGame import Output
from ugame.models.all import Badania
from ugame.models.all import Budynki_p
from ugame.models.all import Buildings
from ugame.models.all import Flota
from ugame.models.all import Obrona
from ugame.topnav import topnav_site

from ..generic.cms_metaclass import CmsMetaclass


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_budynki(self, object_id=0):
        planeta = self.game.get_current_planet()

        budynek = get_object_or_404(Buildings, pk=object_id)
        produkcja = []
        magazyn = None
        pp = Output()
        try:
            level_od = Budynki_p.objects.get(planeta=planeta, budynek=budynek).level
        except:
            level_od = 1
        if budynek.mag_met > 0 or budynek.mag_cry > 0 or budynek.mag_deu > 0:
            magazyn = []
            for i in range(level_od, level_od + 10):
                magazyn.append([i, int(floor(10000 * MNOZNIK_MAGAZYNOW * pow(1.5, i)))])

        if budynek.czy_produkcja > 0:
            procent = 100
            temp_max = planeta.temp_max
            energia = 0
            metal = 0
            krysztal = 0
            deuter = 0
            for i in range(level_od, level_od + 10):
                prod = Output()
                level = prod.level = i

                prod.energia = int(eval(budynek.ene_formula))
                if energia > 0: prod.energia_plus = prod.energia - energia
                energia = prod.energia

                prod.metal = int(eval(budynek.met_formula))
                if metal > 0: prod.metal_plus = prod.metal - metal
                metal = prod.metal

                prod.krysztal = int(eval(budynek.cry_formula))
                if krysztal > 0: prod.krysztal_plus = prod.krysztal - krysztal
                krysztal = prod.krysztal

                prod.deuter = int(eval(budynek.deu_formula))
                if deuter > 0: prod.deuter_plus = prod.deuter - deuter
                deuter = prod.deuter

                if (prod.metal > 0): pp.metal = "#00ff00"
                if (prod.metal < 0): pp.metal = "#ff0000"
                if (prod.krysztal > 0): pp.krysztal = "#00ff00"
                if (prod.krysztal < 0): pp.krysztal = "#ff0000"
                if (prod.deuter > 0): pp.deuter = "#00ff00"
                if (prod.deuter < 0): pp.deuter = "#ff0000"
                if (prod.energia > 0): pp.energia = "#00ff00"
                if (prod.energia < 0): pp.energia = "#ff0000"
                produkcja.append(prod)

        topnav = topnav_site(self.game)
        return {"topnav": topnav, "budynek": budynek, "pp": pp, "produkcja": produkcja, "magazyn": magazyn}

    def site_badania(self, object_id=0):
        planeta = self.game.get_current_planet()

        budynek = get_object_or_404(Badania, pk=object_id)

        topnav = topnav_site(self.game)

        return {"topnav": topnav, "budynek": budynek}

    def site_flota(self, object_id=0):
        planeta = self.game.get_current_planet()

        budynek = get_object_or_404(Flota, pk=object_id)
        budynek.opis_dlugi = unicode(budynek.opis_dlugi).replace("\n", "<br>")

        topnav = topnav_site(self.game)
        return {"topnav": topnav, "budynek": budynek}

    def site_obrona(self, object_id=0):
        planeta = self.game.get_current_planet()

        budynek = get_object_or_404(Obrona, pk=object_id)
        budynek.opis_dlugi = unicode(budynek.opis_dlugi).replace("\n", "<br>")

        topnav = topnav_site(self.game)
        return {"topnav": topnav, "budynek": budynek}
