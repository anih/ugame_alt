# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import sqrt
from string import split
from time import localtime
from time import strftime
from time import time

from django.contrib.auth.models import User

from ugame.models.all import Galaxy
from ugame.models.all import Planets


class BaseHelper():
    current_planet_id = None
    user_planets = {}
    galaktyki = {}


    def bud_get_level(self, planet, id, kolejka=0):
        # id = int(id)
        level = 0
        if(kolejka > 0):
            try:
                obj = planet.budynki_f_set.filter(budynek=id).order_by('-level')[0]
                self.cache_obj.get_budynek_f(planet.pk, obj.pk)
            except:pass

            if planet.pk in self.cache_obj.cache_budynki_f:
                for pk in self.cache_obj.cache_budynki_f[planet.pk]:
                    if self.cache_obj.cache_budynki_f[planet.pk][pk].budynek_id == id:
                        if self.cache_obj.cache_budynki_f[planet.pk][pk].level > level:
                            level = self.cache_obj.cache_budynki_f[planet.pk][pk].level

        if not level > 0:
            obj = self.cache_obj.get_budynek_p(planet.pk, id)
            if obj:
                level = obj.level
        return int(level)


    def bad_get_level(self, user, id, kolejka=0):
        level = 0
        if(kolejka > 0):
            try:
                obj = user.badania_f_set.filter(badanie=id).order_by('-level')[0]
                self.cache_obj.get_badanie_f(user.pk, obj.pk)
            except:pass
            if user.pk in self.cache_obj.cache_badania_f:
                for pk in self.cache_obj.cache_badania_f[user.pk]:
                    if self.cache_obj.cache_badania_f[user.pk][pk].badanie_id == id:
                        if self.cache_obj.cache_badania_f[user.pk][pk].level > level:
                            level = self.cache_obj.cache_badania_f[user.pk][pk].level

        if not level > 0:
            obj = self.cache_obj.get_badanie_p(user.pk, id)
            if obj:
                level = obj.level
        return int(level)
    def get_flota_kolejka_czas(self, planeta):
        czas = time()
        try:
            obj = planeta.flota_f_set.order_by("-time")[0]
            self.cache_obj.get_flota_f(planeta.pk, obj.pk)
        except:pass
        if planeta.pk in self.cache_obj.cache_flota_f:
            for fl  in self.cache_obj.cache_flota_f[planeta.pk]:
                if not czas > self.cache_obj.cache_flota_f[planeta.pk][fl].time:
                    czas = self.cache_obj.cache_flota_f[planeta.pk][fl].time

        return czas

    def get_obrona_kolejka_czas(self, planeta):
        czas = time()
        try:
            obj = planeta.obrona_f_set.order_by("-time")[0]
            self.cache_obj.get_obrona_f(planeta.pk, obj.pk)
        except:pass
        if planeta.pk in self.cache_obj.cache_obrona_f:
            for fl  in self.cache_obj.cache_obrona_f[planeta.pk]:
                if not czas > self.cache_obj.cache_obrona_f[planeta.pk][fl].time:
                    czas = self.cache_obj.cache_obrona_f[planeta.pk][fl].time

        return czas

    def get_budynki_kolejka_czas(self, planeta):
        czas = time()
        try:
            obj = planeta.budynki_f_set.order_by("-time")[0]
            self.cache_obj.get_budynek_f(planeta.pk, obj.pk)
        except:pass
        if planeta.pk in self.cache_obj.cache_budynki_f:
            for fl  in self.cache_obj.cache_budynki_f[planeta.pk]:
                if not czas > self.cache_obj.cache_budynki_f[planeta.pk][fl].time:
                    czas = self.cache_obj.cache_budynki_f[planeta.pk][fl].time

        return czas

    def get_badania_kolejka_czas(self, user):
        czas = time()
        try:
            obj = user.badania_f_set.order_by("-time")[0]
            self.cache_obj.get_badanie_f(user.pk, obj.pk)
        except:pass
        if user.pk in self.cache_obj.cache_badania_f:
            for fl  in self.cache_obj.cache_badania_f[user.pk]:
                if not czas > self.cache_obj.cache_badania_f[user.pk][fl].time:
                    czas = self.cache_obj.cache_badania_f[user.pk][fl].time

        return czas




    def get_all_planets(self):
        planety = list(Planets.objects.values_list('id', flat=True).select_for_update().filter(owner=self.user))
        return planety

    def get_current_planet(self):
        return self.get_planet(self.current_planet_id)

    def get_planet(self, id_planety):
        id_planety = int(id_planety)
        if self.user_planets.has_key(id_planety):
            return self.user_planets[id_planety]
        else:
            if Planets.objects.filter(pk=id_planety).count() > 0:
                planeta = Planets.objects.select_for_update().get(pk=id_planety)
                self.user_planets[id_planety] = planeta
                return self.user_planets[id_planety]
            else:
                return None

    def get_galaxy(self, id_galaxy):
        id_galaxy = int(id_galaxy)
        if self.galaktyki.has_key(id_galaxy):
            return self.galaktyki[id_galaxy]
        else:
            if Galaxy.objects.filter(pk=id_galaxy).count() > 0:
                galaxy = Galaxy.objects.select_for_update().get(pk=id_galaxy)
                self.galaktyki[id_galaxy] = galaxy
                return self.galaktyki[id_galaxy]
            else:
                return None


    def rename_planet(self, name):
        planeta = self.get_planet(self.current_planet_id)
        planeta.name = name
