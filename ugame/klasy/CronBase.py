# -*- coding: utf-8 -*-
from __future__ import division
from time import localtime, strftime, time
from string import split
from math import sqrt

from django.db.models import Q
from ugame.models.all import Budynki_f, Badania_f, Flota_f, Obrona_f, Galaxy, \
    Fleets

def sort_queue(x, y):
    return cmp(x.time, y.time)
from ..klasy.CronSurowce import CronSurowce
from ..klasy.FleetMain import FleetMain


class CronBase(CronSurowce, FleetMain):

    def cron_function(self, id_planety, czas_teraz=None):
        if not czas_teraz:
            czas_teraz = int(time())

        planeta = self.get_planet(id_planety)
        last_update = planeta.last_update
        if not planeta.last_update > czas_teraz:
            planeta.last_update = czas_teraz
        else:
            return True


        kolejka_budynki = Budynki_f.objects.select_for_update().filter(planeta=planeta, time__lte=czas_teraz).order_by("time")
        kolejka_badania = Badania_f.objects.select_for_update().filter(user=self.user, time__lte=czas_teraz).order_by("time")
        kolejka_flota = Flota_f.objects.select_for_update().filter(planeta=planeta).extra(where=[" (time - time_one <=  '" + str(czas_teraz) + "')  "])
        kolejka_obrona = Obrona_f.objects.select_for_update().filter(planeta=planeta).extra(where=[" (time - time_one <=  '" + str(czas_teraz) + "')  "])

        galaktyki_usera = Galaxy.objects.filter(planet__in=self.get_all_planets())
        kolejka_fleet = Fleets.objects.select_for_update().filter(Q(fleet_owner=self.user) | Q(galaxy_end__in=galaktyki_usera)).filter(time__lte=czas_teraz).order_by("time")

        kolejka = []
        for i in kolejka_badania:
            kolejka.append(i)
        for i in kolejka_budynki:
            kolejka.append(i)
        for i in kolejka_flota:
            kolejka.append(i)
        for i in kolejka_obrona:
            kolejka.append(i)
        for i in kolejka_fleet:
            kolejka.append(i)

        kolejka.sort(sort_queue)

        czas = czas_teraz

        for buduj in kolejka:

            if isinstance(buduj, Budynki_f):
                czas = buduj.time
                self.update_sur(czas, id_planety, last_update)
                last_update = czas
                self.update_budynek(buduj, id_planety, buduj.time)

            elif isinstance(buduj, Badania_f):
                czas = buduj.time
                self.update_sur(czas, id_planety, last_update)
                last_update = czas
                self.update_badanie(buduj, id_planety, buduj.time)

            elif isinstance(buduj, Flota_f):
                self.update_flota(buduj, id_planety, czas_teraz)

            elif isinstance(buduj, Obrona_f):
                self.update_obrona(buduj, id_planety, czas_teraz)

            elif isinstance(buduj, Fleets):
                czas = buduj.time
                self.update_sur(czas, id_planety, last_update)
                last_update = czas
                self.flota_update(buduj, buduj.time)

        if last_update < czas_teraz:
            self.update_sur(czas_teraz, id_planety, last_update)
