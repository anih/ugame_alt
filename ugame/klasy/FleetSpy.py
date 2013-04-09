# -*- coding: utf-8 -*-
from __future__ import division
from math import floor, ceil
from string import split
from random import randint, uniform
import copy

from django.template.loader import render_to_string

from ..funkcje import lock_user_cron
from ..cron_fun import helpers, raporty_fun
from settings import GAME_SPEED, RES_SPEED, MNOZNIK_MAGAZYNOW, ILOSC_PLANET
from ugame.models.all import Flota, Badania, Buildings, Obrona

class Output():pass

class FleetSpy():

    def flota_spy_alien(self, flota, czas_teraz):
        req_alien = Output()
        req_alien.user = flota.fleet_owner
        from ..klasy.BaseGame import BaseGame
        GraAlienObj = BaseGame(req_alien, czas_teraz=flota.time, cron=False)

        obronca = self
        agresor = GraAlienObj

        planeta_new = self.fleet_spy(flota, GraAlienObj, self)

        GraAlienObj.save_all()

        return True




    def flota_spy(self, flota, czas_teraz):
        req_alien = Output()
        req_alien.user = flota.galaxy_end.planet.owner
        print "atakkk-----------------------------------------------------------"
        from ..klasy.BaseGame import BaseGame
        GraAlienObj = BaseGame(req_alien, czas_teraz=flota.time, cron=False)
        GraAlienObj.cron_function(flota.galaxy_end.planet_id, flota.time - 1)


        """
        tutaj user jest obronca!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        """
        planeta_new = self.fleet_spy(flota, self, GraAlienObj)

        GraAlienObj.save_all()

        return True


    def fleet_spy(self, flota_atak, agresor, obronca):
        jednostki = Flota.objects.all()
        spy_tech = Badania.objects.get(szpieg__gt=0)
        comp_tech = Badania.objects.get(komputerowa=True)



        obronca_galaktyka = obronca.get_galaxy(flota_atak.galaxy_end_id)
        obronca_planeta = obronca.get_planet(obronca_galaktyka.planet_id)

        agresor_galaktyka = agresor.get_galaxy(flota_atak.galaxy_start_id)
        agresor_planeta = agresor.get_planet(agresor_galaktyka.planet_id)

        ilosc_floty_w_obronie = 0
        for j in jednostki:
            jednostka = obronca.cache_obj.get_flota_p(obronca_planeta.pk, j.pk)
            if jednostka:
                ilosc_floty_w_obronie += jednostka.ilosc
        fleet_array = split(flota_atak.fleet_array, ";")
        statki = []

        ilosc_sond_w_ataku = 0
        for s in fleet_array:
            tmp = split(s, ",")
            ilosc = float(tmp[1])
            statek = Flota.objects.get(pk=tmp[0])
            print "statek:", statek.nazwa, statek.spy
            if statek.spy:
                ilosc_sond_w_ataku += ilosc
            statki.append((statek, ilosc))

        agresor_spy_tech = agresor.cache_obj.get_badanie_p(agresor.user.pk, spy_tech.pk)
        if not agresor_spy_tech:agresor_spy_tech = 0
        else:agresor_spy_tech = agresor_spy_tech.level

        agresor_comp_tech = agresor.cache_obj.get_badanie_p(agresor.user.pk, comp_tech.pk)
        if not agresor_comp_tech:agresor_comp_tech = 0
        else:agresor_comp_tech = agresor_comp_tech.level

        obronca_spy_tech = obronca.cache_obj.get_badanie_p(obronca.user.pk, spy_tech.pk)
        if not obronca_spy_tech:obronca_spy_tech = 0
        else:obronca_spy_tech = obronca_spy_tech.level

        obronca_comp_tech = obronca.cache_obj.get_badanie_p(obronca.user.pk, comp_tech.pk)
        if not obronca_comp_tech:obronca_comp_tech = 0
        else:obronca_comp_tech = obronca_comp_tech.level

        dane = {"agresor":agresor, "obronca":obronca, "badania":None, "budynki":None, "flota":None, "obrona":None, "surowce":None, "straty":[], "szansa_na_zestrzelenie":None}
        punkty_szpiega_agresor_all = 0


        print "a_techy:", agresor_comp_tech, agresor_spy_tech
        print "o_techy:", obronca_comp_tech, obronca_spy_tech

        if agresor_spy_tech > obronca_spy_tech:
            print "agresor wiekszy tech"
            punkty_szpiega_agresor_all = ilosc_sond_w_ataku + (agresor_spy_tech - obronca_spy_tech) ** 2
        elif agresor_spy_tech < obronca_spy_tech:
            print "obronca wiekszy tech"
            punkty_szpiega_agresor_all = ilosc_sond_w_ataku - (obronca_spy_tech - agresor_spy_tech) ** 2
        else:
            print "rowne techy"
            punkty_szpiega_agresor_all = ilosc_sond_w_ataku


        if punkty_szpiega_agresor_all >= 7:
            dane['badania'] = self.fleet_spy_badania(obronca, obronca_planeta)
        if punkty_szpiega_agresor_all >= 5:
            dane['budynki'] = self.fleet_spy_budynki(obronca, obronca_planeta)
        if punkty_szpiega_agresor_all >= 2:
            dane['flota'] = self.fleet_spy_flota(obronca, obronca_planeta)
        if punkty_szpiega_agresor_all >= 3:
            dane['obrona'] = self.fleet_spy_obrona(obronca, obronca_planeta)

        dane['surowce'] = obronca_planeta

        szansa_na_zestrzelenie = None
        agresor_tech = agresor_spy_tech + round(agresor_comp_tech / 2)
        obronca_tech = obronca_spy_tech + round(obronca_comp_tech / 2)

        if agresor_tech > obronca_tech:
            szansa_na_zestrzelenie = round(ilosc_floty_w_obronie / (8 * (agresor_tech - obronca_tech)))
        elif agresor_tech < obronca_tech:
            szansa_na_zestrzelenie = round((ilosc_floty_w_obronie / 2) * (obronca_tech - agresor_tech))
        else:
            szansa_na_zestrzelenie = round(ilosc_floty_w_obronie / 4)

        if szansa_na_zestrzelenie > 100:
            szansa_na_zestrzelenie = 100
        print szansa_na_zestrzelenie

        szansa_na_zestrzelenie = floor(uniform(0, szansa_na_zestrzelenie)) / 100


        dane["szansa_na_zestrzelenie"] = int(szansa_na_zestrzelenie * 100)
        if szansa_na_zestrzelenie > 0:
            statki = []
            for s in fleet_array:
                tmp = split(s, ",")
                ilosc = float(tmp[1])
                statek = Flota.objects.get(pk=tmp[0])
                stracil = 0
                if statek.spy:
                    stracil = int(round(ilosc * szansa_na_zestrzelenie))
                    punkty_strata = (statek.c_met + statek.c_cry + statek.c_deu) / 1000 * stracil
                    obronca_galaktyka.metal += statek.c_met * stracil * 0.7
                    obronca_galaktyka.crystal += statek.c_cry * stracil * 0.7
                    agresor_planeta.points_flota -= punkty_strata
                    agresor.userprofile.points_flota -= punkty_strata
                    agresor.userprofile.points -= punkty_strata
                dane['straty'].append({"nazwa":statek.nazwa, "stracil":stracil, "ilosc":ilosc})
                ilosc -= stracil
                statki.append("%s,%s" % (statek.pk, ilosc))
            flota_atak.fleet_array = ";".join(statki)
        raporty_fun.rap_spy(dane, flota_atak)
        helpers.make_fleet_back(flota_atak)



    def fleet_spy_budynki(self, obronca, planeta):
        budynki = Buildings.objects.all().order_by('id')
        colspan = len(budynki)
        budynki_levele = []
        for b in budynki:
            budynki_levele.append(obronca.bud_get_level(planeta, b.pk))
        return {"budynki":budynki, "levele":budynki_levele}
    def fleet_spy_badania(self, obronca, planeta):
        badania = Badania.objects.all().order_by('id')
        colspan = len(badania)
        levele = []
        for b in badania:
            level = obronca.bad_get_level(obronca.user, b.pk)
            levele.append(level)
        return {"badania":badania, "levele":levele}
    def fleet_spy_flota(self, obronca, planeta):
        floty = Flota.objects.all().order_by('id')
        colspan = len(floty)
        levele = []
        for f in floty:
            obj = obronca.cache_obj.get_flota_p(planeta.pk, f.pk)
            if obj:ilosc = obj.ilosc
            else:ilosc = 0
            levele.append(ilosc)
        return {"flota":floty, "levele":levele}
    def fleet_spy_obrona(self, obronca, planeta):
        obrona = Obrona.objects.all().order_by('id')
        colspan = len(obrona)
        levele = []
        for f in obrona:
            obj = obronca.cache_obj.get_obrona_p(planeta.pk, f.pk)
            if obj:ilosc = obj.ilosc
            else:ilosc = 0
            levele.append(ilosc)
        return {"obrona":obrona, "levele":levele}
