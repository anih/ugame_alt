# -*- coding: utf-8 -*-
from ..generic.cms_metaclass import CmsMetaclass
from ugame.topnav import topnav_site, Output
from ugame.models.all import Buildings, Flota


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        current_planet = self.game.get_current_planet()

        budynki_produkujace = Buildings.objects.filter(czy_produkcja__gt=0)
        flota_produkujaca = Flota.objects.filter(czy_produkcja__gt=0)

        budynki = current_planet.budynki_p_set.filter(budynek__in=budynki_produkujace).order_by("budynek")
        flota = current_planet.flota_p_set.filter(budynek__in=flota_produkujaca).order_by("budynek")

        if self.request.POST:

            for tmp in budynki:
                b = self.game.cache_obj.get_budynek_p(current_planet.pk, tmp.budynek_id)
                if b:
                    building_key = "bud_%s" % b.budynek_id
                    if building_key in self.request.POST:
                        try:
                            tmp_procenty = int(self.request.POST[building_key])
                            if (tmp_procenty <= 100) and tmp_procenty >= 0:
                                b.procent = tmp_procenty
                        except:
                            pass

            for tmp in flota:
                b = self.game.cache_obj.get_flota_p(current_planet.pk, tmp.budynek_id)
                if b:
                    building_key = "flo_%s" % b.budynek_id
                    if building_key in self.request.POST:
                        try:
                            tmp_procenty = int(self.request.POST[building_key])
                            if (tmp_procenty <= 100) and tmp_procenty >= 0:
                                b.procent = tmp_procenty
                        except:
                            pass

        # self.game.cron_function(current_planet.pk)
        # self.game.save_all()
        surowce = []

        resources = []
        for tmp in budynki:
            i = Output()
            i.dane = self.game.cache_obj.get_budynek_p(current_planet.pk, tmp.budynek_id)
            i.czy_budynek = 1
            resources.append(i)
        for tmp in flota:
            i = Output()
            i.dane = self.game.cache_obj.get_flota_p(current_planet.pk, tmp.budynek_id)
            i.czy_statek = 1
            resources.append(i)

        produkcja = Output()
        produkcja.metal = 0
        produkcja.crystal = 0
        produkcja.deuter = 0
        produkcja.energy = 0
        ilosc_produkujacych = 0
        procenty = 0
        for b in resources:
            sur = Output()
            statek = b.dane
            sur.statek = b
            sur.nazwa = statek.budynek.nazwa
            procent = statek.procent
            procenty += procent
            ilosc_produkujacych += 1
            level = statek.level
            ilosc = statek.ilosc
            temp_max = current_planet.temp_max
            # sur.metal = sur.crystal = sur.deuter = sur.energy = 0
            sur.metal = int(eval(statek.budynek.met_formula))
            sur.id = statek.budynek_id
            produkcja.metal += sur.metal
            sur.crystal = int(eval(statek.budynek.cry_formula))
            produkcja.crystal += sur.crystal
            sur.deuter = int(eval(statek.budynek.deu_formula))
            produkcja.deuter += sur.deuter
            sur.energy = int(eval(statek.budynek.ene_formula))
            produkcja.energy += sur.energy
            surowce.append(sur)

        try:
            produkcja.procent = int(procenty / ilosc_produkujacych)
        except:
            produkcja.procent = 0

        produkcja.metal_dzien = produkcja.metal * 24
        produkcja.metal_tydzien = produkcja.metal_dzien * 7
        produkcja.metal_miesiac = produkcja.metal_dzien * 30
        produkcja.metal_ladownosc_procent = int(current_planet.metal * 100 / current_planet.metal_max)

        produkcja.crystal_dzien = produkcja.crystal * 24
        produkcja.crystal_tydzien = produkcja.crystal_dzien * 7
        produkcja.crystal_miesiac = produkcja.crystal_dzien * 30
        produkcja.crystal_ladownosc_procent = int(current_planet.crystal * 100 / current_planet.crystal_max)

        produkcja.deuter_dzien = produkcja.deuter * 24
        produkcja.deuter_tydzien = produkcja.deuter_dzien * 7
        produkcja.deuter_miesiac = produkcja.deuter_dzien * 30
        produkcja.deuter_ladownosc_procent = int(current_planet.deuter * 100 / current_planet.deuter_max)

        topnav = topnav_site(self.game)
        return {
            'topnav': topnav, "surowce": surowce,
            "planet": current_planet, "produkcja": produkcja
        }

    site_main.url = "^ugame/resources/$"
