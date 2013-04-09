# -*- coding: utf-8 -*-
from __future__ import division
from time import localtime, strftime, time
from string import split
from math import sqrt, floor

from django.contrib.auth.models import User

from ..klasy.BaseHelper import BaseHelper
from ..klasy.CronBase import CronBase
from ..cron_fun import helpers
from settings import GAME_SPEED, RES_SPEED

from django.db import connection, backend, models
from ugame.models.all import Badania, Buildings, Budynki_p, Badania_f

class Output:pass

class BuildTech():


    def buduj_technologie(self, bad):
        # query = "lock table game_badania_f in ACCESS EXCLUSIVE MODE"
        # cursor = connection.cursor()
        # cursor.execute(query)
        planeta = self.get_current_planet()
        if planeta:
            badanie = Badania.objects.get(pk=bad)
            build = Output()
            build.level = self.bad_get_level(self.user, badanie.id, 1) + 1
            build.c_met = badanie.c_met * pow(badanie.c_factor, build.level - 1)
            build.c_cry = badanie.c_cry * pow(badanie.c_factor, build.level - 1)
            build.c_deu = badanie.c_deu * pow(badanie.c_factor, build.level - 1)
            build.c_ene = badanie.c_ene * pow(badanie.c_factor, build.level - 1)
            build.c_czas = (build.c_cry + build.c_met + build.c_deu) / GAME_SPEED
            build.mozna = 1
            for i in Buildings.objects.filter(minus_czas_bad_tak__gt=0):
                budynki_laczy_level = i.badania_set.all()
                if len(budynki_laczy_level) > 0:
                    budynki_laczy_level = budynki_laczy_level[0]
                    # try:
                    if True:
                        ilosc_polaczonych = self.user.badania_p_set.filter(badanie=budynki_laczy_level)
                        level = floor(self.bud_get_level(planeta, i.id))
                        if len(ilosc_polaczonych) > 0:
                            ilosc_polaczonych = ilosc_polaczonych[0].level
                            if ilosc_polaczonych > 0:
                                kandydaci = Budynki_p.objects.filter(planeta__owner=self.user, budynek=i).exclude(planeta=planeta).order_by("-level")[:ilosc_polaczonych]
                                for z in kandydaci:
                                    level += floor(z.level)
                    # except:
                    #    level = floor(self.bud_get_level(planetrow, i.id))
                else:
                    level = floor(self.bud_get_level(planeta, i.id))
                build.c_czas = build.c_czas * eval(i.minus_czas_bad)
            build.c_czas = int(build.c_czas * 60 * 60)

            build.z_met = planeta.metal - build.c_met
            if build.z_met < 0:
                build.mozna = None
            build.z_cry = planeta.crystal - build.c_cry
            if build.z_cry < 0:
                build.mozna = None
            build.z_deu = planeta.deuter - build.c_deu
            if build.z_deu < 0:
                build.mozna = None
            if build.mozna:
                zaleznosc = split(badanie.w_bud, ";")
                for zal in zaleznosc:
                    z_bud = split(zal, ",")
                    if len(z_bud) > 1:
                        if(int(z_bud[1]) > int(self.bud_get_level(planeta, z_bud[0]))):
                            build.mozna = None
                if not build.mozna:
                    zaleznosc = split(badanie.w_bad, ";")
                    for zal in zaleznosc:
                        badanie_z = split(zal, ",")
                        if len(badanie_z) > 1:
                            if(int(badanie_z[1]) > int(self.bad_get_level(self.user, badanie_z[0]))):
                                build.mozna = None
                                break
                if build.mozna:
                    czas = self.get_badania_kolejka_czas(self.user)
                    build.points = float(build.c_met + build.c_cry + build.c_deu) / 1000.0

                    kolejka = Badania_f.objects.create(badanie=badanie, planeta=planeta, user=self.user, level=build.level, time=czas + build.c_czas, points=build.points)
                    self.cache_obj.get_badanie_f(self.user.pk, kolejka.pk)
                    planeta.metal -= build.c_met
                    planeta.crystal -= build.c_cry
                    planeta.deuter -= build.c_deu


    def anuluj_technologie(self, id_badanie):
        query = "lock table game_badania_f in ACCESS EXCLUSIVE MODE"
        cursor = connection.cursor()
        cursor.execute(query)
        try:
        # if True:
            id_badanie = int(id_badanie)
            bud_kol = Badania_f.objects.select_for_update().filter(user=self.user, badanie=id_badanie).order_by("-level")[0]
            max_level = self.cache_obj.get_badanie_f(self.user.pk, bud_kol.pk)
        except:
            max_level = None
        if max_level:

            planeta = self.get_planet(max_level.planeta_id)

            id_pozycji = max_level.pk
            level = max_level.level

            badanie = max_level.badanie
            c_met = badanie.c_met * pow(badanie.c_factor, level - 1) * 0.5
            c_cry = badanie.c_cry * pow(badanie.c_factor, level - 1) * 0.5
            c_deu = badanie.c_deu * pow(badanie.c_factor, level - 1) * 0.5
            c_ene = badanie.c_ene * pow(badanie.c_factor, level - 1) * 0.5

            planeta.metal += c_met
            planeta.crystal += c_cry
            planeta.deuter += c_deu


            c_czas = max_level.time
            self.cache_obj.del_badanie_f(self.user.pk, max_level.pk)

            kolejka = Badania_f.objects.values_list('id', flat=True).select_for_update().filter(user=self.user, time__gt=c_czas).order_by("time")
            if len(kolejka) > 0:
                try:
                    poprzednie = Badania_f.objects.select_for_update().filter(user=self.user, time__lt=c_czas).order_by("-time")[0]
                    c_czas = c_czas - poprzednie.time
                except:
                    c_czas = c_czas - time()


                for k in kolejka:
                    obj = self.cache_obj.get_badanie_f(self.user.pk, k)
                    obj.time -= c_czas

            return planeta
