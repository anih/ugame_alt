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
class FleetPrzeslij():
    def flota_przeslij_alien(self, flota, czas_teraz):
        galaktyka_end = flota.galaxy_end
        galaktyka_start = flota.galaxy_start

        req_alien = Output()
        req_alien.user = flota.fleet_owner
        from ..klasy.BaseGame import BaseGame
        GraAlienObj = BaseGame(req_alien, czas_teraz=flota.time - 1, cron=False)


        planeta = self.get_planet(galaktyka_end.planet_id)

        flota.bak = int(flota.bak / 2)
        planeta.metal += flota.fleet_resource_metal
        planeta.crystal += flota.fleet_resource_crystal
        planeta.deuter += flota.fleet_resource_deuterium + flota.bak

        statki = split(flota.fleet_array, ";")

        statki_przeslane = []

        for i in statki:
            tmp = split(i, ",")
            statek_id = int(tmp[0])
            statek_ilosc = int(tmp[1])
            statek_row = self.cache_obj.get_flota_p(planeta.pk, statek_id)
            if not statek_row:
                Flota_p.objects.create(budynek_id=statek_id, planeta=planeta, ilosc=0)
                statek_row = self.cache_obj.get_flota_p(planeta.pk, statek_id)
            statek_row.ilosc += float(statek_ilosc)

            statki_przeslane.append({"ilosc":statek_ilosc, "nazwa":statek_row.budynek.nazwa})

        raporty_fun.rap_przeslij(flota, statki_przeslane, GraAlienObj)
        raporty_fun.rap_przeslij(flota, statki_przeslane, self)

        GraAlienObj.save_all()
        flota.delete()
        return True

    def flota_przeslij(self, flota, czas_teraz):
        galaktyka_end = flota.galaxy_end
        galaktyka_start = flota.galaxy_start

        if not galaktyka_end.planet.owner_id == self.user.pk:
            req_alien = Output()
            req_alien.user = flota.galaxy_end.planet.owner
            from ..klasy.BaseGame import BaseGame
            GraAlienObj = BaseGame(req_alien, czas_teraz=flota.time - 1, cron=False)
            GraAlienObj.cron_function(flota.galaxy_end.planet_id, flota.time - 1)
            planeta = GraAlienObj.get_planet(galaktyka_end.planet_id)
        else:
            planeta = self.get_planet(galaktyka_end.planet_id)
            GraAlienObj = self

        flota.bak = int(flota.bak / 2)

        planeta.metal += flota.fleet_resource_metal
        planeta.crystal += flota.fleet_resource_crystal
        planeta.deuter += flota.fleet_resource_deuterium + flota.bak

        statki = split(flota.fleet_array, ";")

        statki_przeslane = []

        for i in statki:
            tmp = split(i, ",")
            statek_id = int(tmp[0])
            statek_ilosc = int(tmp[1])
            statek_row = GraAlienObj.cache_obj.get_flota_p(planeta.pk, statek_id)
            if not statek_row:
                Flota_p.objects.create(budynek_id=statek_id, planeta=planeta, ilosc=0)
                statek_row = GraAlienObj.cache_obj.get_flota_p(planeta.pk, statek_id)
            statek_row.ilosc += float(statek_ilosc)

            statki_przeslane.append({"ilosc":statek_ilosc, "nazwa":statek_row.budynek.nazwa})

        raporty_fun.rap_przeslij(flota, statki_przeslane, self)
        if not planeta.owner_id == self.user.pk:
            raporty_fun.rap_przeslij(flota, statki_przeslane, GraAlienObj)
            GraAlienObj.save_all()

        flota.delete()
        return True
