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
from ugame.models.all import Buildings, Obrona_f, Obrona_p

class Output:pass

class BuildObrona():

    def buduj_obrone(self, f, ilosc):
        planeta = self.get_current_planet()
        msg = []
        # query = "lock table game_obrona_f in ACCESS EXCLUSIVE MODE"
        # cursor = connection.cursor()
        # cursor.execute(query)

        if planeta:
            flota = Output()
            flota.c_met = f.c_met * ilosc
            flota.c_cry = f.c_cry * ilosc
            flota.c_deu = f.c_deu * ilosc
            flota.c_czas = (f.c_cry + f.c_met) / GAME_SPEED
            flota.mozna = 1
            for i in Buildings.objects.filter(minus_czas_flota_tak__gt=0):
                level = floor(self.bud_get_level(planeta, i.id))
                flota.c_czas = flota.c_czas * eval(i.minus_czas_flota)
            flota.c_czas_one = flota.c_czas * 60 * 60
            flota.c_czas = (flota.c_czas * 60 * 60) * ilosc

            if f.limit > 0:

                tmp = Obrona_f.objects.filter(planeta=planeta, budynek=f)

                kol_ilosc = 0
                for q in tmp:
                    kol_ilosc += q.ilosc
                try:
                    float.ilosc = Obrona_p.objects.get(planeta=planeta, budynek=f).ilosc
                except:flota.ilosc = 0

                if f.limit < flota.ilosc + kol_ilosc + ilosc:
                    self.user.message_set.create(message="Limit dla " + f.nazwa + " został wyczerpany")
                    flota.mozna = None


            flota.z_met = planeta.metal - flota.c_met
            if flota.z_met < 0:
                self.user.message_set.create(message="Za mało metalu do wybudowania " + f.nazwa)
                flota.mozna = None

            flota.z_cry = planeta.crystal - flota.c_cry
            if flota.z_cry < 0:
                self.user.message_set.create(message="Za mało kryształu do wybudowania " + f.nazwa)
                flota.mozna = None

            flota.z_deu = planeta.deuter - flota.c_deu
            if flota.z_deu < 0:
                self.user.message_set.create(message="Za mało deuteru do wybudowania " + f.nazwa)
                flota.mozna = None
            zaleznosc = split(f.w_bud, ";")
            if flota.mozna:
                for zal in zaleznosc:
                    budynek = split(zal, ",")
                    if len(budynek) > 1:
                        if(int(budynek[1]) > int(self.bud_get_level(planeta, budynek[0]))):
                            self.user.message_set.create(message="Nie spełnione zależności budynków dla " + f.nazwa)
                            flota.mozna = None
                            break
            if flota.mozna:
                zaleznosc = split(f.w_bad, ";")
                for zal in zaleznosc:
                    badanie = split(zal, ",")
                    if len(badanie) > 1:
                        if(int(badanie[1]) > int(self.bad_get_level(self.user, badanie[0]))):
                            self.user.message_set.create(message="Nie spełnione zależności badań dla " + f.nazwa)
                            flota.mozna = None
                            break
            if flota.mozna:
                czas = self.get_obrona_kolejka_czas(planeta)

                flota.points = (f.c_met + f.c_cry + f.c_deu) / 1000.0
                kolejka = Obrona_f.objects.create(budynek=f, planeta=planeta, ilosc=ilosc, time=czas + flota.c_czas, points=flota.points, time_one=flota.c_czas_one * (ilosc - 1), anulowanie=True)
                self.cache_obj.get_obrona_f(planeta.pk, kolejka.pk)
                planeta.metal -= flota.c_met
                planeta.crystal -= flota.c_cry
                planeta.deuter -= flota.c_deu




    def anuluj_obrone(self, id_budynek):
        planeta = self.get_current_planet()
        query = "lock table game_obrona_f in ACCESS EXCLUSIVE MODE"
        cursor = connection.cursor()
        cursor.execute(query)
        try:
        # if True:
            id_budynek = int(id_budynek)
            max_level = self.cache_obj.get_obrona_f(planeta.pk, id_budynek)
            print max_level
        except:
            max_level = None

        if max_level:
            if not max_level.anulowanie == True:return True
            id_pozycji = max_level.pk
            ilosc = max_level.ilosc
            budynek = max_level.budynek
            c_met = budynek.c_met * ilosc
            c_cry = budynek.c_cry * ilosc
            c_deu = budynek.c_deu * ilosc

            planeta.metal += c_met * 0.5
            planeta.crystal += c_cry * 0.5
            planeta.deuter += c_deu * 0.5
            c_czas = max_level.time
            self.cache_obj.del_obrona_f(planeta.pk, max_level.pk)

            kolejka = Obrona_f.objects.values_list('id', flat=True).select_for_update().filter(planeta=planeta, time__gt=c_czas).order_by("time")
            if len(kolejka) > 0:
                try:
                    poprzednie = Obrona_f.objects.select_for_update().filter(planeta=planeta, time__lt=c_czas).order_by("-time")[0]
                    c_czas = c_czas - poprzednie.time
                except:
                    c_czas = c_czas - time()
                for k in kolejka:
                    obj = self.cache_obj.get_obrona_f(planeta.pk, k)
                    obj.time -= c_czas

        return True
