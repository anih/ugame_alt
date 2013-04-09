# -*- coding: utf-8 -*-
from __future__ import division
from string import split
from math import floor

from ..cron_fun import helpers, raporty_fun
from ugame.models.all import Fleets, Flota


class Output():
    pass


class FleetZlom():

    def fleet_zlom_alien(self, flota, czas_teraz):
        req_alien = Output()
        req_alien.user = flota.fleet_owner
        from ..klasy.BaseGame import BaseGame
        GraAlienObj = BaseGame(req_alien, czas_teraz=flota.time, cron=False)

        galaktyka = self.get_galaxy(flota.galaxy_end_id)

        floty_wczesniejsze = Fleets.objects.filter(fleet_mission=5, fleet_back__lte=0, time__lt=czas_teraz, galaxy_end=flota.galaxy_end).order_by("time")

        for fl in floty_wczesniejsze:
            req_alien = Output()
            req_alien.user = fl.fleet_owner
            from ..klasy.BaseGame import BaseGame
            GraAlienWszesniejszeObj = BaseGame(req_alien, czas_teraz=flota.time, cron=False)
            print "flota innnaa-----------------------------------------------------------"
            self.fleet_zlomuj(fl, GraAlienWszesniejszeObj, galaktyka)
            GraAlienWszesniejszeObj.save_all()

        self.fleet_zlomuj(flota, GraAlienObj, galaktyka)
        GraAlienObj.save_all()

    def fleet_zlom(self, flota, czas_teraz):
        planeta = flota.galaxy_end.planet

        if planeta.owner and not planeta.owner_id == self.user.pk:
            req_alien = Output()
            req_alien.user = planeta.owner
            print req_alien.user
            print "zlom-----------------------------------------------------------"
            from ..klasy.BaseGame import BaseGame
            GraAlienObj = BaseGame(req_alien, czas_teraz=flota.time, cron=False)
            GraAlienObj.cron_function(planeta.pk, flota.time - 1)
            galaktyka = GraAlienObj.get_galaxy(flota.galaxy_end_id)
        else:
            galaktyka = self.get_galaxy(flota.galaxy_end_id)

        floty_wczesniejsze = Fleets.objects.filter(fleet_mission=5, fleet_back__lte=0, time__lt=czas_teraz, galaxy_end=flota.galaxy_end).order_by("time")

        for fl in floty_wczesniejsze:
            if planeta.owner and not planeta.owner_id == self.user.pk:
                self.fleet_zlomuj(fl, self, galaktyka)
            else:
                req_alien = Output()
                req_alien.user = fl.fleet_owner
                from ..klasy.BaseGame import BaseGame
                GraAlienWszesniejszeObj = BaseGame(req_alien, czas_teraz=flota.time, cron=False)
                print "flota innnaa-----------------------------------------------------------"
                self.fleet_zlomuj(fl, GraAlienWszesniejszeObj, galaktyka)
                GraAlienWszesniejszeObj.save_all()

        self.fleet_zlomuj(flota, self, galaktyka)
        if planeta.owner and not planeta.owner_id == self.user.pk:
            GraAlienObj.save_all()
        '''
        if  planeta.owner and not planeta.owner_id==self.user.pk:
            GraAlienObj.save_all()
        '''

    def fleet_zlomuj(self, flota, GraObj, galaktyka):
        statki = split(flota.fleet_array, ";")
        pojemnosc_floty = 0
        for s in statki:
            st = split(s, ",")
            statek = Flota.objects.get(pk=st[0])
            if statek.recycler:
                pojemnosc_floty += statek.capacity * int(st[1])

        surowce_zdobyte = {}
        print "pojemnosc zlomiarzy:", pojemnosc_floty
        if pojemnosc_floty > 0:
            metal_pojemnosc = floor(pojemnosc_floty / 2)
            if metal_pojemnosc < galaktyka.metal:
                galaktyka.metal -= metal_pojemnosc
                flota.fleet_resource_metal += metal_pojemnosc
            else:
                metal_pojemnosc = galaktyka.metal
                flota.fleet_resource_metal += metal_pojemnosc
                galaktyka.metal = 0

            crystal_pojemnosc = pojemnosc_floty - metal_pojemnosc
            if crystal_pojemnosc < galaktyka.crystal:
                galaktyka.crystal -= crystal_pojemnosc
                flota.fleet_resource_crystal += crystal_pojemnosc
            else:
                crystal_pojemnosc = galaktyka.crystal
                flota.fleet_resource_crystal += crystal_pojemnosc
                galaktyka.crystal = 0

            zostalo_pojemnosc = pojemnosc_floty - metal_pojemnosc - crystal_pojemnosc
            if zostalo_pojemnosc > 0:
                if zostalo_pojemnosc < galaktyka.metal:
                    galaktyka.metal -= zostalo_pojemnosc
                    flota.fleet_resource_metal += zostalo_pojemnosc
                else:
                    zostalo_pojemnosc = galaktyka.metal
                    flota.fleet_resource_metal += zostalo_pojemnosc
                    galaktyka.metal = 0

        raporty_fun.rap_zlom(flota, GraObj)

        helpers.make_fleet_back(flota)
