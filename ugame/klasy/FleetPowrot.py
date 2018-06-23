# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from string import find
from string import split

from settings import GAME_SPEED
from settings import ILOSC_PLANET
from settings import MNOZNIK_MAGAZYNOW
from settings import RES_SPEED
from ugame.models.all import Flota_p

from ..cron_fun import helpers
from ..cron_fun import raporty_fun
from ..funkcje import lock_user_cron


class Output():pass
class FleetPowrot():
    def flota_powrot(self, flota, czas_teraz):
        galaktyka_end = flota.galaxy_end
        galaktyka_start = flota.galaxy_start
        planeta = self.get_planet(galaktyka_end.planet_id)

        statki = split(flota.fleet_array, ";")

        statki_przeslane = []
        for s in statki:
            statek = split(s, ",")
            statek_id = int(statek[0])
            statek_row = self.cache_obj.get_flota_p(planeta.pk, statek_id)
            if not statek_row:
                Flota_p.objects.create(budynek_id=statek_id, planeta=planeta, ilosc=0)
                statek_row = self.cache_obj.get_flota_p(planeta.pk, statek_id)
            statek_row.ilosc += float(statek[1])

            statki_przeslane.append({"ilosc":statek[1], "nazwa":statek_row.budynek.nazwa})

        planeta.metal += flota.fleet_resource_metal
        planeta.crystal += flota.fleet_resource_crystal
        planeta.deuter += flota.fleet_resource_deuterium

        raporty_fun.rap_powrot(flota, statki_przeslane, self)
        flota.delete()
        return True

    def flota_powrot_alien(self, flota, czas_teraz):
        galaktyka_end = flota.galaxy_end
        galaktyka_start = flota.galaxy_start

        req_alien = Output()
        req_alien.user = flota.fleet_owner_id
        from ..klasy.BaseGame import BaseGame
        GraAlienObj = BaseGame(req_alien, czas_teraz=flota.time - 1, cron=False)
        GraAlienObj.cron_function(flota.galaxy_end.planet_id, flota.time - 1)
        planeta = GraAlienObj.get_planet(galaktyka_end.planet_id)


        statki = split(flota.fleet_array, ";")

        statki_przeslane = []
        for s in statki:
            statek = split(s, ",")
            statek_id = int(statek[0])
            statek_row = GraAlienObj.cache_obj.get_flota_p(planeta.pk, statek_id)
            if not statek_row:
                Flota_p.objects.create(budynek_id=statek_id, planeta=planeta, ilosc=0)
                statek_row = GraAlienObj.cache_obj.get_flota_p(planeta.pk, statek_id)
            statek_row.ilosc += float(statek[1])

            statki_przeslane.append(str(statek[1]) + " " + str(statek_row.budynek.nazwa))

        planeta.metal += flota.fleet_resource_metal
        planeta.crystal += flota.fleet_resource_crystal
        planeta.deuter += flota.fleet_resource_deuterium

        raporty_fun.rap_powrot(flota, statki_przeslane, GraAlienObj)

        flota.delete()

        GraAlienObj.save_all()
        return True
