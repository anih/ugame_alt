# -*- coding: utf-8 -*-
from ..generic.cms_metaclass import CmsMetaclass
from ugame.topnav import topnav_site, Output
from ugame.models.all import Buildings, Badania, Budynki_p, Badania_f
from settings import GAME_SPEED
from math import floor
from string import split
from time import time
from utils.jinja.filters import pretty_time


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        current_planet = self.game.get_current_planet()

        if "bud" in self.request.REQUEST:
            self.game.buduj_technologie(self.request.REQUEST['bud'])
        elif "anuluj" in self.request.REQUEST:
            self.game.anuluj_technologie(self.request.REQUEST['anuluj'])

        ts = Badania.objects.all().order_by("id")
        builds = []

        for t in ts:
            tech = Output()
            tech.id = t.id
            tech.nazwa = t.nazwa
            tech.opis = t.opis

            tech.level = self.game.bad_get_level(self.game.user, t.id, 1) + 1
            tech.level_faktyczny = self.game.bad_get_level(self.game.user, t.id)
            tech.c_met = t.c_met * pow(t.c_factor, tech.level - 1)
            tech.c_cry = t.c_cry * pow(t.c_factor, tech.level - 1)
            tech.c_deu = t.c_deu * pow(t.c_factor, tech.level - 1)
            tech.c_ene = t.c_ene * pow(t.c_factor, tech.level - 1)
            tech.c_czas = (tech.c_cry + tech.c_met + tech.c_deu) / GAME_SPEED
            tech.energy = None
            tech.mozna = 1
            for i in Buildings.objects.filter(minus_czas_bad_tak__gt=0):
                budynki_laczy_level = i.badania_set.all()
                if len(budynki_laczy_level) > 0:
                    budynki_laczy_level = budynki_laczy_level[0]
                    # try:
                    if True:
                        ilosc_polaczonych = self.game.user.badania_p_set.filter(badanie=budynki_laczy_level)
                        level = floor(self.game.bud_get_level(current_planet, i.id))
                        if len(ilosc_polaczonych) > 0:
                            ilosc_polaczonych = ilosc_polaczonych[0].level
                            if ilosc_polaczonych > 0:
                                kandydaci = Budynki_p.objects.filter(planeta__owner=self.game.user, budynek=i).exclude(planeta=current_planet).order_by("-level")[:ilosc_polaczonych]
                                for z in kandydaci:
                                    level += floor(z.level)
                    # except:
                    #    level = floor(self.game.bud_get_level(planetrow, i.id))
                else:
                    level = floor(self.game.bud_get_level(current_planet, i.id))
                tech.c_czas = tech.c_czas * (eval(i.minus_czas_bad))
            tech.c_czas = int(tech.c_czas * 60 * 60)
            tech.z_met = current_planet.metal - tech.c_met
            if tech.z_met < 0:
                tech.mozna = None
                tech.c_met_color = 'red'
            else:
                tech.c_met_color = 'lime'

            tech.z_cry = current_planet.crystal - tech.c_cry
            if tech.z_cry < 0:
                tech.mozna = None
                tech.c_cry_color = 'red'
            else:
                tech.c_cry_color = 'lime'

            tech.z_deu = current_planet.deuter - tech.c_deu
            if tech.z_deu < 0:
                tech.mozna = None
                tech.c_deu_color = 'red'
            else:
                tech.c_deu_color = 'lime'
            tech.niedodawaj = None
            zaleznosc = split(t.w_bud, ";")
            for zal in zaleznosc:
                budynek = split(zal, ",")
                if len(budynek) > 1:
                    if(int(budynek[1]) > int(self.game.bud_get_level(current_planet, budynek[0]))):
                        tech.niedodawaj = 1
                        break
            if not tech.niedodawaj:
                zaleznosc = split(t.w_bad, ";")
                for zal in zaleznosc:
                    badanie = split(zal, ",")
                    if len(badanie) > 1:
                        if(int(badanie[1]) > int(self.game.bad_get_level(self.game.user, badanie[0]))):
                            tech.niedodawaj = 1
                            break
                # TODO badania trzeba zrobic
            if not tech.niedodawaj:
                builds.append(tech)

        try:
            kol = Badania_f.objects.filter(user=self.game.user).order_by("time")
            print Badania_f.objects.filter(user=1)
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

        topnav = topnav_site(self.game)
        return {
                "builds": builds, 'topnav': topnav, "kolejka": kolejka
                }
    site_main.url = "^ugame/resources/$"
