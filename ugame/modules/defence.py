# -*- coding: utf-8 -*-
from ..generic.cms_metaclass import CmsMetaclass
from ugame.klasy.BaseGame import BaseGame
from ugame.funkcje import Output
from ugame.models.all import Obrona, Obrona_p, Buildings, Obrona_f
from settings import GAME_SPEED
from math import floor
from utils.jinja.filters import pretty_time
from string import split
from time import time
from ugame.topnav import topnav_site


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        GraObject = BaseGame(self)
        current_planet = GraObject.get_current_planet()

        fl = Obrona.objects.all().order_by("id")
        for f in fl:
            key = "id_" + str(f.pk)
            if key in self.request.POST:
                try:
                    ilosc = int(self.request.POST[key])
                    if ilosc > 0:
                        GraObject.buduj_obrone(f, ilosc)
                except:
                    pass
        if "anuluj" in self.request.REQUEST:
            GraObject.anuluj_obrone(self.request.REQUEST['anuluj'])
        floty = []
        for f in fl:
            flota = Output()
            flota.id = f.id
            flota.nazwa = f.nazwa
            flota.opis = f.opis
            flota.energy = None
            flota.c_met = f.c_met
            flota.c_cry = f.c_cry
            flota.c_deu = f.c_deu
            try:
                flota.ilosc = Obrona_p.objects.get(planeta=current_planet, budynek=f).ilosc
            except:
                flota.ilosc = 0

            flota.c_czas = (f.c_cry + f.c_met) / GAME_SPEED
            flota.mozna = 1
            for i in Buildings.objects.filter(minus_czas_flota_tak__gt=0):
                level = floor(GraObject.bud_get_level(current_planet, i.id))
                flota.c_czas = flota.c_czas * eval(i.minus_czas_flota)
            flota.c_czas = pretty_time(int(flota.c_czas * 60 * 60))

            if f.limit > 0:
                try:
                    tmp = Obrona_f.objects.filter(planeta=current_planet, budynek=f)
                    kol_ilosc = 0
                    for q in tmp:
                        kol_ilosc += q.ilosc
                except:
                    kol_ilosc = 0

                if f.limit <= flota.ilosc + kol_ilosc:
                    flota.mozna = None
                    flota.limit_gt = 1

            ile_mozna_tmp = []
            if flota.c_met > 0:
                ile_mozna_tmp.append(floor(current_planet.metal / f.c_met))
            if flota.c_cry > 0:
                ile_mozna_tmp.append(floor(current_planet.crystal / f.c_cry))
            if flota.c_deu > 0:
                ile_mozna_tmp.append(floor(current_planet.deuter / f.c_deu))
            if f.limit > 0:
                ile_mozna_tmp.append(f.limit - (flota.ilosc + kol_ilosc))
            flota.ile_mozna = int(min(ile_mozna_tmp))

            flota.z_met = current_planet.metal - f.c_met
            if flota.z_met < 0:
                flota.mozna = None
                flota.c_met_color = 'red'
            else:
                flota.c_met_color = 'lime'

            flota.z_cry = current_planet.crystal - f.c_cry
            if flota.z_cry < 0:
                flota.mozna = None
                flota.c_cry_color = 'red'
            else:
                flota.c_cry_color = 'lime'

            flota.z_deu = current_planet.deuter - f.c_deu
            if flota.z_deu < 0:
                flota.mozna = None
                flota.c_deu_color = 'red'
            else:
                flota.c_deu_color = 'lime'
            flota.niedodawaj = None
            zaleznosc = split(f.w_bud, ";")
            for zal in zaleznosc:
                budynek = split(zal, ",")
                if len(budynek) > 1:
                    if(int(budynek[1]) > int(GraObject.bud_get_level(current_planet, budynek[0]))):
                        flota.niedodawaj = 1
                        break
            if not flota.niedodawaj:
                zaleznosc = split(f.w_bad, ";")
                for zal in zaleznosc:
                    badanie = split(zal, ",")
                    if len(badanie) > 1:
                        if(int(badanie[1]) > int(GraObject.bad_get_level(GraObject.user, badanie[0]))):
                            flota.niedodawaj = 1
                            break
            if not flota.niedodawaj:
                floty.append(flota)

        try:
            kol = Obrona_f.objects.filter(planeta=current_planet).order_by("time")
            kolejka = []
            czas_minus = time() - 1
            for i in kol:
                time_new = int(i.time - czas_minus)
                czas_minus = i.time

                i.time = pretty_time(time_new)
                i.seconds = time_new
                kolejka.append(i)
        except:
            kolejka = None

        topnav = topnav_site(GraObject)
        return {
                "floty": floty, 'topnav': topnav,
                "kolejka": kolejka,
                }

    site_main.url = "^ugame/defence/$"
