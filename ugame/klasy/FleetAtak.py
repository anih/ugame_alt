# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import ceil
from math import floor
from random import uniform
from string import split

from ugame.models.all import Flota

from ..cron_fun import helpers
from ..cron_fun import raporty_fun


class Output(): pass


class FleetAtak():

    def flota_atak_alien(self, flota, czas_teraz):
        req_alien = Output()
        req_alien.user = flota.fleet_owner
        from ..klasy.BaseGame import BaseGame
        GraAlienObj = BaseGame(req_alien, czas_teraz=flota.time, cron=False)

        obronca = self
        agresor = GraAlienObj

        planeta_new = self.walka(flota, GraAlienObj, self)

        GraAlienObj.save_all()

        return True

    def flota_atak(self, flota, czas_teraz):
        req_alien = Output()
        if not flota.galaxy_end.planet.owner:
            helpers.make_fleet_back(flota)
            return True
        req_alien.user = flota.galaxy_end.planet.owner
        from ..klasy.BaseGame import BaseGame
        GraAlienObj = BaseGame(req_alien, czas_teraz=flota.time, cron=False)
        GraAlienObj.cron_function(flota.galaxy_end.planet_id, flota.time - 1)

        """
        tutaj user jest obronca!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        """
        planeta_new = self.walka(flota, self, GraAlienObj)

        GraAlienObj.save_all()

        return True

    def get_agresor_statki(self, flota_array):
        agresor_statki_tmp = split(flota_array, ";")
        agresor_statki = {}
        agresor_zlom_poczatek = {"met": 0, "cry": 0}

        for i in agresor_statki_tmp:
            tmp = split(i, ",")
            statek = Flota.objects.get(pk=tmp[0])
            ilosc = int(tmp[1])
            agresor_statki[statek.pk] = {"statek": statek, "ilosc": ilosc, "typ": "f"}
            agresor_zlom_poczatek['met'] += ilosc * statek.c_met
            agresor_zlom_poczatek['cry'] += ilosc * statek.c_cry
        return agresor_statki, agresor_zlom_poczatek

    def get_obronca_obrona(self, GraObj, obronca_planeta):
        obronca_obrona_tmp = obronca_planeta.obrona_p_set.values_list("budynek_id",
                                                                      flat=True).select_for_update().filter(ilosc__gt=0)
        obronca_statki = {}
        obronca_zlom_obrona_poczatek = {"met": 0, "cry": 0}
        for i in obronca_obrona_tmp:
            obrona_p_obj = GraObj.cache_obj.get_obrona_p(obronca_planeta.pk, i)
            obronca_statki[i] = {"statek": obrona_p_obj.budynek, "ilosc": obrona_p_obj.ilosc, "typ": "o"}
            ilosc = int(obrona_p_obj.ilosc)
            obronca_zlom_obrona_poczatek['met'] += ilosc * obrona_p_obj.budynek.c_met
            obronca_zlom_obrona_poczatek['cry'] += ilosc * obrona_p_obj.budynek.c_cry
        return obronca_statki, obronca_zlom_obrona_poczatek

    def get_obronca_statki(self, GraObj, obronca_planeta):
        obronca_statki_tmp = obronca_planeta.flota_p_set.values_list("budynek_id",
                                                                     flat=True).select_for_update().filter(ilosc__gt=0)
        obronca_statki = {}
        obronca_zlom_poczatek = {"met": 0, "cry": 0}

        for i in obronca_statki_tmp:
            obrona_p_obj = GraObj.cache_obj.get_flota_p(obronca_planeta.pk, i)
            obronca_statki[i] = {"statek": obrona_p_obj.budynek, "ilosc": obrona_p_obj.ilosc, "typ": "f"}
            ilosc = int(obrona_p_obj.ilosc)
            obronca_zlom_poczatek['met'] += ilosc * obrona_p_obj.budynek.c_met
            obronca_zlom_poczatek['cry'] += ilosc * obrona_p_obj.budynek.c_cry

        return obronca_statki, obronca_zlom_poczatek

    def get_technologie(self, user, dane):
        try:
            dane.military_tech = user.badania_p_set.get(badanie__atak=1).level
        except:
            dane.military_tech = 0
        try:
            dane.defence_tech = user.badania_p_set.get(badanie__ochrona=1).level
        except:
            dane.defence_tech = 0
        try:
            dane.shield_tech = user.badania_p_set.get(badanie__pancerz=1).level
        except:
            dane.shield_tech = 0
        try:
            dane.spy_tech = user.badania_p_set.get(badanie__szpieg=1).level
        except:
            dane.spy_tech = 0

    def przelicz_sile(self, agresor_statki, agresor_dane):
        agresor_atak = 0
        agresor_defence = 0
        agresor_tarcza = 0
        agresor_ilosc = 0
        for i in agresor_statki:
            statek = agresor_statki[i]['statek']
            ilosc = agresor_statki[i]['ilosc']
            agresor_statki[i]['obrona'] = (ilosc * (statek.c_met + statek.c_cry) / 10) * (
                        1 + agresor_dane.defence_tech * 0.1)
            agresor_statki[i]['tarcza'] = ilosc * statek.shield * (1 + agresor_dane.shield_tech * 0.1) * uniform(80,
                                                                                                                 120)\
                                          / 100
            agresor_statki[i]['atak'] = ilosc * statek.attack * (1 + agresor_dane.military_tech * 0.1) * uniform(80,
                                                                                                                 120)\
                                        / 100
            agresor_atak += agresor_statki[i]['atak']
            agresor_defence += agresor_statki[i]['obrona']
            agresor_tarcza += agresor_statki[i]['tarcza']
            agresor_ilosc += agresor_statki[i]['ilosc']
        return agresor_atak, agresor_defence, agresor_tarcza, agresor_ilosc

    def daj_poczatkowe_ilosc(self, agresor_statki):
        dane = {}
        for i in agresor_statki:
            statek = agresor_statki[i]['statek']
            ilosc = agresor_statki[i]['ilosc']
            dane[statek.pk] = {"statek": statek, "ilosc": ilosc}
        return dane

    def walka(self, flota_atak, agresor, obronca):

        obronca_galaktyka = obronca.get_galaxy(flota_atak.galaxy_end_id)
        obronca_planeta = obronca.get_planet(obronca_galaktyka.planet_id)

        agresor_galaktyka = agresor.get_galaxy(flota_atak.galaxy_start_id)
        agresor_planeta = agresor.get_planet(agresor_galaktyka.planet_id)

        agresor_dane = Output()
        self.get_technologie(agresor.user, agresor_dane)

        agresor_statki, agresor_zlom_poczatek = self.get_agresor_statki(flota_atak.fleet_array)

        obronca_dane = Output()
        self.get_technologie(obronca.user, obronca_dane)

        obronca_statki, obronca_zlom_poczatek = self.get_obronca_statki(obronca, obronca_planeta)
        obronca_obrona, obronca_zlom_obrona_poczatek = self.get_obronca_obrona(obronca, obronca_planeta)

        dane_raport = Output()
        dane_raport.poczatek = Output()
        dane_raport.poczatek.agresor_statki = self.daj_poczatkowe_ilosc(agresor_statki)
        dane_raport.poczatek.obronca_statki = self.daj_poczatkowe_ilosc(obronca_statki)
        dane_raport.poczatek.obronca_obrona = self.daj_poczatkowe_ilosc(obronca_obrona)
        dane_raport.rundy = []

        agresor_atak, agresor_defence, agresor_tarcza, agresor_ilosc = self.przelicz_sile(agresor_statki, agresor_dane)
        dane_raport.poczatek.agresor_atak = agresor_atak
        dane_raport.poczatek.agresor_defence = agresor_defence
        dane_raport.poczatek.agresor_tarcza = agresor_tarcza
        dane_raport.poczatek.agresor_ilosc = agresor_ilosc

        obronca_atak, obronca_defence, obronca_tarcza, obronca_ilosc = self.przelicz_sile(obronca_statki, obronca_dane)
        obronca_atak_tmp, obronca_defence_tmp, obronca_tarcza_tmp, obronca_ilosc_tmp = self.przelicz_sile(
            obronca_obrona, obronca_dane)
        obronca_atak += obronca_atak_tmp
        obronca_defence += obronca_defence_tmp
        obronca_tarcza += obronca_tarcza_tmp
        obronca_ilosc += obronca_ilosc_tmp
        dane_raport.poczatek.obronca_atak = obronca_atak
        dane_raport.poczatek.obronca_defence = obronca_defence
        dane_raport.poczatek.obronca_tarcza = obronca_tarcza
        dane_raport.poczatek.obronca_ilosc = obronca_ilosc

        for run in range(1, 11):
            if obronca_ilosc <= 0 or agresor_ilosc <= 0:
                break

            agresor_statki_ilosci = {}
            for ind in agresor_statki:
                statek = agresor_statki[ind]['statek']
                ilosc = agresor_statki[ind]['ilosc']
                tarcza = agresor_statki[ind]['tarcza']

                obronca_moc = ilosc * obronca_atak / agresor_ilosc

                if tarcza < obronca_moc:
                    max_zdjac = floor(ilosc * obronca_ilosc / agresor_ilosc)
                    obronca_moc -= tarcza
                    agresor_tarcza += tarcza

                    ile_zdjac = floor(obronca_moc / ((statek.c_met + statek.c_cry) / 10))
                    if ile_zdjac > max_zdjac:
                        ile_zdjac = max_zdjac
                    ilosc = ceil(ilosc - ile_zdjac)
                    if ilosc < 0:
                        ilosc = 0
                else:
                    agresor_tarcza += obronca_moc
                agresor_statki_ilosci[statek.pk] = {"statek": statek, "ilosc": ilosc}

            obronca_obrona_ilosci = {}
            for ind in obronca_obrona:
                statek = obronca_obrona[ind]['statek']
                ilosc = obronca_obrona[ind]['ilosc']
                tarcza = obronca_obrona[ind]['tarcza']

                agresor_moc = ilosc * agresor_atak / obronca_ilosc
                if tarcza < agresor_moc:
                    max_zdjac = floor(ilosc * agresor_ilosc / obronca_ilosc)
                    agresor_moc -= tarcza
                    obronca_tarcza += tarcza
                    ile_zdjac = floor(agresor_moc / ((statek.c_met + statek.c_cry) / 10))
                    if ile_zdjac > max_zdjac:
                        ile_zdjac = max_zdjac
                    ilosc = ceil(ilosc - ile_zdjac)
                    if ilosc < 0:
                        ilosc = 0
                else:
                    obronca_tarcza += agresor_moc
                obronca_obrona_ilosci[statek.pk] = {"statek": statek, "ilosc": ilosc}

            obronca_statki_ilosci = {}
            for ind in obronca_statki:
                statek = obronca_statki[ind]['statek']
                ilosc = obronca_statki[ind]['ilosc']
                tarcza = obronca_statki[ind]['tarcza']

                agresor_moc = ilosc * agresor_atak / obronca_ilosc
                if tarcza < agresor_moc:
                    max_zdjac = floor(ilosc * agresor_ilosc / obronca_ilosc)
                    agresor_moc -= tarcza
                    obronca_tarcza += tarcza
                    ile_zdjac = floor(agresor_moc / ((statek.c_met + statek.c_cry) / 10))
                    if ile_zdjac > max_zdjac:
                        ile_zdjac = max_zdjac
                    ilosc = ceil(ilosc - ile_zdjac)
                    if ilosc < 0:
                        ilosc = 0
                else:
                    obronca_tarcza += agresor_moc
                obronca_statki_ilosci[statek.pk] = {"statek": statek, "ilosc": ilosc}

            for ind in agresor_statki:
                ilosc = agresor_statki[ind]['ilosc']
                if len(agresor_statki[ind]['statek'].sd_flota) > 0:
                    sd = split(agresor_statki[ind]['statek'].sd_flota, ";")
                    for sd_o in sd:
                        obj = split(sd_o, ",")
                        statek_id = int(obj[0])
                        if obronca_statki_ilosci.has_key(statek_id):
                            ile = floor(ilosc * float(obj[1]) * uniform(70.0, 100.0) / 100.0)
                            obronca_statki_ilosci[statek_id]['ilosc'] -= ile
                            if obronca_statki_ilosci[statek_id]['ilosc'] <= 0:
                                obronca_statki_ilosci[statek_id]['ilosc'] = 0

                if len(agresor_statki[ind]['statek'].sd_obrona) > 0:
                    sd_obrona = split(agresor_statki[ind]['statek'].sd_obrona, ";")
                    for sd_o in sd_obrona:
                        obj = split(sd_o, ",")
                        statek_id = int(obj[0])
                        if obronca_obrona_ilosci.has_key(statek_id):
                            ile = floor(ilosc * float(obj[1]) * uniform(70.0, 100.0) / 100)
                            obronca_obrona_ilosci[statek_id]['ilosc'] -= ile
                            if obronca_obrona_ilosci[statek_id]['ilosc'] <= 0:
                                obronca_obrona_ilosci[statek_id]['ilosc'] = 0

            for ind in obronca_statki:
                if len(obronca_statki[ind]['statek'].sd_flota) > 0:
                    ilosc = obronca_statki[ind]['ilosc']
                    sd = split(obronca_statki[ind]['statek'].sd_flota, ";")
                    for sd_o in sd:
                        obj = split(sd_o, ",")
                        statek_id = int(obj[0])
                        if agresor_statki_ilosci.has_key(statek_id):
                            ile = floor(ilosc * float(obj[1]) * uniform(70.0, 100.0) / 100.0)
                            agresor_statki_ilosci[statek_id]['ilosc'] -= ile
                            if agresor_statki_ilosci[statek_id]['ilosc'] <= 0:
                                agresor_statki_ilosci[statek_id]['ilosc'] = 0

            for statek_id in agresor_statki:
                agresor_statki[statek_id]['ilosc'] = agresor_statki_ilosci[statek_id]['ilosc']

            for statek_id in obronca_statki:
                obronca_statki[statek_id]['ilosc'] = obronca_statki_ilosci[statek_id]['ilosc']

            for statek_id in obronca_obrona:
                obronca_obrona[statek_id]['ilosc'] = obronca_obrona_ilosci[statek_id]['ilosc']

            agresor_atak, agresor_defence, agresor_tarcza, agresor_ilosc = self.przelicz_sile(agresor_statki,
                                                                                              agresor_dane)

            obronca_atak, obronca_defence, obronca_tarcza, obronca_ilosc = self.przelicz_sile(obronca_statki,
                                                                                              obronca_dane)
            obronca_atak_tmp, obronca_defence_tmp, obronca_tarcza_tmp, obronca_ilosc_tmp = self.przelicz_sile(
                obronca_obrona, obronca_dane)
            obronca_atak += obronca_atak_tmp
            obronca_defence += obronca_defence_tmp
            obronca_tarcza += obronca_tarcza_tmp
            obronca_ilosc += obronca_ilosc_tmp

            dane_raport.rundy.append({"agresor_statki": agresor_statki_ilosci,
                                      "obronca_statki": obronca_statki_ilosci,
                                      "obronca_obrona": obronca_obrona_ilosci,
                                      "agresor_atak": agresor_atak,
                                      "agresor_defence": agresor_defence,
                                      "agresor_tarcza": agresor_tarcza,
                                      "agresor_ilosc": agresor_ilosc,
                                      "obronca_atak": obronca_atak,
                                      "obronca_defence": obronca_defence,
                                      "obronca_tarcza": obronca_tarcza,
                                      "obronca_ilosc": obronca_ilosc,
                                      })

            if agresor_ilosc <= 0 or obronca_ilosc <= 0:
                break
        # koniec fora dla rund
        wygrana = ''
        if agresor_ilosc <= 0 or obronca_ilosc <= 0:
            if agresor_ilosc <= 0 and obronca_ilosc <= 0:
                wygrana = 'R'
            else:
                if agresor_ilosc <= 0:
                    wygrana = 'O'
                else:
                    wygrana = 'A'
        else:
            wygrana = 'R'

        agresor_zlom_koniec = {"met": 0, "cry": 0}

        for i in agresor_statki:
            statek = agresor_statki[i]['statek']
            agresor_zlom_koniec['met'] += int(agresor_statki[i]['ilosc']) * statek.c_met
            agresor_zlom_koniec['cry'] += int(agresor_statki[i]['ilosc']) * statek.c_cry

        obronca_zlom_koniec = {"met": 0, "cry": 0}
        for i in obronca_statki:
            obronca_zlom_koniec['met'] += int(obronca_statki[i]['ilosc']) * obronca_statki[i]["statek"].c_met
            obronca_zlom_koniec['cry'] += int(obronca_statki[i]['ilosc']) * obronca_statki[i]["statek"].c_cry

        obronca_zlom_obrona_koniec = {"met": 0, "cry": 0}
        for i in obronca_obrona:
            obronca_zlom_obrona_koniec['met'] += int(obronca_obrona[i]['ilosc']) * obronca_obrona[i]["statek"].c_met
            obronca_zlom_obrona_koniec['cry'] += int(obronca_obrona[i]['ilosc']) * obronca_obrona[i]["statek"].c_cry

        ilosc_obronca = 0
        straty_obronca_obrona = 0
        odbudowa_obrona = []
        for statek_id in obronca_obrona:
            statek = obronca_obrona[statek_id]['statek']
            try:
                ilosc = dane_raport.poczatek.obronca_obrona[statek_id]['ilosc']
            except:
                ilosc = obronca_obrona[statek_id]['ilosc']

            stracil_faltycznie = ilosc - obronca_obrona[statek_id]['ilosc']
            odbudowal = int(stracil_faltycznie * uniform(60, 80) / 100)
            odbudowa_obrona.append({"statek": statek, "ilosc": odbudowal})

            stracil = stracil_faltycznie - odbudowal
            straty_obronca_obrona += (stracil) * (statek.c_met + statek.c_cry)

            pozycja = obronca.cache_obj.get_obrona_p(obronca_planeta.pk, statek.pk)
            punkty_strata = (statek.c_met + statek.c_cry + statek.c_deu) / 1000 * stracil
            obronca_planeta.points_obrona -= punkty_strata
            obronca.userprofile.points_obrona -= punkty_strata
            obronca.userprofile.points -= punkty_strata
            pozycja.ilosc -= stracil

        straty_obronca_statki = 0
        for statek_id in obronca_statki:
            statek = obronca_statki[statek_id]['statek']
            try:
                ilosc = dane_raport.poczatek.obronca_statki[statek_id]['ilosc']
            except:
                ilosc = obronca_statki[statek_id]['ilosc']
            stracil = ilosc - obronca_statki[statek_id]['ilosc']
            straty_obronca_statki += (stracil) * (statek.c_met + statek.c_cry)

            pozycja = obronca.cache_obj.get_flota_p(obronca_planeta.pk, statek.pk)

            punkty_strata = (statek.c_met + statek.c_cry + statek.c_deu) / 1000 * stracil

            obronca_planeta.points_flota -= punkty_strata
            obronca.userprofile.points_flota -= punkty_strata
            obronca.userprofile.points -= punkty_strata
            pozycja.ilosc -= stracil

        straty_agresor_statki = 0
        agresor_flota_powrot = []
        pojemnosc_floty = 0
        for statek_id in agresor_statki:
            statek = agresor_statki[statek_id]['statek']
            try:
                ilosc = dane_raport.poczatek.agresor_statki[statek_id]['ilosc']
            except:
                ilosc = agresor_statki[statek_id]['ilosc']
            stracil = ilosc - agresor_statki[statek_id]['ilosc']
            straty_agresor_statki += (stracil) * (statek.c_met + statek.c_cry)
            agresor_flota_powrot.append("%s,%s" % (statek.pk, agresor_statki[statek_id]['ilosc']))

            pojemnosc_floty += int(statek.capacity) * int(agresor_statki[statek_id]['ilosc'])

            punkty_strata = (statek.c_met + statek.c_cry + statek.c_deu) / 1000 * stracil
            agresor_planeta.points_flota -= punkty_strata
            agresor.userprofile.points_flota -= punkty_strata
            agresor.userprofile.points -= punkty_strata

        zlom_metal = (obronca_zlom_poczatek['met'] - obronca_zlom_koniec['met'] + agresor_zlom_poczatek['met'] -
                      agresor_zlom_koniec['met']) * 0.70

        zlom_crystal = (obronca_zlom_poczatek['cry'] - obronca_zlom_koniec['cry'] + agresor_zlom_poczatek['cry'] -
                        agresor_zlom_koniec['cry']) * 0.70
        zlom = {}
        zlom['metal_agresor'] = agresor_zlom_poczatek['met'] - agresor_zlom_koniec['met']
        zlom['crystal_agresor'] = agresor_zlom_poczatek['cry'] - agresor_zlom_koniec['cry']
        zlom['procent_agresor'] = int(floor((zlom['metal_agresor'] + zlom['crystal_agresor']) / 100000))

        zlom['metal_obronca'] = obronca_zlom_poczatek['met'] - obronca_zlom_koniec[
            'met']  # + obronca_zlom_obrona_poczatek['met']-obronca_zlom_obrona_koniec['met']
        zlom['crystal_obronca'] = obronca_zlom_poczatek['cry'] - obronca_zlom_koniec[
            'cry']  # + obronca_zlom_obrona_poczatek['cry']-obronca_zlom_obrona_koniec['cry']
        zlom['procent_obronca'] = int(floor((zlom['metal_obronca'] + zlom['crystal_obronca']) / 100000))

        zlom['procent'] = zlom['procent_obronca'] + zlom['procent_agresor']

        # ODBUDOWA
        # for odb in odbudowa_obrona:
        #    if int(odb['ilosc'])>0:
        #        msg = odbudowa(odb['statek'],odb['ilosc'], obronca_planeta)

        if (wygrana == 'A'):
            surowce_zdobyte = {}
            if pojemnosc_floty > 0:
                metal = obronca_planeta.metal / 2
                krysztal = obronca_planeta.crystal / 2
                deuter = obronca_planeta.deuter / 2

                surowce_zdobyte['met'] = 0
                surowce_zdobyte['cry'] = 0
                surowce_zdobyte['deu'] = 0
                while 1 == 1:
                    ile_surowcow = 0
                    if metal > 0:
                        ile_surowcow += 1
                    if krysztal > 0:
                        ile_surowcow += 1
                    if deuter > 0:
                        ile_surowcow += 1
                    if ile_surowcow <= 0:
                        break

                    zabieramy_pojedynczego_surowca = pojemnosc_floty / ile_surowcow

                    if metal > 0:
                        if metal > zabieramy_pojedynczego_surowca:
                            surowce_zdobyte['met'] += zabieramy_pojedynczego_surowca
                            pojemnosc_floty -= zabieramy_pojedynczego_surowca
                            metal -= zabieramy_pojedynczego_surowca
                        else:
                            surowce_zdobyte['met'] += metal
                            pojemnosc_floty -= metal
                            metal = 0

                    if krysztal > 0:
                        if krysztal > zabieramy_pojedynczego_surowca:
                            surowce_zdobyte['cry'] += zabieramy_pojedynczego_surowca
                            pojemnosc_floty -= zabieramy_pojedynczego_surowca
                            krysztal -= zabieramy_pojedynczego_surowca
                        else:
                            surowce_zdobyte['cry'] += krysztal
                            pojemnosc_floty -= krysztal
                            krysztal = 0

                    if deuter > 0:
                        if deuter > zabieramy_pojedynczego_surowca:
                            surowce_zdobyte['deu'] += zabieramy_pojedynczego_surowca
                            pojemnosc_floty -= zabieramy_pojedynczego_surowca
                            deuter -= zabieramy_pojedynczego_surowca
                        else:
                            surowce_zdobyte['deu'] += deuter
                            pojemnosc_floty -= deuter
                            deuter = 0

                    pojemnosc_floty = floor(pojemnosc_floty)
                    if pojemnosc_floty <= 0:
                        break

                surowce_zdobyte['met'] = round(surowce_zdobyte['met'])
                surowce_zdobyte['cry'] = round(surowce_zdobyte['cry'])
                surowce_zdobyte['deu'] = round(surowce_zdobyte['deu'])

                obronca_planeta.metal -= surowce_zdobyte['met']
                obronca_planeta.crystal -= surowce_zdobyte['cry']
                obronca_planeta.deuter -= surowce_zdobyte['deu']
        else:
            surowce_zdobyte = {}
            surowce_zdobyte['met'] = 0
            surowce_zdobyte['cry'] = 0
            surowce_zdobyte['deu'] = 0

        obronca_galaktyka.metal += zlom_metal
        obronca_galaktyka.crystal += zlom_crystal

        # tutaj laduje raport
        dane_raport = {"agresor": agresor, "obronca": obronca, "dane": dane_raport, "surowce_zdobyte": surowce_zdobyte,
                       "galaktyka": obronca_galaktyka, "obronca_dane": obronca_dane, "agresor_dane": agresor_dane,
                       "zlom": zlom}
        raporty_fun.rap_atak(dane_raport, flota_atak, wygrana)

        if wygrana != 'O':
            flota_atak.fleet_resource_metal += surowce_zdobyte['met']
            flota_atak.fleet_resource_crystal += surowce_zdobyte['cry']
            flota_atak.fleet_resource_deuterium += surowce_zdobyte['deu']
            flota_atak.fleet_array = ";".join(agresor_flota_powrot)
            helpers.make_fleet_back(flota_atak)
        else:
            flota_atak.delete()
