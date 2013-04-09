# -*- coding: utf-8 -*-
from ..generic.cms_metaclass import CmsMetaclass
from ugame.klasy.BaseGame import BaseGame
from ugame.topnav import topnav_site, Output
from ugame.models.all import Buildings, Budynki_f
from utils.jinja.filters import pretty_time
from settings import GAME_SPEED
from math import floor
from string import split, find
from time import time


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        GraObject = BaseGame(self)
        if "bud" in self.request.REQUEST:
            GraObject.buduj_budynek(self.request.REQUEST['bud'])
        elif "anuluj" in self.request.REQUEST:
            GraObject.anuluj_budynek(self.request.REQUEST['anuluj'])
        current_planet = GraObject.get_current_planet()

        bs = Buildings.objects.all().order_by("id")
        builds = []
        build = Output()
        for b in bs:
            build = Output()
            build.id = b.id
            build.opis = b.opis
            build.nazwa = b.nazwa
            build.level = GraObject.bud_get_level(current_planet, b.id, 1) + 1
            build.level_faktyczny = GraObject.bud_get_level(current_planet, b.id)
            build.c_met = b.c_met * pow(b.c_factor, build.level - 1)
            build.c_cry = b.c_cry * pow(b.c_factor, build.level - 1)
            build.c_deu = b.c_deu * pow(b.c_factor, build.level - 1)
            build.c_czas = (build.c_cry + build.c_met) / GAME_SPEED
            build.energy = None
            if(build.level > 1):
                build.c_powierzchnia = b.c_powierzchnia_level
            else:
                build.c_powierzchnia = b.c_powierzchnia
            build.mozna = 1
            for i in Buildings.objects.filter(minus_czas_tak__gt=0):
                level = floor(GraObject.bud_get_level(current_planet, i.id))
                build.c_czas = build.c_czas * eval(i.minus_czas, {"__builtins__": None, "pow": pow}, {"level": level})
            build.c_czas = pretty_time(int(build.c_czas * 60 * 60))

            if(int(build.c_powierzchnia) > int(current_planet.powierzchnia_max) - int(current_planet.powierzchnia_zajeta)):
                build.koniec_powierzchni = 1
                build.mozna = None

            build.z_met = current_planet.metal - build.c_met
            if build.z_met < 0:
                build.mozna = None
                build.c_met_color = 'red'
            else:
                build.c_met_color = 'lime'

            build.z_cry = current_planet.crystal - build.c_cry
            if build.z_cry < 0:
                build.mozna = None
                build.c_cry_color = 'red'
            else:
                build.c_cry_color = 'lime'

            build.z_deu = current_planet.deuter - build.c_deu
            if build.z_deu < 0:
                build.mozna = None
                build.c_deu_color = 'red'
            else:
                build.c_deu_color = 'lime'
            build.niedodawaj = None
            zaleznosc = split(b.w_bud, ";")
            for zal in zaleznosc:
                budynek = split(zal, ",")
                if len(budynek) > 1:
                    if(int(budynek[1]) > int(GraObject.bud_get_level(current_planet, budynek[0]))):
                        build.niedodawaj = 1
                        break
            if not build.niedodawaj:
                zaleznosc = split(b.w_bad, ";")
                for zal in zaleznosc:
                    badanie = split(zal, ",")
                    if len(badanie) > 1:
                        if(int(badanie[1]) > int(GraObject.bad_get_level(GraObject.user, badanie[0]))):
                            build.niedodawaj = 1
                            break
            if not build.niedodawaj:
                if find(b.ene_formula, "-") == 0:
                    try:
                        i = b.budynki_p_set.get(planeta=current_planet)
                        level = build.level
                        procent = i.procent
                        energy_next = int(eval(b.ene_formula, {"__builtins__": None, "pow": pow}, {"level": level, "procent": procent}))
                        level = build.level + 1
                        build.energy = (energy_next - int(eval(b.ene_formula, {"__builtins__": None, "pow": pow}, {"level": level, "procent": procent})))
                        if(build.energy > current_planet.energy_max - current_planet.energy_used):
                            build.c_ene_color = "red"
                        else:
                            build.c_ene_color = "lime"
                    except:
                        procent = 100
                        level = build.level
                        build.energy = int(eval(b.ene_formula, {"__builtins__": None, "pow": pow}, {"level": level, "procent": procent}))
                builds.append(build)

        kol = Budynki_f.objects.values_list("pk", flat=True).filter(planeta=current_planet).order_by("time")
        kolejka = []
        czas_minus = time() - 1
        for t in kol:
            i = GraObject.cache_obj.get_budynek_f(current_planet.pk, t)
            time_new = int(i.time - czas_minus)
            czas_minus = i.time
            kolejka.append({"level": i.level, "budynek": i.budynek, "time": pretty_time(time_new), "seconds": time_new})

        topnav = topnav_site(GraObject)
        return {"builds": builds, 'topnav': topnav, "kolejka": kolejka}
    site_main.url = "^ugame/buildings/$"
