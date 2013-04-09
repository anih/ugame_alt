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
from ugame.models.all import Buildings, Flota_f

class Output:pass

class BuildFleet():


    def buduj_flote(self, bud, ilosc):
        # query = "lock table game_flota_f in ACCESS EXCLUSIVE MODE"
        # cursor = connection.cursor()
        # cursor.execute(query)
        planeta = self.get_current_planet()
        if planeta:
            flota = Output()
            flota.c_met = bud.c_met * ilosc
            flota.c_cry = bud.c_cry * ilosc
            flota.c_deu = bud.c_deu * ilosc
            flota.c_czas = (bud.c_cry + bud.c_met) / GAME_SPEED
            flota.mozna = 1
            for i in Buildings.objects.filter(minus_czas_flota_tak__gt=0):
                level = floor(self.bud_get_level(planeta, i.id))
                flota.c_czas = flota.c_czas * eval(i.minus_czas_flota)
            flota.c_czas_one = flota.c_czas * 60 * 60
            flota.c_czas = flota.c_czas * 60 * 60 * ilosc


            flota.z_met = planeta.metal - flota.c_met
            if flota.z_met < 0:
                self.user.message_set.create(message=u"Za mało metalu do wybudowania %s" % (bud.nazwa,))
                flota.mozna = None

            flota.z_cry = planeta.crystal - flota.c_cry
            if flota.z_cry < 0:
                self.user.message_set.create(message=u"Za mało kryształu do wybudowania %s" % (bud.nazwa,))
                flota.mozna = None

            flota.z_deu = planeta.deuter - flota.c_deu
            if flota.z_deu < 0:
                self.user.message_set.create(message=u"Za mało deuteru do wybudowania %s" % (bud.nazwa,))
                flota.mozna = None
            zaleznosc = split(bud.w_bud, ";")
            if flota.mozna:
                for zal in zaleznosc:
                    budynek = split(zal, ",")
                    if len(budynek) > 1:
                        if int(budynek[1]) > self.bud_get_level(planeta, budynek[0]):
                            self.user.message_set.create(message=u"Nie spełnione zależności budynków dla %s" % (bud.nazwa,))
                            flota.mozna = None
                            break
            if flota.mozna:
                zaleznosc = split(bud.w_bad, ";")
                for zal in zaleznosc:
                    badanie = split(zal, ",")
                    if len(badanie) > 1:
                        if int(badanie[1]) > self.bad_get_level(self.user, badanie[0]):
                            self.user.message_set.create(message=u"Nie spełnione zależności badań dla %s" % (bud.nazwa,))
                            flota.mozna = None
                            break
            if flota.mozna:
                czas = self.get_flota_kolejka_czas(planeta)
                flota.points = (bud.c_met + bud.c_cry + bud.c_deu) / 1000.0
                kolejka = Flota_f.objects.create(budynek=bud, planeta=planeta, ilosc=ilosc, time=czas + flota.c_czas, points=flota.points, time_one=flota.c_czas_one * (ilosc - 1))
                self.cache_obj.get_flota_f(planeta.pk, kolejka.pk)
                planeta.metal -= flota.c_met
                planeta.crystal -= flota.c_cry
                planeta.deuter -= flota.c_deu


    def anuluj_flote(self, id_poz):
        planeta = self.get_current_planet()
        try:
            id_poz = int(id_poz)
            max_level = self.cache_obj.get_flota_f(planeta.pk, id_poz)
        except:
            max_level = None
        if max_level:
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
            self.cache_obj.del_flota_f(planeta.pk, max_level.pk)

            kolejka = Flota_f.objects.values_list('id', flat=True).select_for_update().filter(planeta=planeta, time__gt=c_czas).order_by("time")
            if len(kolejka) > 0:
                try:
                    poprzednie = Flota_f.objects.select_for_update().filter(planeta=planeta, time__lt=c_czas).order_by("-time")[0]
                    c_czas = c_czas - poprzednie.time
                except:
                    c_czas = c_czas - time()
                for k in kolejka:
                    obj = self.cache_obj.get_flota_f(planeta.pk, k)
                    obj.time -= c_czas
        # except:
            # pass

