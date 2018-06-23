# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import ceil
from math import floor
from string import find

from settings import GAME_SPEED
from settings import MNOZNIK_MAGAZYNOW
from ugame.models.all import Badania_p
from ugame.models.all import Budynki_f
from ugame.models.all import Budynki_p
from ugame.models.all import Buildings
from ugame.models.all import Flota
from ugame.models.all import Flota_f
from ugame.models.all import Flota_p
from ugame.models.all import Obrona_p


def sort_queue(x, y):
    return cmp(x.time, y.time)


class CronSurowce():

    def update_sur(self, totime, id_planety, last_update):
        czas_calc = float(totime - last_update)
        if czas_calc < 0:
            return 0

        planeta = self.get_planet(id_planety)

        # if czas_calc<0:czas_calc=0
        bud_prod = Buildings.objects.filter(czy_produkcja__gt=0)
        flota_prod = Flota.objects.filter(czy_produkcja__gt=0)

        do_update_bud = planeta.budynki_p_set.select_for_update().filter(budynek__in=bud_prod)
        do_update_flota = planeta.flota_p_set.select_for_update().filter(budynek__in=flota_prod)
        do_update = []

        for i in do_update_bud:
            do_update.append(self.cache_obj.get_budynek_p(planeta.pk, i.budynek_id))
        for i in do_update_flota:
            do_update.append(self.cache_obj.get_flota_p(planeta.pk, i.budynek_id))

        energia_zuzyta = 0.0
        zuzycie_met = 0.0
        zuzycie_cry = 0.0
        zuzycie_deu = 0.0
        temp_max = planeta.temp_max
        for i in do_update:
            level = i.level
            ilosc = i.ilosc
            procent = float(i.procent)
            if find(i.budynek.ene_formula, "-") != 0:
                if find(i.budynek.met_formula, "-") == 0:
                    zuzycie_met += float(eval(i.budynek.met_formula)) * czas_calc / 3600.0
                if find(i.budynek.cry_formula, "-") == 0:
                    zuzycie_cry += float(eval(i.budynek.cry_formula)) * czas_calc / 3600.0
                if find(i.budynek.deu_formula, "-") == 0:
                    zuzycie_deu += float(eval(i.budynek.deu_formula)) * czas_calc / 3600.0

        if (float(planeta.metal) + zuzycie_met < 0) and zuzycie_met > 0:
            for i in do_update:
                if find(i.budynek.met_formula, "-") == 0:
                    i.procent = -int(procent * 0.01 * planeta.metal * 100.0 / zuzycie_met)
                    if i.procent < 0:
                        i.procent = 0
        if (planeta.crystal + zuzycie_cry < 0) and zuzycie_cry > 0:
            for i in do_update:
                if find(i.budynek.cry_formula, "-") == 0:
                    i.procent = -int(procent * 0.01 * planeta.crystal * 100.0 / zuzycie_cry)
                    if i.procent < 0:
                        i.procent = 0
        if (float(planeta.deuter) + zuzycie_deu < 0) and zuzycie_deu > 0:
            for i in do_update:
                if find(i.budynek.deu_formula, "-") == 0:
                    i.procent = -int(procent * 0.01 * planeta.deuter * 100.0 / zuzycie_deu)
                    if i.procent < 0:
                        i.procent = 0

        max_energy = 0.0
        used_energy = 0.0
        max_used_energy = 0.0
        for i in do_update:
            ilosc = i.ilosc
            level = i.level
            procent = float(i.procent)
            if find(i.budynek.ene_formula, "-") != 0:
                max_energy += float(eval(i.budynek.ene_formula))
            if find(i.budynek.ene_formula, "-") == 0:
                used_energy += float(eval(i.budynek.ene_formula))
                procent = 100
                max_used_energy += float(eval(i.budynek.ene_formula))

        planeta.energy_used = -used_energy
        planeta.energy_max = max_energy

        if (max_energy + used_energy < 0):
            try:
                procent_produkcji = -max_energy * 100.0 / used_energy
            except:
                procent_produkcji = 0
            used_energy = 0.0

            for i in do_update:
                if find(i.budynek.ene_formula, "-") == 0:
                    procent = i.procent = int(i.procent * 0.01 * procent_produkcji)
                    ilosc = i.ilosc
                    level = i.level
                    used_energy += float(eval(i.budynek.ene_formula))
            planeta.energy_used = -used_energy
        planeta.metal_perhour = 500.0
        planeta.crystal_perhour = 500.0
        planeta.deuter_perhour = 500.0
        for i in do_update:
            level = i.level
            if i.procent < 0:
                i.procent = 0
            procent = i.procent
            ilosc = i.ilosc
            planeta.metal_perhour += eval(i.budynek.met_formula)
            planeta.crystal_perhour += eval(i.budynek.cry_formula)
            planeta.deuter_perhour += eval(i.budynek.deu_formula)

        add_metal = planeta.metal_perhour * czas_calc / 3600.0
        if planeta.metal + add_metal > planeta.metal_max:
            if not planeta.metal > planeta.metal_max:
                planeta.metal = planeta.metal_max
        else:
            planeta.metal += add_metal

        add_crystal = planeta.crystal_perhour * czas_calc / 3600.0
        if planeta.crystal + add_crystal > planeta.crystal_max:
            if not planeta.crystal > planeta.crystal_max:
                planeta.crystal = planeta.crystal_max
        else:
            planeta.crystal += add_crystal

        add_deuter = planeta.deuter_perhour * czas_calc / 3600.0
        if planeta.deuter + add_deuter > planeta.deuter_max:
            if not planeta.deuter > planeta.deuter_max:
                planeta.deuter = planeta.deuter_max
        else:
            planeta.deuter += add_deuter

    def update_obrona(self, buduj_tmp, id_planety, czas_teraz):
        planeta = self.get_planet(id_planety)
        buduj = self.cache_obj.get_obrona_f(planeta.pk, buduj_tmp.pk)
        if buduj.ilosc > 1:
            czas_jednego_statku = buduj.time_one / (buduj.ilosc - 1)
            czas_koncowy_budowy = buduj.time
            czas_pozostaly = buduj.time - czas_teraz
            if czas_jednego_statku <= 0:
                ilosc_statkow_do_konca = 0
            else:
                ilosc_statkow_do_konca = int(ceil(czas_pozostaly / czas_jednego_statku))
            if ilosc_statkow_do_konca < 0:
                ilosc_statkow_do_konca = 0
            if czas_pozostaly < 0:
                czas_pozostaly = 0
        elif buduj.ilosc == 1:
            czas_pozostaly = 0
            czas_jednego_statku = 0
            ilosc_statkow_do_konca = 0
        else:
            self.cache_obj.del_obrona_f(planeta.pk, buduj_tmp.pk)
            return True
        ilosc_wybudowanych = buduj.ilosc - ilosc_statkow_do_konca
        tmp = self.cache_obj.get_obrona_p(planeta.pk, buduj.budynek_id)
        if not tmp:
            Obrona_p.objects.create(budynek=buduj.budynek, planeta=planeta)
            tmp = self.cache_obj.get_obrona_p(planeta.pk, buduj.budynek_id)
        tmp.ilosc += ilosc_wybudowanych

        buduj.ilosc -= ilosc_wybudowanych
        buduj.time_one -= czas_jednego_statku * ilosc_wybudowanych

        if buduj.ilosc <= 0:
            self.cache_obj.del_obrona_f(planeta.pk, buduj_tmp.pk)
        punkty = buduj.points * ilosc_wybudowanych
        planeta.points_obrona += punkty
        self.userprofile.points_obrona += punkty
        self.userprofile.points += punkty

    def update_flota(self, buduj_tmp, id_planety, czas_teraz):
        planeta = self.get_planet(id_planety)
        buduj = self.cache_obj.get_flota_f(planeta.pk, buduj_tmp.pk)
        if buduj.ilosc > 1:
            czas_jednego_statku = buduj.time_one / (buduj.ilosc - 1)
            czas_koncowy_budowy = buduj.time
            czas_pozostaly = buduj.time - czas_teraz
            if czas_jednego_statku > 0:
                ilosc_statkow_do_konca = int(ceil(czas_pozostaly / czas_jednego_statku))
            else:
                ilosc_statkow_do_konca = 0
            if ilosc_statkow_do_konca < 0:
                ilosc_statkow_do_konca = 0
            if czas_pozostaly < 0:
                czas_pozostaly = 0
        elif buduj.ilosc == 1:
            czas_pozostaly = 0
            czas_jednego_statku = 0
            ilosc_statkow_do_konca = 0
        else:
            self.cache_obj.del_flota_f(planeta.pk, buduj_tmp.pk)
            return True

        ilosc_wybudowanych = buduj.ilosc - ilosc_statkow_do_konca
        tmp = self.cache_obj.get_flota_p(planeta.pk, buduj_tmp.budynek_id)
        if not tmp:
            Flota_p.objects.create(budynek=buduj.budynek, planeta=planeta)
            tmp = self.cache_obj.get_flota_p(planeta.pk, buduj_tmp.budynek_id)

        tmp.ilosc += ilosc_wybudowanych

        buduj.ilosc -= ilosc_wybudowanych
        buduj.time_one -= czas_jednego_statku * ilosc_wybudowanych

        if buduj.ilosc <= 0:
            self.cache_obj.del_flota_f(planeta.pk, buduj_tmp.pk)
        punkty = buduj.points * ilosc_wybudowanych
        planeta.points_flota += punkty
        self.userprofile.points_flota += punkty
        self.userprofile.points += punkty

    def update_badanie(self, buduj_tmp, id_planety, czas_teraz):
        planeta = self.get_planet(id_planety)

        buduj = self.cache_obj.get_badanie_f(self.user.pk, buduj_tmp.pk)
        tmp = self.cache_obj.get_badanie_p(self.user.pk, buduj.badanie_id)
        if not tmp:
            Badania_p.objects.create(badanie=buduj.badanie, user=self.user)
            tmp = self.cache_obj.get_badanie_p(self.user.pk, buduj.badanie_id)

        self.cache_obj.del_badanie_f(self.user.pk, buduj_tmp.pk)

        tmp.level = buduj.level

        self.userprofile.points_tech += buduj.points
        self.userprofile.points += buduj.points

    def update_budynek(self, buduj_tmp, id_planety, czas_teraz):
        planeta = self.get_planet(id_planety)

        buduj = self.cache_obj.get_budynek_f(planeta.pk, buduj_tmp.pk)

        tmp = self.cache_obj.get_budynek_p(planeta.pk, buduj_tmp.budynek_id)
        if not tmp:
            Budynki_p.objects.create(budynek=buduj.budynek, planeta=planeta)
            tmp = self.cache_obj.get_budynek_p(planeta.pk, buduj_tmp.budynek_id)
        if buduj.budynek.mag_met > 0:
            planeta.metal_max = floor(10000 * MNOZNIK_MAGAZYNOW * pow(1.5, buduj.level))
        if buduj.budynek.mag_cry > 0:
            planeta.crystal_max = floor(10000 * MNOZNIK_MAGAZYNOW * pow(1.5, buduj.level))
        if buduj.budynek.mag_deu > 0:
            planeta.deuter_max = floor(10000 * MNOZNIK_MAGAZYNOW * pow(1.5, buduj.level))
        if buduj.budynek.terraformer > 0:
            planeta.terraformer_fields += buduj.budynek.terraformer
            planeta.powierzchnia_max += buduj.budynek.terraformer
        planeta.points_builds += buduj.points
        self.userprofile.points_builds += buduj.points
        self.userprofile.points += buduj.points

        tmp.level = buduj.level
        tmp.procent = 100
        self.cache_obj.del_budynek_f(planeta.pk, buduj_tmp.pk)

        if buduj.budynek.minus_czas_tak > 0:
            self.update_kolejka_czas_budynki(id_planety, czas_teraz, buduj)
        if buduj.budynek.minus_czas_flota_tak > 0:
            self.update_kolejka_czas_flota(id_planety, czas_teraz, buduj)

    def update_kolejka_czas_flota(self, id_planety, czas_teraz, buduj):
        planeta = self.get_planet(id_planety)

        tmp_kol = Flota_f.objects.values_list('id', flat=True).select_for_update().filter(planeta=planeta,
                                                                                          time__gt=czas_teraz).order_by(
            "time")
        budynki_obnizajace_czas = Buildings.objects.filter(minus_czas_flota_tak__gt=0)
        obnizanie_czasu = 0
        for tmp_bud in tmp_kol:
            budynek_f = self.cache_obj.get_flota_f(planeta.pk, tmp_bud)
            c_met = budynek_f.budynek.c_met
            c_cry = budynek_f.budynek.c_cry
            c_deu = budynek_f.budynek.c_deu
            c_czas_new = (c_cry + c_met) / GAME_SPEED
            c_czas_old = (c_cry + c_met) / GAME_SPEED
            for i in budynki_obnizajace_czas:
                if i.id == buduj.budynek.id:
                    level = self.bud_get_level(planeta, i.id)
                    c_czas_new = c_czas_new * eval(i.minus_czas_flota)
                    level = level - 1
                    c_czas_old = c_czas_old * eval(i.minus_czas_flota)
                else:
                    level = self.bud_get_level(planeta, i.id)
                    c_czas_old = c_czas_old * eval(i.minus_czas_flota)
                    c_czas_new = c_czas_new * eval(i.minus_czas_flota)
            obnizanie_czasu += (c_czas_old * 60 * 60 - c_czas_new * 60 * 60) * budynek_f.ilosc
            obnizanie_czasu_one = (c_czas_old * 60 * 60 - c_czas_new * 60 * 60) * (budynek_f.ilosc - 1)
            budynek_f.time = budynek_f.time - obnizanie_czasu
            budynek_f.time_one = budynek_f.time_one - obnizanie_czasu_one

    def update_kolejka_czas_budynki(self, id_planety, czas_teraz, buduj):
        planeta = self.get_planet(id_planety)

        tmp_kol = Budynki_f.objects.values_list('id', flat=True).select_for_update().filter(planeta=planeta,
                                                                                            time__gt=czas_teraz).order_by(
            "time")
        budynki_obnizajace_czas = Buildings.objects.filter(minus_czas_tak__gt=0)
        obnizanie_czasu = 0
        for tmp_bud in tmp_kol:
            budynek_f = self.cache_obj.get_budynek_f(planeta.pk, tmp_bud)
            c_met = budynek_f.budynek.c_met * pow(budynek_f.budynek.c_factor, budynek_f.level - 1)
            c_cry = budynek_f.budynek.c_cry * pow(budynek_f.budynek.c_factor, budynek_f.level - 1)
            c_czas_new = (c_cry + c_met) / GAME_SPEED
            c_czas_old = (c_cry + c_met) / GAME_SPEED
            for i in budynki_obnizajace_czas:
                if i.id == buduj.budynek.id:
                    level = floor(self.bud_get_level(planeta, i.id))
                    c_czas_new = c_czas_new * eval(i.minus_czas)
                    level = level - 1
                    c_czas_old = c_czas_old * eval(i.minus_czas)
                else:
                    level = floor(self.bud_get_level(planeta, i.id))
                    c_czas_old = c_czas_old * eval(i.minus_czas)
                    c_czas_new = c_czas_new * eval(i.minus_czas)
            obnizanie_czasu += c_czas_old * 60 * 60 - c_czas_new * 60 * 60
            budynek_f.time = budynek_f.time - obnizanie_czasu
