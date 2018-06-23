# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import floor
from string import split
from time import time

from settings import GAME_SPEED
from ugame.models.all import Budynki_f
from ugame.models.all import Buildings


class Output: pass


class BuildBuilding():

    def buduj_budynek(self, bud):
        # query = "lock table game_budynki_f in ACCESS EXCLUSIVE MODE"
        # cursor = connection.cursor()
        # cursor.execute(query)

        planeta = self.get_current_planet()

        if planeta:
            budynek = Buildings.objects.get(pk=bud)
            build = Output()
            build.level = self.bud_get_level(planeta, budynek.id, 1) + 1
            build.c_met = budynek.c_met * pow(budynek.c_factor, build.level - 1)
            build.c_cry = budynek.c_cry * pow(budynek.c_factor, build.level - 1)
            build.c_deu = budynek.c_deu * pow(budynek.c_factor, build.level - 1)
            build.c_ene = budynek.c_ene * pow(budynek.c_factor, build.level - 1)
            build.c_czas = (build.c_cry + build.c_met) / GAME_SPEED

            if (build.level > 1):
                build.c_powierzchnia = budynek.c_powierzchnia_level
            else:
                build.c_powierzchnia = budynek.c_powierzchnia
            build.mozna = 1
            for i in Buildings.objects.filter(minus_czas_tak__gt=0):
                level = floor(self.bud_get_level(planeta, i.id))
                build.c_czas = build.c_czas * eval(i.minus_czas)
            build.c_czas = int(build.c_czas * 60 * 60)

            if (int(build.c_powierzchnia) > int(planeta.powierzchnia_max) - int(planeta.powierzchnia_zajeta)):
                build.koniec_powierzchni = 1
                build.mozna = None

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
                zaleznosc = split(budynek.w_bud, ";")
                for zal in zaleznosc:
                    z_bud = split(zal, ",")
                    if len(z_bud) > 1:
                        if (int(z_bud[1]) > int(self.bud_get_level(planeta, z_bud[0]))):
                            build.mozna = None
                if not build.mozna:
                    zaleznosc = split(budynek.w_bad, ";")
                    for zal in zaleznosc:
                        badanie = split(zal, ",")
                        if len(badanie) > 1:
                            if (int(badanie[1]) > int(self.bad_get_level(self.user, badanie[0]))):
                                build.mozna = None
                                break
                if build.mozna:
                    czas = self.get_budynki_kolejka_czas(planeta)
                    build.points = float(build.c_met + build.c_cry + build.c_deu) / 1000.0

                    kolejka = Budynki_f.objects.create(budynek=budynek, planeta=planeta, level=build.level,
                                                       time=czas + build.c_czas, points=build.points, czas_start=czas)
                    self.cache_obj.get_budynek_f(planeta.pk, kolejka.pk)
                    planeta.metal -= build.c_met
                    planeta.crystal -= build.c_cry
                    planeta.deuter -= build.c_deu
                    planeta.powierzchnia_zajeta += build.c_powierzchnia

    def anuluj_budynek(self, id_budynek):
        # query = "lock table game_budynki_f in ACCESS EXCLUSIVE MODE"
        # cursor = connection.cursor()
        # cursor.execute(query)
        planeta = self.get_current_planet()
        try:
            id_budynek = int(id_budynek)
            bud_kol = \
            Budynki_f.objects.select_for_update().filter(planeta=planeta, budynek=id_budynek).order_by("-level")[0]
            max_level = self.cache_obj.get_budynek_f(planeta.pk, bud_kol.pk)
        except:
            max_level = None

        if max_level:
            id_pozycji = max_level.pk
            level = max_level.level
            budynek = max_level.budynek
            c_met = budynek.c_met * pow(budynek.c_factor, level - 1)
            c_cry = budynek.c_cry * pow(budynek.c_factor, level - 1)
            c_deu = budynek.c_deu * pow(budynek.c_factor, level - 1)
            c_ene = budynek.c_ene * pow(budynek.c_factor, level - 1)
            c_czas = (c_cry + c_met) / GAME_SPEED
            if (level > 1):
                c_powierzchnia = budynek.c_powierzchnia_level
            else:
                c_powierzchnia = budynek.c_powierzchnia
            planeta.powierzchnia_zajeta -= c_powierzchnia
            planeta.metal += c_met * 0.5
            planeta.crystal += c_cry * 0.5
            planeta.deuter += c_deu * 0.5

            c_czas = max_level.time
            self.cache_obj.del_budynek_f(planeta.pk, max_level.pk)
            kolejka = Budynki_f.objects.values_list('id', flat=True).select_for_update().filter(planeta=planeta,
                                                                                                time__gte=c_czas).order_by(
                "time")
            if len(kolejka) > 0:
                try:
                    poprzednie = \
                    Budynki_f.objects.select_for_update().filter(planeta=planeta, time__lt=c_czas).order_by("-time")[0]
                    c_czas = c_czas - poprzednie.time
                except:
                    c_czas = c_czas - time()
                for pk in kolejka:
                    k = self.cache_obj.get_budynek_f(planeta.pk, pk)
                    k.czas_start -= c_czas
                    k.time -= c_czas
        return True
