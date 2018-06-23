# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import ceil
from math import floor
from math import pow
from random import randint
from string import find
from string import split
from time import time

from settings import GAME_SPEED
from settings import ILOSC_PLANET
from settings import MNOZNIK_MAGAZYNOW
from settings import RES_SPEED
from ugame.models.all import Fleets
from ugame.models.all import Flota
from ugame.models.all import Galaxy
from ugame.models.all import Planets

from ..cron_fun import helpers
from ..cron_fun import raporty_fun


class Output():pass
class FleetKolonizuj():
    def fleet_kolonizacja_alien(self, flota, czas_teraz):
        req_alien = Output()
        req_alien.user = flota.fleet_owner
        from ..klasy.BaseGame import BaseGame
        GraAlienObj = BaseGame(req_alien, czas_teraz=flota.time, cron=False)

        self.fleet_kolonizuj(flota, GraAlienObj)
        GraAlienObj.save_all()
        # helpers.make_fleet_back(flota)


    def fleet_kolonizacja(self, flota, czas_teraz):

        floty_obce = Fleets.objects.select_for_update().filter(galaxy_end=flota.galaxy_end, time__lt=flota.time).exclude(pk=flota.pk).order_by("time").count()
        ilosc_planet = self.user.planets_set.count()
        if not floty_obce > 0 and not ilosc_planet > ILOSC_PLANET:
            self.fleet_kolonizuj(flota, self)
        elif ilosc_planet > ILOSC_PLANET and not floty_obce > 0:
            raporty_fun.kolonizajca_fail_planety(flota, self)
            helpers.make_fleet_back(flota)
        else:
            flota_kolonizacyjna = Fleets.objects.select_for_update().filter(galaxy_end=flota.galaxy_end, time__lt=flota.time).order_by("time")[0]

            req_alien = Output()
            req_alien.user = flota_kolonizacyjna.fleet_owner
            from ..klasy.BaseGame import BaseGame
            GraAlienObj = BaseGame(req_alien, czas_teraz=flota_kolonizacyjna.time, cron=False)
            self.fleet_kolonizuj(flota_kolonizacyjna, GraAlienObj)

            raporty_fun.kolonizacja_fail_ktoinny(flota, GraAlienObj)
            helpers.make_fleet_back(flota)

            GraAlienObj.save_all()

    def fleet_kolonizuj(self, flota, GraObj):
        new_galaxy = Galaxy.objects.select_for_update().get(pk=flota.galaxy_end_id)
        planeta = Planets.objects.select_for_update().get(pk=new_galaxy.planet_id)
        try:
            kolej_planeta = Planets.objects.filter(owner=GraObj.user).order_by("-kolej")[0].kolej + 1
        except:
            kolej_planeta = 1
            raise
        planeta.kolej = kolej_planeta
        if not planeta.owner:
            if planeta.nowa:
                planet = new_galaxy.field
                if planet == 1 or planet == 2 or planet == 3:
                    powierzchnia_max = randint(150, 200)
                    temp_min = randint(0, 100)
                    temp_max = temp_min + randint(10, 40)
                    image = "trockenplanet"
                elif planet == 4 or planet == 5 or planet == 6:
                    powierzchnia_max = randint(200, 300)
                    temp_min = randint(-25, 75)
                    temp_max = temp_min + randint(10, 40)
                    image = "dschjungelplanet"
                elif planet == 7 or planet == 8 or planet == 9:
                    powierzchnia_max = randint(180, 250)
                    temp_min = randint(-50, 50)
                    temp_max = temp_min + randint(10, 40)
                    image = "normaltempplanet"
                elif planet == 10 or planet == 11 or planet == 12:
                    powierzchnia_max = randint(200, 250)
                    temp_min = randint(-75, 25)
                    temp_max = temp_min + randint(10, 40)
                    image = "wasserplanet"
                else:
                    powierzchnia_max = randint(180, 280)
                    temp_min = randint(-100, 10)
                    temp_max = temp_min + randint(10, 40)
                    image = "eisplanet"
                planet_type = 1
                tmp = randint(1, 10)
                if tmp < 10:image = image + "0" + str(tmp)
                else: image = image + str(tmp)

                planeta.nowa = False
                planeta.name = "Nowa planeta"
                planeta.last_update = flota.time
                planeta.planet_type = planet_type
                planeta.image = image
                planeta.powierzchnia_max = powierzchnia_max
                planeta.powierzchnia_podstawowa = powierzchnia_max
                planeta.powierzchnia_zajeta = 0
                planeta.temp_min = temp_min
                planeta.temp_max = temp_max
                planeta.metal = 500 + flota.fleet_resource_metal
                planeta.metal_max = 10000 * MNOZNIK_MAGAZYNOW
                planeta.crystal = 500 + flota.fleet_resource_crystal
                planeta.crystal_max = 10000 * MNOZNIK_MAGAZYNOW
                planeta.deuter = 100 + flota.fleet_resource_deuterium
                planeta.deuter_max = 10000 * MNOZNIK_MAGAZYNOW

            planeta.owner = GraObj.user

            raporty_fun.kolonizacja_ok(flota, GraObj)

            kolonizacyjne = Flota.objects.filter(kolonizacja__gt=0, lata__gt=0)
            kolonizacyjne_id = []
            for i in kolonizacyjne:kolonizacyjne_id.append(i.pk)
            statki = split(flota.fleet_array, ";")
            statki_left = []
            odjety = None
            for i in statki:
                tmp = split(i, ",")
                if odjety:
                    statki_left.append(i)
                elif int(tmp[0]) in kolonizacyjne_id:
                    odjety = 1
                    if int(tmp[1]) > 1:
                        statki_left.append(tmp[0] + "," + str(int(tmp[1]) - 1))
                else:
                    statki_left.append(i)
            if len(statki_left) > 0:
                flota.fleet_array = ";".join(statki_left)
                flota.fleet_amount -= 1
                flota.fleet_resource_metal = 0
                flota.fleet_resource_crystal = 0
                flota.fleet_resource_deuterium = 0
                helpers.make_fleet_back(flota)
            else:
                planeta.deuter += flota.bak / 2
                flota.delete()
            planeta.save(force_update=True)
        else:
            raporty_fun.kolonizacja_fail_ktoinny(flota, GraObj)
            helpers.make_fleet_back(flota)
